import pyomo.core as pyomo

def add_lng_block_pricing(m, commodity="LNG", com_type="Stock"):

    # ----- Filter LNG tuples only -----
    lng_tuples = [c for c in m.com_tuples if c[3] == commodity and c[2] == com_type]

    # ----- Variables per block -----
    m.e_co_stock_block = pyomo.Var(
        lng_tuples, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="LNG usage per block per year"
    )

    # ----- Link LNG blocks to e_pro_in -----
    def link_blocks_to_pro_in_rule(m, c, b):
        stf, sit, pro, com = c
        return m.e_pro_in[(stf, (stf, sit, pro, com))] == sum(
            m.e_co_stock_block[c, bb] for bb in m.blocks
        )
    m.link_lng_to_pro_in = pyomo.Constraint(
        [(c, b) for c in lng_tuples for b in m.blocks],
        rule=link_blocks_to_pro_in_rule
    )

    # ----- Per-year block caps -----
    def block_cap_per_year_rule(m, stf, b):
        # Get all LNG tuples for this year
        tuples_this_year = [c for c in lng_tuples if c[0] == stf]
        if not tuples_this_year:
            return pyomo.Constraint.Feasible  # Skip if no LNG for this year
        return sum(m.e_co_stock_block[c, b] for c in tuples_this_year) <= m.block_limits[b, stf]

    m.block_cap_per_year = pyomo.Constraint(m.stf, m.blocks, rule=block_cap_per_year_rule)

    # ----- Total LNG cost -----
    m.LNG_cost = pyomo.Expression(
        expr=sum(
            m.block_price[b] * m.e_co_stock_block[c, b]
            for c in lng_tuples
            for b in m.blocks
        )
    )

    return m
