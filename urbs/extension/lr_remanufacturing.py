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
        # ✅ CORRECTED: Use auxiliary variable instead of bilinear product
        # Original bilinear: P_sec_investment[n] * BD_sec[n] * capacity_ext_eusecondary
        # Linearized: P_sec_investment[n] * auxiliary_product_BD_q[n]

        investment_reduction_value = sum(
            m.P_sec_investment[location, tech, n]
            * m.auxiliary_product_BD_q[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        expr = (
            m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech]
            == investment_reduction_value
        )

        # Improved debug formatting - separate lines for better visibility
        if DEBUG:
            print("=" * 60)
            print(
                f"[INVESTMENT COSTSAVINGS DEBUG] STF={stf}, Location={location}, Tech={tech}"
            )
            print(f"  Investment reduction value: {investment_reduction_value}")
            bd_values = [
                m.BD_sec[stf, location, tech, n].value
                if hasattr(m.BD_sec[stf, location, tech, n], "value")
                else "unset"
                for n in m.nsteps_sec
            ]
            print(f"  BD_sec values: {bd_values}")
            p_values = [m.P_sec_investment[location, tech, n] for n in m.nsteps_sec]
            print(f"  P_sec_investment values: {p_values}")
            # Simplified active step contributions without nested quotes
            contributions = []
            for n in m.nsteps_sec:
                bd_val = (
                    m.BD_sec[stf, location, tech, n].value
                    if hasattr(m.BD_sec[stf, location, tech, n], "value")
                    else "unset"
                )
                contributions.append(
                    (n, m.P_sec_investment[location, tech, n], f"BD_sec={bd_val}")
                )
            print(f"  Active step contributions: {contributions}")
            print(f"  Expression: {expr}")
            print("=" * 60)

        return expr


class pricereduction_stage_calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        investement_reduction_stage_value = sum(
            m.P_sec_investment[location, tech, n] * m.BD_sec[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        expr = (
            m.pricereduction_sec_investment[stf, location, tech]
            == investement_reduction_stage_value
        )
        return expr  # ✅ FIXED: Added missing return statement


class BD_limitation_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        bd_sum_value_sec = sum(m.BD_sec[stf, location, tech, n] for n in m.nsteps_sec)
        expr_ok = bd_sum_value_sec == 1  # Force exactly one selection instead of <= 1

        # Enhanced debugging
        if DEBUG:
            print("=" * 80)
            print(f"[BD_limitation DETAILED] STF={stf}, loc={location}, tech={tech}")
            print(f"  Number of steps (nsteps_sec): {len(list(m.nsteps_sec))}")
            print(f"  Steps available: {list(m.nsteps_sec)}")
            print(f"  Sum constraint: {bd_sum_value_sec} == 1")

            # Check if this constraint might cause infeasibility
            try:
                # Check P_sec values to see if there are incentives
                p_inv_values = [
                    m.P_sec_investment[location, tech, n] for n in m.nsteps_sec
                ]
                p_rec_values = [
                    m.P_sec_recycling[location, tech, n] for n in m.nsteps_sec
                ]
                print(f"  P_sec_investment values: {p_inv_values}")
                print(f"  P_sec_recycling values: {p_rec_values}")

                # Check capacity requirements
                cap_values = [
                    m.capacityperstep_sec[location, tech, n] for n in m.nsteps_sec
                ]
                print(f"  Capacity per step values: {cap_values}")

            except Exception as e:
                print(f"  Warning: Could not access parameter values: {e}")
            print("=" * 80)

        debug_print(
            f"[BD_limitation] STF={stf}, loc={location}, tech={tech}  ➞ "
            f"bd_sum_value_sec={bd_sum_value_sec} == 1? {expr_ok}"
        )
        return expr_ok


class relation_pnew_to_pprior_constraint_sec(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if stf == 2024:
            # REVERTED: Skip 2024 as originally intended
            # The BD numerical tolerance issue should be solved differently
            debug_print(f"[relation_pnew] STF={stf} (2024) ➞ SKIP (no prior year)")
            return pyomo.Constraint.Skip

        # Separate if-else block for all other years (not 2024)
        if stf == value(m.y0):
            lhs = m.pricereduction_sec_investment[stf, location, tech]
            rhs = m.pricereduction_sec_init[location, tech]
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

class upper_bound_z_constraint_primary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        lhs_value = m.auxiliary_product_BD_q_primary[stf, location, tech, nsteps_sec]
        rhs_value = m.gamma_sec * m.BD_sec[stf, location, tech, nsteps_sec]
        return lhs_value <= rhs_value


class upper_bound_z_q1_eq_primary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        lhs_value = m.auxiliary_product_BD_q_primary[stf, location, tech, nsteps_sec]
        rhs_value = m.capacity_ext_euprimary[stf, location, tech]
        return lhs_value <= rhs_value


class lower_bound_z_eq_primary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        lhs_value = m.auxiliary_product_BD_q_primary[stf, location, tech, nsteps_sec]
        rhs_value = m.capacity_ext_euprimary[stf, location, tech] - (
            1 - m.BD_sec[stf, location, tech, nsteps_sec]
        ) * m.gamma_sec
        return lhs_value >= rhs_value


class non_negativity_z_eq_primary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, nsteps_sec):
        lhs_value = m.auxiliary_product_BD_q_primary[stf, location, tech, nsteps_sec]
        return lhs_value >= 0


def apply_combined_lr_constraints(m):
    constraints_rm1 = [
        costsavings_constraint_sec_investment(),
        pricereduction_stage_calc(),  # ✅ Added back the fixed constraint
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

    primary_constraints = [
        upper_bound_z_constraint_primary(),
        upper_bound_z_q1_eq_primary(),
        lower_bound_z_eq_primary(),
        non_negativity_z_eq_primary(),
    ]

    # ❌ REMOVED: auxiliary_variable_calculation() - this makes the model bilinear again!
    # The Big-M constraints (constraints_rm2) already fully define the auxiliary variable

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
                rule=lambda m,
                stf,
                loc,
                tech,
                constraint=constraint: constraint.apply_rule(m, stf, loc, tech),
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
                rule=lambda m,
                stf,
                loc,
                tech,
                nsteps_sec,
                constraint=constraint: constraint.apply_rule(
                    m, stf, loc, tech, nsteps_sec
                ),
            ),
        )

    for i, constraint in enumerate(primary_constraints):
        constraint_name = f"constraint_primary_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf, m.location, m.tech, m.nsteps_sec,
                rule=lambda m, stf, loc, tech, n, constraint=constraint: constraint.apply_rule(m, stf, loc, tech, n)
            )
        )

    # ✅ FIXED: Replace the recycling expression to use auxiliary variable #TODO reenable pricereduction on Scrap if needed
    # def recycling_reduction_rule(m, stf, location, tech):
    #    # Use auxiliary variable instead of trilinear product
    #    recycling_reduction_value = sum(
    #        m.P_sec_recycling[location, tech, n] * m.auxiliary_product_BD_q[stf, location, tech, n]
    #        for n in m.nsteps_sec
    #    )
    #    if DEBUG:
    #        print("=" * 60)
    #        print(f"[RECYCLING EXPRESSION DEBUG] STF={stf}, Location={location}, Tech={tech}")
    #        print(f"  Recycling reduction value (LINEARIZED): {recycling_reduction_value}")
    #        print("=" * 60)
    #    return recycling_reduction_value

    # Override the recycling price reduction variable with a linear expression
    # m.pricereduction_sec_recycling = pyomo.Expression(
    #    m.stf,
    #    m.location,
    #    m.tech,
    #   rule=recycling_reduction_rule,
    #    doc="Recycling price reduction using linearized auxiliary variable"
    # )
