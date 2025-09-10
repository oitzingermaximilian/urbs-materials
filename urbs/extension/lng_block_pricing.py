import pyomo.core as pyomo

def apply_lng_block_pricing(m, data):
    # --- Sets ---
    # keep whatever block count you have; here 1..14
    m.blocks = pyomo.Set(initialize=list(range(1, 4)))  # 3 blocks

    # --- Parameters ---
    # block_limits: yearly volume limit per block (same indexing as data)
    m.block_limits = pyomo.Param(
        m.blocks,
        initialize={b: data["lng_block_limits"][b] for b in m.blocks},
        doc="Max LNG volume per block (yearly)"
    )

    # block_price: price per block (€/MWh) - same indexing as data["lng_block_price"]
    m.block_price = pyomo.Param(
        m.blocks,
        initialize=data["lng_block_price"],
        doc="LNG block price €/MWh"
    )

    # --- Variables ---
    # LNG usage split across blocks (per-timestep)
    m.e_co_stock_block = pyomo.Var(
        m.tm, m.stf, m.sit, m.com, m.com_type, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="LNG usage per timestep, site, commodity, type, block"
    )

    # LNG costs per year
    m.lng_costs = pyomo.Var(
        m.stf,
        within=pyomo.NonNegativeReals,
        doc="LNG costs per year"
    )

    # Total LNG cost (scalar)
    m.lng_total_costs = pyomo.Var(
        within=pyomo.NonNegativeReals,
        doc="Total LNG cost over all years"
    )

    # --- Constraints ---

    # 1) Yearly block capacity: sum over tm & sit for each year and block <= block limit
    def yearly_block_limit_rule(m, stf, b):
        return sum(
            m.e_co_stock_block[tm, stf, sit, "LNG", "Stock", b]
            for tm in m.tm for sit in m.sit
        ) <= m.block_limits[b]
    m.lng_block_yearly_caps = pyomo.Constraint(m.stf, m.blocks, rule=yearly_block_limit_rule)

    # 2) Link: the sum across blocks must equal the original e_co_stock for LNG/Stock
    #    Keep the same index pattern as m.e_co_stock
    def link_blocks_to_total_rule(m, tm, stf, sit, com, com_type):
        if com != "LNG" or com_type != "Stock":
            return pyomo.Constraint.Skip
        return m.e_co_stock[tm, stf, sit, com, com_type] == \
               sum(m.e_co_stock_block[tm, stf, sit, com, com_type, b] for b in m.blocks)
    # create the constraint over all e_co_stock indices (tm,stf,sit,com,com_type)
    m.lng_block_link = pyomo.Constraint(m.tm, m.stf, m.sit, m.com, m.com_type, rule=link_blocks_to_total_rule)

    # 3) Yearly LNG cost: cost = sum_{tm,sit,b} block_price[b] * e_co_stock_block[tm,stf,sit,"LNG","Stock",b]
    def yearly_lng_cost_rule(m, stf):
        yearly_lng_cost = sum(
            m.block_price[b] * m.e_co_stock_block[tm, stf, sit, "LNG", "Stock", b]
            for tm in m.tm
            for sit in m.sit
            for b in m.blocks
        )
        return m.lng_costs[stf] == yearly_lng_cost
    m.lng_cost_constraint = pyomo.Constraint(m.stf, rule=yearly_lng_cost_rule)

    # 4) Total LNG cost across all years
    def total_lng_cost_rule(m):
        return m.lng_total_costs == sum(m.lng_costs[stf] for stf in m.stf)
    m.lng_total_cost_constraint = pyomo.Constraint(rule=total_lng_cost_rule)

    # 5) Total LNG usage each year
    # New variable: yearly LNG usage per block
    m.lng_usage_block = pyomo.Var(
        m.stf, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="Total LNG usage per block per year (MWh)"
    )

    def yearly_usage_block_rule(m, stf, b):
        return m.lng_usage_block[stf, b] == sum(
            m.e_co_stock_block[tm, stf, sit, "LNG", "Stock", b]
            for tm in m.tm for sit in m.sit
        )

    m.lng_usage_block_constraint = pyomo.Constraint(m.stf, m.blocks, rule=yearly_usage_block_rule)

    m.lng_usage_total = pyomo.Var(
        m.stf,
        within=pyomo.NonNegativeReals,
        doc="Total LNG usage per year (MWh)"
    )

    def yearly_usage_total_rule(m, stf):
        return m.lng_usage_total[stf] == sum(m.lng_usage_block[stf, b] for b in m.blocks)

    m.lng_usage_total_constraint = pyomo.Constraint(m.stf, rule=yearly_usage_total_rule)

    # Small sanity print (optional)
    print("✅ LNG block pricing applied (continuous allocation, yearly caps).")
