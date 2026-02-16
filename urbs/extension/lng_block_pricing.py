import pyomo.core as pyomo
from .costs import discount_factor, effective_distance
from urbs.features.modelhelper import stf_dist


def apply_gas_block_pricing(m, data):
    """
    Apply block-based gas pricing with internal GWh scaling for numerical stability.
    Input data remains in MWh/€ per MWh, but internal math is scaled.
    """

    # --- Sets ---
    m.blocks = pyomo.Set(initialize=list(data["block_names"]))

    # --- Parameters ---
    # NOM: L^{gas}_{y,b} | Scaled to GWh
    m.block_limits = pyomo.Param(
        m.stf, m.blocks,
        initialize=lambda m, stf, blk: data["block_limits"][(stf, blk)] ,
        within=pyomo.NonNegativeReals,
        doc="Max volume per block per year (Internal: GWh)",
    )

    # NOM: P^{gas}_{y,b} | Scaled to EUR/GWh
    # Price must be divided by scale so that (EUR/GWh * GWh) = EUR
    m.block_prices = pyomo.Param(
        m.stf, m.blocks,
        initialize=lambda m, stf, blk: data["block_price"][(stf, blk)],
        within=pyomo.NonNegativeReals,
        doc="Price per block per year (Internal: EUR/GWh)",
    )

    # --- Variables ---
    # This variable now operates in the GWh range
    m.e_co_stock_block = pyomo.Var(
        m.tm, m.stf, m.sit, m.com, m.com_type, m.blocks,
        within=pyomo.NonNegativeReals,
        doc="Gas usage per timestep (Internal: GWh)",
    )

    m.gas_cost = pyomo.Var(m.stf, within=pyomo.NonNegativeReals)
    m.gas_total_cost = pyomo.Var(within=pyomo.NonNegativeReals)

    # We keep this in MWh for easier reporting/debugging
    m.gas_usage_block = pyomo.Var(m.stf, m.blocks, within=pyomo.NonNegativeReals)

    # --- Constraints ---

    # 1) Yearly usage per block (GWh vs GWh)
    def yearly_block_limit_rule(m, stf, blk):
        return sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit
        ) <= m.block_limits[stf, blk]

    m.block_limit_constraint = pyomo.Constraint(m.stf, m.blocks, rule=yearly_block_limit_rule)

    # 2) Link: Original e_co_stock (MWh) == Sum of blocks (GWh) * 1000
    def link_block_to_original_rule(m, tm, stf, sit, com, com_type):
        if com != "Gas" or com_type != "Stock":
            return pyomo.Constraint.Skip
        return m.e_co_stock[tm, stf, sit, com, com_type] == sum(
            m.e_co_stock_block[tm, stf, sit, com, com_type, blk] for blk in m.blocks
        )

    m.link_block_to_original_constraint = pyomo.Constraint(
        m.tm, m.stf, m.sit, m.com, m.com_type, rule=link_block_to_original_rule
    )

    # 3) Yearly cost (EUR/GWh * GWh = EUR)
    def yearly_cost_rule(m, stf):
        yearly_gas_cost = sum(
            m.block_prices[stf, blk] * m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit for blk in m.blocks
        )
        dist = stf_dist(stf, m)
        gas_cost_factor = discount_factor(stf) * effective_distance(dist)
        return m.gas_cost[stf] == yearly_gas_cost * gas_cost_factor

    m.yearly_cost_constraint = pyomo.Constraint(m.stf, rule=yearly_cost_rule)

    # 4) Total cost
    m.total_cost_constraint = pyomo.Constraint(
        expr=m.gas_total_cost == sum(m.gas_cost[stf] for stf in m.stf)
    )

    # 5) Yearly usage definition (Convert GWh back to MWh for the variable)
    def yearly_usage_block_rule(m, stf, blk):
        return m.gas_usage_block[stf, blk] == sum(
            m.e_co_stock_block[tm, stf, sit, "Gas", "Stock", blk]
            for tm in m.tm for sit in m.sit
        )

    m.yearly_usage_block_constraint = pyomo.Constraint(m.stf, m.blocks, rule=yearly_usage_block_rule)

