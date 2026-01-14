from abc import ABC, abstractmethod
import pyomo.core as pyomo
from pyomo.environ import value


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


DEBUG = False  # Set True to enable debug logs


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# ==============================================================================
# GROUP 1: LOGIC CONSTRAINTS (Index: stf, location, tech, STAGE)
# ==============================================================================

class costsavings_constraint_sec_investment(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Calculates Total Cost Savings based on active learning step
        # Savings = Sum_n( Reduction_Value[n] * Aux_Production[n] )

        investment_reduction_value = sum(
            m.P_sec_investment[location, tech, stage, n]
            * m.auxiliary_product_BD_q[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )

        return m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech, stage] == investment_reduction_value


class pricereduction_stage_calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Calculates Unit Price Reduction (EUR/MW) based on active binary

        unit_reduction_value = sum(
            m.P_sec_investment[location, tech, stage, n] * m.BD_sec[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )

        return m.pricereduction_sec_investment[stf, location, tech, stage] == unit_reduction_value


class BD_limitation_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Force exactly one learning step to be active per stage
        bd_sum = sum(m.BD_sec[stf, location, tech, stage, n] for n in m.nsteps_sec)
        return bd_sum == 1


class relation_pnew_to_pprior_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Enforce Monotonicity: Price Reduction(y) >= Price Reduction(y-1)
        # "We cannot unlearn"

        if stf == 2024:
            return pyomo.Constraint.Skip

        if stf == value(m.y0):
            # Compare to Initial State parameter (ensure param has stage index)
            # Assuming m.pricereduction_sec_init is indexed by (loc, tech, stage)
            lhs = m.pricereduction_sec_investment[stf, location, tech, stage]
            # Fallback if init param doesn't have stage:
            rhs = 0  # Placeholder if no init data for stages yet
            return lhs >= rhs
        else:
            lhs = m.pricereduction_sec_investment[stf, location, tech, stage]
            rhs = m.pricereduction_sec_investment[stf - 1, location, tech, stage]
            return lhs >= rhs


class q_perstep_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        """
        THE DRIVER: Cumulative Production >= Threshold of active step.
        """
        y0 = min(m.stf)

        # 1. Calculate Cumulative Production (History + Current Accumulation)
        # Using capacity_produced_output as the driver
        cumulative_prod = m.total_production_cap_inital[location, tech, stage] + sum(
            m.capacity_produced_output[year, location, tech, stage]
            for year in m.stf
            if y0 <= year <= stf
        )

        # 2. Identify Threshold of active step
        # Note: capacityperstep_production now has [loc, tech, stage, n]
        active_threshold = sum(
            m.BD_sec[stf, location, tech, stage, n] * m.capacityperstep_production[location, tech, stage, n]
            for n in m.nsteps_sec
        )

        return cumulative_prod >= active_threshold


# ==============================================================================
# GROUP 2: LINEARIZATION CONSTRAINTS (Index: stf, location, tech, STAGE, n)
# ==============================================================================

class upper_bound_z_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux <= BigM * Binary
        # Using m.gamma_prod as BigM
        lhs = m.auxiliary_product_BD_q[stf, location, tech, stage, n]
        rhs = m.gamma_prod * m.BD_sec[stf, location, tech, stage, n]
        return lhs <= rhs


class upper_bound_z_q1_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux <= Current Production
        # We apply cost savings to CURRENT production
        lhs = m.auxiliary_product_BD_q[stf, location, tech, stage, n]
        rhs = m.capacity_produced_output[stf, location, tech, stage]
        return lhs <= rhs


class lower_bound_z_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux >= Current Production - BigM * (1 - Binary)
        lhs = m.auxiliary_product_BD_q[stf, location, tech, stage, n]
        rhs = (
                m.capacity_produced_output[stf, location, tech, stage]
                - (1 - m.BD_sec[stf, location, tech, stage, n]) * m.gamma_prod
        )
        return lhs >= rhs


class non_negativity_z_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        return m.auxiliary_product_BD_q[stf, location, tech, stage, n] >= 0



# ==============================================================================
# APPLICATION LOGIC
# ==============================================================================

def apply_combined_lr_constraints(m):
    # 1. Logic Constraints (Index: ... STAGE)
    constraints_stage_logic = [
        costsavings_constraint_sec_investment(),
        pricereduction_stage_calc(),
        BD_limitation_constraint_sec(),
        relation_pnew_to_pprior_constraint_sec(),
        q_perstep_constraint_sec(),
    ]

    # 2. Linearization Constraints (Index: ... STAGE, n)
    constraints_stage_linearization = [
        upper_bound_z_constraint_sec(),
        upper_bound_z_q1_eq_sec(),
        lower_bound_z_eq_sec(),
        non_negativity_z_eq_sec(),
    ]

    print(f"DEBUG: Registering Learning Rate Constraints with Stages...")
    print(f"DEBUG: m.stf = {list(m.stf)}")
    # print(f"DEBUG: m.stages = {list(m.stages)}") # Uncomment if you want to verify stages

    # Apply Logic Constraints
    for i, constraint in enumerate(constraints_stage_logic):
        constraint_name = f"constraint_lr_logic_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf, m.location, m.tech, m.stages,  # <--- Added Stage
                rule=lambda m, stf, loc, tech, stage: constraint.apply_rule(m, stf, loc, tech, stage),
            ),
        )

    # Apply Linearization Constraints
    for i, constraint in enumerate(constraints_stage_linearization):
        constraint_name = f"constraint_lr_lin_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf, m.location, m.tech, m.stages, m.nsteps_sec,  # <--- Added Stage
                rule=lambda m, stf, loc, tech, stage, n: constraint.apply_rule(m, stf, loc, tech, stage, n),
            ),
        )

    print("Stage-Dependent Learning Rate constraints applied successfully.")

    #m.pricereduction_sec_recycling = pyomo.Expression(
    #    m.stf,
    #    m.location,
    #    m.tech,
    #    rule=recycling_reduction_rule,
    #    doc="Recycling price reduction using linearized auxiliary variable",
    #)
