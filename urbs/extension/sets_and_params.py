import pyomo.environ as pyomo


def apply_sets_and_params(m, data_urbsextensionv1):
    ###############################################
    # universal sets and params for extension v1.0#
    ###############################################

    # Excel read in
    base_params = data_urbsextensionv1["base_params"]
    # hard coded cost_types
    m.cost_type_new = pyomo.Set(
        initialize=m.cost_new_list, doc="Set of cost types (hard-coded)"
    )
    # Base sheet read in
    m.timesteps_ext = pyomo.Set(initialize=range(1, 13), doc="Timesteps")
    m.y0 = pyomo.Param(initialize=base_params["y0"], mutable=True)  # Initial year
    m.y_end = pyomo.Param(initialize=base_params["y_end"], mutable=True)  # End year
    m.hours = pyomo.Param(
        m.timesteps_ext, initialize=base_params["hours"]
    )  # Hours per year
    # locations sheet read in
    m.location = pyomo.Set(
        initialize=data_urbsextensionv1["locations_list"]
    )  # sites to be modelled

    # Extract all unique technologies across all locations
    all_techs = set()
    for loc in data_urbsextensionv1["technologies"]:
        all_techs.update(data_urbsextensionv1["technologies"][loc].keys())

    # Define the technology set
    m.tech = pyomo.Set(initialize=all_techs)

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
    m.n = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("n turnover stockpile", default_value=0),
    )  # Turnover of stockpile
    m.l = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("l", default_value=0)
    )

    m.Installed_Capacity_Q_s = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("InitialCapacity", default_value=0),
    )  # Initial installed capacity MW
    m.Existing_Stock_Q_stock = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("InitialStockpile", default_value=0),
    )  # Initial stocked capacity
    m.FT = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("FT", default_value=0)
    )  # Factor
    m.anti_dumping_index = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("anti duping Index", default_value=0),
    )  # Anti-dumping index
    m.deltaQ_EUprimary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("dQ EU Primary", default_value=0),
    )  # ΔQ EU Primary
    m.deltaQ_EUsecondary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("dQ EU Secondary", default_value=0),
    )  # ΔQ EU Secondary
    m.IR_EU_primary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR EU Primary", default_value=0),
    )  # IR EU Primary
    m.IR_EU_secondary = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR EU Secondary", default_value=0),
    )  # IR EU Secondary
    m.DR_primary = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("DR Primary", default_value=0)
    )  # DR Primary
    m.DR_secondary = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("DR Secondary", default_value=0)
    )  # DR Secondary
    m.STORAGECOST = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("Storagecost", default_value=0)
    )
    m.logisticcost = pyomo.Param(
        m.location, m.tech, initialize=initialize_param("logisticcost", default_value=0)
    )

    # cost sheet read in
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

    # instalable_capacity_sheet read in
    m.Q_ext_new = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["installable_capacity_dict"],
    )
    # DCR sheet read in
    m.DCR_solar = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["dcr_dict"]
    )  # DCR Solar
    # stocklvl sheet read in
    m.min_stocklvl = pyomo.Param(
        m.stf, m.location, m.tech, initialize=data_urbsextensionv1["stocklvl_dict"]
    )
    # loadfactors sheet read in
    # Capacity to Balance with loadfactor and h/a
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

    # -------EU-Primary-------# ToDo enable if needed
    # index set for n (=steps of linearization)
    # m.nsteps_pri = pyomo.Set(initialize=range(0, 7))
    # param def for price reduction
    # m.P_pri = pyomo.Param(m.nsteps_pri, initialize={0: 0, 1: 172444.8, 2: 246826.8
    #    , 3: 279008.4, 4: 292974, 5: 299046, 6: 301656.96})
    # m.capacityperstep_pri = pyomo.Param(m.nsteps_pri, initialize={0: 0, 1: 100, 2: 1000, 3: 10000, 4: 100000, 5:1000000, 6:10000000})
    # param for gamma
    # m.gamma_pri = pyomo.Param(initialize=1e10)

    # -------EU-Secondary-------#
    # index set for n (=steps of linearization)
    m.nsteps_sec = pyomo.Set(initialize=range(0, 7))
    # param def for price reduction

    # m.P_sec = pyomo.Param(m.nsteps_sec, initialize={
    #    0: 0,
    #    1: 13593.82044,
    #    2: 26741.2835,
    #    3: 39457.04547,
    #    4: 51755.28139,
    #    5: 63649.70086,
    #    6: 75153.56332
    # })
    # 2 LR 2%
    # m.P_sec = pyomo.Param(m.nsteps_sec, initialize={
    #    0: 0,
    #    1: 26872.52452,
    #    2: 52000.76746,
    #    3: 75497.94923,
    #    4: 97469.94116,
    #    5: 118015.7425,
    #    6: 137227.9266
    # })

    # 3 LR 5%
    variation_5 = {
        0: 0,
        1: 64859.87772,
        2: 119558.3938,
        3: 165687.4918,
        4: 204589.7114,
        5: 237397.2614,
        6: 265064.9716,
    }

    # 4 LR 10%
    variation_10 = {
        0: 0,
        1: 108674,
        2: 185256,
        3: 239222,
        4: 277252,
        5: 304051,
        6: 322936,
    }

    # 5 LR 25%
    variation_25 = {
        0: 0,
        1: 254792.7496,
        2: 352775.4865,
        3: 390455.5883,
        4: 404945.7946,
        5: 410518.1277,
        6: 412661.0161,
    }
    # EEM6 LR 2.5%
    variation_6 = {
        0: 0,
        1: 33395.02122,
        2: 64096.25634,
        3: 92320.99775,
        4: 118269.0101,
        5: 142123.9441,
        6: 164054.6365,
    }
    # EEM7 LR 3%
    variation_7 = {
        0: 0,
        1: 39840.31305,
        2: 75846.68759,
        3: 108388.0736,
        4: 137797.9162,
        5: 164377.572,
        6: 188399.3973,
    }
    # EEM8 LR 3.5%
    variation_8 = {
        0: 0,
        1: 46208.92298,
        2: 87260.20208,
        3: 123729.5116,
        4: 156128.2716,
        5: 184910.8195,
        6: 210480.7816,
    }
    # EEM9 LR 4%
    variation_9 = {
        0: 0,
        1: 52501.37307,
        2: 98344.78919,
        3: 138374.5766,
        4: 173327.9901,
        5: 203848.7895,
        6: 230499.0966,
    }
    # EEM10 LR 4.5%
    variation_45 = {
        0: 0,
        1: 58718.18454,
        2: 109108.2889,
        3: 152351.496,
        4: 189461.4601,
        5: 221308.0674,
        6: 248637.827,
    }
    # EEM11 LR 3.75%
    variation_11 = {
        0: 0,
        1: 49364.63541,
        2: 92843.11808,
        3: 131137.3026,
        4: 164865.3556,
        5: 194571.7345,
        6: 220735.9768,
    }
    # EEM12 LR 3.6%
    variation_12 = {
        0: 0,
        1: 47473.48909,
        2: 89503.18068,
        3: 126713.3165,
        4: 159656.5562,
        5: 188822.1859,
        6: 214643.3852,
    }
    # EEM13 LR 3.7%
    variation_13 = {
        0: 0,
        1: 48735.01299,
        2: 91733.06585,
        3: 129669.4987,
        4: 163140.1525,
        5: 192670.7272,
        6: 218725.0388,
    }
    # EEM14 LR 3.55%
    # Define variation_14 correctly for each (nsteps_sec, tech) combination.
    # Assuming wind is added to m.tech and further locations
    # P_sec initialization (price reduction)
    variation_14_updated = {
        (n, tech, loc): (
            value if tech in ["solarPV", "windon", "windoff", "Batteries"] else 0
        )
        for n, value in {
            0: 0,
            1: 46841.69972,
            2: 88383.54549,
            3: 125225.1836,
            4: 157898.4141,
            5: 186874.8668,
            6: 212572.8099,
        }.items()
        for tech in m.tech
        for loc in m.location
    }

    uniform_cost_reduction = {
        0: 0,
        1: 46841.69972,
        2: 88383.54549,
        3: 125225.1836,
        4: 157898.4141,
        5: 186874.8668,
        6: 212572.8099,
    }

    # Cost reduction for wind onshore and offshore 25 %
    wind_cost_reduction = {
        0: 0,
        1: 305258.9464,
        2: 422648.8921,
        3: 467792.20,
        4: 485152.4495,
        5: 491828.4814,
        6: 494395.80,
    }

    # Cost reduction for batteries 25%
    batterie_cost_reduction = {
        0: 0,
        1: 141551.5276,
        2: 195986.3814,
        3: 216919.77,
        4: 224969.88,
        5: 228065.6265,
        6: 229256.12,
    }

    # Cost reduction for pv 25%
    PV_cost_reduction = {
        0: 0,
        1: 226482.4441,
        2: 313578.21,
        3: 347071.634,
        4: 359951.8174,
        5: 364905,
        6: 366809.7921,
    }

    # New: 25% reduction percentage for all techs
    reduction_percentage_25 = {
        0: 1,
        1: 0.384558576,
        2: 0.147885298,
        3: 0.05687056,
        4: 0.021870061,
        5: 0.00841032,
        6: 0.003234261,
    }

    # Updated: 1% reduction percentage for all techs
    reduction_percentage_1 = {
        0: 1,
        1: 0.967164685,
        2: 0.935407528,
        3: 0.904693127,
        4: 0.874987243,
        5: 0.846256761,
        6: 0.818469654,
    }

    # Scale factor to make the numbers larger for numerical stability
    scaling_factor = 100000  # Scale up by 100,000

    # Convert percentage multipliers to scaled reduction amounts
    # Since we want cost reduction to INCREASE from 0 to 6, we calculate (1 - percentage) and scale
    scaled_reductions_1 = {
        n: (1 - reduction_percentage_1[n]) * scaling_factor
        for n in reduction_percentage_1.keys()
    }

    scaled_reductions_25 = {
        n: (1 - reduction_percentage_25[n]) * scaling_factor
        for n in reduction_percentage_25.keys()
    }

    # Define reduction percentage for 3.5 scenario
    reduction_percentage_3_5 = {
        0: 1,
        1: 0.888384244,
        2: 0.789226565,
        3: 0.701136445,
        4: 0.622878571,
        5: 0.553355508,
        6: 0.491592315,
    }

    scaled_reduction3_5 = {
        n: (1 - reduction_percentage_3_5[n]) * scaling_factor
        for n in reduction_percentage_3_5.keys()
    }

    # Define reduction percentage for 4% scenario
    reduction_percentage_4 = {
        0: 1,
        1: 0.873185089,
        2: 0.7624522,
        3: 0.665761892,
        4: 0.581333357,
        5: 0.507611619,
        6: 0.443238897,
    }

    scaled_reduction4 = {
        n: (1 - reduction_percentage_4[n]) * scaling_factor
        for n in reduction_percentage_4.keys()
    }

    # Define reduction percentage for 10% scenario
    reduction_percentage_10 = {
        0: 1,
        1: 0.70468805,
        2: 0.496585247,
        3: 0.349937689,
        4: 0.246596908,
        5: 0.173773894,
        6: 0.122456386,
    }

    scaled_reduction10 = {
        n: (1 - reduction_percentage_10[n]) * scaling_factor
        for n in reduction_percentage_10.keys()
    }

    # Define reduction percentage for 5% scenario
    reduction_percentage_5 = {
        0: 1,
        1: 0.843333629,
        2: 0.711211609,
        3: 0.599788667,
        4: 0.505821953,
        5: 0.426576663,
        6: 0.359746445,
    }

    scaled_reduction5 = {
        n: (1 - reduction_percentage_5[n]) * scaling_factor
        for n in reduction_percentage_5.keys()
    }

    # Define reduction percentage for 6% scenario (new)
    reduction_percentage_6 = {
        0: 1,
        1: 0.814202932,
        2: 0.662926414,
        3: 0.53975663,
        4: 0.439471431,
        5: 0.357818927,
        6: 0.29133722,
    }

    scaled_reduction6 = {
        n: (1 - reduction_percentage_6[n]) * scaling_factor
        for n in reduction_percentage_6.keys()
    }

    # Store the scaling factor as a parameter for use in cost calculations
    m.scaling_factor = pyomo.Param(initialize=scaling_factor, doc="Scaling factor for price reductions")

    # Initialize P_sec with scaled values
    m.P_sec = pyomo.Param(
        m.location,  # Locations
        m.tech,  # Technologies
        m.nsteps_sec,  # Steps
        initialize=lambda m, loc, tech, n: scaled_reductions_25[n],
        doc="Scaled price reduction values (to be divided by scaling_factor in cost function)"
    )

    # param def for Capacity needed to reach next step
    # Initialize the dictionary with values for capacityperstep_sec
    # capacity_init_values = {}

    # Loop over all nsteps_sec, location, and tech
    # for n in m.nsteps_sec:
    #    for loc in m.location:
    #        for tech in m.tech:
    #            if tech == "solarPV":
    #                # Use the predefined capacity values for solarPV (or any logic you want for tech)
    #                capacity_init_values[(n, loc, tech)] = {
    #                    0: 0,
    #                    1: 100,
    #                    2: 1000,
    #                    3: 10000,
    #                    4: 100000,
    #                    5: 1000000,
    #                    6: 10000000,
    #                }.get(n, 0)  # Default to 0 for other steps
    #            else:
    #               # For other technologies (like wind), set the default to 0
    #               capacity_init_values[(n, loc, tech)] = {
    #                   0: 0,
    #                   1: 100,
    #                   2: 1000,
    #                   3: 10000,
    #                   4: 100000,
    #                   5: 1000000,
    #                   6: 10000000,
    #               }.get(n, 0)  # Default to 0 for other steps
    # print(capacity_init_values)

    # Now initialize the Param with the dictionary TODO reenable if wokrs again
    # m.capacityperstep_sec = pyomo.Param(
    #    m.nsteps_sec, m.location, m.tech, initialize=capacity_init_values
    # )

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
        (loc, tech, n): uniform_step_values.get(n, 0)
        for loc in m.location
        for tech in m.tech
        for n in m.nsteps_sec
    }

    # Initialize the Pyomo Param
    m.capacityperstep_sec = pyomo.Param(
        m.location,  # First dimension
        m.tech,  # Second dimension
        m.nsteps_sec,  # Third dimension
        initialize=capacity_init_values,
    )

    # param for gamma
    m.gamma_sec = pyomo.Param(initialize=1e10)

    m.total_secondary_cap_inital = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("Initial_secondary_cap", default_value=0),
    )

    ##########----------end EEM Addition-----------###############
    ##########----------    urbs-scrap  -----------###############
    m.f_scrap = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("scrap", default_value=0),
        doc="tons per MW",
    )
    m.f_mining = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("mining"),
        doc="tons per MW",
    )
    m.f_recycling = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("recycling_efficiency"),
        doc="recycling efficiency in %",
    )
    m.f_scrap_rec = pyomo.Param(
        m.stf,
        m.location,
        m.tech,
        initialize=data_urbsextensionv1["recyclingcost_dict"],
        doc="cost for recycling in EUR/ton",
    )
    m.f_increase = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("IR_recycling", default_value=0),
        doc="Fraction of increase in production",
    )
    m.capacity_dec_start = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("Initial_decommisions", default_value=0),
        doc="initial decommisions",
    )

    ##########----------end urbs-scrap  -----------###############
    # added for carry over.
    m.pricereduction_sec_init = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("price_reduction_init", default_value=0),
        doc="price_reduction_init",
    )

    m.cap_prim_prior = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("last_prim_cap", default_value=0),
        doc="last_prim_cap",
    )
    m.cap_sec_prior = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("last_sec_cap", default_value=0),
        doc="last_sec_cap",
    )

    m.factor_bess = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("factor_bess", default_value=0),
        doc="factor_bess",
    )

    m.scrap_total = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("capacity_scrap_total", default_value=0),
        doc="capacity_scrap_total",
    )
    m.total_facility_cap_initial = pyomo.Param(
        m.location,
        m.tech,
        initialize=initialize_param("total_facility_cap_initial", default_value=0),
        doc="total_facility_cap_initial",
    )

