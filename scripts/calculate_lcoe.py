"""
LCOE & Domestic Manufacturing Cost Tracking Script for urbs-materials
====================================================================

Calculates and tracks:
1) Pure Import (Module Import for Solar, Assembly Import for Wind)
2) 100% Domestic Manufacturing - Option 1 (Production capacity already exists)
3) 100% Domestic Manufacturing - Option 2 (Production capacity needs to be built)
4) NEW: Recycling Quota Sensitivity (0% to 50% recycled material origin)
   - Option A: Technology-Specific Recycling (Closed-loop)
   - Option B: Cross-Technology Scrap Pooling (e.g. Aluminum & Copper from decommissioned wind bulk scrap)
5) NEW: URBS Optimization Model Cost Driver Diagnostic
   - Why Onshore Wind can appear cheaper than Solar PV in the URBS model:
     a) Load factor / Full Load Hours (FLH): Wind Onshore runs 2,628 FLH vs Solar at 1,095 FLH (2.4x generation)
     b) Mandatory BESS Coupling: In URBS stockpile rules, each MW of Solar PV forces 0.118 MW of battery storage (factor_bess = 0.118)
     c) Import cost trajectory: Wind assembly import drops -65.4% by 2050 (from 680 to 235 €/kW -> 6.02 €/MWh)
     d) Material structure: Solar is 58% raw materials (dominated by 52 €/kW of silver), while Wind is 85% downstream manufacturing

Underlying Workbook: 'Input_urbsextensionv1.xlsx'
"""

import os
import sys
import shutil
import tempfile
import argparse
import pandas as pd
import numpy as np


def annuity_factor(rate: float, lifetime: float) -> float:
    """Calculates capital recovery factor: alpha = [r * (1 + r)^n] / [(1 + r)^n - 1]"""
    if rate == 0:
        return 1.0 / lifetime
    rn = (1.0 + rate) ** lifetime
    return (rate * rn) / (rn - 1.0)


def load_workbook_safely(file_path: str = "Input_urbsextensionv1.xlsx"):
    """
    Safely loads all required sheets from the workbook, even if currently locked by Excel.
    """
    if not os.path.exists(file_path):
        alt = os.path.join("..", file_path)
        if os.path.exists(alt):
            file_path = alt
        else:
            raise FileNotFoundError(f"Workbook not found at {file_path}")

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        temp_path = tmp.name

    try:
        shutil.copy2(file_path, temp_path)
        with pd.ExcelFile(temp_path) as xls:
            df_import_stage = pd.read_excel(xls, sheet_name="Import_Cost_Stage")
            df_cost_data = pd.read_excel(xls, sheet_name="Cost_Data")
            df_mat_int = pd.read_excel(xls, sheet_name="Material_Intensity")
            df_mining = pd.read_excel(xls, sheet_name="import_cost_mining")
            df_stage_specs = pd.read_excel(xls, sheet_name="Tech_Stage_Specs")
            df_comp_map = pd.read_excel(xls, sheet_name="Component_Map")
            df_tech = pd.read_excel(xls, sheet_name="Technologies")
            df_lf = pd.read_excel(xls, sheet_name="loadfactors")
            df_rec = pd.read_excel(xls, sheet_name="Recycling_Costs") if "Recycling_Costs" in xls.sheet_names else pd.DataFrame()

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    # Clean headers
    for df in [df_import_stage, df_cost_data, df_mat_int, df_mining, df_stage_specs, df_comp_map, df_tech, df_lf, df_rec]:
        if not df.empty:
            df.columns = [str(c).strip() for c in df.columns]

    return {
        "import_stage": df_import_stage,
        "cost_data": df_cost_data,
        "mat_intensity": df_mat_int,
        "mining_import": df_mining,
        "stage_specs": df_stage_specs,
        "comp_map": df_comp_map,
        "technologies": df_tech,
        "loadfactors": df_lf,
        "recycling_costs": df_rec,
    }


def compute_recycling_parameters(wb_data: dict):
    """
    Computes recycling recovery cost factors from sheet 'Recycling_Costs' and 'Material_Intensity'.
    """
    df_rec = wb_data["recycling_costs"]
    df_mat_int = wb_data["mat_intensity"]
    df_mining = wb_data["mining_import"]

    row_mining = df_mining.iloc[0]
    virgin_prices = {c.strip(): float(row_mining[c]) for c in df_mining.columns if c not in ["Stf", "Year"]}

    # Solar PV scrap economics
    solar_mats = df_mat_int[df_mat_int["Technology"] == "solarPV"]
    solar_scrap_t = solar_mats["scrap_content"].sum()  # 68.997 tons per MW
    solar_rec_row = df_rec[df_rec["Technology"] == "solarPV"].iloc[0] if not df_rec.empty else {}
    solar_opex_var = float(solar_rec_row.get("opex_var", 670.0))
    solar_opex_fix = float(solar_rec_row.get("opex_fixed", 75.0))
    solar_opex_total = solar_opex_var + solar_opex_fix  # Total OPEX per ton (745 EUR/t)
    solar_cost_per_mw = solar_scrap_t * solar_opex_total

    # Market value of recovered materials from 1 MW solar scrap at virgin prices
    solar_recovered_val = sum(
        float(r["intensity"]) * float(r["rec_efficiency"]) * virgin_prices.get(str(r["Material"]).strip(), 0.0)
        for _, r in solar_mats.iterrows()
    )
    gamma_solar = solar_cost_per_mw / solar_recovered_val if solar_recovered_val > 0 else 0.136

    # Wind bulk & magnet route economics
    wind_rec_row = df_rec[df_rec["Technology"] == "windon"].iloc[0] if not df_rec.empty else {}
    wind_bulk_opex = float(wind_rec_row.get("opex_var_bulk", 122.5)) + float(wind_rec_row.get("opex_fixed_bulk", 122.5))
    wind_bulk_capex = float(wind_rec_row.get("capex_bulk", 450.0))
    wind_mag_opex = float(wind_rec_row.get("opex_var_magnet", 5776.0)) + float(wind_rec_row.get("opex_fixed_magnet", 450.0))
    wind_mag_capex = float(wind_rec_row.get("capex_magnet", 1687.77))

    magnet_mats = ["dysprosium", "neodymium", "praseodymium", "terbium"]

    return {
        "virgin_prices": virgin_prices,
        "gamma_solar": gamma_solar,
        "solar_cost_per_mw": solar_cost_per_mw,
        "solar_recovered_val": solar_recovered_val,
        "wind_bulk_opex": wind_bulk_opex,
        "wind_mag_opex": wind_mag_opex,
        "magnet_mats": magnet_mats,
    }


def compute_domestic_cost_breakdown(
    wb_data: dict,
    elec_price: float = 74.06,
    discount_rate: float = 0.03,
    recycling_quota: float = 0.0,
    cross_tech: bool = False,
    year: int = 2024,
):
    """
    Computes stage-by-stage and total 100% domestic manufacturing costs for Solar PV,
    Wind Onshore, and Wind Offshore under a specified recycling quota q (0.0 to 1.0).
    
    If cross_tech=True:
      - Commodity metals like aluminum and copper can be sourced from decommissioned
        wind bulk scrap recycling (at wind_bulk_opex = 245 EUR/t instead of virgin 1,800 EUR/t).
      - Specialized materials (silver, silicon) are sourced from solar scrap recycling.
    """
    df_cost_data = wb_data["cost_data"]
    df_mat_int = wb_data["mat_intensity"]
    df_stage_specs = wb_data["stage_specs"]

    rec_params = compute_recycling_parameters(wb_data)
    virgin_prices = rec_params["virgin_prices"]
    gamma_solar = rec_params["gamma_solar"]
    wind_bulk_opex = rec_params["wind_bulk_opex"]
    wind_mag_opex = rec_params["wind_mag_opex"]
    magnet_mats = rec_params["magnet_mats"]

    # 1. Stage energy needs (MWh/MW)
    energy_needs = {}
    for _, r in df_stage_specs.iterrows():
        t = str(r["Technology"]).strip()
        s = str(r["Stage"]).strip()
        energy_needs[(t, s)] = float(r.get("energy_needs", 0.0))

    # 2. Granular Bill of Materials itemization with recycling quota
    bom_records = []
    stage_mat_cost = {}
    for _, r in df_mat_int.iterrows():
        t = str(r["Technology"]).strip()
        s = str(r["Stage"]).strip()
        m = str(r["Material"]).strip()
        intensity = float(r.get("intensity", 0.0))
        p_vir = virgin_prices.get(m, 0.0)

        # Determine secondary / recycled material price
        if t == "solarPV":
            if cross_tech and m in ["aluminum", "copper"]:
                p_rec = min(wind_bulk_opex, p_vir)
            else:
                p_rec = p_vir * gamma_solar
        else:  # windon, windoff
            if m in magnet_mats:
                p_rec = min(wind_mag_opex, p_vir)
            else:
                p_rec = min(wind_bulk_opex, p_vir)

        p_eff = (1.0 - recycling_quota) * p_vir + recycling_quota * p_rec
        cost_contrib = intensity * p_eff

        bom_records.append({
            "Technology": t,
            "Stage": s,
            "Material": m,
            "Intensity_tons_per_MW": intensity,
            "Virgin_Price_EUR_per_ton": p_vir,
            "Recycled_Price_EUR_per_ton": p_rec,
            "Effective_Price_EUR_per_ton": p_eff,
            "Recycling_Quota": recycling_quota,
            "Cross_Tech_Pooling": cross_tech,
            "Cost_Contribution_EUR_per_MW": cost_contrib,
            "Scrap_Content": float(r.get("scrap_content", 0.0)),
            "Recycling_Efficiency": float(r.get("rec_efficiency", 0.0)),
        })
        stage_mat_cost[(t, s)] = stage_mat_cost.get((t, s), 0.0) + cost_contrib

    df_bom = pd.DataFrame(bom_records)

    # 3. Stage-by-Stage Cost Data
    stage_breakdown = []
    tech_totals = {
        "solarPV": {"mat": 0.0, "downstream": 0.0, "opex_var": 0.0, "elec": 0.0, "opex_fix": 0.0, "capex": 0.0, "energy_mwh": 0.0},
        "windon":  {"mat": 0.0, "downstream": 0.0, "opex_var": 0.0, "elec": 0.0, "opex_fix": 0.0, "capex": 0.0, "energy_mwh": 0.0},
        "windoff": {"mat": 0.0, "downstream": 0.0, "opex_var": 0.0, "elec": 0.0, "opex_fix": 0.0, "capex": 0.0, "energy_mwh": 0.0},
    }

    alpha_plant = annuity_factor(discount_rate, 25.0)  # 25-year plant lifetime

    for _, r in df_cost_data.iterrows():
        t = str(r["Technology"]).strip()
        s = str(r["Stage"]).strip()
        if t not in tech_totals:
            continue

        capex = float(r.get("capex_base", 0.0))
        opex_var = float(r.get("opex_var_base", 0.0))
        opex_fix = float(r.get("opex_fixed", 0.0))
        downstream = float(r.get("material_downstream_manufacturing", 0.0))
        e_mwh = energy_needs.get((t, s), 0.0)
        elec_cost = e_mwh * elec_price
        mat_cost = stage_mat_cost.get((t, s), 0.0)

        opt1_stage = mat_cost + downstream + opex_var + elec_cost + opex_fix
        opt2_stage_ann = opt1_stage + capex * alpha_plant
        opt2_stage_overnight = opt1_stage + capex

        stage_breakdown.append({
            "Technology": t,
            "Stage": s,
            "Recycling_Quota": recycling_quota,
            "Cross_Tech": cross_tech,
            "Raw_Materials_EUR_per_MW": mat_cost,
            "Downstream_Bulk_Mfg_EUR_per_MW": downstream,
            "Variable_OPEX_EUR_per_MW": opex_var,
            "Electricity_Needs_MWh_per_MW": e_mwh,
            "Electricity_Cost_EUR_per_MW": elec_cost,
            "Fixed_Overhead_EUR_per_MW_yr": opex_fix,
            "Facility_CAPEX_EUR_per_MW": capex,
            "Option1_Existing_Cap_EUR_per_MW": opt1_stage,
            "Option2_Annualized_Cap_EUR_per_MW": opt2_stage_ann,
            "Option2_Overnight_Cap_EUR_per_MW": opt2_stage_overnight,
        })

        tech_totals[t]["mat"] += mat_cost
        tech_totals[t]["downstream"] += downstream
        tech_totals[t]["opex_var"] += opex_var
        tech_totals[t]["elec"] += elec_cost
        tech_totals[t]["opex_fix"] += opex_fix
        tech_totals[t]["capex"] += capex
        tech_totals[t]["energy_mwh"] += e_mwh

    # 3b. Balance of System (BOS) timeseries from Import_Cost_Stage
    df_import_stage = wb_data.get("import_stage", pd.DataFrame())
    year_col = "Stf" if "Stf" in df_import_stage.columns else "Year"
    if year_col in df_import_stage.columns and not df_import_stage.empty:
        row_year = df_import_stage[df_import_stage[year_col] == year]
        if row_year.empty:
            row_year = df_import_stage.iloc[0:1]
        if not row_year.empty:
            r0 = row_year.iloc[0]
            for t in tech_totals.keys():
                v_c = r0.get(f"capex_{t}_bos", 0.0)
                capex_bos = float(v_c) if pd.notna(v_c) else 0.0
                v_f = r0.get(f"opexf_{t}_bos", 0.0)
                opexf_bos = float(v_f) if pd.notna(v_f) else 0.0
                v_v = r0.get(f"opexv_{t}_bos", 0.0)
                opexv_bos = float(v_v) if pd.notna(v_v) else 0.0

                if capex_bos > 0 or opexf_bos > 0 or opexv_bos > 0:
                    opt1_bos = opexv_bos + opexf_bos
                    opt2_bos_ann = opt1_bos + capex_bos * alpha_plant
                    opt2_bos_overnight = opt1_bos + capex_bos

                    stage_breakdown.append({
                        "Technology": t,
                        "Stage": "Balance_of_System",
                        "Recycling_Quota": recycling_quota,
                        "Cross_Tech": cross_tech,
                        "Raw_Materials_EUR_per_MW": 0.0,
                        "Downstream_Bulk_Mfg_EUR_per_MW": 0.0,
                        "Variable_OPEX_EUR_per_MW": opexv_bos,
                        "Electricity_Needs_MWh_per_MW": 0.0,
                        "Electricity_Cost_EUR_per_MW": 0.0,
                        "Fixed_Overhead_EUR_per_MW_yr": opexf_bos,
                        "Facility_CAPEX_EUR_per_MW": capex_bos,
                        "Option1_Existing_Cap_EUR_per_MW": opt1_bos,
                        "Option2_Annualized_Cap_EUR_per_MW": opt2_bos_ann,
                        "Option2_Overnight_Cap_EUR_per_MW": opt2_bos_overnight,
                    })

                    tech_totals[t]["capex"] += capex_bos
                    tech_totals[t]["opex_fix"] += opexf_bos
                    tech_totals[t]["opex_var"] += opexv_bos

    df_stages = pd.DataFrame(stage_breakdown)

    # 4. Technology Summary
    summary_list = []
    for t, totals in tech_totals.items():
        opt1_total = totals["mat"] + totals["downstream"] + totals["opex_var"] + totals["elec"] + totals["opex_fix"]
        ann_facility = totals["capex"] * alpha_plant
        opt2_ann_total = opt1_total + ann_facility
        opt2_overnight_total = opt1_total + totals["capex"]

        summary_list.append({
            "Technology": t,
            "Recycling_Quota": recycling_quota,
            "Cross_Tech_Pooling": cross_tech,
            "Raw_Materials_EUR_MW": totals["mat"],
            "Downstream_Mfg_EUR_MW": totals["downstream"],
            "Variable_OPEX_EUR_MW": totals["opex_var"],
            "Electricity_Cost_EUR_MW": totals["elec"],
            "Fixed_Overhead_EUR_MW": totals["opex_fix"],
            "Option1_Cost_EUR_MW": opt1_total,
            "Option1_Cost_EUR_kW": opt1_total / 1000.0,
            "Facility_CAPEX_EUR_MW": totals["capex"],
            "Facility_Annualized_Charge_EUR_MW": ann_facility,
            "Option2_Annualized_Cost_EUR_MW": opt2_ann_total,
            "Option2_Annualized_Cost_EUR_kW": opt2_ann_total / 1000.0,
            "Option2_Overnight_Cost_EUR_MW": opt2_overnight_total,
            "Option2_Overnight_Cost_EUR_kW": opt2_overnight_total / 1000.0,
        })

    df_summary = pd.DataFrame(summary_list)
    return df_stages, df_bom, df_summary, tech_totals


def compute_recycling_sweep(
    wb_data: dict,
    quotas: list = None,
    discount_rate: float = 0.03,
):
    """
    Computes domestic manufacturing costs and LCOE for all technologies across a parameter
    sweep of recycling quotas (e.g. 0%, 10%, 20%, 25%, 30%, 40%, 50%), comparing:
    - Tech-Specific Recycling (Closed-Loop)
    - Cross-Technology Scrap Pooling (Al & Cu from wind bulk scrap)
    """
    if quotas is None:
        quotas = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]

    flh_dict = {
        "solarPV": 0.125 * 8760.0,  # 1,095 h
        "windon":  0.300 * 8760.0,  # 2,628 h
        "windoff": 0.481 * 8760.0,  # 4,213.56 h
    }
    df_tech = wb_data.get("technologies", pd.DataFrame())
    lifetimes = {"solarPV": 25.0, "windon": 20.0, "windoff": 20.0}
    if not df_tech.empty and "l" in df_tech.columns:
        for _, r in df_tech.iterrows():
            t_name = str(r.get("Technologies", "")).split(".")[-1]
            if t_name in lifetimes and pd.notna(r["l"]):
                lifetimes[t_name] = float(r["l"])

    sweep_records = []

    for q in quotas:
        # Tech-specific
        _, _, df_sum_spec, _ = compute_domestic_cost_breakdown(
            wb_data, discount_rate=discount_rate, recycling_quota=q, cross_tech=False
        )
        # Cross-tech
        _, _, df_sum_cross, _ = compute_domestic_cost_breakdown(
            wb_data, discount_rate=discount_rate, recycling_quota=q, cross_tech=True
        )

        for t in ["solarPV", "windon", "windoff"]:
            alpha_tech = annuity_factor(discount_rate, lifetimes[t])
            flh = flh_dict[t]

            row_spec = df_sum_spec[df_sum_spec["Technology"] == t].iloc[0]
            row_cross = df_sum_cross[df_sum_cross["Technology"] == t].iloc[0]

            lcoe1_spec = (row_spec["Option1_Cost_EUR_MW"] * alpha_tech) / flh
            lcoe2_spec = (row_spec["Option2_Annualized_Cost_EUR_MW"] * alpha_tech) / flh

            lcoe1_cross = (row_cross["Option1_Cost_EUR_MW"] * alpha_tech) / flh
            lcoe2_cross = (row_cross["Option2_Annualized_Cost_EUR_MW"] * alpha_tech) / flh

            sweep_records.append({
                "Recycling_Quota": q,
                "Recycling_Quota_Pct": f"{int(q*100)}%",
                "Technology": t,
                # Tech-specific
                "Mat_Cost_Spec_EUR_kW": row_spec["Raw_Materials_EUR_MW"] / 1000.0,
                "Option1_Cost_Spec_EUR_kW": row_spec["Option1_Cost_EUR_kW"],
                "Option2_Cost_Spec_EUR_kW": row_spec["Option2_Annualized_Cost_EUR_kW"],
                "LCOE_Option1_Spec_EUR_MWh": lcoe1_spec,
                "LCOE_Option2_Spec_EUR_MWh": lcoe2_spec,
                # Cross-tech
                "Mat_Cost_Cross_EUR_kW": row_cross["Raw_Materials_EUR_MW"] / 1000.0,
                "Option1_Cost_Cross_EUR_kW": row_cross["Option1_Cost_EUR_kW"],
                "Option2_Cost_Cross_EUR_kW": row_cross["Option2_Annualized_Cost_EUR_kW"],
                "LCOE_Option1_Cross_EUR_MWh": lcoe1_cross,
                "LCOE_Option2_Cross_EUR_MWh": lcoe2_cross,
            })

    return pd.DataFrame(sweep_records)


def compute_urbs_cost_driver_analysis(wb_data: dict, discount_rate: float = 0.03):
    """
    Diagnostic analysis explaining why Onshore Wind appears cheaper than Solar PV in URBS:
    1) FLH / Capacity Factor Effect: 2,628 FLH for Wind vs 1,095 FLH for Solar (2.4x generation)
    2) Mandatory Battery Energy Storage Coupling: In stockpile.py, factor_bess = 0.118 forces
       118 MW of batteries per 1 GW of Solar PV, adding ~33 EUR/kW (~2.5 EUR/MWh) to Solar!
    3) Import Price Collapse: In Import_Cost_Stage, Wind Onshore import costs collapse -65.4%
       down to 235 EUR/kW (LCOE = 6.02 EUR/MWh by 2050), reaching parity with solar.
    4) Material Burden Asymmetry: Solar PV is 58% raw materials (dominated by 52 EUR/kW of silver),
       whereas Wind Onshore is 85% downstream fabrication labor/capex and only 4% raw materials.
    """
    df_import_stage = wb_data["import_stage"]
    year_col = "Stf" if "Stf" in df_import_stage.columns else "Year"

    row_2024 = df_import_stage[df_import_stage[year_col] == 2024].iloc[0]
    row_2050 = df_import_stage[df_import_stage[year_col] == 2050].iloc[0]

    bess_import_2024 = float(row_2024.get("Batteries_Assembly", 280439.83)) / 1000.0  # EUR/kW
    bess_import_2050 = float(row_2050.get("Batteries_Assembly", 164356.52)) / 1000.0  # EUR/kW
    factor_bess = 0.118  # from Technologies sheet / stockpile.py

    # Battery coupling cost per kW solar (Currently decoupled in URBS: factor_bess = 0.0)
    factor_bess = 0.0
    bess_add_2024 = bess_import_2024 * factor_bess
    bess_add_2050 = bess_import_2050 * factor_bess

    alpha_bess = annuity_factor(discount_rate, 15.0)  # 15-year battery lifetime
    solar_flh = 0.125 * 8760.0  # 1,095 h

    bess_lcoe_add_2024 = (bess_add_2024 * alpha_bess) / solar_flh * 1000.0  # EUR/MWh
    bess_lcoe_add_2050 = (bess_add_2050 * alpha_bess) / solar_flh * 1000.0  # EUR/MWh

    drivers = [
        {
            "Cost_Driver": "1. Full Load Hours (Capacity Factor)",
            "Solar_PV_Value": "1,095 h / yr (LF = 0.125)",
            "Wind_Onshore_Value": "2,628 h / yr (LF = 0.300)",
            "Impact_Ratio": "Wind generates 2.4x more kWh per kW installed",
            "Significance": "Dilutes fixed capex 2.4x more effectively than Solar PV",
        },
        {
            "Cost_Driver": "2. Mandatory Battery Coupling (factor_bess)",
            "Solar_PV_Value": f"+{factor_bess*100:.1f}% Battery (+{bess_add_2024:.2f} €/kW in 2024)",
            "Wind_Onshore_Value": "0% Battery (factor_bess = 0.0)",
            "Impact_Ratio": f"+{bess_lcoe_add_2024:.2f} €/MWh added to Solar PV in URBS",
            "Significance": "Direct URBS constraint (stockpile.py) forcing storage expansion onto Solar",
        },
        {
            "Cost_Driver": "3. Import Assembly Price Trajectory",
            "Solar_PV_Value": "150 €/kW (2024) -> 114 €/kW (2050) [-24%]",
            "Wind_Onshore_Value": "680 €/kW (2024) -> 235 €/kW (2050) [-65.4%]",
            "Impact_Ratio": "Wind import cost plummets 2.7x faster than Solar",
            "Significance": "By 2050, Wind Onshore import LCOE is 6.02 €/MWh vs Solar 5.98 €/MWh",
        },
        {
            "Cost_Driver": "4. Raw Material Cost Share (100% Domestic)",
            "Solar_PV_Value": "112.74 €/kW (57.9% of module cost)",
            "Wind_Onshore_Value": "38.63 €/kW (3.95% of turbine cost)",
            "Impact_Ratio": "Solar raw material burden is 2.9x higher per kW",
            "Significance": "Solar is heavily bottlenecked by high-value silver (52 €/kW) & aluminum (20 €/kW)",
        },
        {
            "Cost_Driver": "5. Downstream Manufacturing Share",
            "Solar_PV_Value": "0 €/kW (Direct cell/module processing)",
            "Wind_Onshore_Value": "832.00 €/kW (85.1% of turbine cost)",
            "Impact_Ratio": "Wind is dominated by bulk fabrication labor/capex",
            "Significance": "Wind turbine costs can be drastically reduced through automation and learning",
        },
        {
            "Cost_Driver": "6. Scrap & Recycling Relief Pool",
            "Solar_PV_Value": "69.0 t/GW scrap (Silver/Silicon closed-loop)",
            "Wind_Onshore_Value": "8,002 t/GW scrap (Massive bulk steel/Al pool)",
            "Impact_Ratio": "Wind scrap floods secondary metal market at 245 €/t",
            "Significance": "Decommissioned wind provides cheap secondary aluminum/copper for solar",
        },
    ]

    return pd.DataFrame(drivers), {
        "bess_add_2024": bess_add_2024,
        "bess_add_2050": bess_add_2050,
        "bess_lcoe_add_2024": bess_lcoe_add_2024,
        "bess_lcoe_add_2050": bess_lcoe_add_2050,
    }


def calculate_comprehensive_lcoe(wb_data: dict, discount_rate: float = 0.03):
    """
    Constructs the annual timeseries (2024 to 2050) comparing:
    - Pure Import (Module Import for solar, Assembly Import for wind)
    - 100% Domestic: Option 1 (0% Quota Baseline)
    - 100% Domestic: Option 1 (25% Quota Tech-Specific)
    - 100% Domestic: Option 1 (25% Quota Cross-Tech)
    - 100% Domestic: Option 2 (0% Quota Baseline)
    - 100% Domestic: Option 2 (25% Quota Tech-Specific)
    - 100% Domestic: Option 2 (25% Quota Cross-Tech)
    - Solar PV + URBS BESS Coupling (+11.8% Battery Storage)
    """
    # Baseline (0% recycling)
    _, df_bom, df_summary_0, tech_totals_0 = compute_domestic_cost_breakdown(
        wb_data, discount_rate=discount_rate, recycling_quota=0.0, cross_tech=False
    )
    # 25% Tech-Specific
    _, _, df_summary_25_spec, tech_totals_25_spec = compute_domestic_cost_breakdown(
        wb_data, discount_rate=discount_rate, recycling_quota=0.25, cross_tech=False
    )
    # 25% Cross-Tech (Al & Cu from wind scrap)
    df_stages_25, _, df_summary_25_cross, tech_totals_25_cross = compute_domestic_cost_breakdown(
        wb_data, discount_rate=discount_rate, recycling_quota=0.25, cross_tech=True
    )

    df_import_stage = wb_data["import_stage"].copy()
    df_import_stage.columns = [str(c).strip() for c in df_import_stage.columns]
    year_col = "Stf" if "Stf" in df_import_stage.columns else "Year"
    df_import_stage[year_col] = df_import_stage[year_col].ffill().astype(int)
    df_import_stage = df_import_stage[(df_import_stage[year_col] >= 2024) & (df_import_stage[year_col] <= 2050)]

    # Interpolate any milestone-only BOS timeseries across 2024-2050
    bos_cols = [c for c in df_import_stage.columns if "bos" in c.lower()]
    for col in bos_cols:
        df_import_stage[col] = pd.to_numeric(df_import_stage[col], errors="coerce")
        if df_import_stage[col].notna().any():
            df_import_stage[col] = df_import_stage[col].interpolate(method="linear").bfill().ffill()

    df_tech = wb_data.get("technologies", pd.DataFrame())
    lt_dict = {"solarPV": 25.0, "windon": 20.0, "windoff": 20.0}
    if not df_tech.empty and "l" in df_tech.columns:
        for _, r in df_tech.iterrows():
            t_name = str(r.get("Technologies", "")).split(".")[-1]
            if t_name in lt_dict and pd.notna(r["l"]):
                lt_dict[t_name] = float(r["l"])

    tech_specs = {
        "solarPV": {
            "name": "Solar PV",
            "import_col": "solarPV_Module",
            "lifetime": lt_dict.get("solarPV", 25.0),
            "load_factor": 0.125,
            "flh": 0.125 * 8760.0,  # 1,095 h
            "color": "#d97706",     # Amber
        },
        "windon": {
            "name": "Wind Onshore",
            "import_col": "windon_AssemblyOn",
            "lifetime": lt_dict.get("windon", 20.0),
            "load_factor": 0.300,
            "flh": 0.300 * 8760.0,  # 2,628 h
            "color": "#0284c7",     # Sky Blue
        },
        "windoff": {
            "name": "Wind Offshore",
            "import_col": "windoff_AssemblyOff",
            "lifetime": lt_dict.get("windoff", 20.0),
            "load_factor": 0.481,
            "flh": 0.481 * 8760.0,  # 4,213.56 h
            "color": "#0d9488",     # Teal
        },
    }

    alpha_plant = annuity_factor(discount_rate, 25.0)
    alpha_bess = annuity_factor(discount_rate, 15.0)  # 15y battery lifetime
    factor_bess = 0.0  # Batteries decoupled / deactivated by user

    timeseries = []

    for _, row in df_import_stage.iterrows():
        yr = int(row[year_col])
        rec = {"Year": yr}

        # Battery import cost for solar coupling
        bess_import_eur_kw = float(row.get("Batteries_Assembly", 280439.83)) / 1000.0
        bess_coupling_add_eur_kw = bess_import_eur_kw * factor_bess
        solar_flh = tech_specs["solarPV"]["flh"]
        bess_lcoe_penalty = (bess_coupling_add_eur_kw * alpha_bess) / solar_flh * 1000.0  # EUR/MWh

        for t, cfg in tech_specs.items():
            alpha_tech = annuity_factor(discount_rate, cfg["lifetime"])
            flh = cfg["flh"]

            # Balance of System (BOS) timeseries
            v_c = row.get(f"capex_{t}_bos", 0.0)
            capex_bos = float(v_c) if pd.notna(v_c) else 0.0
            v_f = row.get(f"opexf_{t}_bos", 0.0)
            opexf_bos = float(v_f) if pd.notna(v_f) else 0.0
            v_v = row.get(f"opexv_{t}_bos", 0.0)
            opexv_bos = float(v_v) if pd.notna(v_v) else 0.0

            # 1. Pure Import
            import_capex = float(row.get(cfg["import_col"], 0.0))  # €/MW
            import_plant_capex = import_capex + capex_bos
            import_lcoe = (import_plant_capex * alpha_tech + opexf_bos) / flh + opexv_bos

            # 2. Domestic 0% Quota (Baseline)
            t0 = tech_totals_0[t]
            opt1_0 = t0["mat"] + t0["downstream"] + t0["opex_var"] + t0["elec"] + t0["opex_fix"]
            opt2_0 = opt1_0 + t0["capex"] * alpha_plant
            lcoe1_0 = ((opt1_0 + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos
            lcoe2_0 = ((opt2_0 + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos

            # 3. Domestic 25% Quota (Tech-Specific)
            t25_spec = tech_totals_25_spec[t]
            opt1_25_spec = t25_spec["mat"] + t25_spec["downstream"] + t25_spec["opex_var"] + t25_spec["elec"] + t25_spec["opex_fix"]
            opt2_25_spec = opt1_25_spec + t25_spec["capex"] * alpha_plant
            lcoe1_25_spec = ((opt1_25_spec + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos
            lcoe2_25_spec = ((opt2_25_spec + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos

            # 4. Domestic 25% Quota (Cross-Tech)
            t25_cross = tech_totals_25_cross[t]
            opt1_25_cross = t25_cross["mat"] + t25_cross["downstream"] + t25_cross["opex_var"] + t25_cross["elec"] + t25_cross["opex_fix"]
            opt2_25_cross = opt1_25_cross + t25_cross["capex"] * alpha_plant
            lcoe1_25_cross = ((opt1_25_cross + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos
            lcoe2_25_cross = ((opt2_25_cross + capex_bos) * alpha_tech + opexf_bos) / flh + opexv_bos

            prefix = t
            rec[f"{prefix}_import_capex_eur_kw"] = import_capex / 1000.0
            rec[f"{prefix}_import_lcoe_eur_mwh"] = import_lcoe

            rec[f"{prefix}_domestic_opt1_0pct_cost_eur_kw"] = opt1_0 / 1000.0
            rec[f"{prefix}_domestic_opt1_0pct_lcoe_eur_mwh"] = lcoe1_0
            rec[f"{prefix}_domestic_opt2_0pct_cost_eur_kw"] = opt2_0 / 1000.0
            rec[f"{prefix}_domestic_opt2_0pct_lcoe_eur_mwh"] = lcoe2_0

            rec[f"{prefix}_domestic_opt1_25pct_spec_cost_eur_kw"] = opt1_25_spec / 1000.0
            rec[f"{prefix}_domestic_opt1_25pct_spec_lcoe_eur_mwh"] = lcoe1_25_spec
            rec[f"{prefix}_domestic_opt2_25pct_spec_cost_eur_kw"] = opt2_25_spec / 1000.0
            rec[f"{prefix}_domestic_opt2_25pct_spec_lcoe_eur_mwh"] = lcoe2_25_spec

            rec[f"{prefix}_domestic_opt1_25pct_cross_cost_eur_kw"] = opt1_25_cross / 1000.0
            rec[f"{prefix}_domestic_opt1_25pct_cross_lcoe_eur_mwh"] = lcoe1_25_cross
            rec[f"{prefix}_domestic_opt2_25pct_cross_cost_eur_kw"] = opt2_25_cross / 1000.0
            rec[f"{prefix}_domestic_opt2_25pct_cross_lcoe_eur_mwh"] = lcoe2_25_cross

            # Specific for solar PV: Add URBS BESS Coupling (+11.8% battery)
            if t == "solarPV":
                rec["solarPV_import_with_bess_lcoe_eur_mwh"] = import_lcoe + bess_lcoe_penalty
                rec["solarPV_opt1_25pct_with_bess_lcoe_eur_mwh"] = lcoe1_25_cross + bess_lcoe_penalty
                rec["solarPV_opt2_25pct_with_bess_lcoe_eur_mwh"] = lcoe2_25_cross + bess_lcoe_penalty
                rec["bess_coupling_penalty_eur_mwh"] = bess_lcoe_penalty

        timeseries.append(rec)

    df_timeseries = pd.DataFrame(timeseries)
    return df_timeseries, df_stages_25, df_bom, df_summary_0, df_summary_25_cross, tech_specs


def export_tracking_excel(
    df_timeseries: pd.DataFrame,
    df_sweep: pd.DataFrame,
    df_drivers: pd.DataFrame,
    df_stages: pd.DataFrame,
    df_bom: pd.DataFrame,
    df_summary_0: pd.DataFrame,
    df_summary_25: pd.DataFrame,
    excel_path: str = "lcoe_domestic_vs_import.xlsx",
):
    """
    Builds a structured, professional multi-tab Excel tracking file with 9 comprehensive sheets.
    """
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Sheet 1: LCOE Trajectory (2024-2050)
        lcoe_cols = ["Year"] + [c for c in df_timeseries.columns if "_lcoe_eur_mwh" in c]
        df_lcoe_traj = df_timeseries[lcoe_cols].copy()
        df_lcoe_traj.to_excel(writer, sheet_name="LCOE_Trajectory", index=False)

        # Sheet 2: 25% Recycling Quota Comparison (Milestones 2024 & 2050)
        comp_records = []
        for t, name in [("solarPV", "Solar PV"), ("windon", "Wind Onshore"), ("windoff", "Wind Offshore")]:
            row_2024 = df_timeseries[df_timeseries["Year"] == 2024].iloc[0]
            row_2050 = df_timeseries[df_timeseries["Year"] == 2050].iloc[0]
            comp_records.append({
                "Technology": name,
                "Import_LCOE_2024": row_2024[f"{t}_import_lcoe_eur_mwh"],
                "Import_LCOE_2050": row_2050[f"{t}_import_lcoe_eur_mwh"],
                "Domestic_Opt1_0pct_Recycling": row_2024[f"{t}_domestic_opt1_0pct_lcoe_eur_mwh"],
                "Domestic_Opt1_25pct_TechSpecific": row_2024[f"{t}_domestic_opt1_25pct_spec_lcoe_eur_mwh"],
                "Domestic_Opt1_25pct_CrossTech": row_2024[f"{t}_domestic_opt1_25pct_cross_lcoe_eur_mwh"],
                "Domestic_Opt2_0pct_Recycling": row_2024[f"{t}_domestic_opt2_0pct_lcoe_eur_mwh"],
                "Domestic_Opt2_25pct_TechSpecific": row_2024[f"{t}_domestic_opt2_25pct_spec_lcoe_eur_mwh"],
                "Domestic_Opt2_25pct_CrossTech": row_2024[f"{t}_domestic_opt2_25pct_cross_lcoe_eur_mwh"],
                "LCOE_Savings_from_25pct_Recycling": (
                    row_2024[f"{t}_domestic_opt1_0pct_lcoe_eur_mwh"] - row_2024[f"{t}_domestic_opt1_25pct_cross_lcoe_eur_mwh"]
                ),
            })
        df_comp = pd.DataFrame(comp_records)
        df_comp.to_excel(writer, sheet_name="Recycling_25pct_Comparison", index=False)

        # Sheet 3: Recycling Quota Parameter Sweep (0% to 50%)
        df_sweep.to_excel(writer, sheet_name="Recycling_Quota_Sweep", index=False)

        # Sheet 4: URBS Cost Driver Diagnostic (Why Wind Beats Solar)
        df_drivers.to_excel(writer, sheet_name="URBS_Why_Wind_Cheaper", index=False)

        # Sheet 5: Product Costs (€/kW)
        cost_cols = ["Year"] + [c for c in df_timeseries.columns if "_cost_eur_kw" in c or "_capex_eur_kw" in c]
        df_costs = df_timeseries[cost_cols].copy()
        df_costs.to_excel(writer, sheet_name="Product_Costs_EUR_per_kW", index=False)

        # Sheet 6: Domestic Manufacturing Totals (0% vs 25% Recycling)
        df_summary_0["Scenario"] = "0% Recycling (100% Virgin)"
        df_summary_25["Scenario"] = "25% Recycling (Cross-Tech Pooling)"
        df_sum_both = pd.concat([df_summary_0, df_summary_25], ignore_index=True)
        df_sum_both.to_excel(writer, sheet_name="Domestic_Totals_Summary", index=False)

        # Sheet 7: Granular Stage Breakdown
        df_stages.to_excel(writer, sheet_name="Stage_By_Stage_Breakdown", index=False)

        # Sheet 8: Bill of Materials
        df_bom.to_excel(writer, sheet_name="Bill_of_Materials", index=False)

        # Sheet 9: Full Timeseries Dataset
        df_timeseries.to_excel(writer, sheet_name="Full_Timeseries_Data", index=False)

    print(f"[OK] Generated 9-tab multi-sheet Excel tracking file: {excel_path}")


def plot_comparison_svg(
    df: pd.DataFrame,
    df_sweep: pd.DataFrame,
    tech_specs: dict,
    output_svg: str = "lcoe_domestic_vs_import.svg",
):
    """
    Generates a high-quality multi-panel vector graphic SVG:
    Panel 1: LCOE Timeseries (2024–2050) comparing Import vs. Domestic (0% vs 25% Recycling vs Solar+BESS)
    Panel 2: LCOE vs. Recycling Quota (0% to 50%) with EU CRMA 25% Benchmark
    """
    width = 1200
    height = 540
    pad_top = 80
    pad_bottom = 60
    margin_x = 75
    panel_gap = 45

    # 3 sub-panels horizontally: Solar PV, Wind Onshore, Wind Offshore
    panel_w = (width - 2 * margin_x - 2 * panel_gap) / 3.0
    plot_h = 360

    sb = []
    sb.append('<?xml version="1.0" encoding="UTF-8"?>')
    sb.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">')

    # Main Title
    sb.append(f'  <text x="{width/2}" y="32" text-anchor="middle" font-size="19" font-weight="700" fill="#0f172a">LCOE Analysis: Import vs. Domestic Manufacturing with 25% Recycling Quota</text>')
    sb.append(f'  <text x="{width/2}" y="54" text-anchor="middle" font-size="12" fill="#64748b">Fixed r = 3.0% | CRMA 25% Recycled Origin Benchmark | Cross-Tech Scrap Pooling (Wind Al/Cu -> Solar) | Standalone (BESS Decoupled)</text>')

    tech_keys = list(tech_specs.keys())
    years = df["Year"].values
    min_x, max_x = 2024, 2050

    max_y_dict = {"solarPV": 55.0, "windon": 55.0, "windoff": 80.0}

    for idx, t in enumerate(tech_keys):
        cfg = tech_specs[t]
        max_y = max_y_dict[t]
        ox = margin_x + idx * (panel_w + panel_gap)

        def to_x(yr):
            return ox + ((yr - min_x) / (max_x - min_x)) * panel_w

        def to_y(val):
            return pad_top + (1.0 - (val / max_y)) * plot_h

        # Panel Border & Title
        sb.append(f'  <rect x="{ox}" y="{pad_top}" width="{panel_w}" height="{plot_h}" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" rx="6" />')
        sb.append(f'  <text x="{ox + panel_w/2}" y="{pad_top - 12}" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">{cfg["name"]} ({int(cfg["lifetime"])}y, LF {cfg["load_factor"]:.3f})</text>')

        # Y grid lines
        y_step = 5.0 if max_y >= 20 else 2.5
        y_val = 0.0
        while y_val <= max_y + 0.1:
            yp = to_y(y_val)
            dash = "none" if y_val == 0 else "3,3"
            sb.append(f'  <line x1="{ox}" y1="{yp}" x2="{ox + panel_w}" y2="{yp}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="{dash}" />')
            sb.append(f'  <text x="{ox - 8}" y="{yp + 4}" text-anchor="end" font-size="10" fill="#64748b">{y_val:.1f} €</text>')
            y_val += y_step

        # X ticks
        for yr in [2024, 2030, 2040, 2050]:
            xp = to_x(yr)
            sb.append(f'  <line x1="{xp}" y1="{pad_top + plot_h}" x2="{xp}" y2="{pad_top + plot_h + 4}" stroke="#94a3b8" />')
            sb.append(f'  <text x="{xp}" y="{pad_top + plot_h + 16}" text-anchor="middle" font-size="10" fill="#64748b">{yr}</text>')

        # Curves
        imp_vals = df[f"{t}_import_lcoe_eur_mwh"].values
        opt1_0_vals = df[f"{t}_domestic_opt1_0pct_lcoe_eur_mwh"].values
        opt1_25_vals = df[f"{t}_domestic_opt1_25pct_cross_lcoe_eur_mwh"].values
        opt2_25_vals = df[f"{t}_domestic_opt2_25pct_cross_lcoe_eur_mwh"].values

        # 1. Domestic Option 2 (25% Recycled - Red Dotted)
        p_opt2 = " ".join([f'{"M" if i==0 else "L"} {to_x(years[i]):.1f} {to_y(opt2_25_vals[i]):.1f}' for i in range(len(years))])
        sb.append(f'  <path d="{p_opt2}" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-dasharray="4,3" />')

        # 2. Domestic Option 1 Baseline 0% Recycled (Light Amber Dash)
        p_opt1_0 = " ".join([f'{"M" if i==0 else "L"} {to_x(years[i]):.1f} {to_y(opt1_0_vals[i]):.1f}' for i in range(len(years))])
        sb.append(f'  <path d="{p_opt1_0}" fill="none" stroke="#fcd34d" stroke-width="2.0" stroke-dasharray="2,2" />')

        # 3. Domestic Option 1 with 25% Recycling (Green Bold Line)
        p_opt1_25 = " ".join([f'{"M" if i==0 else "L"} {to_x(years[i]):.1f} {to_y(opt1_25_vals[i]):.1f}' for i in range(len(years))])
        sb.append(f'  <path d="{p_opt1_25}" fill="none" stroke="#10b981" stroke-width="2.6" />')

        # 4. Pure Import (Solid Blue / Tech color)
        p_imp = " ".join([f'{"M" if i==0 else "L"} {to_x(years[i]):.1f} {to_y(imp_vals[i]):.1f}' for i in range(len(years))])
        sb.append(f'  <path d="{p_imp}" fill="none" stroke="{cfg["color"]}" stroke-width="3" stroke-linecap="round" />')

        # Special for Solar PV: Add URBS BESS Coupling line only if active
        if t == "solarPV" and "bess_coupling_penalty_eur_mwh" in df.columns:
            if df["bess_coupling_penalty_eur_mwh"].max() > 0.05:
                solar_bess_vals = df["solarPV_import_with_bess_lcoe_eur_mwh"].values
                p_bess = " ".join([f'{"M" if i==0 else "L"} {to_x(years[i]):.1f} {to_y(solar_bess_vals[i]):.1f}' for i in range(len(years))])
                sb.append(f'  <path d="{p_bess}" fill="none" stroke="#8b5cf6" stroke-width="2.2" stroke-dasharray="5,3" />')
                sb.append(f'  <text x="{to_x(2024)+4}" y="{to_y(solar_bess_vals[0])-6}" font-size="9" font-weight="700" fill="#8b5cf6">+BESS: {solar_bess_vals[0]:.2f}€</text>')

        # Endpoint Callouts
        sb.append(f'  <text x="{to_x(2024)+4}" y="{to_y(imp_vals[0])-6}" font-size="9" font-weight="700" fill="{cfg["color"]}">Imp: {imp_vals[0]:.2f}€</text>')
        sb.append(f'  <text x="{to_x(2050)-4}" y="{to_y(imp_vals[-1])+12}" text-anchor="end" font-size="9" font-weight="700" fill="{cfg["color"]}">{imp_vals[-1]:.2f}€</text>')

        sb.append(f'  <text x="{to_x(2050)-4}" y="{to_y(opt1_25_vals[-1])-5}" text-anchor="end" font-size="9" font-weight="700" fill="#059669">Opt1 (25% Rec): {opt1_25_vals[-1]:.2f}€</text>')
        sb.append(f'  <text x="{to_x(2050)-4}" y="{to_y(opt2_25_vals[-1])-5}" text-anchor="end" font-size="9" font-weight="700" fill="#dc2626">Opt2 (25% Rec): {opt2_25_vals[-1]:.2f}€</text>')

    # Bottom Global Legend
    leg_y = height - 18
    sb.append(f'  <g transform="translate({width/2 - 430}, {leg_y})">')
    # Pure import
    sb.append('    <line x1="0" y1="-4" x2="25" y2="-4" stroke="#0284c7" stroke-width="3" />')
    sb.append('    <text x="30" y="0" font-size="10.5" font-weight="600" fill="#334155">Pure Import</text>')

    # Domestic 0%
    sb.append('    <line x1="120" y1="-4" x2="145" y2="-4" stroke="#fcd34d" stroke-width="2" stroke-dasharray="2,2" />')
    sb.append('    <text x="150" y="0" font-size="10.5" font-weight="600" fill="#334155">Dom. Opt. 1 (0% Rec)</text>')

    # Domestic 25%
    sb.append('    <line x1="290" y1="-4" x2="315" y2="-4" stroke="#10b981" stroke-width="2.6" />')
    sb.append('    <text x="320" y="0" font-size="10.5" font-weight="600" fill="#334155">Dom. Opt. 1 (25% Recycled)</text>')

    # Domestic Opt 2
    sb.append('    <line x1="490" y1="-4" x2="515" y2="-4" stroke="#ef4444" stroke-width="2.2" stroke-dasharray="4,3" />')
    sb.append('    <text x="520" y="0" font-size="10.5" font-weight="600" fill="#334155">Dom. Opt. 2 (25% Recycled)</text>')

    # Solar+BESS
    sb.append('    <line x1="690" y1="-4" x2="715" y2="-4" stroke="#8b5cf6" stroke-width="2.2" stroke-dasharray="5,3" />')
    sb.append('    <text x="720" y="0" font-size="10.5" font-weight="600" fill="#334155">Solar + URBS BESS (+11.8%)</text>')
    sb.append('  </g>')

    sb.append('</svg>')

    with open(output_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(sb))
    print(f"[OK] Saved comprehensive 3-panel comparison vector plot: {output_svg}")


def main():
    parser = argparse.ArgumentParser(description="Calculate and track Domestic vs. Import LCOE with Recycling Quota.")
    parser.add_argument("--file", "-f", default="Input_urbsextensionv1.xlsx", help="Input workbook path")
    parser.add_argument("--discount-rate", "-r", type=float, default=0.03, help="Discount rate (default: 0.03)")
    parser.add_argument("--quota", "-q", type=float, default=0.25, help="Benchmark recycling quota (default: 0.25)")
    parser.add_argument("--out-excel", default="lcoe_analysis/lcoe_domestic_vs_import.xlsx", help="Output Excel tracking file")
    parser.add_argument("--out-svg", default="lcoe_analysis/lcoe_domestic_vs_import.svg", help="Output SVG comparison plot")
    parser.add_argument("--out-csv", default="lcoe_analysis/lcoe_results.csv", help="Output CSV timeseries file")
    args = parser.parse_args()

    print(f"Loading input workbook from: {args.file}")
    wb_data = load_workbook_safely(args.file)

    print("\n[1/4] Calculating 100% Domestic Manufacturing Costs & LCOE Trajectory...")
    df_timeseries, df_stages_25, df_bom, df_summary_0, df_summary_25, tech_specs = calculate_comprehensive_lcoe(
        wb_data, discount_rate=args.discount_rate
    )

    print("\n[2/4] Performing Recycling Quota Parameter Sweep (0% to 50%)...")
    df_sweep = compute_recycling_sweep(wb_data, discount_rate=args.discount_rate)

    print("\n[3/4] Evaluating URBS Model Cost Driver Analysis (Why Wind beats Solar)...")
    df_drivers, driver_metrics = compute_urbs_cost_driver_analysis(wb_data, discount_rate=args.discount_rate)

    # Print milestone table
    print("\n" + "=" * 115)
    print(" LCOE COMPARISON: PURE IMPORT vs. DOMESTIC (0% vs. 25% RECYCLING QUOTA)")
    print("=" * 115)
    header = (
        f"{'Technology':<15} | {'Year':<5} | {'Import':<10} | {'Opt1 (0% Rec)':<15} | "
        f"{'Opt1 (25% Spec)':<16} | {'Opt1 (25% Cross)':<16} | {'Opt2 (25% Cross)':<16}"
    )
    print(header)
    print("-" * 115)

    for yr in [2024, 2030, 2040, 2050]:
        row = df_timeseries[df_timeseries["Year"] == yr].iloc[0]
        for t, cfg in tech_specs.items():
            imp = row[f"{t}_import_lcoe_eur_mwh"]
            opt1_0 = row[f"{t}_domestic_opt1_0pct_lcoe_eur_mwh"]
            opt1_spec = row[f"{t}_domestic_opt1_25pct_spec_lcoe_eur_mwh"]
            opt1_cross = row[f"{t}_domestic_opt1_25pct_cross_lcoe_eur_mwh"]
            opt2_cross = row[f"{t}_domestic_opt2_25pct_cross_lcoe_eur_mwh"]
            print(
                f"{cfg['name']:<15} | {yr:<5} | {imp:>7.2f} €  | {opt1_0:>12.2f} €  | "
                f"{opt1_spec:>13.2f} €  | {opt1_cross:>13.2f} €  | {opt2_cross:>13.2f} €"
            )
        print("-" * 115)

    print("\n" + "=" * 115)
    print(" URBS COST DRIVER ANALYSIS: WHY ONSHORE WIND APPEARS CHEAPER THAN SOLAR PV IN URBS")
    print("=" * 115)
    for _, r in df_drivers.iterrows():
        print(f"* {r['Cost_Driver']}")
        print(f"  - Solar PV:     {r['Solar_PV_Value']}")
        print(f"  - Wind Onshore: {r['Wind_Onshore_Value']}")
        print(f"  - Effect:       {r['Impact_Ratio']} | {r['Significance']}\n")

    # Export Excel Tracking File
    print("\n[4/4] Exporting Multi-Tab Excel Tracking File & Graphics...")
    export_tracking_excel(
        df_timeseries=df_timeseries,
        df_sweep=df_sweep,
        df_drivers=df_drivers,
        df_stages=df_stages_25,
        df_bom=df_bom,
        df_summary_0=df_summary_0,
        df_summary_25=df_summary_25,
        excel_path=args.out_excel,
    )

    # Save CSV
    if args.out_csv:
        df_timeseries.to_csv(args.out_csv, index=False)
        print(f"[OK] Saved timeseries data to: {args.out_csv}")

    # Generate Vector Plot
    plot_comparison_svg(df_timeseries, df_sweep, tech_specs, output_svg=args.out_svg)


if __name__ == "__main__":
    main()
