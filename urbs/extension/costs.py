from abc import ABC, abstractmethod
import pyomo.core as pyomo


def calc_invcost_factor(dep_prd, wacc, discount=None, year_built=None, stf_min=None):
    """
    Annualized investment cost factor for a process.
    - dep_prd: process lifetime (years)
    - wacc: interest rate / WACC (e.g., 0.06)
    - discount: discount rate for intertemporal planning (same for all processes)
    - year_built: year process is built (required if discount is given)
    - stf_min: first year in model (required if discount is given)
    """
    i = wacc
    d = discount

    if discount is None:
        if i == 0:
            return 1 / dep_prd
        else:
            return ( (1 + i) ** dep_prd * i ) / ( (1 + i) ** dep_prd - 1 )
    elif discount == 0:
        if i == 0:
            return 1
        else:
            return dep_prd * ( (1 + i) ** dep_prd * i ) / ( (1 + i) ** dep_prd - 1 )
    else:
        if i == 0:
            return ((1 + d) ** (1 - (year_built - stf_min)) * ((1 + d) ** dep_prd - 1)) / (dep_prd * d * (1 + d) ** dep_prd)
        else:
            return ((1 + d) ** (1 - (year_built - stf_min)) *
                    (i * (1 + i) ** dep_prd * ((1 + d) ** dep_prd - 1))) / \
                   (d * (1 + d) ** dep_prd * ((1 + i) ** dep_prd - 1))


def calc_overpay_factor(dep_prd, wacc, discount, year_built, stf_min, stf_end):
    """
    Factor to account for the part of CAPEX beyond the model horizon.
    - dep_prd: lifetime of process
    - wacc: interest rate / WACC
    - discount: discount rate
    - year_built: year process is built
    - stf_min: first year
    - stf_end: last year of optimization horizon
    """
    op_time = (year_built + dep_prd) - stf_end - 1
    i = wacc
    d = discount

    if d == 0:
        if i == 0:
            return op_time / dep_prd
        else:
            return op_time * ((1 + i) ** dep_prd * i) / ((1 + i) ** dep_prd - 1)
    else:
        if i == 0:
            return ((1 + d) ** (1 - (year_built - stf_min)) * ((1 + d) ** op_time - 1)) / (dep_prd * d * (1 + d) ** dep_prd)
        else:
            return ((1 + d) ** (1 - (year_built - stf_min)) *
                    (i * (1 + i) ** dep_prd * ((1 + d) ** op_time - 1))) / \
                   (d * (1 + d) ** dep_prd * ((1 + i) ** dep_prd - 1))


def calc_discount_factor(stf, discount, stf_min):
    """
    Discount factor for a payment in year stf.
    - stf: year of payment
    - discount: discount rate
    - stf_min: first year in the model
    """
    return (1 + discount) ** (1 - (stf - stf_min))

# -----------------------------
# Hardcoded financial parameters
# -----------------------------
WACC = 0.071
DISCOUNT = 0.03
STF_MIN = 2024
STF_END = 2050


# -----------------------------
# Wrapper functions
# -----------------------------
def invcost_factor(dep_prd, year_built):
    """Annualized CAPEX factor for a process."""
    return calc_invcost_factor(dep_prd, WACC, DISCOUNT, year_built, STF_MIN)

def overpay_factor(dep_prd, year_built):
    """Fraction of CAPEX beyond model horizon."""
    return calc_overpay_factor(dep_prd, WACC, DISCOUNT, year_built, STF_MIN, STF_END)

def discount_factor(stf):
    """Discount factor for any O&M, variable or fuel cost in year stf."""
    return calc_discount_factor(stf, DISCOUNT, STF_MIN)

class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, stf, location, tech):
        pass


# -----------------------------
# New DefCosts integrating CAPEX / OPEX
# -----------------------------
class DefCostsNew(AbstractConstraint):
    def apply_rule(self, m, cost_type_new):
        total_cost = 0
        for stf in m.stf:
            for location in m.location:
                for tech in m.tech:
                    lifetime = m.l[location, tech]

                    if cost_type_new in ["Importcost", "Eu Cost Primary", "Eu Cost Secondary"]:
                        # CAPEX: annualized with invcost_factor, subtract overpay
                        if cost_type_new == "Importcost":
                            base = m.IMPORTCOST[stf, location, tech] * (
                                m.capacity_ext_imported[stf, location, tech]
                                + m.capacity_ext_stock_imported[stf, location, tech]
                            ) + m.capacity_ext_stock_imported[stf, location, tech] * m.logisticcost[location, tech] \
                                + m.anti_dumping_measures[stf, location, tech]
                        elif cost_type_new == "Eu Cost Primary":
                            base = m.EU_primary_costs[stf, location, tech] * m.capacity_ext_euprimary[stf, location, tech]
                        elif cost_type_new == "Eu Cost Secondary":
                            base = (m.EU_secondary_costs[stf, location, tech] * m.capacity_ext_eusecondary[stf, location, tech]
                                    + m.capacity_facility_eusecondary[stf, location, tech]
                                    + m.cost_scrap[stf, location, tech]
                                    - m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech])

                        total_cost += base * invcost_factor(lifetime, stf) \
                                      - base * overpay_factor(lifetime, stf)

                    elif cost_type_new in ["O_and_M", "Storagecost"]:
                        # OPEX: discount factor
                        if cost_type_new == "O_and_M":
                            base = m.O_and_M_costs[stf, location, tech] * m.capacity_ext[stf, location, tech]
                        elif cost_type_new == "Storagecost":
                            base = m.STORAGECOST[location, tech] * m.capacity_ext_stock[stf, location, tech]
                        total_cost += base * discount_factor(stf)
                    else:
                        raise NotImplementedError(f"Unknown cost type: {cost_type_new}")

        return m.costs_new[cost_type_new] == total_cost


class CalculateYearlyImportCost(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lifetime = m.l[location, tech]
        base = (
            m.IMPORTCOST[stf, location, tech]
            * (m.capacity_ext_imported[stf, location, tech] + m.capacity_ext_stock_imported[stf, location, tech])
            + m.capacity_ext_stock_imported[stf, location, tech] * m.logisticcost[location, tech]
            + m.anti_dumping_measures[stf, location, tech]
        )
        expr = m.costs_ext_import[stf, location, tech] == base * invcost_factor(lifetime, stf) \
               - base * overpay_factor(lifetime, stf)
        return expr

class CalculateYearlyStorageCost(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        base = m.STORAGECOST[location, tech] * m.capacity_ext_stock[stf, location, tech]
        expr = m.costs_ext_storage[stf, location, tech] == base * discount_factor(stf)
        return expr

class CalculateYearlyEUPrimary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lifetime = m.l[location, tech]
        base = m.EU_primary_costs[stf, location, tech] * m.capacity_ext_euprimary[stf, location, tech]
        expr = m.costs_EU_primary[stf, location, tech] == base * invcost_factor(lifetime, stf) \
               - base * overpay_factor(lifetime, stf)
        return expr

class CalculateYearlyEUSecondary(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lifetime = m.l[location, tech]
        base = (
            m.EU_secondary_costs[stf, location, tech] * m.capacity_ext_eusecondary[stf, location, tech]
            + m.capacity_facility_eusecondary[stf, location, tech]
            + m.cost_scrap[stf, location, tech]
            - m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech]
        )
        expr = m.costs_EU_secondary[stf, location, tech] == base * invcost_factor(lifetime, stf) \
               - base * overpay_factor(lifetime, stf)
        return expr

class CalculateYearlyOMCost(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        base = m.O_and_M_costs[stf, location, tech] * m.capacity_ext[stf, location, tech]
        expr = m.costs_O_and_M[stf, location, tech] == base * discount_factor(stf)
        return expr


def apply_costs_constraints(m):
    constraints = [
        CalculateYearlyImportCost(),
        CalculateYearlyStorageCost(),
        CalculateYearlyEUPrimary(),
        CalculateYearlyEUSecondary(),
        CalculateYearlyOMCost(),
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
