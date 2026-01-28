from abc import ABC, abstractmethod
import pyomo.environ as pyomo

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Materials subject to CRMA Strategic Raw Material targets (10% Mining / 15% Recycling)
CRMA_TARGET_MATERIALS = ['Al', 'Si', 'Cu']


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 1. NZIA STRICT (Per Stage) - Starts 2030
# ==============================================================================
class nzia_strict_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if stf < 2030:
            return pyomo.Constraint.Skip
        if tech not in ['SolarPV', 'solarPV']:
            return pyomo.Constraint.Skip

        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage]
        )
        rhs = 0.4 * m.Supply[stf, location, tech, stage]
        return domestic_contribution >= rhs


# ==============================================================================
# 2. NZIA FLEX (Aggregated) - Starts 2030
# ==============================================================================
class nzia_flex_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if stf < 2030:
            return pyomo.Constraint.Skip
        if tech not in ['SolarPV', 'solarPV']:
            return pyomo.Constraint.Skip

        total_domestic_output = sum(
            m.capacity_produced_flow[stf, location, tech, stage] +
            m.capacity_produced_stockout[stf, location, tech, stage]
            for stage in m.stages
        )
        total_supply = sum(
            m.Supply[stf, location, tech, stage]
            for stage in m.stages
        )
        return total_domestic_output >= 0.40 * total_supply


# ==============================================================================
# 3. CRMA MINING (10% of Demand PER MATERIAL) - Starts 2030
#    Target Materials Only: Al, Si, Cu
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat):
        # --- MATERIAL CHECK: Only apply to Strategic Raw Materials ---
        if mat not in CRMA_TARGET_MATERIALS:
            return pyomo.Constraint.Skip

        # --- TIME CHECK: Skip years before 2030 ---
        if stf < 2030:
            return pyomo.Constraint.Skip

        # Constraint: Specific material mining >= 10% of specific material demand
        return m.material_mined[stf, mat] >= 0.10 * m.demand_material_total[stf, mat]


# ==============================================================================
# 4. CRMA RECYCLING (15% of Demand PER MATERIAL) - Starts 2030
#    Target Materials Only: Al, Si, Cu
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat):
        # --- MATERIAL CHECK: Only apply to Strategic Raw Materials ---
        if mat not in CRMA_TARGET_MATERIALS:
            return pyomo.Constraint.Skip

        # --- TIME CHECK: Skip years before 2030 ---
        if stf < 2030:
            return pyomo.Constraint.Skip

        # Constraint: Specific material recycling >= 15% of specific material demand
        return m.material_recycled[stf, mat] >= 0.15 * m.demand_material_total[stf, mat]


# ==============================================================================
# APPLICATION LOGIC
# ==============================================================================
def apply_scenario_constraints(m, nzia_mode='strict', crma_active=True):
    print(f"\n--- Initializing Scenario Constraints ---")
    print(f"   Settings: NZIA='{nzia_mode.upper()}', CRMA={crma_active}")
    print(f"   CRMA Target Materials: {CRMA_TARGET_MATERIALS}")

    # 1. CREATE ALL CONSTRAINTS
    # ---------------------------------------------------------
    strict_logic = nzia_strict_rule()
    m.nzia_strict_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech, m.stages,
        rule=lambda m, y, l, t, s: strict_logic.apply_rule(m, y, l, t, s)
    )

    flex_logic = nzia_flex_rule()
    m.nzia_flex_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech,
        rule=lambda m, y, l, t: flex_logic.apply_rule(m, y, l, t)
    )

    # CRMA Mining (Indexed by MATERIALS)
    extraction_logic = eu_extraction_constraint()
    m.eu_extraction_constraint = pyomo.Constraint(
        m.stf,
        m.materials,
        rule=lambda m, y, mat: extraction_logic.apply_rule(m, y, mat)
    )

    # CRMA Recycling (Indexed by MATERIALS)
    recycling_logic = eu_recycling_constraint()
    m.eu_recycling_constraint = pyomo.Constraint(
        m.stf,
        m.materials,
        rule=lambda m, y, mat: recycling_logic.apply_rule(m, y, mat)
    )

    # 2. TOGGLE NZIA
    # ---------------------------------------------------------
    if nzia_mode == 'strict':
        m.nzia_strict_constraint.activate()
        m.nzia_flex_constraint.deactivate()
        print("✅ NZIA STRICT: Active (>=2030)")
    elif nzia_mode == 'flex':
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.activate()
        print("✅ NZIA FLEX:   Active (>=2030)")
    else:
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.deactivate()
        print("❌ NZIA:        All targets disabled")

    # 3. TOGGLE CRMA
    # ---------------------------------------------------------
    if crma_active:
        m.eu_extraction_constraint.activate()
        m.eu_recycling_constraint.activate()
        print(f"✅ CRMA:        Active (>=2030) for {CRMA_TARGET_MATERIALS}")
    else:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        print("❌ CRMA:        Disabled")