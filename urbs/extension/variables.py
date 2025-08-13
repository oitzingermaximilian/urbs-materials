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
        m.stf, m.location, m.tech, m.nsteps_sec,
        within=pyomo.NonNegativeReals,
        doc="Auxiliary variable for linearizing BD_sec * capacity_ext_eusecondary"
    )

    """
    These Variables are used for the lr_manufacturing.py script constraints.
    """
    # m.pricereduction_pri = pyomo.Var(m.stf, domain=pyomo.NonNegativeReals)
    # m.BD_pri = pyomo.Var(m.stf, m.nsteps_pri, domain=pyomo.Binary)

    """
    These Variables are used for the lr_remanufacturing.py script constraints.
    """
    # New separate variables for investment and recycling cost reductions (absolute values)
    m.pricereduction_sec_investment = pyomo.Var(
        m.stf, m.location, m.tech, domain=pyomo.NonNegativeReals
    )
    # pricereduction_sec_recycling is now defined as an Expression in lr_remanufacturing.py
    # to derive its value from BD_sec variables determined by investment constraint

    m.BD_sec = pyomo.Var(m.stf, m.location, m.tech, m.nsteps_sec, domain=pyomo.Binary)

    m.auxiliary_product_BD_q = pyomo.Var(
        m.stf, m.location, m.tech, m.nsteps_sec, domain=pyomo.NonNegativeReals
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
