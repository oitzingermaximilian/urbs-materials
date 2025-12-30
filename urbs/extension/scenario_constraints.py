from abc import ABC, abstractmethod
import pyomo.core as pyomo


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 1. NZIA Benchmark (40% Domestic Production)
# ==============================================================================
class net_zero_industrialactbenchmark_rule_a(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        """
        Ensures domestic contribution (flow + stockout) is at least 40% of total Supply.
        """
        # Domestic Contribution = Flow from Production + Withdrawals from Domestic Stock
        # (Assuming 'capacity_produced_stockout' represents withdrawal from domestic stock)
        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage]
        )

        rhs = 0.4 * m.Supply[stf, location, tech, stage]

        # Use pyomo.Constraint.Skip if Supply is 0 to avoid numerical noise
        # (Optional but recommended)
        # if rhs == 0:
        #     return pyomo.Constraint.Skip

        return domestic_contribution >= rhs


# ==============================================================================
# 2. CRMA Extraction Target (10% Domestic Mining)
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        """
        Ensures domestic mining covers at least 10% of total material demand.
        """
        lhs = m.material_mined[stf, material]
        rhs = 0.10 * m.demand_material_total[stf, material]

        return lhs >= rhs


# ==============================================================================
# 3. CRMA Recycling Target (15% Recycling)
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        """
        Ensures recycling covers at least 15% of total material demand.
        """
        lhs = m.material_recycled[stf, material]
        rhs = 0.15 * m.demand_material_total[stf, material]

        return lhs >= rhs


# ==============================================================================
# Constraint Registration
# ==============================================================================
def apply_scenario_constraints(m):
    # --- 1. Register Manufacturing Constraints (Index: stf, loc, tech, stage) ---
    nzia_rule = net_zero_industrialactbenchmark_rule_a()

    m.net_zero_industrialactbenchmark_rule_a = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        m.stages,
        rule=lambda m, y, l, t, s: nzia_rule.apply_rule(m, y, l, t, s),
    )

    # --- 2. Register Material Constraints (Index: stf, material) ---
    extraction_rule = eu_extraction_constraint()
    recycling_rule = eu_recycling_constraint()

    m.eu_extraction_constraint = pyomo.Constraint(
        m.stf,
        m.materials,
        rule=lambda m, y, mat: extraction_rule.apply_rule(m, y, mat),
    )

    m.eu_recycling_constraint = pyomo.Constraint(
        m.stf,
        m.materials,
        rule=lambda m, y, mat: recycling_rule.apply_rule(m, y, mat),
    )

    print("Scenario constraints (NZIA & CRMA) registered successfully.")