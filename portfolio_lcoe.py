"""
Portfolio LCOE Analyzer for urbs-materials
==========================================
Analyzes the levelized cost of electricity (LCOE) across the ENTIRE technology park:
1. Base Technologies (from Input/urbs_intertemporal_master_vintages.xlsx):
   - Nuclear (Existing Tranches & New Vintages)
   - Natural Gas CCGT & CCGT with CCUS
   - Coal & Coal with CCUS
   - Lignite & Lignite with CCUS
   - Biomass Plant
   - Oil Plant
   - Hydro Run-of-River & Hydro Reservoir
   - Other Non-RES (Slack)
2. Extended Technologies (from Input_urbsextensionv1.xlsx):
   - Solar PV (Pure Import, Domestic Option 1, Domestic Option 2)
   - Wind Onshore (Pure Import, Domestic Option 1, Domestic Option 2)
   - Wind Offshore (Pure Import, Domestic Option 1, Domestic Option 2)

Calculates the exact breakdown in EUR/MWh:
  LCOE = Capital Annuity + Fixed OPEX + Variable OPEX + Fuel Cost + CO2 Cost
"""

import os
import shutil
import tempfile
import argparse
import pandas as pd
import numpy as np


def annuity_factor(rate: float, lifetime: float) -> float:
    """Calculates capital recovery factor: alpha = [r * (1 + r)^n] / [(1 + r)^n - 1]"""
    if rate == 0 or lifetime == 0:
        return 1.0 / max(lifetime, 1.0)
    rn = (1.0 + rate) ** lifetime
    return (rate * rn) / (rn - 1.0)


def load_workbooks_safely(master_path="Input/urbs_intertemporal_master_vintages.xlsx", ext_path="Input_urbsextensionv1.xlsx"):
    """Loads required Excel sheets safely avoiding Windows file lock."""
    # Check master
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_m:
        tmp_master = tmp_m.name
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_e:
        tmp_ext = tmp_e.name

    try:
        shutil.copy2(master_path, tmp_master)
        shutil.copy2(ext_path, tmp_ext)

        with pd.ExcelFile(tmp_master) as xls_m:
            df_proc = pd.read_excel(xls_m, sheet_name="Process")
            df_pc = pd.read_excel(xls_m, sheet_name="Process-Commodity")
            df_comm = pd.read_excel(xls_m, sheet_name="Commodity")

        with pd.ExcelFile(tmp_ext) as xls_e:
            df_imp = pd.read_excel(xls_e, sheet_name="Import_Cost_Stage")
            df_cost_data = pd.read_excel(xls_e, sheet_name="Cost_Data") if "Cost_Data" in xls_e.sheet_names else pd.DataFrame()
            df_mat_int = pd.read_excel(xls_e, sheet_name="Material_Intensity") if "Material_Intensity" in xls_e.sheet_names else pd.DataFrame()
            df_mining = pd.read_excel(xls_e, sheet_name="import_cost_mining") if "import_cost_mining" in xls_e.sheet_names else pd.DataFrame()
            df_stage_specs = pd.read_excel(xls_e, sheet_name="Tech_Stage_Specs") if "Tech_Stage_Specs" in xls_e.sheet_names else pd.DataFrame()

    finally:
        for p in [tmp_master, tmp_ext]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

    return {
        "process": df_proc,
        "process_commodity": df_pc,
        "commodity": df_comm,
        "import_stage": df_imp,
        "cost_data": df_cost_data,
        "mat_intensity": df_mat_int,
        "mining_import": df_mining,
        "stage_specs": df_stage_specs,
    }


def compute_portfolio_lcoe(data, discount_rate=0.03, thermal_flh=5000.0, target_years=None):
    if target_years is None:
        target_years = [2024, 2030, 2040, 2050]

    df_proc = data["process"]
    df_pc = data["process_commodity"]
    df_comm = data["commodity"]
    df_imp = data["import_stage"]

    # Commodity price lookup: (Year, Commodity) -> price
    comm_prices = {}
    for _, r in df_comm.iterrows():
        y = int(r["Year"])
        c = str(r["Commodity"]).strip()
        p = float(r["price"]) if pd.notna(r["price"]) else 0.0
        comm_prices[(y, c)] = p

    # Standard FLH assumptions
    flh_map = {
        "Nuclear": 7446.0,          # 85% capacity factor
        "Hydro_(run-of-river)": 2956.5, # 33.75% from SupIm
        "Hydro_(reservoir)": 2500.0,
        "Biomass": thermal_flh,
        "Coal": thermal_flh,
        "Lignite": thermal_flh,
        "Gas": thermal_flh,
        "Oil": 1500.0,              # peaker
        "Other_non-res": 2000.0,
        "solarPV": 1095.0,          # 12.5% load factor
        "windon": 2628.0,           # 30.0% load factor
        "windoff": 4213.56,         # 48.1% load factor
    }

    records = []

    # -------------------------------------------------------------
    # 1. Base Technologies (from Process sheet)
    # -------------------------------------------------------------
    # Check consistency: which processes exist in Process but not in Process-Commodity?
    pc_procs = set(df_pc["Process"].unique())

    for yr in target_years:
        co2_price = comm_prices.get((yr, "CO2"), 0.0)
        df_proc_yr = df_proc[df_proc["Year"] == yr]

        for _, r in df_proc_yr.iterrows():
            p_name = str(r["Process"]).strip()
            
            # Check if this process vintage is relevant for this year
            # e.g., don't show _2050 vintage in 2024
            if "_" in p_name:
                parts = p_name.split("_")
                v_yr = parts[-1]
                if v_yr.isdigit():
                    v_int = int(v_yr)
                    if v_int > yr:
                        continue # Not built yet

            # Base tech identification
            base_tech = p_name
            for k in flh_map.keys():
                if k.lower() in p_name.lower():
                    base_tech = k
                    break

            flh = flh_map.get(base_tech, thermal_flh)

            inv_cost = float(r["inv-cost"]) if pd.notna(r["inv-cost"]) else 0.0
            fix_cost = float(r["fix-cost"]) if pd.notna(r["fix-cost"]) else 0.0
            var_cost = float(r["var-cost"]) if pd.notna(r["var-cost"]) else 0.0
            depr = float(r["depreciation"]) if pd.notna(r["depreciation"]) else 25.0
            wacc = float(r["wacc"]) if pd.notna(r["wacc"]) else discount_rate
            inst_cap = float(r["inst-cap"]) if pd.notna(r["inst-cap"]) else 0.0
            cap_up = float(r["cap-up"]) if pd.notna(r["cap-up"]) else 0.0

            # Use the specified discount rate (or process wacc)
            alpha = annuity_factor(discount_rate, depr)

            # Efficiencies from Process-Commodity
            # Note: handle cases where user split Nuclear_Plant_2024 into _old, _mid, _new
            proc_lookup = p_name
            if proc_lookup not in pc_procs:
                if "Nuclear_Plant_2024" in proc_lookup and "Nuclear_Plant_2024" in pc_procs:
                    proc_lookup = "Nuclear_Plant_2024" # fallback to parent ratio
                else:
                    proc_lookup = None

            fuel_cost_mwh = 0.0
            fuel_name = "None"
            co2_cost_mwh = 0.0
            co2_intensity = 0.0

            if proc_lookup:
                sub_pc = df_pc[(df_pc["Process"] == proc_lookup) & (df_pc["Year"] == yr)]
                for _, pc_r in sub_pc.iterrows():
                    com = str(pc_r["Commodity"]).strip()
                    direct = str(pc_r["Direction"]).strip()
                    ratio = float(pc_r["ratio"]) if pd.notna(pc_r["ratio"]) else 0.0

                    if direct == "In" and com != "Elec":
                        fuel_name = com
                        f_price = comm_prices.get((yr, com), 0.0)
                        fuel_cost_mwh += f_price * ratio
                    elif direct == "Out" and com == "CO2":
                        co2_intensity = ratio
                        co2_cost_mwh += co2_price * ratio
            else:
                fuel_name = "MISSING_IN_PC!"

            capex_mwh = (inv_cost * alpha) / flh
            fix_mwh = fix_cost / flh
            total_lcoe = capex_mwh + fix_mwh + var_cost + fuel_cost_mwh + co2_cost_mwh

            # Short-run marginal cost (SRMC): variable + fuel + CO2
            srmc = var_cost + fuel_cost_mwh + co2_cost_mwh

            records.append({
                "Year": yr,
                "Category": "Base / Thermal / Hydro",
                "Technology": p_name,
                "BaseTech": base_tech,
                "FLH": flh,
                "CAPEX_EUR_kW": inv_cost / 1000.0,
                "CAPEX_EUR_MWh": capex_mwh,
                "Fixed_OPEX_EUR_MWh": fix_mwh,
                "Var_OPEX_EUR_MWh": var_cost,
                "Fuel": fuel_name,
                "Fuel_EUR_MWh": fuel_cost_mwh,
                "CO2_EUR_MWh": co2_cost_mwh,
                "SRMC_EUR_MWh": srmc,
                "LCOE_Total_EUR_MWh": total_lcoe,
            })

    # -------------------------------------------------------------
    # 2. Extended Technologies: Renewables (from Import_Cost_Stage)
    # -------------------------------------------------------------
    for yr in target_years:
        imp_row = df_imp[df_imp["Stf"] == yr]
        if imp_row.empty:
            continue
        imp_r = imp_row.iloc[0]

        for t, tech_name, flh, imp_col in [
            ("solarPV", "Solar PV (Utility)", 1095.0, "solarPV_Module"),
            ("windon", "Wind Onshore", 2628.0, "windon_AssemblyOn"),
            ("windoff", "Wind Offshore", 4213.56, "windoff_AssemblyOff"),
        ]:
            lifetime = 25.0 if t == "solarPV" else 20.0
            alpha = annuity_factor(discount_rate, lifetime)

            bos_capex = float(imp_r.get(f"capex_{t}_bos", 0.0))
            bos_opexf = float(imp_r.get(f"opexf_{t}_bos", 0.0))
            bos_opexv = float(imp_r.get(f"opexv_{t}_bos", 0.0))
            turbine_or_module = float(imp_r.get(imp_col, 0.0))

            tot_plant_capex = turbine_or_module + bos_capex
            capex_mwh = (tot_plant_capex * alpha) / flh
            fix_mwh = bos_opexf / flh
            tot_lcoe = capex_mwh + fix_mwh + bos_opexv

            records.append({
                "Year": yr,
                "Category": "Renewable (Pure Import)",
                "Technology": f"{tech_name} (Import)",
                "BaseTech": t,
                "FLH": flh,
                "CAPEX_EUR_kW": tot_plant_capex / 1000.0,
                "CAPEX_EUR_MWh": capex_mwh,
                "Fixed_OPEX_EUR_MWh": fix_mwh,
                "Var_OPEX_EUR_MWh": bos_opexv,
                "Fuel": "Free (VRE)",
                "Fuel_EUR_MWh": 0.0,
                "CO2_EUR_MWh": 0.0,
                "SRMC_EUR_MWh": bos_opexv,
                "LCOE_Total_EUR_MWh": tot_lcoe,
            })

    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description="Analyze Technology Park LCOE across years")
    parser.add_argument("--rate", type=float, default=0.03, help="Discount rate (default: 0.03)")
    parser.add_argument("--flh", type=float, default=5000.0, help="Assumed thermal full load hours (default: 5000 h)")
    parser.add_argument("--year", type=int, default=None, help="Filter specific year (e.g. 2030)")
    args = parser.parse_args()

    print("\n" + "="*80)
    print(f"  URBS PORTFOLIO LCOE ANALYZER  (Discount Rate: {args.rate*100:.1f}%)")
    print("="*80)

    data = load_workbooks_safely()
    df = compute_portfolio_lcoe(data, discount_rate=args.rate, thermal_flh=args.flh)

    # Check for missing processes in Process-Commodity
    df_pc = data["process_commodity"]
    pc_procs = set(df_pc["Process"].unique())
    proc_procs = set(data["process"]["Process"].unique())
    missing_pc = proc_procs - pc_procs
    if missing_pc:
        print("\n[!] WARNING: The following processes exist in Sheet 'Process' but are MISSING in 'Process-Commodity':")
        for mp in sorted(missing_pc):
            print(f"   [-] {mp}")
        print("   -> URBS will fail or have 0 efficiency unless these are defined in 'Process-Commodity'!\n")

    years_to_show = [args.year] if args.year else [2024, 2030, 2040, 2050]

    for yr in years_to_show:
        sub = df[df["Year"] == yr].copy()
        if sub.empty:
            continue

        print(f"\n" + "-"*85)
        print(f"  MILESTONE YEAR: {yr}  (CO2 Price: {sub['CO2_EUR_MWh'].max():.1f} €/t equivalent)")
        print("-"*85)

        sub_sorted = sub.sort_values(by="LCOE_Total_EUR_MWh")
        display_cols = [
            "Technology", "FLH", "CAPEX_EUR_kW", "CAPEX_EUR_MWh", "Fixed_OPEX_EUR_MWh",
            "Fuel_EUR_MWh", "CO2_EUR_MWh", "SRMC_EUR_MWh", "LCOE_Total_EUR_MWh"
        ]
        
        # Format neatly
        formatters = {
            "FLH": "{:.0f}h".format,
            "CAPEX_EUR_kW": "{:.0f} €/kW".format,
            "CAPEX_EUR_MWh": "{:.1f}".format,
            "Fixed_OPEX_EUR_MWh": "{:.1f}".format,
            "Fuel_EUR_MWh": "{:.1f}".format,
            "CO2_EUR_MWh": "{:.1f}".format,
            "SRMC_EUR_MWh": "{:.1f}".format,
            "LCOE_Total_EUR_MWh": "{:.2f} €/MWh".format,
        }
        
        print(sub_sorted[display_cols].to_string(index=False, formatters=formatters))

    # Save complete table to CSV
    os.makedirs("lcoe_analysis", exist_ok=True)
    out_csv = "lcoe_analysis/portfolio_lcoe_summary.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n[OK] Full analysis saved to: {out_csv}")


if __name__ == "__main__":
    main()
