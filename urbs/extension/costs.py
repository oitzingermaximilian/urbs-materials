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
            return ((1 + i) ** dep_prd * i) / ((1 + i) ** dep_prd - 1)
    elif discount == 0:
        if i == 0:
            return 1
        else:
            return dep_prd * ((1 + i) ** dep_prd * i) / ((1 + i) ** dep_prd - 1)
    else:
        if i == 0:
            return (
                (1 + d) ** (1 - (year_built - stf_min)) * ((1 + d) ** dep_prd - 1)
            ) / (dep_prd * d * (1 + d) ** dep_prd)
        else:
            return (
                (1 + d) ** (1 - (year_built - stf_min))
                * (i * (1 + i) ** dep_prd * ((1 + d) ** dep_prd - 1))
                / (d * (1 + d) ** dep_prd * ((1 + i) ** dep_prd - 1))
            )


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
            return (
                (1 + d) ** (1 - (year_built - stf_min))
                * ((1 + d) ** op_time - 1)
                / (dep_prd * d * (1 + d) ** dep_prd)
            )
        else:
            return (
                (1 + d) ** (1 - (year_built - stf_min))
                * (i * (1 + i) ** dep_prd * ((1 + d) ** op_time - 1))
                / (d * (1 + d) ** dep_prd * ((1 + i) ** dep_prd - 1))
            )


def calc_discount_factor(stf, discount, stf_min):
    """
    Discount factor for a payment in year stf.
    - stf: year of payment
    - discount: discount rate
    - stf_min: first year in the model
    """
    return (1 + discount) ** (1 - (stf - stf_min))


def calc_effective_distance(dist, discount):
    if discount == 0:
        return dist
    else:
        return (1 - (1 + discount) ** (-dist)) / discount


# -----------------------------
# Hardcoded financial parameters
# -----------------------------
WACC = 0
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


def effective_distance(stf_dist):
    """Effective distance for variable, fuel, purchase, sell, and fix costs."""
    return calc_effective_distance(stf_dist, DISCOUNT)

