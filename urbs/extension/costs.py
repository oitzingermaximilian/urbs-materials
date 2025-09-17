from abc import ABC, abstractmethod
import pyomo.core as pyomo


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, stf, location, tech):
        pass


class DefCostsNew(AbstractConstraint):
    def apply_rule(self, m, cost_type_new):
        if cost_type_new == "Importcost":
            total_import_cost = sum(
                (
                    m.IMPORTCOST[stf, site, tech]
                    * (
                        m.capacity_ext_imported[stf, site, tech]
                        + m.capacity_ext_stock_imported[stf, site, tech]
                    )
                )
                + (
                    m.capacity_ext_stock_imported[stf, site, tech]
                    * m.logisticcost[site, tech]
                )
                + m.anti_dumping_measures[stf, site, tech]
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_import_cost
            return expr

        elif cost_type_new == "Storagecost":
            total_storage_cost = sum(
                m.STORAGECOST[site, tech] * m.capacity_ext_stock[stf, site, tech]
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_storage_cost
            return expr

        elif cost_type_new == "Eu Cost Primary":
            total_eu_cost_primary = sum(
                m.EU_primary_costs[stf, site, tech]
                * m.capacity_ext_euprimary[stf, site, tech]
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_eu_cost_primary
            return expr

        elif cost_type_new == "Eu Cost Secondary":
            # ✅ PROPERLY LINEARIZED: Use auxiliary variable to avoid bilinear terms
            # Original: (EU_secondary_costs - price_reduction_per_unit) * capacity
            # But price_reduction_per_unit = sum(P_sec * BD_sec) which is bilinear
            # So we use: EU_secondary_costs * capacity - pricereduction_sec_investment
            # where pricereduction_sec_investment = sum(P_sec * auxiliary_product_BD_q)
            total_eu_cost_secondary = sum(
                (
                    # Linear: base cost times capacity
                    m.EU_secondary_costs[stf, site, tech]
                    * m.capacity_ext_eusecondary[stf, site, tech]
                    + 1 * m.capacity_facility_eusecondary[stf, site, tech]
                    + m.cost_scrap[stf, site, tech]
                    # Subtract the linearized price reduction (total absolute reduction)
                    - m.PRICEREDUCTION_CAP_DEP_INV[stf, site, tech]
                )
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_eu_cost_secondary
            return expr

        elif cost_type_new == "O_and_M":
            total_o_and_m_cost = sum(
                (m.O_and_M_costs[stf, site, tech] * m.capacity_ext[stf, site, tech])
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_o_and_m_cost
            return expr
        else:
            raise NotImplementedError(f"Unknown cost type: {cost_type_new}")


class CalculateYearlyImportCost(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        import_cost_value = (
            m.IMPORTCOST[stf, location, tech]
            * (
                m.capacity_ext_imported[stf, location, tech]
                + m.capacity_ext_stock_imported[stf, location, tech]
            )
            + (
                m.capacity_ext_stock_imported[stf, location, tech]
                * m.logisticcost[location, tech]
            )
            + m.anti_dumping_measures[stf, location, tech]
        )
        expr = m.costs_ext_import[stf, location, tech] == import_cost_value
        return expr


class CalculateYearlyStorageCost(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        storage_cost_value = (
            m.STORAGECOST[location, tech] * m.capacity_ext_stock[stf, location, tech]
        )
        expr = m.costs_ext_storage[stf, location, tech] == storage_cost_value
        return expr


class CalculateYearlyEUPrimary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        eu_primary_cost_value = (
            m.EU_primary_costs[stf, location, tech]
            * m.capacity_ext_euprimary[stf, location, tech]
        )
        expr = m.costs_EU_primary[stf, location, tech] == eu_primary_cost_value
        return expr


class CalculateYearlyEUSecondary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # ✅ PROPERLY LINEARIZED: Use the linearized price reduction variable
        # Original bilinear: (EU_secondary_costs - sum(P_sec * BD_sec)) * capacity
        # Linearized: EU_secondary_costs * capacity - pricereduction_sec_investment
        eu_secondary_cost_value = (
            # Linear: base cost times capacity
            m.EU_secondary_costs[stf, location, tech]
            * m.capacity_ext_eusecondary[stf, location, tech]
            + 1 * m.capacity_facility_eusecondary[stf, location, tech]
            + m.cost_scrap[stf, location, tech]
            # Subtract the linearized price reduction (total absolute reduction)
            - m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech]
        )
        expr = m.costs_EU_secondary[stf, location, tech] == eu_secondary_cost_value
        return expr


def apply_costs_constraints(m):
    constraints = [
        CalculateYearlyImportCost(),
        CalculateYearlyStorageCost(),
        CalculateYearlyEUPrimary(),
        CalculateYearlyEUSecondary(),
    ]

    for i, constraint in enumerate(constraints):
        constraint_name = f"yearly_cost_constraint_{i + 1}"
        setattr(
            m,
            constraint_name,
            pyomo.Constraint(
                m.stf,
                m.location,
                m.tech,
                rule=lambda m, stf, loc, tech: constraint.apply_rule(m, stf, loc, tech),
            ),
        )

    # Apply the def_costs_new constraint separately as it uses cost_type_new
    setattr(
        m,
        "cost_constraint_new",
        pyomo.Constraint(
            m.cost_type_new,
            rule=lambda m, cost_type_new: DefCostsNew().apply_rule(m, cost_type_new),
        ),
    )
