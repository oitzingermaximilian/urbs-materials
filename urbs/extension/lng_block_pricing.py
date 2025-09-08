import pyomo.core as pyomo

def add_lng_block_pricing(m, commodity="LNG", com_type="Stock"):
    # ----- Variables -----
    m.e_co_stock_block = pyomo.Var(
        m.tm, m.com_tuples, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="LNG usage per block per timestep and year"
    )

    # ----- Link to total stock -----
    def link_blocks_rule(m, tm, stf, sit, com, ctype):
        if com == commodity and ctype == com_type:
            return m.e_co_stock[tm, stf, sit, com, ctype] == sum(
                m.e_co_stock_block[tm, stf, sit, com, ctype, b] for b in m.blocks
            )
        return pyomo.Constraint.Skip
    m.link_blocks = pyomo.Constraint(m.tm, m.com_tuples, rule=link_blocks_rule)

    # ----- Per-year block caps -----
    def block_cap_per_year_rule(m, stf, b):
        return sum(
            m.e_co_stock_block[tm, stf, sit, com, ctype, b]
            for tm in m.tm
            for (s, sit, com, ctype) in m.com_tuples
            if s == stf and com == commodity and ctype == com_type
        ) <= m.block_limits[b, stf]
    m.block_cap_per_year = pyomo.Constraint(m.stf, m.blocks, rule=block_cap_per_year_rule)

    # ----- Block cost expression -----
    def LNG_cost_rule(m):
        return sum(
            m.block_price[b] * m.e_co_stock_block[tm, stf, sit, com, ctype, b]
            for tm in m.tm
            for (stf, sit, com, ctype) in m.com_tuples
            if com == commodity and ctype == com_type
            for b in m.blocks
        )
    m.LNG_cost = pyomo.Expression(rule=LNG_cost_rule)

    return m