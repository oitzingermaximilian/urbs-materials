import pyomo.core as pyomo

def apply_gas_block_pricing(m, data):
    """
    Apply block-based gas pricing with yearly limits.
    Uses separate sets for years (stf) and block names.
    """
    # --- Sets ---
    m.blocks = pyomo.Set(initialize=list(data["block_names"]))  # block names only

    # m.stf should already exist in your model as years
    # m.tm, m.sit, m.com, m.com_type are assumed defined

    # --- Parameters ---
    # Indexed over (year, block)
    m.block_limits = pyomo.Param(
        m.stf, m.blocks,
        initialize=lambda m, stf, blk: data["block_limits"][(stf, blk)],
        within=pyomo.NonNegativeReals,
        doc="Max volume per block per year"
    )
    m.block_prices = pyomo.Param(
        m.stf, m.blocks,
        initialize=lambda m, stf, blk: data["block_price"][(stf, blk)],
        within=pyomo.NonNegativeReals,
        doc="Price per block per year"
    )

    # --- Variables ---
    m.e_co_stock_block = pyomo.Var(
        m.tm, m.stf, m.sit, m.com, m.com_type, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="Gas usage per timestep, site, commodity, type, year, block"
    )

    m.gas_cost = pyomo.Var(
        m.stf,
        within=pyomo.NonNegativeReals,
        doc="Total gas cost per block per year"
    )

    m.gas_total_cost = pyomo.Var(
        within=pyomo.NonNegativeReals,
        doc="Total gas cost over all years"
    )
    m.gas_usage_block = pyomo.Var(
        m.stf, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="Total Gas USage per Block per year in MWH"
    )

    # --- Constraints ---
    # 1) Yearly usage per block
    def yearly_block_limit_rule(m, stf, blk):
        return sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock",blk]
            for tm in m.tm for sit in m.sit
        ) <= m.block_limits[stf, blk]

    m.block_limit_constraint = pyomo.Constraint(m.stf, m.blocks, rule=yearly_block_limit_rule)

    # 2) Link: Link: the sum across blocks must equal the original e_co_stock for LNG/Stock
    #    Keep the same index pattern as m.e_co_stock

    def link_block_to_original_rule(m, tm, stf, sit, com, com_type):
        if com != "Gas" or com_type != "Stock":
            return pyomo.Constraint.Skip
        else:
            return m.e_co_stock[tm, stf, sit, com, com_type] == \
                sum(m.e_co_stock_block[tm, stf, sit, com, com_type, blk] for blk in m.blocks)
    m.link_block_to_original_rule = pyomo.Constraint(m.tm, m.stf, m.sit, m.com, m.com_type, rule=link_block_to_original_rule)

    # 3) Yearly cost per block
    def yearly_cost_rule(m, stf):
        yearly_gas_cost = sum(
            m.block_prices[stf, blk] * m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit for blk in m.blocks
        )
        return m.gas_cost[stf] == yearly_gas_cost

    m.yearly_cost_constraint = pyomo.Constraint(m.stf, rule=yearly_cost_rule)

    # 4) Total cost across all years and blocks
    def total_cost_rule(m):
        return m.gas_total_cost == sum(m.gas_cost[stf] for stf in m.stf)
    m.total_cost_constraint = pyomo.Constraint(rule=total_cost_rule)

    # 5) Yearly usage per block
    def yearly_usage_block_rule(m, stf, blk):
        return m.gas_usage_block[stf, blk] == sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit
        )
    m.yearly_usage_block_constraint = pyomo.Constraint(m.stf, m.blocks, rule=yearly_usage_block_rule)

    print("✅ Gas block pricing applied successfully (separate sets for years and blocks).")
