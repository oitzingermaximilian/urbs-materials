import pyomo.environ as pyomo
import os


def apply_sets_and_params(m, data_urbsextensionv1):
    ###############################################
    # universal sets and params for extension v1.0#
    ###############################################

    # Learning rate selection via environment variable
    LEARNING_RATE = os.environ.get("URBS_LR", "LR4")  # Default to LR4
    print(f"Using Learning Rate: {LEARNING_RATE}")

    # Excel read in
    base_params = data_urbsextensionv1["base_params"]

    # hard coded cost_types
    # NOM: CostType_{new} | Set of cost types (hard-coded) | -
    m.cost_type_new = pyomo.Set(
        initialize=m.cost_new_list, doc="Set of cost types (hard-coded)"
    )
    # Base sheet read in
    # NOM: T_{ext} | Set of extended timesteps | -
    m.timesteps_ext = pyomo.Set(initialize=range(1, 13), doc="Timesteps")

    # NOM: y_0 | Initial year of the model | Year
    m.y0 = pyomo.Param(initialize=base_params["y0"], mutable=True)  # Initial year

    # NOM: y_{end} | End year of the model | Year
    m.y_end = pyomo.Param(initialize=base_params["y_end"], mutable=True)  # End year

    # NOM: h_t | Number of hours per timestep | h
    m.hours = pyomo.Param(
        m.timesteps_ext, initialize=base_params["hours"]
    )  # Hours per year

    # locations sheet read in
    # NOM: L | Set of locations (sites) | -
    m.location = pyomo.Set(
        initialize=data_urbsextensionv1["locations_list"]
    )  # sites to be modelled

    # Extract all unique technologies across all locations
    all_techs = set()
    for loc in data_urbsextensionv1["technologies"]:
        all_techs.update(data_urbsextensionv1["technologies"][loc].keys())

    # Define the technology set
    # NOM: K | Set of technologies | -
    m.tech = pyomo.Set(initialize=sorted(list(all_techs)))

    #
    # Helper function to initialize parameters with default values
    def initialize_param(param_name, default_value=0):
        return {
            (loc, t): data_urbsextensionv1["technologies"]
            .get(loc, {})
            .get(t, {})
            .get(param_name, default_value)
            for loc in m.location
            for t in m.tech
        }

    # Define parameters using the helper function
    # NOM: n^{turnover} | Turnover rate of stockpile | 1/a
    m.n = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("n turnover stockpile", default_value=0),
    )  # Turnover of stockpile

    # NOM: l_{k} | Technical lifetime | a
    m.l = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("l", default_value=0)
    )

    # NOM: i | Global WACC / Interest Rate | %
    m.i = pyomo.Param(initialize=0.071, doc="Global WACC / Interest Rate")

    # NOM: Q_{init} | Initial installed capacity | MW
    m.Installed_Capacity_Q_s = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("InitialCapacity", default_value=0),
    )  # Initial installed capacity MW

    # NOM: S_{init} | Initial stockpile level | MW
    m.Existing_Stock_Q_stock = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("InitialStockpile", default_value=0),
    )  # Initial stocked capacity

    # NOM: FT | Calibration Factor | -
    m.FT = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("FT", default_value=0)
    )  # Factor

    # NOM: I_{dump} | Anti-dumping index | -
    m.anti_dumping_index = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("anti duping Index", default_value=0),
    )  # Anti-dumping index

    # NOM: \Delta Q^{prim} | Change in EU primary capacity | MW
    m.deltaQ_EUprimary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("dQ EU Primary", default_value=0),
    )  # ΔQ EU Primary

    # NOM: \Delta Q^{sec} | Change in EU secondary capacity | MW
    m.deltaQ_EUsecondary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("dQ EU Secondary", default_value=0),
    )  # ΔQ EU Secondary

    # NOM: IR^{prim} | Increase rate EU Primary | %
    m.IR_EU_primary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR EU Primary", default_value=0),
    )  # IR EU Primary

    # NOM: IR^{sec} | Increase rate EU Secondary | %
    m.IR_EU_secondary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR EU Secondary", default_value=0),
    )  # IR EU Secondary

    # NOM: DR^{prim} | Decrease rate Primary | %
    m.DR_primary = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("DR Primary", default_value=0)
    )  # DR Primary

    # NOM: DR^{sec} | Decrease rate Secondary | %
    m.DR_secondary = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("DR Secondary", default_value=0)
    )  # DR Secondary

    # NOM: C^{store} | Storage cost | EUR/MW
    m.STORAGECOST = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("Storagecost", default_value=0)
    )

    # NOM: C^{log} | Logistic cost | EUR/MW
    m.logisticcost = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("logisticcost", default_value=0)
    )

    # cost sheet read in
    # NOM: C^{imp} | Import cost | EUR/MW
    m.IMPORTCOST = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["importcost_dict"]
    )

    # NOM: C^{prim} | Manufacturing cost EU Primary | EUR/MW
    m.EU_primary_costs = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["manufacturingcost_dict"],
    )

    # NOM: C^{sec} | Remanufacturing cost EU Secondary | EUR/MW
    m.EU_secondary_costs = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["remanufacturingcost_dict"],
    )

    # NOM: C^{O\&M} | Operation and Maintenance costs | EUR/MW/a
    m.O_and_M_costs = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["o_and_m_dict"],
    )

    # instalable_capacity_sheet read in
    # NOM: Q^{new}_{lim} | New installable capacity limit | MW
    m.Q_ext_new = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["installable_capacity_dict"],
    )
    # DCR sheet read in
    # NOM: DCR | Domestic Content Requirement | %
    m.DCR_solar = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["dcr_dict"]
    )  # DCR Solar

    # stocklvl sheet read in
    # NOM: S_{min} | Minimum stock level requirement | %
    m.min_stocklvl = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["stocklvl_dict"]
    )
    # loadfactors sheet read in
    # Capacity to Balance with loadfactor and h/a
    # NOM: LF | Load Factor | -
    m.lf_solar = pyomo.Param(
        m.timesteps_ext,
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["loadfactors_dict"],
    )  # lf Solar

    ########################################
    # dynamic feedback loop EEM sets and params#     13. January 2025
    ########################################
    # -------EU-Secondary-------#
    # index set for n (=steps of linearization)
    # NOM: N_{steps} | Set of linearization steps | -
    m.nsteps_sec = pyomo.Set(initialize=range(0, 7))

    # Define m.stages
    all_stages = set()
    if "static_tech_specs" in data_urbsextensionv1 and "init_cap" in data_urbsextensionv1["static_tech_specs"]:
        for (loc, tech, stage) in data_urbsextensionv1["static_tech_specs"]["init_cap"].keys():
            all_stages.add(stage)

    # NOM: S | Set of Manufacturing stages | -
    m.stages = pyomo.Set(initialize=sorted(list(all_stages)), doc="Manufacturing stages")

    # Define m.materials
    all_mats = set()
    if "material_intensity_dict" in data_urbsextensionv1:
        for (tech, stage, mat) in data_urbsextensionv1["material_intensity_dict"].keys():
            all_mats.add(mat)

    # NOM: M | Set of Raw materials | -
    m.materials = pyomo.Set(initialize=sorted(list(all_mats)), doc="Raw materials")

    # NOM: KS | Set of Valid Tech-Stage pairs | -
    m.tech_stage_combinations = pyomo.Set(
        dimen=2,
        initialize=data_urbsextensionv1.get("valid_tech_stage_list", []),
        doc="Valid Tech-Stage pairs"
    )

    # ==============================================================================
    # 2. PROCESSING & TECH PARAMETERS
    # ==============================================================================

    # Static parameters (No time index)
    # NOM: t_{build} | Time lag for building capacity | years
    m.build_time = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1["static_tech_specs"].get("build_time", {}),
        default=1,
        doc="Time lag for building capacity"
    )

    # NOM: E_{need} | Energy required for processing | MWh/unit
    m.energy_needs = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1["static_tech_specs"].get("energy_needs", {}),
        default=100,
        doc="Energy required for processing"
    )

    # Check if the parameter is empty or has data
    print("--- Inspecting Energy Needs Parameter ---")
    # This prints all values that represent "True" data (non-default)
    m.energy_needs.display()

    # Initial Capacity (Time-indexed, but only populated for start year by the Slicer)
    # NOM: Cap^{proc}_{0} | Initial processing capacity | t/yr
    m.processing_cap_init = pyomo.Param(
        m.location, m.tech, m.stages,
        # FIX: Point to static_tech_specs -> init_cap
        initialize=data_urbsextensionv1["static_tech_specs"].get("init_cap", {}),
        default=0,
        doc="Initial processing capacity (Active only at y0)"
    )

    # NOM: \Delta Cap^{proc} | Processing growth delta | t/yr
    m.processing_delta_grow = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=3000,
        default=3000,
    )

    # NOM: r^{proc} | Processing avg growth rate | %
    m.processing_avg_growth = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=0.05,
        default=0.05,
    )

    # NOM: Cap^{scrap}_{0} | Initial scrap handling capacity | t/yr
    m.capacity_scrap_handling_init = pyomo.Param(
        m.location, m.tech,
        # FIX: Point to static_tech_specs -> init_cap
        initialize=0,
        default=0,
        doc="Initial processing capacity (Active only at y0)"
    )

    # NOM: \Delta Cap^{scrap} | Scrap handling growth delta | t/yr
    m.scraphandling_delta_grow = pyomo.Param(
        m.location, m.tech,
        initialize=20000,
        default=20000,
    )

    # NOM: r^{scrap} | Scrap handling avg growth rate | %
    m.scraphandling_avg_growth = pyomo.Param(
        m.location, m.tech,
        initialize=0.15,
        default=0.15,
    )

    # NOM: Map^{final} | Final stage mapping | -
    m.final_stage = pyomo.Param(
        m.tech,
        initialize=data_urbsextensionv1.get("final_stage_map", {}),
        within=pyomo.Any,
        doc="Map: Which stage is the final product for a technology"
    )

    # ==============================================================================
    # 3. MATERIAL INTENSITY & RECYCLING
    # ==============================================================================

    # NOM: I_{mat} | Material input intensity | t/MW
    m.material_intensity = pyomo.Param(
        m.tech, m.stages, m.materials,
        initialize=data_urbsextensionv1.get("material_intensity_dict", {}),
        default=0,
        doc="Material input required per unit of output"
    )

    # NOM: C_{scrap} | Scrap content available | t
    m.scrap_content = pyomo.Param(
        m.tech, m.materials,
        initialize=data_urbsextensionv1.get("material_content_dict", {}),
        default=0,
        doc="Scrap content available from recycling"
    )

    # NOM: \eta_{rec} | Recycling efficiency | %
    m.recycling_efficiency = pyomo.Param(
        m.tech, m.materials,
        initialize=data_urbsextensionv1.get("recycling_efficiency_dict", {}),
        default=0,
        doc="Efficiency of recycling process"
    )

    # 1. Energy Sector Share Parameter (Dynamic over time)
    # Represents: The % of the mining limit accessible to the energy sector in Year Y.
    # NOM: \sigma^{mine} | Mining energy sector share | %
    m.mining_energy_transission_share = pyomo.Param(
        m.stf, m.materials,  # <--- NOW INDEXED BY TIME
        initialize=data_urbsextensionv1.get("mining_energy_share_dict", {}),
        default=1.0,
        doc="Share of mining limit allocated to energy sector (e.g., 2025: 0.4, 2050: 0.8)"
    )

    # 2. Conversion Factor (Stays Static) #todo initialize!
    # Physics doesn't change over time, so this remains indexed by Material only.
    # NOM: f^{conv} | Mining conversion factor | -
    m.mining_conversion_factor = pyomo.Param(
        m.stf, m.materials,
        initialize=data_urbsextensionv1.get("conversion_factor_mat", {}),
        default=1.0,
        doc="Ratio of Raw Input to Metal Content (e.g. 5.0 for Bauxite->Al)"
    )

    # ==============================================================================
    # 4. MATERIAL MARKET (Broadcasted to Time by Slicer)
    # ==============================================================================

    # 1. Availability / Limit
    # NOM: Lim^{mine} | Global mining limit per year | t/yr
    m.primary_material_availability = pyomo.Param(
        m.stf, m.materials,
        # MUST MATCH the key name you used in the return dictionary
        initialize=data_urbsextensionv1.get("mat_mining_limit_dict", {}),
        default=1e7,
        doc="Global mining limit per year"
    )

    # 2. Mining Cost
    # NOM: C^{mine} | Cost of mining raw material | EUR/t
    m.cost_mining = pyomo.Param(
        m.stf, m.materials,
        # MUST MATCH the key name you used in the return dictionary
        initialize=data_urbsextensionv1.get("mat_mining_cost_dict", {}),
        default=0,
        doc="Cost of mining raw material"
    )

    # 3. Import Cost
    # NOM: C^{imp,mat} | Cost of importing raw material | EUR/t
    m.cost_import_material = pyomo.Param(
        m.stf, m.materials,
        # MUST MATCH the key name you used in the return dictionary
        initialize=data_urbsextensionv1.get("mat_import_cost_dict", {}),
        default=0,
        doc="Cost of importing raw material"
    )

    # NOM: C^{elec} | Cost of electricity | EUR/MWh
    m.cost_electricity = pyomo.Param(
        m.stf,
        initialize=74.06,
        default=74.06,
        doc="Cost of electricity per MWh"
    )

    # ==============================================================================
    # 5. PROCESSING COSTS (Time-Indexed)
    # ==============================================================================

    # NOM: C^{capex}_{proc} | CAPEX for processing plants | EUR
    m.cost_capex = pyomo.Param(
        m.stf, m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1.get("processing_stage_cost_dict", {}),
        default=1e7,
        doc="CAPEX for processing plants"
    )

    # NOM: C^{var}_{proc} | Variable OPEX for processing | EUR
    m.cost_variable = pyomo.Param(
        m.stf, m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1.get("processing_opex_var_dict", {}),
        default=1e7,
        doc="Variable OPEX for processing"
    )

    # NOM: C^{fix}_{proc} | Fixed OPEX for processing | EUR
    m.cost_fixed = pyomo.Param(
        m.stf, m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1.get("processing_opex_dict", {}),
        default=1e7,
        doc="Fixed OPEX for processing"
    )

    # NOM: C^{imp,part} | Cost to import intermediate parts | EUR
    m.cost_import_part = pyomo.Param(
        m.stf, m.location, m.tech, m.stages,
        initialize=data_urbsextensionv1.get("part_import_cost_dict", {}),
        # default=1,  <-- DELETE OR COMMENT THIS OUT! It hides bugs!
        default=1e7,  # Set to a penalty value so missing data implies "Impossible to build"
        doc="Cost to import intermediate parts"
    )

    # ==============================================================================
    # 6. BILL OF MATERIALS (BOM) MAP
    # ==============================================================================

    # NOM: BOM | Bill of Materials Ratio | -
    m.bom_map = pyomo.Param(
        m.tech, m.stages, m.tech, m.stages,
        initialize=data_urbsextensionv1.get("bom_map_dict", {}),
        default=0,
        doc="Ratio of Input Tech/Stage needed for Consumer Tech/Stage"
    )

    # ==============================================================================
    # 7. STOCK INITIALIZATION (Defaults)
    # ==============================================================================

    # NOM: S^{dom}_{0} | Initial domestic stock | MW
    m.stock_domestic_init = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=0, default=0
    )

    stock_data = {
        ('EU27', 'solarPV', 'Module'): 56000  # 56 GW -> 56,000 MW
    }

    # 2. Update your Parameter definition
    # NOM: S^{imp}_{0} | Initial imported stock | MW
    m.stock_imported_init = pyomo.Param(
        m.location, m.tech, m.stages,
        initialize=stock_data,  # <--- Pass the dictionary here
        default=0)  # All other combos (e.g. Wind, Batteries) stay 0

    # Todo fix this
    # NOM: R_{0} | Initial total reserves | t
    m.initial_total_reserves = pyomo.Param(
        m.materials,
        initialize=1e9, default=1e9
    )

    # ========================================
    # LEARNING RATE REDUCTION PERCENTAGES (sorted by learning rate %)
    # ========================================

    # 1% Learning Rate reduction percentage
    reduction_percentage_1 = {
        0: 1,
        1: 0.967164685,
        2: 0.935407528,
        3: 0.904693127,
        4: 0.874987243,
        5: 0.846256761,
        6: 0.818469654,
    }

    # 3.5% Learning Rate reduction percentage
    reduction_percentage_3_5 = {
        0: 1,
        1: 0.888384244,
        2: 0.789226565,
        3: 0.701136445,
        4: 0.622878571,
        5: 0.553355508,
        6: 0.491592315,
    }

    # 4% Learning Rate reduction percentage
    reduction_percentage_4 = {
        0: 1,
        1: 0.873185089,
        2: 0.7624522,
        3: 0.665761892,
        4: 0.581333357,
        5: 0.507611619,
        6: 0.443238897,
    }

    # 5% Learning Rate reduction percentage
    reduction_percentage_5 = {
        0: 1,
        1: 0.843333629,
        2: 0.711211609,
        3: 0.599788667,
        4: 0.505821953,
        5: 0.426576663,
        6: 0.359746445,
    }

    # 6% Learning Rate reduction percentage
    reduction_percentage_6 = {
        0: 1,
        1: 0.814202932,
        2: 0.662926414,
        3: 0.53975663,
        4: 0.439471431,
        5: 0.357818927,
        6: 0.29133722,
    }

    # 7% Learning Rate reduction percentage
    reduction_percentage_7 = {
        0: 1,
        1: 0.785782986,
        2: 0.617454902,
        3: 0.485185557,
        4: 0.381250556,
        5: 0.2995802,
        6: 0.235405024,
    }

    # 8% Learning Rate reduction percentage
    reduction_percentage_8 = {
        0: 1,
        1: 0.758063814,
        2: 0.574660746,
        3: 0.435629517,
        4: 0.330234973,
        5: 0.250339183,
        6: 0.189773076,
    }

    # 9% Learning Rate reduction percentage
    reduction_percentage_9 = {
        0: 1,
        1: 0.731035472,
        2: 0.534412861,
        3: 0.390674758,
        4: 0.285597106,
        5: 0.208781615,
        6: 0.152626766,
    }

    # 10% Learning Rate reduction percentage
    reduction_percentage_10 = {
        0: 1,
        1: 0.70468805,
        2: 0.496585247,
        3: 0.349937689,
        4: 0.246596908,
        5: 0.173773894,
        6: 0.122456386,
    }

    # 25% Learning Rate reduction percentage
    reduction_percentage_25 = {
        0: 1,
        1: 0.384558576,
        2: 0.147885298,
        3: 0.05687056,
        4: 0.021870061,
        5: 0.00841032,
        6: 0.003234261,
    }

    # ========================================
    # ABSOLUTE VALUE PRICE REDUCTION CALCULATION
    # ========================================

    # Get the cost data for absolute value calculations
    recycling_costs = data_urbsextensionv1["recyclingcost_dict"]

    # Create absolute value dictionaries for recycling costs (f_scrap_rec)
    def create_absolute_recycling_dict(reduction_percentages):
        absolute_dict = {}
        for n in reduction_percentages.keys():
            absolute_dict[n] = {}
            for (stf, location, tech), cost in recycling_costs.items():
                absolute_dict[n][(stf, location, tech)] = cost * (
                        1 - reduction_percentages[n]
                )
        return absolute_dict

    # 1. Define the source dictionary OUTSIDE the function (or just reference it)
    processing_stage_costs = data_urbsextensionv1["processing_stage_cost_dict"]

    def create_absolute_stage_reduction_dict(reduction_percentages):
        absolute_dict = {}

        # Outer Loop: Steps (n)
        for n in reduction_percentages.keys():
            absolute_dict[n] = {}

            # Inner Loop: Iterate over the dictionary items
            # Just like recycling, but unpacking 4 items now: (stf, loc, tech, STAGE)
            for (stf, location, tech, stage), cost in processing_stage_costs.items():
                absolute_dict[n][(stf, location, tech, stage)] = cost * (
                        1 - reduction_percentages[n]
                )

        return absolute_dict

    # Generate absolute value dictionaries for all learning rates #NOTE this is for CAPEX Cost
    absolute_stage_reductions = {
        "LR1": create_absolute_stage_reduction_dict(reduction_percentage_1),
        "LR3_5": create_absolute_stage_reduction_dict(reduction_percentage_3_5),
        "LR4": create_absolute_stage_reduction_dict(reduction_percentage_4),
        "LR4": create_absolute_stage_reduction_dict(reduction_percentage_5),
        "LR6": create_absolute_stage_reduction_dict(reduction_percentage_6),
        "LR7": create_absolute_stage_reduction_dict(reduction_percentage_7),
        "LR8": create_absolute_stage_reduction_dict(reduction_percentage_8),
        "LR9": create_absolute_stage_reduction_dict(reduction_percentage_9),
        "LR10": create_absolute_stage_reduction_dict(reduction_percentage_10),
        "LR25": create_absolute_stage_reduction_dict(reduction_percentage_25),
    }

    absolute_recycling_reductions = {
        "LR1": create_absolute_recycling_dict(reduction_percentage_1),
        "LR3_5": create_absolute_recycling_dict(reduction_percentage_3_5),
        "LR4": create_absolute_recycling_dict(reduction_percentage_4),
        "LR4": create_absolute_recycling_dict(reduction_percentage_5),
        "LR6": create_absolute_recycling_dict(reduction_percentage_6),
        "LR7": create_absolute_recycling_dict(reduction_percentage_7),
        "LR8": create_absolute_recycling_dict(reduction_percentage_8),
        "LR9": create_absolute_recycling_dict(reduction_percentage_9),
        "LR10": create_absolute_recycling_dict(reduction_percentage_10),
        "LR25": create_absolute_recycling_dict(reduction_percentage_25),
    }

    # Mapping from learning rate labels to the existing step dicts
    all_relative_reductions = {
        "LR1": reduction_percentage_1,
        "LR3_5": reduction_percentage_3_5,
        "LR4": reduction_percentage_4,
        "LR4": reduction_percentage_5,
        "LR6": reduction_percentage_6,
        "LR7": reduction_percentage_7,
        "LR8": reduction_percentage_8,
        "LR9": reduction_percentage_9,
        "LR10": reduction_percentage_10,
        "LR25": reduction_percentage_25,
    }

    selected_relative_reductions = all_relative_reductions.get(
        LEARNING_RATE, all_relative_reductions["LR4"]
    )

    # Select the appropriate reductions based on environment variable
    selected_stage_reductions = absolute_stage_reductions.get(
        LEARNING_RATE, absolute_stage_reductions["LR4"]
    )
    selected_recycling_reductions = absolute_recycling_reductions.get(
        LEARNING_RATE, absolute_recycling_reductions["LR4"]
    )

    print(f"Selected stage reduction values for {LEARNING_RATE}")
    print(f"Selected recycling reduction values for {LEARNING_RATE}")

    # Initialize P_sec_investment with absolute stage cost reductions
    # NOM: \Delta P^{inv} | Absolute OPEX reduction per stage | EUR
    m.P_sec_investment = pyomo.Param(
        m.location,
        m.tech,
        m.stages,  # <--- ADDED THIS
        m.nsteps_sec,
        # Updated lambda to accept stage and look up (2024, loc, tech, stage)
        initialize=lambda m, loc, tech, stage, n: selected_stage_reductions[n].get(
            (2024, loc, tech, stage), 0
        ),
        doc=f"Absolute OPEX reduction per STAGE for {LEARNING_RATE}",
    )

    # Define a Pyomo Param for the selected relative reductions
    # NOM: P^{rel} | Selected relative reductions | -
    m.P_sec_relative = pyomo.Param(
        m.nsteps_sec,  # Steps
        initialize=lambda m, n: selected_relative_reductions.get(n, 0),
        mutable=False,
        doc=f"Selected relative reductions for --lr {LEARNING_RATE}",
    )

    # Initialize P_sec_recycling with absolute recycling cost reductions
    # NOM: \Delta C^{rec} | Absolute recycling cost reduction | EUR
    m.P_sec_recycling = pyomo.Param(
        m.location,  # Locations
        m.tech,  # Technologies
        m.nsteps_sec,  # Steps
        initialize=lambda m, loc, tech, n: selected_recycling_reductions[n].get(
            (2024, loc, tech), 0
        ),  # Use 2024 as base year
        doc=f"Absolute recycling cost reduction values for {LEARNING_RATE}",
    )

    tons_step_values = {
        0: 0,
        1: 1000,
        2: 10000,
        3: 100000,
        4: 1000000,
        5: 10000000,
        6: 100000000,
    }

    tons_init_values = {
        (loc, tech, n): tons_step_values.get(n, 0)
        for loc in m.location
        for tech in m.tech
        for n in m.nsteps_sec
    }

    # NOM: T_{step} | Tons per step recycling | t
    m.tons_perstep_recycling = pyomo.Param(
        m.location,
        m.tech,
        m.nsteps_sec,
        initialize=tons_init_values,
    )

    # NOM: Cap^{rec}_{0} | Initial total recycling capacity history | t
    m.total_recycling_cap_initial = pyomo.Param(
        m.location,
        m.tech,
        initialize=0,  # <--- Set strictly to 0
        default=0,
        doc="Global accumulated recycling history (tons)"
    )

    # NOM: \gamma^{scrap} | Gamma scrap factor | -
    m.gamma_scrap = pyomo.Param(initialize=1e6)

    # Define the step values (same for all technologies)
    uniform_step_values = {
        0: 0,
        1: 100,
        2: 1000,
        3: 10000,
        4: 100000,
        5: 1000000,
        6: 10000000,
    }

    # Initialize the dictionary with uniform values for all (n, loc, tech)
    capacity_init_values = {
        (loc, tech, stage, n): uniform_step_values.get(n, 0)
        for loc in m.location
        for tech in m.tech
        for stage in m.stages
        for n in m.nsteps_sec
    }

    # Initialize the Pyomo Param
    # NOM: Cap_{step}^{prod} | Capacity per step production | MW
    m.capacityperstep_production = pyomo.Param(
        m.location,
        m.tech,
        m.stages,  # <--- ADDED THIS
        m.nsteps_sec,
        initialize=capacity_init_values,
    )

    # param for gamma
    # NOM: \gamma^{prod} | Gamma production factor | -
    m.gamma_prod = pyomo.Param(initialize=200000)

    # NOM: Cap^{prod}_{0} | Initial total production capacity history | MW
    m.total_production_cap_inital = pyomo.Param(
        m.location,
        m.tech,
        m.stages,
        initialize=0,  # <--- Set strictly to 0
        default=0,
        doc="Global accumulated production history (MW)"
    )

    ##########----------end EEM Addition-----------###############
    ##########----------    urbs-scrap  -----------###############
    # NOM: f_{scrap} | Scrap generation factor | t/MW
    m.f_scrap = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("scrap", default_value=0),
        doc="tons per MW",
    )
    # NOM: f_{mining} | Mining generation factor | t/MW
    m.f_mining = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("mining"),
        doc="tons per MW",
    )
    # NOM: f_{recycling} | Recycling factor | %
    m.f_recycling = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("recycling_efficiency"),
        doc="recycling efficiency in %",
    )
    # NOM: C_{rec} | Recycling cost per ton | EUR/ton
    m.f_scrap_rec = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["recyclingcost_dict"],
        doc="cost for recycling in EUR/ton",
    )
    # NOM: f_{inc} | Fraction of increase in production | -
    m.f_increase = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR_recycling", default_value=0),
        doc="Fraction of increase in production",
    )
    # NOM: Cap^{dec}_{0} | Initial decommissioned capacity | MW
    m.capacity_dec_start = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("Initial_decommisions", default_value=0),
        doc="initial decommisions",
    )

    ##########----------end urbs-scrap  -----------###############
    # added for carry over - updated for new absolute value system
    # NOM: P^{red}_{init} | Initial investment price reduction | EUR
    m.pricereduction_sec_init = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("price_reduction_investment_init", default_value=0),
        doc="Initial investment price reduction for carryover (absolute values)",
    )

    # NOM: Cap^{prim}_{prior} | Last primary capacity | MW
    m.cap_prim_prior = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("last_prim_cap", default_value=0),
        doc="last_prim_cap",
    )
    # NOM: Cap^{sec}_{prior} | Last secondary capacity | MW
    m.cap_sec_prior = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("last_sec_cap", default_value=0),
        doc="last_sec_cap",
    )

    # NOM: f_{bess} | BESS Factor | -
    m.factor_bess = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("factor_bess", default_value=0),
        doc="factor_bess",
    )

    # NOM: S^{tot} | Total capacity scrap | t
    m.scrap_total = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("capacity_scrap_total", default_value=0),
        doc="capacity_scrap_total",
    )
    # NOM: Cap^{fac}_{0} | Initial total facility capacity | MW
    m.total_facility_cap_initial = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("total_facility_cap_initial", default_value=0),
        doc="total_facility_cap_initial",
    )


    ####################################################################
    # solar only economies of
    ####################################################################

    # Create the subset 'gatekeeper'
    # NOM: K_{sol} | Solar Technology Subset | -
    m.one_tech_only = pyomo.Set(initialize=['solarPV'], within=m.tech)