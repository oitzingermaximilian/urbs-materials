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
            # Linearized version - only EU secondary costs need linearization now
            # Scrap costs are handled directly in scrap.py with pricereduction applied to f_scrap_rec
            total_eu_cost_secondary = sum(
                (
                    # Linearized EU secondary costs: EU_secondary_costs - eu_secondary_cost_reduction
                    (m.EU_secondary_costs[stf, site, tech] - m.pricereduction_sec_investment[stf, site, tech])
                    * m.capacity_ext_eusecondary[stf, site, tech]
                    + 1000 * m.capacity_facility_eusecondary[stf, site, tech]
                    # Scrap costs are now linear (no reduction applied here, it's in scrap.py)
                    + m.cost_scrap[stf, site, tech]
                )
                for stf in m.stf
                for site in m.location
                for tech in m.tech
            )
            expr = m.costs_new[cost_type_new] == total_eu_cost_secondary
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
        # Linearized version - only EU secondary costs need linearization now
        # Scrap costs are handled directly in scrap.py with pricereduction applied to f_scrap_rec
        eu_secondary_cost_value = (
            # Linearized EU secondary costs: EU_secondary_costs - eu_secondary_cost_reduction
            (m.EU_secondary_costs[stf, location, tech] - m.pricereduction_sec_investment[stf, location, tech])
            * m.capacity_ext_eusecondary[stf, location, tech]
            + 1000 * m.capacity_facility_eusecondary[stf, location, tech]
            # Scrap costs are now linear (no reduction applied here, it's in scrap.py)
            + m.cost_scrap[stf, location, tech]
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
