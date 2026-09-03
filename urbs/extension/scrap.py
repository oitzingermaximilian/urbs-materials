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
                    == m.decommissioned_cap[stf, location, tech]
                )
                debug_print(
                    f"[decommissioned, lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                    f"DEC == {m.decommissioned_cap[stf, location, tech]} (exogenous)\n    expr: {expr}"
                )
        else:
            # lifetime disabled → always use exogenous
            expr = (
                m.capacity_dec[stf, location, tech]
                == m.decommissioned_cap[stf, location, tech]
            )
            debug_print(
                f"[decommissioned, no lifetime] STF={stf}, loc={location}, tech={tech} ➞ "
                f"DEC == {m.decommissioned_cap[stf, location, tech]} (exogenous)\n    expr: {expr}"
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


class capacity_scrap_rec_rule(AbstractConstraint):  # INACTIVE
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
        # 1. Annuitization factors for CAPEX
        j, i, n = 0.03, 0.071, 25
        stf_min, stf_end = min(m.stf), max(m.stf)
        f_inv = (
            (1 + j) ** (1 - (stf - stf_min))
            * (i * (1 + i) ** n * ((1 + j) ** n - 1))
            / (j * (1 + j) ** n * ((1 + i) ** n - 1))
        )
        op_time = (stf + n) - stf_end - 1
        f_over = 0
        if op_time > 0:
            f_over = (
                (1 + j) ** (1 - (stf - stf_min))
                * (i * (1 + i) ** n * ((1 + j) ** op_time - 1))
                / (j * (1 + j) ** n * ((1 + i) ** n - 1))
            )

        # Calculate physical weight scaling factors for Magnet and Bulk
        magnet_mats = ["dysprosium", "neodymium", "praseodymium", "terbium"]
        magnet_intensity = sum(
            m.scrap_content[tech, mat]
            for mat in magnet_mats
            if (tech, mat) in m.scrap_content
        )
        # Assuming REE is ~32% of magnet weight, scale up to get full magnet physical weight
        magnet_weight = magnet_intensity / 0.32 if magnet_intensity > 0 else 0

        bulk_weight = sum(
            m.scrap_content[tech, mat]
            for mat in m.materials
            if mat not in magnet_mats and (tech, mat) in m.scrap_content
        )

        # 2. Base Cost = Variable OPEX + CAPEX + Fixed OPEX
        if tech in ["windon", "windoff"]:
            # Magnet Route: Pays Magnet costs on magnet fraction + Bulk costs on bulk fraction
            magnet_route_opex = (
                m.f_scrap_rec_magnet[stf, location, tech] * magnet_weight
            ) + (m.f_scrap_rec_bulk[stf, location, tech] * bulk_weight)
            bulk_route_opex = m.f_scrap_rec_bulk[stf, location, tech] * bulk_weight

            opex_cost = (
                magnet_route_opex * m.capacity_scrap_magnet_route[stf, location, tech]
                + bulk_route_opex * m.capacity_scrap_bulk_route[stf, location, tech]
            )

            magnet_route_capex = (
                m.f_scrap_capex_magnet[stf, location, tech] * magnet_weight
            ) + (m.f_scrap_capex_bulk[stf, location, tech] * bulk_weight)
            bulk_route_capex = m.f_scrap_capex_bulk[stf, location, tech] * bulk_weight

            capex_cost = (
                m.scraphandling_cap_new_magnet[stf, location, tech]
                * magnet_route_capex
                * (f_inv - f_over)
            ) + (
                m.scraphandling_cap_new_bulk[stf, location, tech]
                * bulk_route_capex
                * (f_inv - f_over)
            )

            magnet_route_fom = (
                m.f_scrap_fom_magnet[stf, location, tech] * magnet_weight
            ) + (m.f_scrap_fom_bulk[stf, location, tech] * bulk_weight)
            bulk_route_fom = m.f_scrap_fom_bulk[stf, location, tech] * bulk_weight

            fom_cost = (
                magnet_route_fom
                * m.capacity_scrap_handling_magnet_total[stf, location, tech]
                + bulk_route_fom
                * m.capacity_scrap_handling_bulk_total[stf, location, tech]
            )

            base_cost = opex_cost + capex_cost + fom_cost

            # Deduct the linear capacity-based economies of scale savings for magnet
            savings = 0
            savings_capex = 0
            savings_fom = 0
            if hasattr(m, "PRICEREDUCTION_SCRAP_WINDON_CAP_BASED"):
                if tech == "windon":
                    savings = (
                        m.PRICEREDUCTION_SCRAP_WINDON_CAP_BASED[stf, location]
                        * magnet_weight
                    )
                    savings_capex = (
                        m.PRICEREDUCTION_SCRAP_WINDON_CAPEX_CAP_BASED[stf, location]
                        * magnet_weight
                        * (f_inv - f_over)
                    )
                    savings_fom = (
                        m.PRICEREDUCTION_SCRAP_WINDON_FOM_CAP_BASED[stf, location]
                        * magnet_weight
                    )
                elif tech == "windoff":
                    savings = (
                        m.PRICEREDUCTION_SCRAP_WINDOFF_CAP_BASED[stf, location]
                        * magnet_weight
                    )
                    savings_capex = (
                        m.PRICEREDUCTION_SCRAP_WINDOFF_CAPEX_CAP_BASED[stf, location]
                        * magnet_weight
                        * (f_inv - f_over)
                    )
                    savings_fom = (
                        m.PRICEREDUCTION_SCRAP_WINDOFF_FOM_CAP_BASED[stf, location]
                        * magnet_weight
                    )

        else:
            total_weight = magnet_weight + bulk_weight
            # Fallback to 1.0 if no intensities are defined so costs don't vanish
            total_weight = total_weight if total_weight > 0 else 1.0

            opex_cost = (
                m.f_scrap_rec[stf, location, tech]
                * total_weight
                * m.capacity_scrap_rec[stf, location, tech]
            )
            capex_cost = (
                m.scraphandling_cap_new[stf, location, tech]
                * m.f_scrap_capex[stf, location, tech]
                * total_weight
                * (f_inv - f_over)
            )
            fom_cost = (
                m.f_scrap_fom[stf, location, tech]
                * total_weight
                * m.capacity_scrap_handling_total[stf, location, tech]
            )

            base_cost = opex_cost + capex_cost + fom_cost

            # Deduct the linear capacity-based economies of scale savings for solar
            savings = 0
            savings_capex = 0
            savings_fom = 0
            if tech == "solarPV" and hasattr(m, "PRICEREDUCTION_SCRAP_SOLAR_CAP_BASED"):
                savings = (
                    m.PRICEREDUCTION_SCRAP_SOLAR_CAP_BASED[stf, location] * total_weight
                )
                savings_capex = (
                    m.PRICEREDUCTION_SCRAP_SOLAR_CAPEX_CAP_BASED[stf, location]
                    * total_weight
                    * (f_inv - f_over)
                )
                savings_fom = (
                    m.PRICEREDUCTION_SCRAP_SOLAR_FOM_CAP_BASED[stf, location]
                    * total_weight
                )

        # 3. Final Equation
        return (
            m.cost_scrap[stf, location, tech]
            == base_cost - savings - savings_capex - savings_fom
        )


class capacity_scrap_routing_magnet_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech not in ["windon", "windoff"]:
            return m.capacity_scrap_magnet_route[stf, location, tech] == 0
        return pyomo.Constraint.Skip


class capacity_scrap_routing_bulk_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech not in ["windon", "windoff"]:
            return m.capacity_scrap_bulk_route[stf, location, tech] == 0
        return pyomo.Constraint.Skip


class capacity_scrap_routing_sum_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            return (
                m.capacity_scrap_rec[stf, location, tech]
                == m.capacity_scrap_magnet_route[stf, location, tech]
                + m.capacity_scrap_bulk_route[stf, location, tech]
            )
        else:
            return pyomo.Constraint.Skip


# --- Scrap Handling Capacity Rules (Moved from materials.py) ---


class ScrapHandlingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        return (
            m.capacity_scrap_handling_total[stf, location, tech]
            >= m.capacity_scrap_rec[stf, location, tech]
        )


class ScrapHandlingOutputDecreaseLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            return pyomo.Constraint.Skip

        if stf == min(m.stf):
            return pyomo.Constraint.Skip
        else:
            lhs = (
                m.capacity_scrap_rec[stf - 1, location, tech]
                - m.capacity_scrap_rec[stf, location, tech]
            )
            rhs = 100.0 + 0.50 * m.capacity_scrap_rec[stf - 1, location, tech]
            return lhs <= rhs


class ScrapHandlingCapacitiesSizeRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lhs = m.capacity_scrap_handling_total[stf, location, tech]
        rhs = m.capacity_scrap_handling_init[location, tech] + sum(
            m.scraphandling_cap_new[y, location, tech] for y in m.stf if y <= stf
        )
        return lhs == rhs


class ScrapHandlingOutputGrowthLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            return pyomo.Constraint.Skip

        # SCALING NOTE: Values in kton (k-Universe)
        if stf == min(m.stf):
            return m.capacity_scrap_rec[stf, location, tech] <= 200.0
        else:
            lhs = (
                m.capacity_scrap_rec[stf, location, tech]
                - m.capacity_scrap_rec[stf - 1, location, tech]
            )
            rhs = 200.0 + 0.50 * m.capacity_scrap_rec[stf - 1, location, tech]
            return lhs <= rhs


class ScrapHandlingCapacitiesOutputLimitMagnetRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            return (
                m.capacity_scrap_handling_magnet_total[stf, location, tech]
                >= m.capacity_scrap_magnet_route[stf, location, tech]
            )
        else:
            return m.capacity_scrap_handling_magnet_total[stf, location, tech] == 0


class ScrapHandlingCapacitiesOutputLimitBulkRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            return (
                m.capacity_scrap_handling_bulk_total[stf, location, tech]
                >= m.capacity_scrap_bulk_route[stf, location, tech]
            )
        else:
            return m.capacity_scrap_handling_bulk_total[stf, location, tech] == 0


class ScrapHandlingCapacitiesSizeMagnetRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            lhs = m.capacity_scrap_handling_magnet_total[stf, location, tech]
            rhs = sum(
                m.scraphandling_cap_new_magnet[y, location, tech]
                for y in m.stf
                if y <= stf
            )
            return lhs == rhs
        else:
            return m.scraphandling_cap_new_magnet[stf, location, tech] == 0


class ScrapHandlingCapacitiesSizeBulkRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            lhs = m.capacity_scrap_handling_bulk_total[stf, location, tech]
            rhs = sum(
                m.scraphandling_cap_new_bulk[y, location, tech]
                for y in m.stf
                if y <= stf
            )
            return lhs == rhs
        else:
            return m.scraphandling_cap_new_bulk[stf, location, tech] == 0


class ScrapHandlingOutputGrowthLimitMagnetRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            if stf == min(m.stf):
                return m.capacity_scrap_magnet_route[stf, location, tech] <= 250.0
            else:
                lhs = (
                    m.capacity_scrap_magnet_route[stf, location, tech]
                    - m.capacity_scrap_magnet_route[stf - 1, location, tech]
                )
                rhs = (
                    200.0
                    + 0.50 * m.capacity_scrap_magnet_route[stf - 1, location, tech]
                )
                return lhs <= rhs
        else:
            return pyomo.Constraint.Skip


class ScrapHandlingOutputGrowthLimitBulkRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            if stf == min(m.stf):
                return m.capacity_scrap_bulk_route[stf, location, tech] <= 250.0
            else:
                lhs = (
                    m.capacity_scrap_bulk_route[stf, location, tech]
                    - m.capacity_scrap_bulk_route[stf - 1, location, tech]
                )
                rhs = (
                    200.0 + 0.50 * m.capacity_scrap_bulk_route[stf - 1, location, tech]
                )
                return lhs <= rhs
        else:
            return pyomo.Constraint.Skip


class ScrapHandlingOutputDecreaseLimitMagnetRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            if stf == min(m.stf):
                return pyomo.Constraint.Skip
            lhs = (
                m.capacity_scrap_magnet_route[stf - 1, location, tech]
                - m.capacity_scrap_magnet_route[stf, location, tech]
            )
            rhs = 100.0 + 0.50 * m.capacity_scrap_magnet_route[stf - 1, location, tech]
            return lhs <= rhs
        else:
            return pyomo.Constraint.Skip


class ScrapHandlingOutputDecreaseLimitBulkRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if tech in ["windon", "windoff"]:
            if stf == min(m.stf):
                return pyomo.Constraint.Skip
            lhs = (
                m.capacity_scrap_bulk_route[stf - 1, location, tech]
                - m.capacity_scrap_bulk_route[stf, location, tech]
            )
            rhs = 100.0 + 0.50 * m.capacity_scrap_bulk_route[stf - 1, location, tech]
            return lhs <= rhs
        else:
            return pyomo.Constraint.Skip


def apply_scrap_constraints(m):
    m.decommissioned_capacity_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: decommissioned_capacity_rule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.capacity_scrap_dec_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: capacity_scrap_dec_rule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.capacity_scrap_total_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: capacity_scrap_total_rule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.cost_scrap_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: cost_scrap_rule().apply_rule(m, stf, loc, tech),
    )
    m.capacity_scrap_routing_magnet_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: capacity_scrap_routing_magnet_rule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.capacity_scrap_routing_bulk_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: capacity_scrap_routing_bulk_rule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.capacity_scrap_routing_sum_rule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: capacity_scrap_routing_sum_rule().apply_rule(
            m, stf, loc, tech
        ),
    )

    # Facility constraints
    m.ScrapHandlingCapacitiesOutputLimitRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingCapacitiesOutputLimitRule().apply_rule(m, stf, loc, tech),
    )
    m.ScrapHandlingOutputDecreaseLimitRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingOutputDecreaseLimitRule().apply_rule(m, stf, loc, tech),
    )
    m.ScrapHandlingCapacitiesSizeRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: ScrapHandlingCapacitiesSizeRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingOutputGrowthLimitRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: ScrapHandlingOutputGrowthLimitRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingCapacitiesOutputLimitMagnetRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingCapacitiesOutputLimitMagnetRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingCapacitiesOutputLimitBulkRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingCapacitiesOutputLimitBulkRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingCapacitiesSizeMagnetRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingCapacitiesSizeMagnetRule().apply_rule(m, stf, loc, tech),
    )
    m.ScrapHandlingCapacitiesSizeBulkRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m, stf, loc, tech: ScrapHandlingCapacitiesSizeBulkRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingOutputGrowthLimitMagnetRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingOutputGrowthLimitMagnetRule().apply_rule(m, stf, loc, tech),
    )
    m.ScrapHandlingOutputGrowthLimitBulkRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingOutputGrowthLimitBulkRule().apply_rule(m, stf, loc, tech),
    )
    m.ScrapHandlingOutputDecreaseLimitMagnetRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingOutputDecreaseLimitMagnetRule().apply_rule(
            m, stf, loc, tech
        ),
    )
    m.ScrapHandlingOutputDecreaseLimitBulkRule = pyomo.Constraint(
        m.stf,
        m.location,
        m.tech,
        rule=lambda m,
        stf,
        loc,
        tech: ScrapHandlingOutputDecreaseLimitBulkRule().apply_rule(m, stf, loc, tech),
    )
