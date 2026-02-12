from abc import ABC, abstractmethod
import pyomo.environ as pyomo
from pyomo.environ import value


# ==============================================================================
# 1. SETUP FUNCTION
# ==============================================================================

def setup_scrap_onetech_learning(m, target_tech_name='solarPV'):
    """
    Sets up economies of scale specifically for the SCRAP/RECYCLING module.
    Limits variables to a single technology to prevent memory bloat/crashes.
    """
    print(f"--- Initializing Scrap Learning Module for {target_tech_name} ---")

    # A. Define the Subset (The Gatekeeper)
    # This creates a generic set 'm.tech_scrap_onetech' containing only your target
    if not hasattr(m, 'tech_scrap_onetech'):
        m.tech_scrap_onetech = pyomo.Set(initialize=[target_tech_name], within=m.tech)

    # B. Define Variables (Indexed by tech_scrap_onetech)

    # 1. Binary Step Variable (Which learning step is active for Recycling?)
    m.BD_scrap_onetech = pyomo.Var(
        m.stf, m.location, m.tech_scrap_onetech, m.nsteps_sec,
        domain=pyomo.Binary,
        doc="Binary: 1 if this recycling scale step is active"
    )

    # 2. Total Savings Variable ($)
    # This is the variable you subtract from the Total Cost
    m.PRICEREDUCTION_SCRAP_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_scrap_onetech,
        domain=pyomo.NonNegativeReals,
        doc="Total recycling cost savings ($)"
    )

    # 3. Unit Price Reduction ($/ton) - Tracks the learning curve depth
    m.pricereduction_scrap_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_scrap_onetech,
        domain=pyomo.NonNegativeReals,
        doc="Unit recycling cost reduction ($/ton)"
    )

    # 4. Linearization Aux Variable
    m.aux_scrap_onetech = pyomo.Var(
        m.stf, m.location, m.tech_scrap_onetech, m.nsteps_sec,
        domain=pyomo.NonNegativeReals,
        doc="Linearization variable for Capacity * Binary"
    )

    # C. Apply Constraints
    _apply_constraints(m)
    print("--- Scrap Single-Tech Learning Module Ready ---")


# ==============================================================================
# 2. CONSTRAINT LOGIC
# ==============================================================================

class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args): pass


# --- GROUP 1: LOGIC CONSTRAINTS ---

class Scrap_TotalSavings_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # Savings ($) = Sum( Step_Price_Reduction * Aux_Capacity )
        val = sum(
            m.P_sec_recycling[location, tech, n]
            * m.aux_scrap_onetech[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        return m.PRICEREDUCTION_SCRAP_ONETECH_TOTAL[stf, location, tech] == val


class Scrap_UnitReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # Unit Price ($/ton) = Sum( Step_Price * Binary )
        val = sum(
            m.P_sec_recycling[location, tech, n] * m.BD_scrap_onetech[stf, location, tech, n]
            for n in m.nsteps_sec
        )
        return m.pricereduction_scrap_onetech_unit[stf, location, tech] == val


class Scrap_Binary_Limit(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # Force exactly one step to be active
        return sum(m.BD_scrap_onetech[stf, location, tech, n] for n in m.nsteps_sec) == 1


class Scrap_Monotonicity(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # "Cannot unlearn": Price reduction today >= Price reduction yesterday
        if stf == min(m.stf):
            return pyomo.Constraint.Skip

        return m.pricereduction_scrap_onetech_unit[stf, location, tech] >= \
            m.pricereduction_scrap_onetech_unit[stf - 1, location, tech]


class Scrap_Production_Trigger(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # Cumulative Recycling Capacity >= Threshold of active step
        y0 = min(m.stf)

        # 1. Calc Cumulative Recycling Capacity
        cumulative_cap = m.total_recycling_cap_initial[location, tech] + sum(
            m.capacity_scrap_rec[year, location, tech]
            for year in m.stf
            if y0 <= year <= stf
        )

        # 2. Identify Threshold
        active_threshold = sum(
            m.BD_scrap_onetech[stf, location, tech, n] * m.tons_perstep_recycling[location, tech, n]
            for n in m.nsteps_sec
        )

        return cumulative_cap >= active_threshold


# --- GROUP 2: LINEARIZATION CONSTRAINTS ---

class Scrap_Lin_BigM_Upper(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        # Aux <= BigM * Binary
        return m.aux_scrap_onetech[stf, location, tech, n] <= \
            m.gamma_scrap * m.BD_scrap_onetech[stf, location, tech, n]


class Scrap_Lin_Cap_Upper(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        # Aux <= Current Recycling Capacity
        return m.aux_scrap_onetech[stf, location, tech, n] <= \
            m.capacity_scrap_rec[stf, location, tech]


class Scrap_Lin_Cap_Lower(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        # Aux >= Capacity - BigM * (1 - Binary)
        rhs = (
                m.capacity_scrap_rec[stf, location, tech]
                - (1 - m.BD_scrap_onetech[stf, location, tech, n]) * m.gamma_scrap
        )
        return m.aux_scrap_onetech[stf, location, tech, n] >= rhs


class Scrap_NonNegativity(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, n):
        return m.aux_scrap_onetech[stf, location, tech, n] >= 0


# ==============================================================================
# 3. INTERNAL CONSTRAINT APPLIER
# ==============================================================================

def _apply_constraints(m):
    # A. Logic Constraints (Index: stf, location, tech_scrap_onetech)
    logic_map = {
        "scrap_constr_savings": Scrap_TotalSavings_Calc(),
        "scrap_constr_unit": Scrap_UnitReduction_Calc(),
        "scrap_constr_limit": Scrap_Binary_Limit(),
        "scrap_constr_mono": Scrap_Monotonicity(),
        "scrap_constr_trig": Scrap_Production_Trigger(),
    }

    for name, constr_obj in logic_map.items():
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech_scrap_onetech,  # <--- INDEXED ON SUBSET
            rule=lambda m, t, l, tech: constr_obj.apply_rule(m, t, l, tech)
        ))

    # B. Linearization Constraints (Index: stf, location, tech, n)
    lin_map = {
        "scrap_lin_bigM": Scrap_Lin_BigM_Upper(),
        "scrap_lin_cup": Scrap_Lin_Cap_Upper(),
        "scrap_lin_clo": Scrap_Lin_Cap_Lower(),
        "scrap_lin_noneg": Scrap_NonNegativity(),
    }

    for name, constr_obj in lin_map.items():
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech_scrap_onetech, m.nsteps_sec,  # <--- INDEXED ON SUBSET
            rule=lambda m, t, l, tech, n: constr_obj.apply_rule(m, t, l, tech, n)
        ))