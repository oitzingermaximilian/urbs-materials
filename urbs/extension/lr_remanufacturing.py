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


class costsavings_constraint_sec_investment(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        investment_reduction_value = sum(
            m.P_sec_investment[location, tech, n] * m.BD_sec[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        expr = m.pricereduction_sec_investment[stf, location, tech] == investment_reduction_value

        # Improved debug formatting - separate lines for better visibility
        if DEBUG:
            print("=" * 60)
            print(f"[INVESTMENT COSTSAVINGS DEBUG] STF={stf}, Location={location}, Tech={tech}")
            print(f"  Investment reduction value: {investment_reduction_value}")
            print(
                f"  BD_sec values: {[m.BD_sec[stf, location, tech, n].value if hasattr(m.BD_sec[stf, location, tech, n], 'value') else 'unset' for n in m.nsteps_sec]}"
            )
            print(f"  P_sec_investment values: {[m.P_sec_investment[location, tech, n] for n in m.nsteps_sec]}")
            print(f"  Expression: {expr}")
            print("=" * 60)

        return expr


class costsavings_constraint_sec_recycling(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        recycling_reduction_value = sum(
            m.P_sec_recycling[location, tech, n] * m.BD_sec[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        expr = m.pricereduction_sec_recycling[stf, location, tech] == recycling_reduction_value

        # Improved debug formatting - separate lines for better visibility
        if DEBUG:
            print("=" * 60)
            print(f"[RECYCLING COSTSAVINGS DEBUG] STF={stf}, Location={location}, Tech={tech}")
            print(f"  Recycling reduction value: {recycling_reduction_value}")
            print(
                f"  BD_sec values: {[m.BD_sec[stf, location, tech, n].value if hasattr(m.BD_sec[stf, location, tech, n], 'value') else 'unset' for n in m.nsteps_sec]}"
            )
            print(f"  P_sec_recycling values: {[m.P_sec_recycling[location, tech, n] for n in m.nsteps_sec]}")
            print(f"  Expression: {expr}")
            print("=" * 60)

        return expr


class BD_limitation_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        bd_sum_value_sec = sum(m.BD_sec[stf, location, tech, n] for n in m.nsteps_sec)
        expr_ok = bd_sum_value_sec <= 1
        debug_print(
            f"[BD_limitation] STF={stf}, loc={location}, tech={tech}  ➞ "
            f"bd_sum_value_sec={bd_sum_value_sec} <= 1? {expr_ok}"
        )
        return expr_ok


class relation_pnew_to_pprior_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if stf == 2024:
            debug_print(f"[relation_pnew] STF={stf} (2024) ➞ SKIP")
            return pyomo.Constraint.Skip

        # Use investment price reduction as representative since both correlate perfectly
        if stf == value(m.y0):
            lhs = m.pricereduction_sec_investment[stf, location, tech]
            rhs = m.pricereduction_sec_init[location, tech]  # Back to original parameter name
            expr = lhs >= rhs
            debug_print(
                f"[relation_pnew-init] STF={stf} == y0 ➞ {lhs} >= {rhs} ? {expr}"
            )
        else:
            lhs = m.pricereduction_sec_investment[stf, location, tech]
            rhs = m.pricereduction_sec_investment[stf - 1, location, tech]
            expr = lhs >= rhs
            debug_print(
                f"[relation_pnew-recursive] STF={stf} ➞ {lhs} >= {rhs} ? {expr}"
            )
        return expr


class q_perstep_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        """
        Ensures cumulative capacity (carryover + yearly extensions from y0 to y)
        meets step requirements in year y.
        """
        y0 = min(m.stf)  # First model year

        # LHS = Carryover (only added once) + sum of extensions from y0 to stf

        lhs = m.total_secondary_cap_inital[location, tech] + sum(
            m.capacity_ext_eusecondary[year, location, tech]
            for year in m.stf
            if y0 <= year <= stf
        )

        # RHS = Sum of required steps for current year
        rhs = sum(
            m.BD_sec[stf, location, tech, n] * m.capacityperstep_sec[location, tech, n]
            for n in m.nsteps_sec
        )

        # Debug output
        expr = lhs >= rhs
        debug_print(
            f"[q_perstep] STF={stf}, loc={location}, tech={tech}  ➞\n"
            f"    LHS={lhs}\n"
            f"    RHS={rhs}, expr: {expr}"
        )

        return expr


class auxiliary_variable_calculation(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        """
        Defines the auxiliary variable as equal to BD_sec * capacity_ext_eusecondary.
        This constraint establishes the relationship between the auxiliary variable
        and the bilinear product it represents.
        """
        expr = (
            m.auxiliary_product_BD_q[stf, location, tech, nsteps_sec]
            == m.BD_sec[stf, location, tech, nsteps_sec] * m.capacity_ext_eusecondary[stf, location, tech]
        )
        debug_print(
            f"[auxiliary_variable] STF={stf}, step={nsteps_sec}  ➞ "
            f"aux_BD_q == BD_sec * capacity_ext"
        )
        return expr


class upper_bound_z_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        """
        Uses auxiliary variable instead of bilinear product BD_sec * capacity_ext_eusecondary
        """
        lhs_value = m.auxiliary_product_BD_q[stf, location, tech, nsteps_sec]
        rhs_value = m.gamma_sec * m.BD_sec[stf, location, tech, nsteps_sec]

        expr = lhs_value <= rhs_value
        debug_print(
            f"[upper_bound_z] STF={stf}, step={nsteps_sec}  ➞ "
            f"LHS={lhs_value}, RHS={rhs_value}, expr: {expr}"
        )
        return expr


class upper_bound_z_q1_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        """
        Uses auxiliary variable instead of bilinear product BD_sec * capacity_ext_eusecondary
        """
        lhs_value = m.auxiliary_product_BD_q[stf, location, tech, nsteps_sec]
        rhs_value = m.capacity_ext_eusecondary[stf, location, tech]

        expr = lhs_value <= rhs_value
        debug_print(
            f"[upper_bound_z_q1] STF={stf}, step={nsteps_sec}  ➞ "
            f"LHS={lhs_value}, RHS={rhs_value}, expr: {expr}"
        )
        return expr


class lower_bound_z_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        """
        Uses auxiliary variable instead of bilinear product BD_sec * capacity_ext_eusecondary
        """
        lhs_value = m.auxiliary_product_BD_q[stf, location, tech, nsteps_sec]
        rhs_value = (
            m.capacity_ext_eusecondary[stf, location, tech]
            - (1 - m.BD_sec[stf, location, tech, nsteps_sec]) * m.gamma_sec
        )

        expr = lhs_value >= rhs_value
        debug_print(
            f"[lower_bound_z] STF={stf}, step={nsteps_sec}  ➞ "
            f"LHS={lhs_value}, RHS={rhs_value}, expr: {expr}"
        )
        return expr


class non_negativity_z_eq_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        """
        Uses auxiliary variable instead of bilinear product BD_sec * capacity_ext_eusecondary
        """
        lhs_value = m.auxiliary_product_BD_q[stf, location, tech, nsteps_sec]

        expr = lhs_value >= 0
        debug_print(
            f"[non_negativity] STF={stf}, step={nsteps_sec}  ➞ "
            f"LHS={lhs_value}, expr: {expr}"
        )
        return expr


def apply_combined_lr_constraints(m):
    constraints_rm1 = [
        costsavings_constraint_sec_investment(),
        costsavings_constraint_sec_recycling(),
        BD_limitation_constraint_sec(),
        relation_pnew_to_pprior_constraint_sec(),
        q_perstep_constraint_sec(),
    ]

    constraints_rm2 = [
        upper_bound_z_constraint_sec(),
        upper_bound_z_q1_eq_sec(),
        lower_bound_z_eq_sec(),
        non_negativity_z_eq_sec(),
    ]

    # Add auxiliary variable constraint
    constraints_auxiliary = [
        auxiliary_variable_calculation(),
    ]

    # Debug: Print the sets being used
    print(f"DEBUG: m.stf = {list(m.stf)}")
    print(f"DEBUG: m.location = {list(m.location)}")
    print(f"DEBUG: m.tech = {list(m.tech)}")
    print(f"DEBUG: m.nsteps_sec = {list(m.nsteps_sec)}")

    for i, constraint in enumerate(constraints_rm1):
        constraint_name = f"constraint_rm1_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf,
                m.location,
                m.tech,
                rule=lambda m, stf, loc, tech, constraint=constraint: constraint.apply_rule(m, stf, loc, tech),
            ),
        )

    for i, constraint in enumerate(constraints_rm2):
        constraint_name = f"constraint_rm2_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf,
                m.location,
                m.tech,
                m.nsteps_sec,
                rule=lambda m, stf, loc, tech, nsteps_sec, constraint=constraint: constraint.apply_rule(
                    m, stf, loc, tech, nsteps_sec
                ),
            ),
        )

    # Add auxiliary variable constraints with proper lambda closure
    for i, constraint in enumerate(constraints_auxiliary):
        constraint_name = f"constraint_auxiliary_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf,
                m.location,
                m.tech,
                m.nsteps_sec,
                rule=lambda m, stf, loc, tech, nsteps_sec, constraint=constraint: constraint.apply_rule(
                    m, stf, loc, tech, nsteps_sec
                ),
            ),
        )
