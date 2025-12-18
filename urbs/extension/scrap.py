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
        # --- determine exogenous ---
        if tech == "solarPV":
            _exogenous = 7.5 * 1000
        elif (
            tech == "windon"
        ):  # file:///C:/Users/maxoi/OneDrive/Desktop/urbs_crm_data/WindEurope-European-Stats-2024.pdf page 17: 1.3 GW dec
            _exogenous = 1 * 1000
        elif tech == "windoff":
            _exogenous = 0.3 * 1000
        else:
            _exogenous = 2 * 1000

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
                == _exogenous + 0.15 * m.capacity_ext_new[stf, location, tech]
            )
            debug_print(
                f"[decommissioned, no lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                f"DEC == {_exogenous} + 0.15·EXT_NEW[{stf}]\n    expr: {expr}"
            )

        return expr


class capacity_scrap_dec_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
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
        if stf == 2024:
            expr = (
                m.capacity_scrap_total[stf, location, tech]
                == m.capacity_scrap_dec[stf, location, tech]
                - m.capacity_scrap_rec[stf, location, tech]
            )
            debug_print(f"[scrap_total start] STF=2024 ➞ expr: {expr}")
        elif stf == value(m.y0):
            expr = (
                m.capacity_scrap_total[stf, location, tech]
                == m.scrap_total[location, tech]
                + m.capacity_scrap_dec[stf, location, tech]
                - m.capacity_scrap_rec[stf, location, tech]
            )
            debug_print(f"[scrap_total init] STF={stf} ➞ expr: {expr}")
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
        # ✅ PROPERLY LINEARIZED: Use base cost minus linearized reduction
        # Original would be: (f_scrap_rec - price_reduction_per_unit) * capacity_scrap_rec
        # But price_reduction_per_unit involves bilinear terms
        # So we use: f_scrap_rec * capacity_scrap_rec - pricereduction_sec_recycling
        # where pricereduction_sec_recycling = sum(P_sec_recycling[n] * auxiliary_product_BD_q[n])

        expr = (
            m.cost_scrap[stf, location, tech]
            == (
                m.f_scrap_rec[stf, location, tech]
                * m.capacity_scrap_rec[stf, location, tech]
            )
            #- m.pricereduction_sec_recycling[stf, location, tech]
        )

        debug_print(f"[cost_scrap] STF={stf} ➞ expr: {expr}")
        return expr


class scrap_total_decrease_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
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
        if stf == value(m.y0):
            debug_print(f"[scrap_increase] STF={stf} (start) ➞ SKIP")
            return pyomo.Constraint.Skip
        lhs = (
            m.capacity_scrap_rec[stf, location, tech]
            - m.capacity_scrap_rec[stf - 1, location, tech]
        )
        rhs = (
            m.f_increase[location, tech] * m.capacity_scrap_rec[stf - 1, location, tech]
        )
        expr = lhs <= rhs
        debug_print(
            f"[scrap_increase] STF={stf} ➞ LHS: {lhs}, RHS: {rhs}, expr: {expr}"
        )
        return expr


def apply_scrap_constraints(m):
    constraints = [
        decommissioned_capacity_rule(),
        capacity_scrap_dec_rule(),
        capacity_scrap_rec_rule(),
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
    m.capacity_scrap_rec_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[2].apply_rule(m, stf, loc, tech),
    )
    m.capacity_scrap_total_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[3].apply_rule(m, stf, loc, tech),
    )
    m.cost_scrap_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: constraints[4].apply_rule(m, stf, loc, tech),
    )
