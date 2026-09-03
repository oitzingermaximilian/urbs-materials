import pyomo.environ as pyomo
import os

# ==============================================================================
# GLOBAL CONSTANTS & HARDCODED DATA
# Ideally, move these to a separate config.json or config.py file later.
# ==============================================================================
GW_SCALE = 1e-3
MASS_SCALE = 1e-3
LEARNING_RATE_SELECTION = os.environ.get("URBS_LR", "LR4")

# Tons (kton) and Capacity (GW) Step values for linearization
TONS_STEP_VALUES = {0: 0, 1: 1, 2: 10, 3: 100, 4: 1000, 5: 10000, 6: 100000}
CAPACITY_STEP_VALUES = {0: 0, 1: 0.1, 2: 1.0, 3: 10.0, 4: 100.0, 5: 1000.0, 6: 10000.0}

# Learning Rate Reduction Percentages
LEARNING_RATES = {
    "LR1": {
        0: 1,
        1: 0.967164685,
        2: 0.935407528,
        3: 0.904693127,
        4: 0.874987243,
        5: 0.846256761,
        6: 0.818469654,
    },
    "LR3_5": {
        0: 1,
        1: 0.888384244,
        2: 0.789226565,
        3: 0.701136445,
        4: 0.622878571,
        5: 0.553355508,
        6: 0.491592315,
    },
    "LR4": {
        0: 1,
        1: 0.873185089,
        2: 0.7624522,
        3: 0.665761892,
        4: 0.581333357,
        5: 0.507611619,
        6: 0.443238897,
    },
    "LR5": {
        0: 1,
        1: 0.843333629,
        2: 0.711211609,
        3: 0.599788667,
        4: 0.505821953,
        5: 0.426576663,
        6: 0.359746445,
    },
    "LR6": {
        0: 1,
        1: 0.814202932,
        2: 0.662926414,
        3: 0.53975663,
        4: 0.439471431,
        5: 0.357818927,
        6: 0.29133722,
    },
    "LR7": {
        0: 1,
        1: 0.785782986,
        2: 0.617454902,
        3: 0.485185557,
        4: 0.381250556,
        5: 0.2995802,
        6: 0.235405024,
    },
    "LR8": {
        0: 1,
        1: 0.758063814,
        2: 0.574660746,
        3: 0.435629517,
        4: 0.330234973,
        5: 0.250339183,
        6: 0.189773076,
    },
    "LR9": {
        0: 1,
        1: 0.731035472,
        2: 0.534412861,
        3: 0.390674758,
        4: 0.285597106,
        5: 0.208781615,
        6: 0.152626766,
    },
    "LR10": {
        0: 1,
        1: 0.70468805,
        2: 0.496585247,
        3: 0.349937689,
        4: 0.246596908,
        5: 0.173773894,
        6: 0.122456386,
    },
    "LR25": {
        0: 1,
        1: 0.384558576,
        2: 0.147885298,
        3: 0.05687056,
        4: 0.021870061,
        5: 0.00841032,
        6: 0.003234261,
    },
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def _apply_cost_reductions(source_dict, reductions, filter_func=None, map_func=None):
    """
    Applies learning rate reductions to a base cost dictionary.
    Replaces the dozen repetitive 'create_absolute_X' functions.
    """
    result = {n: {} for n in reductions}
    for n, reduction_factor in reductions.items():
        for key, cost in source_dict.items():
            if filter_func and not filter_func(key):
                continue

            output_key = map_func(key) if map_func else key
            result[n][output_key] = cost * (1 - reduction_factor)
    return result


def apply_sets_and_params(m, data_urbsextensionv1):
    print(f"Using Learning Rate: {LEARNING_RATE_SELECTION} | Units: [GW], [kton], [k€]")

    # -------------------------------------------------------------------------
    # 1. UNIVERSAL SETS & PARAMS
    # -------------------------------------------------------------------------
    base_params = data_urbsextensionv1["base_params"]

    m.cost_type_new = pyomo.Set(initialize=m.cost_new_list, doc="Set of cost types")
    m.timesteps_ext = pyomo.Set(initialize=range(1, 13), doc="Timesteps")
    m.y0 = pyomo.Param(initialize=base_params["y0"], mutable=True)
    m.y_end = pyomo.Param(initialize=base_params["y_end"], mutable=True)
    m.hours = pyomo.Param(m.timesteps_ext, initialize=base_params["hours"])
    m.location = pyomo.Set(initialize=data_urbsextensionv1["locations_list"])
    m.i = pyomo.Param(initialize=0.071, doc="Global WACC / Interest Rate")

    # Extract technologies
    all_techs = {
        tech
        for loc in data_urbsextensionv1["technologies"]
        for tech in data_urbsextensionv1["technologies"][loc]
    }
    m.tech = pyomo.Set(initialize=sorted(list(all_techs)))

    # Local param builder
    def init_tech_param(param_name, default_value=0, scale=1.0):
        return {
            (loc, t): data_urbsextensionv1["technologies"]
            .get(loc, {})
            .get(t, {})
            .get(param_name, default_value)
            * scale
            for loc in m.location
            for t in m.tech
        }

    m.n = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("n turnover stockpile")
    )
    m.l = pyomo.Param(m.location, m.tech, initialize=init_tech_param("l"))
    m.Installed_Capacity_Q_s = pyomo.Param(
        m.location,
        m.tech,
        initialize=init_tech_param("InitialCapacity", scale=GW_SCALE),
    )
    m.FT = pyomo.Param(m.location, m.tech, initialize=init_tech_param("FT"))
    m.anti_dumping_index = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("anti duping Index")
    )

    # -------------------------------------------------------------------------
    # 2. COSTS & CAPACITY LIMITS
    # -------------------------------------------------------------------------
    m.IMPORTCOST = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["importcost_dict"]
    )
    m.EU_primary_costs = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["manufacturingcost_dict"],
    )
    m.EU_secondary_costs = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["remanufacturingcost_dict"],
    )
    m.O_and_M_costs = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["o_and_m_dict"]
    )
    m.Q_ext_new = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["installable_capacity_dict"],
    )
    m.DCR_solar = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["dcr_dict"]
    )
    m.min_stocklvl = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["stocklvl_dict"]
    )
    m.lf_solar = pyomo.Param(
        m.timesteps_ext,
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["loadfactors_dict"],
    )

    # -------------------------------------------------------------------------
    # 3. MANUFACTURING STAGES & MATERIALS
    # -------------------------------------------------------------------------
    m.nsteps_sec = pyomo.Set(initialize=range(0, 7))

    stages = {
        s
        for k in data_urbsextensionv1.get("static_tech_specs", {})
        .get("init_cap", {})
        .keys()
        for s in [k[2]]
    }
    m.stages = pyomo.Set(initialize=sorted(list(stages)), doc="Manufacturing stages")

    mats = {
        m
        for k in data_urbsextensionv1.get("material_intensity_dict", {}).keys()
        for m in [k[2]]
    }
    m.materials = pyomo.Set(initialize=sorted(list(mats)), doc="Raw materials")
    m.tech_stage_combinations = pyomo.Set(
        dimen=2, initialize=data_urbsextensionv1.get("valid_tech_stage_list", [])
    )

    # Tech parameters
    specs = data_urbsextensionv1.get("static_tech_specs", {})
    m.build_time = pyomo.Param(
        m.location,
        m.tech_stage_combinations,
        initialize=specs.get("build_time", {}),
        default=1,
    )
    m.energy_needs = pyomo.Param(
        m.location,
        m.tech_stage_combinations,
        initialize=specs.get("energy_needs", {}),
        default=100 * GW_SCALE,
    )
    m.processing_cap_init = pyomo.Param(
        m.location,
        m.tech_stage_combinations,
        initialize=specs.get("init_cap", {}),
        default=0,
    )
    m.processing_delta_grow = pyomo.Param(
        m.location, m.tech_stage_combinations, initialize=3000 * MASS_SCALE
    )
    m.processing_avg_growth = pyomo.Param(
        m.location, m.tech, m.stages, initialize=0.05, default=0.05
    )

    m.capacity_scrap_handling_init = pyomo.Param(
        m.location, m.tech, initialize=0, default=0
    )
    m.scraphandling_delta_grow = pyomo.Param(
        m.location, m.tech, initialize=20000 * MASS_SCALE
    )
    m.scraphandling_avg_growth = pyomo.Param(
        m.location, m.tech, initialize=0.15, default=0.15
    )
    m.final_stage = pyomo.Param(
        m.tech,
        initialize=data_urbsextensionv1.get("final_stage_map", {}),
        within=pyomo.Any,
    )

    # -------------------------------------------------------------------------
    # 4. MATERIALS, MINING, RECYCLING
    # -------------------------------------------------------------------------
    m.material_intensity = pyomo.Param(
        m.tech_stage_combinations,
        m.materials,
        initialize=data_urbsextensionv1.get("material_intensity_dict", {}),
        default=0,
    )
    m.scrap_content = pyomo.Param(
        m.tech,
        m.materials,
        initialize=data_urbsextensionv1.get("material_content_dict", {}),
        default=0,
    )
    m.recycling_efficiency = pyomo.Param(
        m.tech,
        m.materials,
        initialize=data_urbsextensionv1.get("recycling_efficiency_dict", {}),
        default=0,
    )

    m.mining_energy_transission_share = pyomo.Param(
        m.stf,
        m.materials,
        initialize=data_urbsextensionv1.get("mining_energy_share_dict", {}),
        default=1.0,
    )
    m.mining_conversion_factor = pyomo.Param(
        m.stf,
        m.materials,
        initialize=data_urbsextensionv1.get("conversion_factor_mat", {}),
        default=1.0,
    )

    m.primary_material_availability = pyomo.Param(
        m.stf,
        m.materials,
        initialize=data_urbsextensionv1.get("mat_mining_limit_dict", {}),
        default=1e7 * MASS_SCALE,
    )
    m.cost_mining = pyomo.Param(
        m.stf,
        m.materials,
        initialize=data_urbsextensionv1.get("mat_mining_cost_dict", {}),
        default=0,
    )
    m.cost_import_material = pyomo.Param(
        m.stf,
        m.materials,
        initialize=data_urbsextensionv1.get("mat_import_cost_dict", {}),
        default=0,
    )
    m.cost_electricity = pyomo.Param(m.stf, initialize=74.06, default=74.06)

    # Processing Costs & BOM
    m.cost_capex = pyomo.Param(
        m.stf,
        m.location,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("processing_stage_cost_dict", {}),
    )
    m.cost_variable = pyomo.Param(
        m.stf,
        m.location,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("processing_opex_var_dict", {}),
    )
    m.material_downstream_manufacturing_cost = pyomo.Param(
        m.stf,
        m.location,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("material_downstream_cost_dict", {}),
        default=0,
    )
    m.cost_fixed = pyomo.Param(
        m.stf,
        m.location,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("processing_opex_dict", {}),
    )
    m.cost_import_part = pyomo.Param(
        m.stf,
        m.location,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("part_import_cost_dict", {}),
    )
    m.bom_map = pyomo.Param(
        m.tech_stage_combinations,
        m.tech_stage_combinations,
        initialize=data_urbsextensionv1.get("bom_map_dict", {}),
        default=0,
    )

    # Initial Stocks
    m.stock_domestic_init = pyomo.Param(
        m.location, m.tech_stage_combinations, initialize=0, default=0
    )
    m.stock_imported_init = pyomo.Param(
        m.location,
        m.tech_stage_combinations,
        initialize={("EU27", "solarPV", "Module"): 56.0},
        default=0,
    )
    m.initial_total_reserves = pyomo.Param(m.materials, initialize=1e9 * MASS_SCALE)

    # -------------------------------------------------------------------------
    # 5. LEARNING CURVE REDUCTIONS (Dynamic Application)
    # -------------------------------------------------------------------------
    active_reductions = LEARNING_RATES.get(
        LEARNING_RATE_SELECTION, LEARNING_RATES["LR4"]
    )

    # 5.1 Calculate Absolutes using Unified Helper
    abs_stage = _apply_cost_reductions(
        data_urbsextensionv1.get("processing_stage_cost_dict", {}), active_reductions
    )
    abs_opex_var = _apply_cost_reductions(
        data_urbsextensionv1.get("processing_opex_var_dict", {}), active_reductions
    )
    abs_fom = _apply_cost_reductions(
        data_urbsextensionv1.get("processing_opex_dict", {}), active_reductions
    )
    abs_downstream = _apply_cost_reductions(
        data_urbsextensionv1.get("material_downstream_cost_dict", {}), active_reductions
    )

    # Cost filtering functions
    is_solar = lambda k: k[2] == "solarPV"
    is_wind = lambda k: k[2] in ["windon", "windoff"]
    drop_tech = lambda k: (
        k[0],
        k[1],
    )  # Drops tech from the (stf, location, tech) tuple

    abs_rec = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingcost_dict", {}), active_reductions
    )
    abs_rec_solar = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingcapex_dict", {}),
        active_reductions,
        filter_func=is_solar,
        map_func=drop_tech,
    )
    abs_fom_solar = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingfom_dict", {}),
        active_reductions,
        filter_func=is_solar,
        map_func=drop_tech,
    )

    abs_rec_wind_capex = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingcapex_magnet_dict", {}),
        active_reductions,
        filter_func=is_wind,
        map_func=drop_tech,
    )
    abs_rec_wind_fom = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingfom_magnet_dict", {}),
        active_reductions,
        filter_func=is_wind,
        map_func=drop_tech,
    )
    abs_rec_wind_cost = _apply_cost_reductions(
        data_urbsextensionv1.get("recyclingcost_magnet_dict", {}),
        active_reductions,
        filter_func=is_wind,
        map_func=drop_tech,
    )

    # 5.2 Assign Pyomo Params
    m.P_sec_relative = pyomo.Param(
        m.nsteps_sec, initialize=lambda m, n: active_reductions.get(n, 0), mutable=False
    )

    m.P_sec_capex = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        initialize=lambda m, l, t, s, n: abs_stage[n].get((2024, l, t, s), 0),
    )
    m.P_sec_opex_var = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        initialize=lambda m, l, t, s, n: abs_opex_var[n].get((2024, l, t, s), 0),
    )
    m.P_sec_fom = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        initialize=lambda m, l, t, s, n: abs_fom[n].get((2024, l, t, s), 0),
    )
    m.P_sec_downstream_manufacturing = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        initialize=lambda m, l, t, s, n: abs_downstream[n].get((2024, l, t, s), 0),
    )
    m.P_sec_recycling = pyomo.Param(
        m.location,
        m.tech,
        m.nsteps_sec,
        initialize=lambda m, l, t, n: abs_rec[n].get((2024, l, t), 0),
    )

    # Tech specific recycling reductions
    m.P_sec_recycling_wind = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_rec_wind_cost[n].get((2024, l), 0),
    )
    m.P_sec_recycling_solar = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_rec[n].get((2024, l, "solarPV"), 0),
    )
    m.P_sec_recycling_capex_solar = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_rec_solar[n].get((2024, l), 0),
    )
    m.P_sec_recycling_fom_solar = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_fom_solar[n].get((2024, l), 0),
    )
    m.P_sec_recycling_capex_wind = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_rec_wind_capex[n].get((2024, l), 0),
    )
    m.P_sec_recycling_fom_wind = pyomo.Param(
        m.location,
        m.nsteps_sec,
        initialize=lambda m, l, n: abs_rec_wind_fom[n].get((2024, l), 0),
    )

    # -------------------------------------------------------------------------
    # 6. LINEARIZATION STEPS (Scrap & Capacity)
    # -------------------------------------------------------------------------
    m.tons_perstep_recycling = pyomo.Param(
        m.location,
        m.tech,
        m.nsteps_sec,
        initialize=lambda m, l, t, n: TONS_STEP_VALUES.get(n, 0),
    )
    m.total_recycling_cap_initial = pyomo.Param(
        m.location, m.tech, initialize=0, default=0
    )
    m.gamma_scrap = pyomo.Param(initialize=200000)

    m.capacityperstep_production = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        m.nsteps_sec,
        initialize=lambda m, l, t, s, n: CAPACITY_STEP_VALUES.get(n, 0),
    )
    m.gamma_prod = pyomo.Param(initialize=20000)
    m.total_production_cap_inital = pyomo.Param(
        m.location, m.tech, m.stages, initialize=0, default=0
    )

    # -------------------------------------------------------------------------
    # 7. URBS-SCRAP & END-OF-LIFE
    # -------------------------------------------------------------------------
    m.f_scrap = pyomo.Param(m.location, m.tech, initialize=init_tech_param("scrap"))
    m.f_mining = pyomo.Param(m.location, m.tech, initialize=init_tech_param("mining"))
    m.f_recycling = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("recycling_efficiency")
    )

    m.f_scrap_rec = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcost_dict", {}),
        default=0,
    )
    m.f_scrap_rec_magnet = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcost_magnet_dict", {}),
        default=0,
    )
    m.f_scrap_rec_bulk = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcost_bulk_dict", {}),
        default=0,
    )

    m.f_scrap_capex_magnet = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcapex_magnet_dict", {}),
        default=0,
    )
    m.f_scrap_capex_bulk = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcapex_bulk_dict", {}),
        default=0,
    )
    m.f_scrap_fom_magnet = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingfom_magnet_dict", {}),
        default=0,
    )
    m.f_scrap_fom_bulk = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingfom_bulk_dict", {}),
        default=0,
    )

    m.f_scrap_capex = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingcapex_dict", {}),
        default=0,
    )
    m.f_scrap_fom = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("recyclingfom_dict", {}),
        default=0,
    )

    m.scrap_utilization_penalty = pyomo.Param(m.location, m.tech, default=1e6)
    m.f_increase = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("IR_recycling")
    )

    m.capacity_dec_start = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("Initial_decommisions")
    )
    m.decommissioned_cap = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1.get("decommissioned_cap_dict", {}),
        default=0,
    )

    m.pricereduction_sec_init = pyomo.Param(
        m.location,
        m.tech,
        initialize=init_tech_param("price_reduction_investment_init"),
    )
    m.cap_prim_prior = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("last_prim_cap")
    )
    m.cap_sec_prior = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("last_sec_cap")
    )
    m.factor_bess = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("factor_bess")
    )
    m.scrap_total = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("capacity_scrap_total")
    )
    m.total_facility_cap_initial = pyomo.Param(
        m.location, m.tech, initialize=init_tech_param("total_facility_cap_initial")
    )

    m.one_tech_only = pyomo.Set(initialize=["solarPV"], within=m.tech)
