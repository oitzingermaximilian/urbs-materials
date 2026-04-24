from abc import ABC, abstractmethod
import pyomo.environ as pyomo
from pyomo.environ import value


def _normalize_target_techs(target_tech_name):
    """Allow a single tech string or an iterable of tech strings."""
    if isinstance(target_tech_name, str):
        techs = [target_tech_name]
    else:
        try:
            techs = list(target_tech_name)
        except TypeError as exc:
            raise ValueError("target_tech_name must be a string or a list/tuple of strings") from exc

    techs = [t for t in techs if t is not None and str(t).strip() != ""]
    if not techs:
        raise ValueError("target_tech_name is empty. Provide at least one technology.")

    return list(dict.fromkeys(techs))


# ==============================================================================
# 1. SETUP FUNCTION
# ==============================================================================

def setup_onetech_learning(m, target_tech_name='solarPV', target_stages=None):
    """
    Sets up learning variables for one or multiple target technologies and specific stages.

    Args:
        target_tech_name: str or iterable[str]
            - "solarPV" for one technology
            - ["solarPV", "windon"] for multiple technologies
    """
    tech_targets = _normalize_target_techs(target_tech_name)

    unknown_techs = [t for t in tech_targets if t not in m.tech]
    if unknown_techs:
        raise ValueError(f"Unknown technologies in setup_onetech_learning: {unknown_techs}")

    print(f"--- Initializing Single-Tech Learning Module for {tech_targets} ---")

    # A. Define the Tech Subset
    if not hasattr(m, 'tech_one_tech'):
        m.tech_one_tech = pyomo.Set(initialize=tech_targets, within=m.tech)

    # B. Define the Stage Subset (NEW)
    # If the user provides specific stages, use them. Otherwise, default to all stages.
    stage_set_name = 'stages_one_tech'

    if target_stages:
        unknown_stages = [s for s in target_stages if s not in m.stages]
        if unknown_stages:
            raise ValueError(f"Unknown stages in setup_onetech_learning: {unknown_stages}")
        # Create a subset of stages specifically for this tech
        if not hasattr(m, stage_set_name):
            m.stages_one_tech = pyomo.Set(initialize=target_stages, within=m.stages)
    else:
        # Fallback: Point to the global set if no specific list is given
        m.stages_one_tech = m.stages

    print(f"--- Learning restricted to stages: {[s for s in m.stages_one_tech]} ---")

    # C. Define Variables (Indexed by tech_one_tech AND stages_one_tech)

    # 1. Binary Step Variable
    m.BD_onetech = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.Binary
    )

    # 2. Total Savings Variable ($)
    m.PRICEREDUCTION_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    # 3. Unit Price Reduction ($/MW)
    m.pricereduction_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    # 4. Linearization Aux Variable
    m.aux_onetech_prod = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.NonNegativeReals
    )

    # D. Apply Constraints
    _apply_constraints(m)
    print("--- Single-Tech Learning Module Ready ---")


# ==============================================================================
# 2. CONSTRAINT LOGIC
# ==============================================================================

class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args): pass


# --- GROUP 1: LOGIC CONSTRAINTS ---

class OneTech_CostSavings_Constraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Calculates Total Cost Savings based on active learning step
        investment_reduction_value = sum(
            m.P_sec_investment[location, tech, stage, n]
            * m.aux_onetech_prod[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.PRICEREDUCTION_ONETECH_TOTAL[stf, location, tech, stage] == investment_reduction_value


class OneTech_PriceReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Calculates Unit Price Reduction (EUR/MW) based on active binary
        unit_val = sum(
            m.P_sec_investment[location, tech, stage, n] * m.BD_onetech[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.pricereduction_onetech_unit[stf, location, tech, stage] == unit_val


class OneTech_BD_Limitation(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Force exactly one learning step to be active per stage
        return sum(m.BD_onetech[stf, location, tech, stage, n] for n in m.nsteps_sec) == 1


class OneTech_Relation_Pnew_Pprior(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Enforce Monotonicity: Price Reduction(y) >= Price Reduction(y-1)
        if stf == 2024:
            return pyomo.Constraint.Skip

        if stf == value(m.y0):  # Logic for first year if not 2024
            lhs = m.pricereduction_onetech_unit[stf, location, tech, stage]
            rhs = 0
            return lhs >= rhs
        else:

            lhs = m.pricereduction_onetech_unit[stf, location, tech, stage]
            rhs = m.pricereduction_onetech_unit[stf - 1, location, tech, stage]
            return lhs >= rhs


class OneTech_Q_PerStep(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # Cumulative Production >= Threshold of active step
        y0 = min(m.stf)
        cumulative_prod = m.total_production_cap_inital[location, tech, stage] + sum(
            m.processing_cap_new[year, location, tech, stage]
            for year in m.stf if y0 <= year <= stf
        )

        active_threshold = sum(
            m.BD_onetech[stf, location, tech, stage, n] * m.capacityperstep_production[location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return cumulative_prod >= active_threshold


# --- GROUP 2: LINEARIZATION CONSTRAINTS ---

class OneTech_UpperBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux <= BigM * Binary
        return m.aux_onetech_prod[stf, location, tech, stage, n] <= \
            m.gamma_prod * m.BD_onetech[stf, location, tech, stage, n]


class OneTech_UpperBound_Z_Q1(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux <= Current Production
        return m.aux_onetech_prod[stf, location, tech, stage, n] <= \
            m.processing_cap_new[stf, location, tech, stage]


class OneTech_LowerBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        # Aux >= Current Production - BigM * (1 - Binary)
        rhs = (m.processing_cap_new[stf, location, tech, stage]
               - (1 - m.BD_onetech[stf, location, tech, stage, n]) * m.gamma_prod)
        return m.aux_onetech_prod[stf, location, tech, stage, n] >= rhs


class OneTech_NonNegativity_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        return m.aux_onetech_prod[stf, location, tech, stage, n] >= 0


# ==============================================================================
# 3. INTERNAL CONSTRAINT APPLIER
# ==============================================================================

def _apply_constraints(m):
    # Logic Constraints
    # Note: We now use m.stages_one_tech in the index!

    setattr(m, "c_onetech_costsavings", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                         rule=lambda m, t, l, tech,
                                                                     s: OneTech_CostSavings_Constraint().apply_rule(m,
                                                                                                                    t,
                                                                                                                    l,
                                                                                                                    tech,
                                                                                                                    s)))
    setattr(m, "c_onetech_pricered", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                      rule=lambda m, t, l, tech,
                                                                  s: OneTech_PriceReduction_Calc().apply_rule(m, t, l,
                                                                                                              tech, s)))
    setattr(m, "c_onetech_bdlimit", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                     rule=lambda m, t, l, tech, s: OneTech_BD_Limitation().apply_rule(m,
                                                                                                                      t,
                                                                                                                      l,
                                                                                                                      tech,
                                                                                                                      s)))
    setattr(m, "c_onetech_relation", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                      rule=lambda m, t, l, tech,
                                                                  s: OneTech_Relation_Pnew_Pprior().apply_rule(m, t, l,
                                                                                                               tech,
                                                                                                               s)))
    setattr(m, "c_onetech_qstep", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                   rule=lambda m, t, l, tech, s: OneTech_Q_PerStep().apply_rule(m, t, l,
                                                                                                                tech,
                                                                                                                s)))

    # Linearization Constraints
    setattr(m, "c_onetech_z_upper",
            pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
                             rule=lambda m, t, l, tech, s, n: OneTech_UpperBound_Z().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_q1_up",
            pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
                             rule=lambda m, t, l, tech, s, n: OneTech_UpperBound_Z_Q1().apply_rule(m, t, l, tech, s,
                                                                                                   n)))
    setattr(m, "c_onetech_z_low", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
                                                   rule=lambda m, t, l, tech, s, n: OneTech_LowerBound_Z().apply_rule(m,
                                                                                                                      t,
                                                                                                                      l,
                                                                                                                      tech,
                                                                                                                      s,
                                                                                                                      n)))
    setattr(m, "c_onetech_z_noneg",
            pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
                             rule=lambda m, t, l, tech, s, n: OneTech_NonNegativity_Z().apply_rule(m, t, l, tech, s,
                                                                                                   n)))

