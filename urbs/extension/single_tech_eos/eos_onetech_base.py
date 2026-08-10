from abc import ABC, abstractmethod
import pyomo.environ as pyomo
from pyomo.environ import value, Binary, NonNegativeReals


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args): pass


def _normalize_target_techs(target_tech_name):
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
# 0. HELPER FUNCTION
# ==============================================================================

def check_valid_indices(m, location, tech, stage):
    """
    Returns True if the (location, tech, stage) pair is valid.
    Checks if investment data exists for the first step.
    """
    first_step = list(m.nsteps_sec)[0]
    return (location, tech, stage, first_step) in m.P_sec_capex


# ==============================================================================
# 1. SETUP FUNCTION
# ==============================================================================

def setup_onetech_learning(m, target_tech_name='solarPV', target_stages=None):
    tech_targets = _normalize_target_techs(target_tech_name)

    unknown_techs = [t for t in tech_targets if t not in m.tech]
    if unknown_techs:
        raise ValueError(f"Unknown technologies in setup_onetech_learning: {unknown_techs}")

    print(f"--- Initializing Single-Tech Learning Module for {tech_targets} ---")

    # A. Define the Tech Subset
    if not hasattr(m, 'tech_one_tech'):
        m.tech_one_tech = pyomo.Set(initialize=tech_targets, within=m.tech)

    # B. Define the Stage Subset
    stage_set_name = 'stages_one_tech'
    if target_stages:
        unknown_stages = [s for s in target_stages if s not in m.stages]
        if unknown_stages:
            raise ValueError(f"Unknown stages in setup_onetech_learning: {unknown_stages}")
        if not hasattr(m, stage_set_name):
            m.stages_one_tech = pyomo.Set(initialize=target_stages, within=m.stages)
    else:
        m.stages_one_tech = m.stages

    # C. Define Variables (Indexed by the DENSE sets)

    m.BD_onetech = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.Binary
    )

    m.PRICEREDUCTION_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    m.pricereduction_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    m.aux_onetech_prod = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.NonNegativeReals
    )

    m.PRICEREDUCTION_BULKMAT_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    m.pricereduction_bulkmat_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )

    m.PRICEREDUCTION_CAPEX_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )
    m.pricereduction_capex_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )
    m.aux_onetech_capex = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.NonNegativeReals
    )

    m.PRICEREDUCTION_FOM_ONETECH_TOTAL = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )
    m.pricereduction_fom_onetech_unit = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
        domain=pyomo.NonNegativeReals
    )
    m.aux_onetech_fom = pyomo.Var(
        m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
        domain=pyomo.NonNegativeReals
    )

    # D. Apply Constraints
    _apply_constraints(m)
    _apply_bulkmat_constraints(m)
    # 3. Add the classes for CAPEX and FOM
    _apply_capex_fom_constraints(m)
    print("--- Single-Tech Learning Module Ready ---")

class OneTech_Capex_InvalidZeroRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.PRICEREDUCTION_CAPEX_ONETECH_TOTAL[stf, location, tech, stage] == 0

class OneTech_Fom_InvalidZeroRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.PRICEREDUCTION_FOM_ONETECH_TOTAL[stf, location, tech, stage] == 0

class OneTech_Capex_CostSavings_Constraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        val = sum(m.P_sec_capex[location, tech, stage, n] * m.aux_onetech_capex[stf, location, tech, stage, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_CAPEX_ONETECH_TOTAL[stf, location, tech, stage] == val

class OneTech_Fom_CostSavings_Constraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        val = sum(m.P_sec_fom[location, tech, stage, n] * m.aux_onetech_fom[stf, location, tech, stage, n] for n in m.nsteps_sec)
        return m.PRICEREDUCTION_FOM_ONETECH_TOTAL[stf, location, tech, stage] == val

class OneTech_Capex_PriceReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        val = sum(m.P_sec_capex[location, tech, stage, n] * m.BD_onetech[stf, location, tech, stage, n] for n in m.nsteps_sec)
        return m.pricereduction_capex_onetech_unit[stf, location, tech, stage] == val

class OneTech_Fom_PriceReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        val = sum(m.P_sec_fom[location, tech, stage, n] * m.BD_onetech[stf, location, tech, stage, n] for n in m.nsteps_sec)
        return m.pricereduction_fom_onetech_unit[stf, location, tech, stage] == val

class OneTech_Capex_Relation_Pnew_Pprior(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        if stf == 2024: return pyomo.Constraint.Skip
        if stf == pyomo.value(m.y0): return m.pricereduction_capex_onetech_unit[stf, location, tech, stage] >= 0
        return m.pricereduction_capex_onetech_unit[stf, location, tech, stage] >= m.pricereduction_capex_onetech_unit[stf - 1, location, tech, stage]

class OneTech_Fom_Relation_Pnew_Pprior(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        if stf == 2024: return pyomo.Constraint.Skip
        if stf == pyomo.value(m.y0): return m.pricereduction_fom_onetech_unit[stf, location, tech, stage] >= 0
        return m.pricereduction_fom_onetech_unit[stf, location, tech, stage] >= m.pricereduction_fom_onetech_unit[stf - 1, location, tech, stage]

class OneTech_Capex_UpperBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_capex[stf, location, tech, stage, n] <= m.gamma_prod * m.BD_onetech[stf, location, tech, stage, n]

class OneTech_Capex_UpperBound_Z_Q1(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_capex[stf, location, tech, stage, n] <= m.processing_cap_new[stf, location, tech, stage]

class OneTech_Capex_LowerBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_capex[stf, location, tech, stage, n] >= m.processing_cap_new[stf, location, tech, stage] - (1 - m.BD_onetech[stf, location, tech, stage, n]) * m.gamma_prod

class OneTech_Capex_NonNegativity_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_capex[stf, location, tech, stage, n] >= 0

class OneTech_Fom_UpperBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_fom[stf, location, tech, stage, n] <= m.gamma_prod * m.BD_onetech[stf, location, tech, stage, n]

class OneTech_Fom_UpperBound_Z_Q1(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_fom[stf, location, tech, stage, n] <= m.capacity_processing_total[stf, location, tech, stage]

class OneTech_Fom_LowerBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_fom[stf, location, tech, stage, n] >= m.capacity_processing_total[stf, location, tech, stage] - (1 - m.BD_onetech[stf, location, tech, stage, n]) * m.gamma_prod

class OneTech_Fom_NonNegativity_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_fom[stf, location, tech, stage, n] >= 0

def _apply_capex_fom_constraints(m):
    setattr(m, "c_onetech_invalid_zero_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Capex_InvalidZeroRule().apply_rule(m, t, l, tech, s)))
    setattr(m, "c_onetech_invalid_zero_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Fom_InvalidZeroRule().apply_rule(m, t, l, tech, s)))
    
    setattr(m, "c_onetech_costsavings_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Capex_CostSavings_Constraint().apply_rule(m, t, l, tech, s)))
    setattr(m, "c_onetech_costsavings_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Fom_CostSavings_Constraint().apply_rule(m, t, l, tech, s)))
    
    setattr(m, "c_onetech_pricered_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Capex_PriceReduction_Calc().apply_rule(m, t, l, tech, s)))
    setattr(m, "c_onetech_pricered_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Fom_PriceReduction_Calc().apply_rule(m, t, l, tech, s)))
    
    setattr(m, "c_onetech_relation_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Capex_Relation_Pnew_Pprior().apply_rule(m, t, l, tech, s)))
    setattr(m, "c_onetech_relation_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, rule=lambda m, t, l, tech, s: OneTech_Fom_Relation_Pnew_Pprior().apply_rule(m, t, l, tech, s)))
    
    setattr(m, "c_onetech_z_upper_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Capex_UpperBound_Z().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_q1_up_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Capex_UpperBound_Z_Q1().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_low_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Capex_LowerBound_Z().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_noneg_capex", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Capex_NonNegativity_Z().apply_rule(m, t, l, tech, s, n)))
    
    setattr(m, "c_onetech_z_upper_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Fom_UpperBound_Z().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_q1_up_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Fom_UpperBound_Z_Q1().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_low_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Fom_LowerBound_Z().apply_rule(m, t, l, tech, s, n)))
    setattr(m, "c_onetech_z_noneg_fom", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec, rule=lambda m, t, l, tech, s, n: OneTech_Fom_NonNegativity_Z().apply_rule(m, t, l, tech, s, n)))


# ==============================================================================
# 2. CONSTRAINT LOGIC
# ==============================================================================

# --- INVALID COMBO CLEANUP ---
class OneTech_InvalidZeroRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        """If combination is invalid, force Total Savings to 0 to prevent ghost revenue."""
        if check_valid_indices(m, location, tech, stage):
            return pyomo.Constraint.Skip
        return m.PRICEREDUCTION_ONETECH_TOTAL[stf, location, tech, stage] == 0


class OneTech_InvalidZeroRule_BulkMat(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        """If combination is invalid, force Bulk Mat Savings to 0 to prevent ghost revenue."""
        if check_valid_indices(m, location, tech, stage):
            return pyomo.Constraint.Skip
        return m.PRICEREDUCTION_BULKMAT_ONETECH_TOTAL[stf, location, tech, stage] == 0


class OneTech_InvalidZeroRule_BD(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        """If combination is invalid, force binary variable to 0."""
        if check_valid_indices(m, location, tech, stage):
            return pyomo.Constraint.Skip
        return m.BD_onetech[stf, location, tech, stage, n] == 0


# --- GROUP 1: LOGIC CONSTRAINTS ---

class OneTech_CostSavings_Constraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        investment_reduction_value = sum(
            m.P_sec_opex_var[location, tech, stage, n]
            * m.aux_onetech_prod[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.PRICEREDUCTION_ONETECH_TOTAL[stf, location, tech, stage] == investment_reduction_value


class OneTech_PriceReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        unit_val = sum(
            m.P_sec_opex_var[location, tech, stage, n] * m.BD_onetech[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.pricereduction_onetech_unit[stf, location, tech, stage] == unit_val


class OneTech_BD_Limitation(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return sum(m.BD_onetech[stf, location, tech, stage, n] for n in m.nsteps_sec) == 1


class OneTech_Relation_Pnew_Pprior(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        if stf == 2024:
            return pyomo.Constraint.Skip

        if stf == value(m.y0):
            return m.pricereduction_onetech_unit[stf, location, tech, stage] >= 0
        else:
            lhs = m.pricereduction_onetech_unit[stf, location, tech, stage]
            rhs = m.pricereduction_onetech_unit[stf - 1, location, tech, stage]
            return lhs >= rhs


class OneTech_Q_PerStep(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        y0 = min(m.stf)
        cumulative_prod = m.total_production_cap_inital[location, tech, stage] + sum(
            m.capacity_produced_output[year, location, tech, stage]
            for year in m.stf if y0 <= year <= stf
        )

        active_threshold = sum(
            m.BD_onetech[stf, location, tech, stage, n] * m.capacityperstep_production[location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return cumulative_prod >= active_threshold


# --- BULK MATERIAL EOS CONSTRAINTS ---

class OneTech_BulkMat_CostSavings_Constraint(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        first_step = list(m.nsteps_sec)[0]
        if (location, tech, stage, first_step) not in m.P_sec_downstream_manufacturing:
            return m.PRICEREDUCTION_BULKMAT_ONETECH_TOTAL[stf, location, tech, stage] == 0

        reduction_value = sum(
            m.P_sec_downstream_manufacturing[location, tech, stage, n]
            * m.aux_onetech_prod[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.PRICEREDUCTION_BULKMAT_ONETECH_TOTAL[stf, location, tech, stage] == reduction_value


class OneTech_BulkMat_PriceReduction_Calc(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        first_step = list(m.nsteps_sec)[0]
        if (location, tech, stage, first_step) not in m.P_sec_downstream_manufacturing:
            return m.pricereduction_bulkmat_onetech_unit[stf, location, tech, stage] == 0

        unit_val = sum(
            m.P_sec_downstream_manufacturing[location, tech, stage, n] * m.BD_onetech[stf, location, tech, stage, n]
            for n in m.nsteps_sec
        )
        return m.pricereduction_bulkmat_onetech_unit[stf, location, tech, stage] == unit_val


class OneTech_BulkMat_Relation_Pnew_Pprior(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip

        first_step = list(m.nsteps_sec)[0]
        if (location, tech, stage, first_step) not in m.P_sec_downstream_manufacturing:
            return pyomo.Constraint.Skip

        if stf == 2024:
            return pyomo.Constraint.Skip

        if stf == value(m.y0):
            return m.pricereduction_bulkmat_onetech_unit[stf, location, tech, stage] >= 0
        else:
            lhs = m.pricereduction_bulkmat_onetech_unit[stf, location, tech, stage]
            rhs = m.pricereduction_bulkmat_onetech_unit[stf - 1, location, tech, stage]
            return lhs >= rhs


# --- GROUP 2: LINEARIZATION CONSTRAINTS ---

class OneTech_UpperBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_prod[stf, location, tech, stage, n] <= \
            m.gamma_prod * m.BD_onetech[stf, location, tech, stage, n]


class OneTech_UpperBound_Z_Q1(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_prod[stf, location, tech, stage, n] <= \
            m.capacity_produced_output[stf, location, tech, stage]


class OneTech_LowerBound_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        rhs = (m.capacity_produced_output[stf, location, tech, stage]
               - (1 - m.BD_onetech[stf, location, tech, stage, n]) * m.gamma_prod)
        return m.aux_onetech_prod[stf, location, tech, stage, n] >= rhs


class OneTech_NonNegativity_Z(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, n):
        if not check_valid_indices(m, location, tech, stage): return pyomo.Constraint.Skip
        return m.aux_onetech_prod[stf, location, tech, stage, n] >= 0


# ==============================================================================
# 3. INTERNAL CONSTRAINT APPLIER
# ==============================================================================

def _apply_constraints(m):
    # 0. Zero-Out Invalid Combinations (New)
    setattr(m, "c_onetech_invalid_zero", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                          rule=lambda m, t, l, tech,
                                                                      s: OneTech_InvalidZeroRule().apply_rule(m, t, l,
                                                                                                              tech, s)))

    setattr(m, "c_onetech_invalid_zero_bd",
            pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech, m.nsteps_sec,
                             rule=lambda m, t, l, tech, s, n: OneTech_InvalidZeroRule_BD().apply_rule(m, t, l, tech, s,
                                                                                                      n)))

    # 1. Standard Constraints
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

    # 2. Linearization Constraints
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


def _apply_bulkmat_constraints(m):
    # 0. Zero-Out Invalid Combinations (New)
    setattr(m, "c_bulkmat_onetech_invalid_zero", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                                  rule=lambda m, t, l, tech,
                                                                              s: OneTech_InvalidZeroRule_BulkMat().apply_rule(
                                                                      m, t, l, tech, s)))

    # 1. Standard Constraints
    setattr(m, "c_bulkmat_onetech_costsavings", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                                 rule=lambda m, t, l, tech,
                                                                             s: OneTech_BulkMat_CostSavings_Constraint().apply_rule(
                                                                     m, t, l, tech, s)
                                                                 ))

    setattr(m, "c_bulkmat_onetech_pricered", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                              rule=lambda m, t, l, tech,
                                                                          s: OneTech_BulkMat_PriceReduction_Calc().apply_rule(
                                                                  m, t, l, tech, s)
                                                              ))

    setattr(m, "c_bulkmat_onetech_relation", pyomo.Constraint(m.stf, m.location, m.tech_one_tech, m.stages_one_tech,
                                                              rule=lambda m, t, l, tech,
                                                                          s: OneTech_BulkMat_Relation_Pnew_Pprior().apply_rule(
                                                                  m, t, l, tech, s)
                                                              ))