import pyomo.environ as pyomo


def apply_variables(m):
    """
    These Variables are used for the stockpile.py script constraints
    """

    m.capacity_ext = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)
    m.capacity_ext_new = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_imported = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_stockout = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_euprimary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_facility_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_inactive_eusecondary = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_stock = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_ext_stock_imported = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    m.sum_outofstock = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.sum_stock = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)
    m.anti_dumping_measures = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the balance_converter.py script constraints & build the bridge between the standard urbs model and the extension model.
    The balance_ext variable is added to the res_vertex_rule in the standard urbs model.
    """
    m.balance_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )  # --> res_vertex_rule
    m.balance_import_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.balance_outofstock_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.balance_EU_primary_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.balance_EU_secondary_ext = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the costs.py script constraints & build the bridge between the standard urbs model and the extension model.
    The costs_new variable is added to the main objective function where costs are minimized in the standard urbs model.
    """
    m.costs_new = pyomo.Var(m.cost_type_new, domain=pyomo.NonNegativeReals)
    m.costs_ext_import = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.costs_ext_storage = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.costs_EU_primary = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )
    m.costs_EU_secondary = pyomo.Var(
        m.stf, m.location, m.tech, within=pyomo.NonNegativeReals
    )

    """
    Auxiliary variable for Big-M linearization of bilinear terms
    This replaces the product: BD_sec * capacity_ext_eusecondary
    """
    m.auxiliary_product_BD_q = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.nsteps_sec,
        within=pyomo.NonNegativeReals,
        doc="Auxiliary variable for linearizing BD_sec * capacity_ext_eusecondary",
    )


    """
    These Variables are used for the lr_remanufacturing.py script constraints.
    """
    """
    Binary Decision Variable: Determines which 'Learning Step' (Efficiency Tier) 
    a specific technology stage is currently operating in.
    Dimensions: Time, Location, Tech, STAGE, Step
    """
    m.BD_sec = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,  # <--- ADDED
        m.nsteps_sec,
        domain=pyomo.Binary,
        doc="Binary variable: 1 if stage is in learning step n, 0 otherwise"
    )

    """
    Auxiliary variable for Big-M linearization of bilinear terms.
    This replaces the product: BD_sec * capacity_produced_output
    Dimensions: Time, Location, Tech, STAGE, Step
    """
    m.auxiliary_product_BD_q = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,  # <--- ADDED
        m.nsteps_sec,
        within=pyomo.NonNegativeReals,
        doc="Auxiliary variable for linearizing BD_sec * capacity_produced_output",
    )

    """
    Resulting Unit Price Reduction (EUR/MW).
    This tracks the specific cost reduction value active in a given year.
    Dimensions: Time, Location, Tech, STAGE
    """
    m.pricereduction_sec_investment = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,  # <--- ADDED
        domain=pyomo.NonNegativeReals,
        doc="Current value of cost reduction (EUR/MW) based on active step"
    )

    """
    Total Cost Savings (EUR).
    This is the value subtracted from the total OPEX (Savings = Unit_Reduction * Production).
    Dimensions: Time, Location, Tech, STAGE
    """
    m.PRICEREDUCTION_CAP_DEP_INV = pyomo.Var(
        m.stf,
        m.location,
        m.tech,
        m.stages,  # <--- ADDED
        domain=pyomo.NonNegativeReals,
        doc="Total operational cost savings (EUR) due to learning effects"
    )

    """
    These Variables are used for the scrap.py script constraints.
    """

    m.capacity_dec = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)
    m.capacity_scrap_dec = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_scrap_rec = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.capacity_scrap_total = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.cost_scrap = pyomo.Var(m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals)

    """
    These Variables are used to simulate a imaginary BESS demand in order to cover the dynamics of battery energy storage systems as well
    """

    m.demand_bess = pyomo.Var(m.stf, m.location, domain=pyomo.NonNegativeReals)

    m.capacity_secondary_cumulative = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    m.capacity_facility_cumulative = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    m.costs_O_and_M = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    m.demand_production = pyomo.Var(
        m.timesteps_ext, m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )

    """
    These Variables are used for the materials.py script constraints. And are the latest addition to the model.
    """

    m.capacity_total_factory = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_new_factory = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # --- 2. PRODUCTION & FLOWS (Dimensions: stf, location, tech, stage) ---
    m.capacity_produced_output = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # Domestic Splits
    m.capacity_produced_flow = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_produced_storage = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_produced_stockout = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # Import Splits
    m.capacity_imported = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_imported_flow = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_imported_storage = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.capacity_imported_stockout = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # Supply Available for Next Stage (Coupling Variable)
    m.Supply = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # --- 3. STOCKPILES (Dimensions: stf, location, tech, stage) ---
    m.stock_domestic = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    m.stock_imported = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)
    # Aggregate for reporting
    m.components_stockpile = pyomo.Var(m.stf, m.location, m.tech, m.stages, domain=pyomo.NonNegativeReals)

    # --- 4. MATERIAL FLOWS (Dimensions: stf, [location], material) ---
    # Demand Calculation
    m.demand_material_total = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)

    # Supply Side
    m.material_mined = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)  # Or (stf, loc, mat)
    m.material_imported = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)
    m.material_recycled = pyomo.Var(m.stf, m.materials, domain=pyomo.NonNegativeReals)  # Or (stf, loc, mat)
    m.demand_production = pyomo.Var(
        m.timesteps_ext,
        m.stf,
        m.location,
        m.tech,
        within=pyomo.NonNegativeReals,
        doc="Electricity demand for manufacturing per stage (MWh)"
    )

    # --- 5. COSTS (Dimensions: stf) ---
    m.cost_capex_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)
    m.cost_opex_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)
    m.cost_trade_total_extension = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)
    m.cost_stockpile_holding = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)
