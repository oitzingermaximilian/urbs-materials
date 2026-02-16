from abc import ABC, abstractmethod
import pyomo.core as pyomo
from pyomo.environ import value


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, stf, location, tech):
        pass


DEBUG = False  # Set True to turn on all debug logging


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class decommissioned_capacity_rule(AbstractConstraint):
    def __init__(self, use_lifetime=True):
        """
        use_lifetime: If True, apply the lifetime-based decommissioning (default behavior).
                      If False, ignore lifetimes and use exogenous + 15% for all years.
        """
        self.use_lifetime = use_lifetime

    def apply_rule(self, m, stf, location, tech):
        # CON: Decommissioned Capacity | Calculates capacity reaching end of life based on lifetime or exogenous factors
        # --- determine exogenous ---
        if tech == "solarPV":
            _exogenous = 7.5 #* 1000
        elif (
            tech == "windon"
        ):  # file:///C:/Users/maxoi/OneDrive/Desktop/urbs_crm_data/WindEurope-European-Stats-2024.pdf page 17: 1.3 GW dec
            _exogenous = 1 #* 1000
        elif tech == "windoff":
            _exogenous = 0.3 #* 1000
        else:
            _exogenous = 2 #* 1000

        # --- apply rule ---
        if self.use_lifetime:
            # lifetime logic
            if stf >= value(m.y0) + m.l[location, tech]:
                expr = (
                    m.capacity_dec[stf, location, tech]
                    == m.capacity_ext_new[stf - m.l[location, tech], location, tech]
                )
                debug_print(
                    f"[decommissioned, lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                    f"DEC == EXT_NEW[{stf - m.l[location, tech]}]\n    expr: {expr}"
                )
            else:
                expr = (
                    m.capacity_dec[stf, location, tech]
                    == _exogenous + 0.15 * m.capacity_ext_new[stf, location, tech]
                )
                debug_print(
                    f"[decommissioned, lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                    f"DEC == {_exogenous} + 0.15·EXT_NEW[{stf}]\n    expr: {expr}"
                )
        else:
            # lifetime disabled → always use exogenous + 15%
            expr = (
                m.capacity_dec[stf, location, tech]
                == _exogenous + 0.15 *m.capacity_ext_new[stf, location, tech]
            )
            debug_print(
                f"[decommissioned, no lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                f"DEC == {_exogenous} + 0.15·EXT_NEW[{stf}]\n    expr: {expr}"
            )

        return expr


class capacity_scrap_dec_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Scrap from Decommissioning | Calculates scrap amount generated from decommissioned capacity
        expr = (
            m.capacity_scrap_dec[stf, location, tech]
            == m.f_scrap[location, tech] * m.capacity_dec[stf, location, tech]
        )
        debug_print(
            f"[scrap_dec] STF={stf}, loc={location}, tech={tech}  ➞ "
            f"SCRAP_DEC == f_scrap·DEC\n    expr: {expr}"
        )
        return expr


class capacity_scrap_rec_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Scrap for Recycling | Calculates scrap input required for secondary production
        lhs = (
            m.f_scrap[location, tech]
            / m.f_recycling[
                location, tech
            ]  # switchd f_mining to f_scrap cause same values and f_mining not working
        ) * m.capacity_ext_eusecondary[stf, location, tech]

        rhs = m.capacity_scrap_rec[stf, location, tech]
        debug_print(
            f"[scrap_rec] STF={stf}, loc={location}, tech={tech}  ➞ SCRAP_REC ==  {lhs}"
        )
        return lhs == rhs


class capacity_scrap_total_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Total Scrap Accumulation | Tracks cumulative scrap availability
        if stf == 2024:
            expr = (
                m.capacity_scrap_total[stf, location, tech]
                == m.capacity_scrap_dec[stf, location, tech]
                - m.capacity_scrap_rec[stf, location, tech]
            )
            debug_print(f"[scrap_total start] STF=2024 ➞ expr: {expr}")
        else:
            expr = (
                m.capacity_scrap_total[stf, location, tech]
                == m.capacity_scrap_total[stf - 1, location, tech]
                + m.capacity_scrap_dec[stf, location, tech]
                - m.capacity_scrap_rec[stf, location, tech]
            )
            debug_print(f"[scrap_total] STF={stf} ➞ expr: {expr}")
        return expr


class cost_scrap_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Scrap Processing Cost | Calculates cost of recycling minus learning benefits
        # 1. Base Cost (Recycling Fee * Capacity)
        base_cost = m.f_scrap_rec[stf, location, tech] * m.capacity_scrap_rec[stf, location, tech]

        # 2. Subtract Savings (Only if Tech is in the Scrap Learning Subset)
        savings = 0

        # Check if the subset exists AND if the current 'tech' is inside it
        if hasattr(m, 'tech_scrap_onetech') and tech in m.tech_scrap_onetech:
            # We can safely access the variable because we know 'tech' is valid
            savings = m.PRICEREDUCTION_SCRAP_ONETECH_TOTAL[stf, location, tech]

        # 3. Final Equation
        return m.cost_scrap[stf, location, tech] == base_cost - savings


class scrap_total_decrease_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Scrap Reduction Target | Forces reduction of scrap pile over time
        if tech == "solarPV":
            if stf <= 2030:
                return pyomo.Constraint.Skip
            elif stf == value(m.y0):
                return (
                    m.capacity_scrap_total[stf, location, tech]
                    <= m.scrap_total[location, tech]
                )
            else:
                return (
                    m.capacity_scrap_total[stf, location, tech]
                    <= m.capacity_scrap_total[stf - 1, location, tech]
                )
        else:
            return pyomo.Constraint.Skip


class scrap_recycling_increase_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # CON: Recycling Growth Limit | Limits annual increase in recycling capacity
        if stf == value(m.y0):
            return pyomo.Constraint.Skip

        # Define a "Kickstart" allowance (e.g., 50 MW or 100 MW)
        # This allows the industry to go from 0 to 50 MW in one year.
        # After that, the % growth takes over.
        min_annual_add = 100  # Adjust unit to match your model (e.g. MW or tons)

        lhs = (
                m.capacity_scrap_rec[stf, location, tech]
                - m.capacity_scrap_rec[stf - 1, location, tech]
        )

        # RHS = Growth Limit + Kickstarter
        rhs = (
                m.f_increase[location, tech] * m.capacity_scrap_rec[stf - 1, location, tech]
                + min_annual_add
        )

        return lhs <= rhs


def apply_scrap_constraints(m):
    constraints = [
        decommissioned_capacity_rule(),
        capacity_scrap_dec_rule(),
        capacity_scrap_total_rule(),
        cost_scrap_rule(),
        # Removed obsolete linearization constraints - now using direct absolute values
        # scrap_total_decrease_rule(),
        # scrap_recycling_increase_rule(),
    ]

    m.decommissioned_capacity_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[0].apply_rule(m, stf, loc, tech),
    )
    m.capacity_scrap_dec_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[1].apply_rule(m, stf, loc, tech),
    )
    m.capacity_scrap_total_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[2].apply_rule(m, stf, loc, tech),
    )
    m.cost_scrap_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[3].apply_rule(m, stf, loc, tech),
    )