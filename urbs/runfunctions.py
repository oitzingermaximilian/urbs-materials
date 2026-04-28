import os
import pyomo.environ
from pyomo.opt.base import SolverFactory
from datetime import datetime, date
from .model import create_model
from .report import *
from .plot import *
from .input import *
from .validation import *
from .saveload import *
from pyomo.opt.results import TerminationCondition, SolverStatus
import gurobipy as gp
from collections import defaultdict
import pyomo.environ as pyomo
import pandas as pd
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def prepare_result_directory(result_name):
    """create a time stamped directory within the result folder."""
    # timestamp for result directory
    now = datetime.now().strftime("%Y%m%dT%H%M")

    # create result directory if not existent
    result_dir = os.path.join("result", "{}-{}".format(result_name, now))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir


def setup_solver(optim, logfile="solver.log"):
    """Configure the solver with high-precision settings."""
    if optim.name == "gurobi":
        optim.set_options("logfile={}".format(logfile))
        # 1. ACCURACY & STABILITY
        optim.set_options("MIPGap=1e-5")
    elif optim.name == "glpk":
        optim.set_options("log={}".format(logfile))
        optim.set_options("--mipgap 0")
        print("✅ GLPK binary tolerance set to 0")

    elif optim.name == "cplex":
        optim.set_options("log={}".format(logfile))
        optim.set_options("mip tolerances integrality 0")
        optim.set_options("mip tolerances mipgap 0")
        print("✅ CPLEX binary tolerance set to 0")

    else:
        print(f"Warning: no options set for solver '{optim.name}'!")

    return optim
# =============================================================================
#  GLOBAL SCALING FACTORS (The "k-Universe")
# =============================================================================
# Quantities are scaled to "Big Units" (GW, kton).
# Money is implicitly scaled to "Thousands" (k€).
#
# PHYSICS:
# 1 GW = 1000 MW  -> Scale Factor 1e-3
# 1 kt = 1000 t   -> Scale Factor 1e-3
#
# ECONOMICS:
# Cost (€/MW) -> k€/GW  : (x 1e-3 money / x 1e-3 power) = 1.0 (No Change)
# Cost (€/t)  -> k€/kt  : (x 1e-3 money / x 1e-3 mass)  = 1.0 (No Change)
# Cost (€/MWh)-> k€/GWh : (x 1e-3 money / x 1e-3 energy)= 1.0 (No Change)
# =============================================================================

GW_SCALE = 1e-3  # Power: MW -> GW / MWh -> GWh
MASS_SCALE = 1e-3  # Mass:  Ton -> kton
COST_SCALE = 1



# =============================================================================
#  GLOBAL HELPER FUNCTIONS (Must be strictly Global to apply scaling correctly)
# =============================================================================

def process_cost_sheet(cost_sheet):
    """
    Processes cost data.
    SCALING: Costs are kept RAW (1.0 factor) to represent k€/unit.
    """
    importcost_dict = {}
    manufacturingcost_dict = {}
    remanufacturingcost_dict = {}
    recyclingcost_dict = {}
    o_and_m_dict = {}

    years = cost_sheet["Stf"].unique()

    for col in cost_sheet.columns:
        if col == "Stf": continue

        parts = col.split("_")
        if len(parts) < 3: continue

        costtype = parts[0]
        location = parts[1]
        process = "_".join(parts[2:])

        for year, value in zip(cost_sheet["Stf"], cost_sheet[col]):
            if year not in years: continue
            key = (year, location, process)

            # --- APPLY SCALING (1.0 for k-Universe) ---
            scaled_val = value * COST_SCALE

            if costtype == "recycling":
                recyclingcost_dict[key] = scaled_val
            elif costtype == "import":
                importcost_dict[key] = scaled_val
            elif costtype == "manufacturing":
                manufacturingcost_dict[key] = scaled_val
            elif costtype == "remanufacturing":
                remanufacturingcost_dict[key] = scaled_val
            elif costtype == "oandm":
                o_and_m_dict[key] = scaled_val

    return (
        importcost_dict,
        manufacturingcost_dict,
        remanufacturingcost_dict,
        recyclingcost_dict,
        o_and_m_dict,
    )


def process_technology_sheet(technologies_data):
    """Processes technology data."""
    technologies_dict = {}
    technologies_data = technologies_data.dropna(subset=["Technologies"])

    for _, row in technologies_data.iterrows():
        tech_full_name = row["Technologies"]
        try:
            location, tech_name = tech_full_name.split(".", 1)
        except ValueError:
            print(f"Skipping invalid entry: {tech_full_name}")
            continue

        tech_attributes = row.drop("Technologies").dropna().to_dict()
        if location not in technologies_dict:
            technologies_dict[location] = {}
        technologies_dict[location][tech_name] = tech_attributes

    return technologies_dict


def process_stocklvl_sheet(sheet_data):
    """Processes stock level. SCALING: MW -> GW"""
    stocklvl_dict = {}
    sheet_data = sheet_data.set_index("Stf")

    for col in sheet_data.columns:
        parts = col.split("_")
        if len(parts) < 2: continue

        location = parts[0]
        # FIX: Capture full name (e.g. 'solarPV_Module')
        tech = "_".join(parts[1:])

        for year, value in sheet_data[col].items():
            # SCALE: MW -> GW
            stocklvl_dict[(year, location, tech)] = value * GW_SCALE

    return stocklvl_dict


def process_installable_capacity_sheet(sheet_data):
    """Processes installable capacity. SCALING: MW -> GW"""
    installable_capacity_dict = {}
    sheet_data = sheet_data.set_index("Stf")

    for col in sheet_data.columns:
        parts = col.split("_")
        if len(parts) < 2: continue

        location = parts[0]
        tech = "_".join(parts[1:])

        for year, value in sheet_data[col].items():
            # SCALE: MW -> GW
            installable_capacity_dict[(year, location, tech)] = value * GW_SCALE

    return installable_capacity_dict


def process_dcr_sheet(sheet_data):
    """Processes DCR (%). No scaling needed."""
    dcr_dict = {}
    sheet_data = sheet_data.set_index("Stf")

    for col in sheet_data.columns:
        parts = col.split("_")
        if len(parts) < 2: continue
        tech = parts[1]
        location = parts[0]

        for year, value in sheet_data[col].items():
            dcr_dict[(year, location, tech)] = value

    return dcr_dict


def process_loadfactors_sheet(sheet_data):
    """Processes load factors (0-1). No scaling needed."""
    loadfactors_dict = {}
    if "Stf" not in sheet_data.columns or "timestep" not in sheet_data.columns:
        raise ValueError("Sheet data must contain 'Stf' (year) and 'Timestep' columns.")

    sheet_data = sheet_data.set_index(["Stf", "timestep"])

    for col in sheet_data.columns:
        parts = col.split("_")
        if len(parts) < 2: continue
        location = parts[0]
        tech = parts[1]

        for (year, timestep), value in sheet_data[col].items():
            loadfactors_dict[(timestep, year, location, tech)] = value
    return loadfactors_dict


def process_gas_block_sheet(sheet_data):
    """
    Processes gas blocks.
    SCALING: Limit MWh -> GWh. Price €/MWh -> k€/GWh (1.0 factor).
    """
    block_limits = {}
    block_prices = {}
    required_cols = ["stf", "block", "limit", "price"]
    for col in required_cols:
        if col not in sheet_data.columns:
            raise ValueError(f"Gas block sheet must have column '{col}'")

    sheet_data["stf"] = sheet_data["stf"].ffill().astype(int)
    block_names = set(sheet_data["block"].astype(str).unique())
    for _, row in sheet_data.iterrows():
        stf = row["stf"]
        block = str(row["block"])

        # SCALING APPLIED
        block_limits[(stf, block)] = float(row["limit"]) * GW_SCALE
        block_prices[(stf, block)] = float(row["price"]) * COST_SCALE

    print(f"Gas Blocks Processed. Scaled Limits to GWh.")
    return block_names, block_limits, block_prices


def load_data_from_excel(file_path):
    """Loads data from Excel and processes all relevant sheets with SCALING."""

    # --- HELPERS ---
    def clean_df_strings(df):
        obj_cols = df.select_dtypes(include=['object']).columns
        for col in obj_cols:
            df[col] = df[col].astype(str).str.strip()
        return df

    def clean_headers(df):
        df.columns = [str(c).strip() for c in df.columns]
        return df

    xls = pd.ExcelFile(file_path)

    # Standard Sheets
    base_data = pd.read_excel(file_path, sheet_name="Base")
    cost_sheet = pd.read_excel(file_path, sheet_name="cost_sheet")
    locations_data = pd.read_excel(file_path, sheet_name="locations")
    loadfactors_data = pd.read_excel(file_path, sheet_name="loadfactors")
    technologies_data = pd.read_excel(file_path, sheet_name="Technologies")
    dcr_data = pd.read_excel(file_path, sheet_name="dcr")
    stocklvl_data = pd.read_excel(file_path, sheet_name="stocklvl")
    installable_capacity_data = pd.read_excel(file_path, sheet_name="installable_capacity")
    gas_block_data = pd.read_excel(file_path, sheet_name="gas_block")

    # Process Gas Blocks
    block_names, block_limits_dict, block_price_dict = process_gas_block_sheet(gas_block_data)

    # Material Sheets
    tech_stage_data = clean_headers(clean_df_strings(pd.read_excel(file_path, "Tech_Stage_Specs")))
    mat_intensity_data = clean_headers(clean_df_strings(pd.read_excel(file_path, "Material_Intensity")))

    # Material Markets
    mat_mining_limit = clean_headers(clean_df_strings(pd.read_excel(file_path, "mining_limit")))
    mat_mining_cost = clean_headers(clean_df_strings(pd.read_excel(file_path, "mining_cost")))
    mat_import_cost_mining = clean_headers(clean_df_strings(pd.read_excel(file_path, "import_cost_mining")))
    energy_transision_factor = clean_headers(clean_df_strings(pd.read_excel(file_path, "energy_transition_factor")))
    conversion_factor_mat = clean_headers(clean_df_strings(pd.read_excel(file_path, "ore_metal_factor")))

    if "Cost_Data" in xls.sheet_names:
        proc_cost_data = clean_headers(clean_df_strings(pd.read_excel(xls, "Cost_Data")))
    else:
        proc_cost_data = pd.DataFrame()

    if "Component_Map" in xls.sheet_names:
        component_map_data = clean_headers(clean_df_strings(pd.read_excel(xls, "Component_Map")))
    else:
        component_map_data = pd.DataFrame()

    # Process Standard Dictionaries (USING GLOBAL SCALED FUNCTIONS)
    technologies_dict = process_technology_sheet(technologies_data)
    stocklvl_dict = process_stocklvl_sheet(stocklvl_data)
    dcr_dict = process_dcr_sheet(dcr_data)
    installable_capacity_dict = process_installable_capacity_sheet(installable_capacity_data)
    loadfactors_dict = process_loadfactors_sheet(loadfactors_data)

    base_params = {
        "y0": int(base_data.loc[base_data["Param"] == "Start Year y0", "Value"].values[0]),
        "y_end": int(base_data.loc[base_data["Param"] == "End Year yn", "Value"].values[0]),
        "hours": int(base_data.loc[base_data["Param"] == "hours per year", "Value"].values[0]),
    }

    # --- 3. PROCESS MATERIAL DATA ---

    # A. Tech Specs (Stages)
    static_tech_specs = {}
    final_stage_map = {}
    valid_tech_stage_list = []

    if not tech_stage_data.empty:
        for _, row in tech_stage_data.iterrows():
            t = row['Technology']
            s = row['Stage']
            valid_tech_stage_list.append((t, s))
            val = str(row.get('is_final_stage', '0')).strip().lower()
            if val in ['1', '1.0', 'true', 'yes', 'y']:
                final_stage_map[t] = s

        valid_tech_stage_list = sorted(list(set(valid_tech_stage_list)))

        tech_stage_data.set_index(['Location', 'Technology', 'Stage'], inplace=True)

        # SCALING APPLIED: Init Cap (MW -> GW), Energy Needs (MWh -> GWh)
        static_tech_specs["init_cap"] = {k: v * GW_SCALE for k, v in tech_stage_data['init_cap'].to_dict().items()}
        static_tech_specs["build_time"] = tech_stage_data['build_time_lag'].to_dict()
        static_tech_specs["energy_needs"] = {k: v * GW_SCALE for k, v in
                                             tech_stage_data['energy_needs'].to_dict().items()}

    # B. Material Intensity
    mat_intensity_dict = {}
    mat_content_dict = {}
    mat_eff_dict = {}

    if not mat_intensity_data.empty:
        # SCALING APPLIED: Tons/MW -> kton/GW.
        # (1e-3 mass / 1e-3 power) = 1.0. NO CHANGE NEEDED.
        # mat_intensity_data['intensity'] *= 1000  <-- REMOVED FOR K-UNIVERSE

        if 'scrap_content' in mat_intensity_data.columns:
            mat_intensity_data['scrap_content'] *= 1

        mat_intensity_dict = mat_intensity_data.set_index(['Technology', 'Stage', 'Material'])[
            'intensity'].to_dict()

        for _, row in mat_intensity_data.iterrows():
            k = (row['Technology'], row['Material'])
            mat_content_dict[k] = mat_content_dict.get(k, 0) + float(row.get('scrap_content', 0))
            mat_eff_dict[k] = float(row.get('rec_efficiency', 0))

    # C. Material Market
    mat_mining_limit_dict = {}
    mat_mining_cost_dict = {}
    mat_import_cost_dict = {}
    mat_conversion_dict = {}
    mat_energy_transision_factor_dict = {}

    tasks = [
        (mat_mining_limit, mat_mining_limit_dict),
        (mat_mining_cost, mat_mining_cost_dict),
        (mat_import_cost_mining, mat_import_cost_dict),
        (conversion_factor_mat, mat_conversion_dict),
        (energy_transision_factor, mat_energy_transision_factor_dict)
    ]

    for df_source, target_dict in tasks:
        if df_source.empty: continue
        df = df_source.copy()
        if 'Stf' in df.columns:
            df['Stf'] = df['Stf'].ffill().astype(int)
            df.rename(columns={'Stf': 'Year'}, inplace=True)

        df_melt = df.melt(id_vars=['Year'], var_name='Material', value_name='Value')
        df_melt['Value'] = pd.to_numeric(
            df_melt['Value'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        )
        df_melt.dropna(subset=['Value'], inplace=True)

        for _, row in df_melt.iterrows():
            year = int(row['Year'])
            mat = str(row['Material']).strip()
            val = row['Value']
            if val > 900000000: continue

            # SCALE LIMITS ONLY
            if target_dict is mat_mining_limit_dict:
                target_dict[(year, mat)] = val * MASS_SCALE
            else:
                target_dict[(year, mat)] = val  # Costs stay raw (k€/kt)

    # SCALING MARKET COSTS: NO CHANGE (Interpret as k€/kt)
    # for k in mat_mining_cost_dict: mat_mining_cost_dict[k] *= MEUR_SCALE <-- REMOVED

    print("✅ Material Market processed (k-Universe).")

    # D. Processing Costs (CAPEX/OPEX - Static)
    proc_capex_dict = {}
    proc_opex_dict = {}
    proc_opex_var_dict = {}
    mat_down_cost_dict = {}

    if not proc_cost_data.empty:
        if 'Year' in proc_cost_data.columns:
            proc_cost_data = proc_cost_data.drop(columns=['Year'])

        target_years = range(2024, 2051)
        expanded_dfs = [proc_cost_data.assign(Year=y) for y in target_years]
        proc_cost_data = pd.concat(expanded_dfs)
        proc_cost_data.set_index(['Year', 'Location', 'Technology', 'Stage'], inplace=True)

        # SCALING APPLIED: EUR/MW -> k€/GW (Factor 1.0)
        proc_capex_dict = (proc_cost_data['capex_base'] * COST_SCALE).to_dict()
        proc_opex_dict = (proc_cost_data['opex_fixed'] * COST_SCALE).to_dict()
        proc_opex_var_dict = (proc_cost_data['opex_var_base'] * COST_SCALE).to_dict()
        mat_down_cost_dict = (proc_cost_data['material_downstream_manufacturing'] * COST_SCALE).to_dict()

        # E. Import Cost Stage
        proc_part_import_dict = {}
        sheet_name = "Import_Cost_Stage"

        if sheet_name in xls.sheet_names:
            import_ts_data = pd.read_excel(xls, sheet_name)
            if 'Stf' in import_ts_data.columns:
                import_ts_data['Stf'] = import_ts_data['Stf'].ffill().astype(int)
                import_ts_data.rename(columns={'Stf': 'Year'}, inplace=True)

            import_ts_data.dropna(subset=['Year'], inplace=True)
            df_melt = import_ts_data.melt(id_vars=['Year'], var_name='Header', value_name='Cost')
            processed_records = []

            for index, row in df_melt.iterrows():
                header = str(row['Header']).strip()
                if header == 'Year': continue

                try:
                    cost = float(str(row['Cost']).replace(',', '.'))
                except:
                    continue  # Skip non-numeric

                # Logic: Split 'solarPV_Polysilicon' into ['solarPV', 'Polysilicon']
                if '_' in header:
                    parts = header.split('_', 1)
                    tech = parts[0]
                    stage = parts[1]

                    # Use COST_SCALE (1.0 for k-Universe)
                    scaled_cost = cost * COST_SCALE

                    processed_records.append({
                        'Year': int(row['Year']),
                        'Location': 'EU27',
                        'Technology': tech,
                        'Stage': stage,
                        'Cost': scaled_cost
                    })

            if processed_records:
                df_final = pd.DataFrame(processed_records)
                proc_part_import_dict = df_final.set_index(['Year', 'Location', 'Technology', 'Stage'])[
                    'Cost'].to_dict()

    # F. BOM
    bom_map_dict = {}
    if not component_map_data.empty:
        bom_map_dict = component_map_data.set_index(['Cons_Tech', 'Cons_Stage', 'Input_Tech', 'Input_Stage'])[
            'Ratio'].to_dict()

    locations_list = locations_data.iloc[:, 0].dropna().tolist()

    # Get process cost dicts (Scaling is done inside process_cost_sheet)
    (
        importcost_dict,
        manufacturingcost_dict,
        remanufacturingcost_dict,
        recyclingcost_dict,
        o_and_m_dict,
    ) = process_cost_sheet(cost_sheet)

    data_urbsextensionv1 = {
        "base_params": base_params,
        "importcost_dict": importcost_dict,  # k€/GW
        "manufacturingcost_dict": manufacturingcost_dict,  # k€/GW
        "remanufacturingcost_dict": remanufacturingcost_dict,  # k€/GW
        "recyclingcost_dict": recyclingcost_dict,  # k€/kt
        "o_and_m_dict": o_and_m_dict,  # k€/GW
        "locations_list": locations_list,
        "loadfactors_dict": loadfactors_dict,
        "technologies": technologies_dict,
        "dcr_dict": dcr_dict,
        "stocklvl_dict": stocklvl_dict,  # GW
        "installable_capacity_dict": installable_capacity_dict,  # GW
        "block_limits": block_limits_dict,  # GWh
        "block_price": block_price_dict,  # k€/GWh
        "block_names": block_names,

        "static_tech_specs": static_tech_specs,  # GW & GWh
        "final_stage_map": final_stage_map,
        "mat_mining_limit_dict": mat_mining_limit_dict,  # kton
        "mat_mining_cost_dict": mat_mining_cost_dict,  # k€/kt
        "mat_import_cost_dict": mat_import_cost_dict,  # k€/kt
        "material_intensity_dict": mat_intensity_dict,  # kton/GW (same as Ton/MW)
        "material_content_dict": mat_content_dict,  # kton/GW
        "recycling_efficiency_dict": mat_eff_dict,
        "processing_stage_cost_dict": proc_capex_dict,  # k€/GW
        "processing_opex_dict": proc_opex_dict,  # k€/GW
        "processing_opex_var_dict": proc_opex_var_dict,  # k€/GW
        "material_downstream_cost_dict": mat_down_cost_dict, #k€/GW
        "part_import_cost_dict": proc_part_import_dict,  # k€/GW
        "bom_map_dict": bom_map_dict,
        "valid_tech_stage_list": valid_tech_stage_list,
        "mining_energy_share_dict": mat_energy_transision_factor_dict,
        "conversion_factor_mat": mat_conversion_dict,
    }

    print("✅ EXTENSION Data loading complete. All units scaled to GW / k€ / kton.")
    return data_urbsextensionv1




def read_scenario_prices(window_start):
    """Read scenario-specific prices and SCALE them to k€."""
    scenario_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "scenario_specific_data.xlsx"
    )
    print(f"\nReading scenario prices for window_start: {window_start}")
    print(f"Looking for file: {scenario_file}")

    try:
        # Read Excel
        import_prices = pd.read_excel(scenario_file, sheet_name="import_prices", index_col="Stf")
        manufacturing_prices = pd.read_excel(scenario_file, sheet_name="manufacturing_prices", index_col="Stf")
        piped_gas_prices = pd.read_excel(scenario_file, sheet_name="piped_gas_prices", index_col="Stf")

        # SCALING FACTORS (Matches Global Constants)
        COST_SCALE_SCENARIO = 1.0  # Input €/MW -> Output k€/GW (1.0)
        GAS_SCALE_SCENARIO = 1.0  # Input €/MWh -> Output k€/GWh (1.0)

        gas_col = f"piped_gas_{window_start}"

        # Apply scaling to Gas
        piped_gas_dict = {}
        if gas_col in piped_gas_prices:
            piped_gas_dict = (piped_gas_prices[gas_col] * GAS_SCALE_SCENARIO).to_dict()

        result = {
            "tech_prices": {},
            "piped_gas": piped_gas_dict
        }

        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        for tech in technologies:
            import_col = f"import_EU27_{tech}_{window_start}"
            manufacturing_col = f"manufacturing_EU27_{tech}_{window_start}"

            # Apply scaling to Tech Costs
            imp_dict = {}
            if import_col in import_prices:
                imp_dict = (import_prices[import_col] * COST_SCALE_SCENARIO).to_dict()

            man_dict = {}
            if manufacturing_col in manufacturing_prices:
                man_dict = (manufacturing_prices[manufacturing_col] * COST_SCALE_SCENARIO).to_dict()

            result["tech_prices"][tech] = {
                "import": imp_dict,
                "manufacturing": man_dict,
            }

        return result

    except Exception as e:
        print(f"Error reading/scaling scenario prices: {str(e)}")
        return {"tech_prices": {}, "piped_gas": {}}


def run_scenario(
        input_files,
        Solver,
        timesteps,
        scenario,
        result_dir,
        dt,
        objective,
        plot_tuples=None,
        plot_sites_name=None,
        plot_periods=None,
        report_tuples=None,
        report_sites_name=None,
        initial_conditions=None,
        window_start=None,
        window_end=None,
        indexlist=None,
        windows=None,
        window_length=None,
):
    """run an urbs model for given input, time steps and scenario"""

    # sets a modeled year for non-intertemporal problems
    year = date.today().year

    # scenario name, read and modify data for scenario
    sce = scenario.__name__
    data = read_input(input_files, year)

    # Load the data from the Excel file (Uses GLOBAL scaled functions now)
    data_urbsextensionv1 = load_data_from_excel("Input_urbsextensionv1.xlsx")

    # Apply Scenario Logic
    data, data_urbsextensionv1 = scenario(data, data_urbsextensionv1.copy())

    validate_input(data)
    validate_dc_objective(data, objective)

    import pandas as pd

    def simple_data_audit(data_urbs, data_ext, filename="simple_audit.xlsx"):
        print("Writing simple audit...")
        with pd.ExcelWriter(filename) as writer:
            # 1. Audit Extension Dicts (Manufacturing, Material, etc.)
            for key, val in data_ext.items():
                if isinstance(val, dict):
                    # Flatten dictionary: Keys become columns, Value becomes the last column
                    df = pd.Series(val).reset_index()
                    # Dynamically rename columns based on number of index levels
                    df.columns = [f'attr_{i}' for i in range(len(df.columns) - 1)] + ['value']

                    sheet_name = str(key)[:30]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            # 2. Audit Energy Data (standard Urbs DataFrames)
            # unittype, demand, etc., are already DataFrames
            if 'unittype' in data_urbs:
                data_urbs['unittype'].to_excel(writer, sheet_name='Base_Tech_Specs')

        print(f"✅ Simple audit saved to {filename}")

    # Usage:
    simple_data_audit(data, data_urbsextensionv1)


    # create model
    prob = create_model(
        data,
        data_urbsextensionv1,
        dt,
        timesteps,
        objective,
        initial_conditions=initial_conditions,
        window_start=window_start,
        window_end=window_end,
        indexlist=indexlist,
    )


    log_filename = os.path.join(result_dir, "{}.log").format(sce)
    # solve model and read results
    optim = SolverFactory("gurobi")  #

    optim = setup_solver(optim, logfile=log_filename)


    result = optim.solve(prob, tee=True)

    # --- NEW: PRINT QUALITY CHECKS ---
    print("\n" + "=" * 30)
    print("   NUMERICAL QUALITY CHECK")
    print("=" * 30)

    if hasattr(optim, '_solver_model'):
        try:
            optim._solver_model.printQuality()
        except:
            pass

    # Check solver termination condition
    if str(result.solver.termination_condition) != "optimal":
        print(f"Solver termination condition: {result.solver.termination_condition}")

        if result.solver.termination_condition == TerminationCondition.infeasibleOrUnbounded:
            print("Model is either infeasible or unbounded. Proceeding with IIS analysis...")
            lp_file_path = os.path.abspath("model.lp")
            prob.write(lp_file_path, io_options={"symbolic_solver_labels": True})
            print(f"Pyomo model written to LP file: {lp_file_path}")

            try:
                gurobi_model = gp.read(lp_file_path)
                print("Gurobi model loaded successfully.")
                gurobi_model.computeIIS()
                iis_file_path = os.path.abspath("model_iis.ilp")
                gurobi_model.write(iis_file_path)
                print(f"IIS written to file: {iis_file_path}")
            except Exception as e:
                print(f"Error computing IIS: {e}")

            # RETURN EARLY TO PREVENT CRASH
            return prob
    else:
        print("Model is feasible and solved to optimality.")

    report(
        prob,
        os.path.join(result_dir, "{}.xlsx").format(sce),
        report_tuples=report_tuples,
        report_sites_name=report_sites_name,
    )

    result_figures(
        prob,
        os.path.join(result_dir, "{}".format(sce)),
        timesteps,
        plot_title_prefix=sce.replace("_", " "),
        plot_tuples=plot_tuples,
        plot_sites_name=plot_sites_name,
        periods=plot_periods,
        figure_size=(24, 9),
    )

    return prob
