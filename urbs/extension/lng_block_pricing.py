import pyomo.core as pyomo

def apply_gas_block_pricing(m, data):
    # --- Sets ---
    block_keys = list(data["limit"].keys())  # list of (stf, block_name)
    m.blocks = pyomo.Set(dimen=2, initialize=block_keys)

    # Convenience: blocks available per year
    def blocks_per_year_init(m, stf):
        return [blk for (y, blk) in m.blocks if y == stf]

    m.blocks_per_year = pyomo.Set(m.stf, initialize=blocks_per_year_init)

    # --- Parameters ---
    # --- Parameters ---
    m.block_limits = pyomo.Param(m.blocks, initialize=data["limits"], doc="Max volume per block per year (MWh)")
    m.block_price = pyomo.Param(m.blocks, initialize=data["prices"], doc="Price €/MWh per block per year")

    # --- Variables ---
    m.e_co_stock_block = pyomo.Var(
        m.tm, m.stf, m.sit, m.com, m.com_type, m.blocks_per_year[m.stf],
        within=pyomo.NonNegativeReals,
        doc="Gas usage per timestep, site, block"
    )

    m.block_costs = pyomo.Var(
        m.stf,
        within=pyomo.NonNegativeReals,
        doc="Yearly gas costs across all blocks"
    )

    m.total_block_costs = pyomo.Var(
        within=pyomo.NonNegativeReals,
        doc="Total gas cost across all years"
    )

    m.block_usage = pyomo.Var(
        m.stf, m.blocks_per_year[m.stf],
        within=pyomo.NonNegativeReals,
        doc="Total Gas usage per block per year"
    )

    m.total_usage = pyomo.Var(
        m.stf,
        within=pyomo.NonNegativeReals,
        doc="Total Gas usage per year"
    )

    # --- Constraints ---

    # 1) Yearly block capacity
    def yearly_block_limit_rule(m, stf, blk):
        return sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit
        ) <= m.block_limits[blk]

    m.block_yearly_caps = pyomo.Constraint(
        m.stf, lambda m, stf: m.blocks_per_year[stf],
        rule=yearly_block_limit_rule
    )

    # 2) Link blocks to total Gas stock
    def link_blocks_to_total_rule(m, tm, stf, sit, com, com_type):
        if com != "Gas" or com_type != "Stock":
            return pyomo.Constraint.Skip
        return m.e_co_stock[tm, stf, sit, com, com_type] == sum(
            m.e_co_stock_block[tm, stf, sit, com, com_type, blk]
            for blk in m.blocks_per_year[stf]
        )

    m.block_link = pyomo.Constraint(m.tm, m.stf, m.sit, m.com, m.com_type, rule=link_blocks_to_total_rule)

    # 3) Yearly block cost
    def yearly_block_cost_rule(m, stf):
        return m.block_costs[stf] == sum(
            m.block_price[stf, blk] * m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit for blk in m.blocks_per_year[stf]
        )

    m.block_cost_constraint = pyomo.Constraint(m.stf, rule=yearly_block_cost_rule)

    # 4) Total gas cost
    def total_block_cost_rule(m):
        return m.total_block_costs == sum(m.block_costs[stf] for stf in m.stf)

    m.total_block_cost_constraint = pyomo.Constraint(rule=total_block_cost_rule)

    # 5) Yearly usage per block
    def block_usage_rule(m, stf, blk):
        return m.block_usage[stf, blk] == sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit
        )

    m.block_usage_constraint = pyomo.Constraint(
        m.stf, lambda m, stf: m.blocks_per_year[stf],
        rule=block_usage_rule
    )

    # 6) Total usage per year
    def total_usage_rule(m, stf):
        return m.total_usage[stf] == sum(m.block_usage[stf, blk] for blk in m.blocks_per_year[stf])

    m.total_usage_constraint = pyomo.Constraint(m.stf, rule=total_usage_rule)

    print("✅ Gas block pricing applied (continuous allocation, yearly caps, blocks indexed by stf).")
