from abc import ABC, abstractmethod
import pyomo.environ as pyomo
from pyomo.environ import value

class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m,stf, location, tech):
        pass


DEBUG = False


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# ==============================================================================#
# GROUP 1: LOGIC CONSTRAINTS (Index: stf, location, tech)                       #
# ==============================================================================#

class ScrapCostSavingsCalculationRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        Calculates Total Cost Savings for Recycling based on active scaling step.
        Savings = Sum_n( Reduction_Value[n] * Aux_Recycling_Output[n] )
        """
        # CON: Scrap Cost Savings | Calculates total cost savings for recycling based on active scaling step
        scrap_reduction_value = sum(
            m.P_sec_recycling[location, tech, n]
            * m.ap_BDV_scrap[stf, location, tech, n]
            for n in m.nsteps_sec
        )

        return m.pricereduction_scrap[stf, location, tech] == scrap_reduction_value


class ScrapUnitReductionCalculationRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        Calculates Unit Price Reduction (EUR/MW_recycling) based on active binary.
        """
        # CON: Scrap Unit Price Reduction | Calculates current unit price reduction for recycling
        unit_reduction_value = sum(
            m.P_sec_recycling[location, tech, n] * m.BDV_scrap[stf, location, tech, n]
            for n in m.nsteps_sec
        )

        return m.pricereduction_stage[stf, location, tech] == unit_reduction_value


class ScrapStepSelectionConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        Force exactly one recycling scale step to be active per year/loc/tech.
        """
        # CON: Scrap Step Selection | Forces exactly one recycling scale step to be active
        bd_sum = sum(m.BDV_scrap[stf, location, tech, n] for n in m.nsteps_sec)
        return bd_sum == 1


class ScrapMonotonicityConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        Enforce Monotonicity: We cannot 'unlearn' or lose economies of scale.
        Recycling efficiency (Price Reduction) today >= yesterday.
        """
        # CON: Scrap Price Monotonicity | Ensures recycling price reductions cannot decrease over time
        if stf == 2024:
            return pyomo.Constraint.Skip

        if stf == value(m.y0):
            # Compare to Initial State parameter (ensure param has stage index)
            # Assuming m.pricereduction_sec_init is indexed by (loc, tech)
            lhs = m.pricereduction_stage[stf, location, tech]
            # Fallback if init param doesn't have stage:
            rhs = 0
            return lhs >= rhs

        else:
            lhs = m.pricereduction_stage[stf, location, tech]
            rhs = m.pricereduction_stage[stf - 1, location, tech]
            return lhs >= rhs


class ScrapCumulativeThresholdConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        THE DRIVER: Cumulative Recycling Capacity >= Threshold of active step.
        """
        # CON: Scrap Cumulative Threshold | Links cumulative recycling capacity to the active learning step
        y0 = min(m.stf)

        # 1. Calculate Cumulative Recycling Capacity (Initial + New Installations)
        cumulative_cap = m.total_recycling_cap_initial[location, tech] + sum(
            m.capacity_scrap_rec[year, location, tech]
            for year in m.stf
            if y0 <= year <= stf
        )

        # 2. Identify Threshold of active step
        active_threshold = sum(
            m.BDV_scrap[stf, location, tech, n] * m.tons_perstep_recycling[location, tech, n]
            for n in m.nsteps_sec
        )

        return cumulative_cap >= active_threshold


# ==============================================================================
# GROUP 2: LINEARIZATION CONSTRAINTS (Index: stf, location, tech, n)
# ==============================================================================

class ScrapLinearizationBigMConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        """
        Auxiliary Variable Upper Bound (BigM Logic)
        Aux <= BigM * Binary
        """
        # CON: Scrap Linearization Upper Bound Z | Big-M constraint for scrap linearization
        lhs = m.ap_BDV_scrap[stf, location, tech, n]
        rhs = m.gamma_scrap * m.BDV_scrap[stf, location, tech, n]
        return lhs <= rhs


class ScrapLinearizationOutputConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        """
        Auxiliary Variable <= Current Recycling Output
        Ensures we apply cost savings only to actual capacity deployed.
        """
        # CON: Scrap Linearization Upper Bound Q | Ensures scrap aux variable does not exceed actual output
        lhs = m.ap_BDV_scrap[stf, location, tech, n]
        rhs = m.capacity_scrap_rec[stf, location, tech]
        return lhs <= rhs


class ScrapLinearizationLowerBoundConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        """
        Auxiliary Variable Lower Bound (BigM Logic)
        Aux >= Current Output - BigM * (1 - Binary)
        """
        # CON: Scrap Linearization Lower Bound | Ensures scrap aux variable tracks output when binary is active
        lhs = m.ap_BDV_scrap[stf, location, tech, n]
        rhs = (
                m.capacity_scrap_rec[stf, location, tech]
                - (1 - m.BDV_scrap[stf, location, tech, n]) * m.gamma_scrap
        )
        return lhs >= rhs


class ScrapLinearizationNonNegativityConstraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        # CON: Scrap Linearization Non-Negativity | Ensures scrap aux variable is non-negative
        return m.ap_BDV_scrap[stf, location, tech, n] >= 0


# ==============================================================================
# APPLICATION LOGIC
# ==============================================================================

def apply_scrap_scaling_constraints(m):
    """
    Registers the economies of scale constraints for Scrap/Recycling.
    """

    # 1. Logic Constraints (Index: stf, location, tech)
    constraints_scrap_logic = [
        ScrapCostSavingsCalculationRule(),
        ScrapUnitReductionCalculationRule(),
        ScrapStepSelectionConstraint(),
        ScrapMonotonicityConstraint(),
        ScrapCumulativeThresholdConstraint(),
    ]

    # 2. Linearization Constraints (Index: stf, location, tech, n)
    constraints_scrap_linearization = [
        ScrapLinearizationBigMConstraint(),
        ScrapLinearizationOutputConstraint(),
        ScrapLinearizationLowerBoundConstraint(),
        ScrapLinearizationNonNegativityConstraint(),
    ]

    print(f"DEBUG: Registering Scrap Economies of Scale Constraints...")

    # Apply Logic Constraints
    for i, constraint in enumerate(constraints_scrap_logic):
        # Naming convention: Scrap_Logic_1, Scrap_Logic_2, etc.
        constraint_name = f"constraint_scrap_logic_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf, m.location, m.tech,
                rule=lambda m, stf, loc, tech: constraint.apply_rule(m, stf, loc, tech),
            ),
        )

    # Apply Linearization Constraints
    for i, constraint in enumerate(constraints_scrap_linearization):
        # Naming convention: Scrap_Lin_1, Scrap_Lin_2, etc.
        constraint_name = f"constraint_scrap_lin_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf, m.location, m.tech, m.nsteps_sec,
                rule=lambda m, stf, loc, tech, n: constraint.apply_rule(m, stf, loc, tech, n),
            ),
        )

    print("Scrap/Recycling scaling constraints applied successfully.")