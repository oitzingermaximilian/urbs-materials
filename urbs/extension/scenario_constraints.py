from abc import ABC, abstractmethod
import pyomo.environ as pyomo

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
# Materials subject to CRMA Strategic Raw Material targets
CRMA_TARGET_MATERIALS = [
    'aluminum', 'copper', 'silicon', 'cobalt', 'dysprosium', 'gallium',
    'graphite', 'lithium', 'manganese', 'neodymium', 'nickel', 'niobium',
    'praseodymium', 'terbium', 'titanium', 'vanadium', 'boron'
]


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 2. NZIA CONSTRAINTS (40% Assembly in the EU)
# ==============================================================================
class nzia_strict_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, target_techs):
        if stf < 2030:
            return pyomo.Constraint.Skip

        if tech not in target_techs:
            return pyomo.Constraint.Skip

        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage]
        )
        return domestic_contribution >= 0.40 * m.Supply[stf, location, tech, stage]


class nzia_flex_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, target_techs):
        if stf < 2030:
            return pyomo.Constraint.Skip

        if tech not in target_techs:
            return pyomo.Constraint.Skip

        # Aggregates across all stages available for the technology
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
# 3. CRMA CONSTRAINTS (Per Material with Dynamic Geology Check)
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat):
        if stf < 2030:
            return pyomo.Constraint.Skip

        if mat not in CRMA_TARGET_MATERIALS or mat not in m.materials:
            return pyomo.Constraint.Skip

        # FIXED: Match the 2-index structure [stf, mat]
        if (stf, mat) not in m.primary_material_availability:
            return pyomo.Constraint.Skip
        availability = m.primary_material_availability[stf, mat]

        if isinstance(availability, pyomo.Param) or isinstance(availability, (int, float)):
            if availability <= 0:
                return pyomo.Constraint.Skip

        # Enforce the 10% benchmark
        return m.material_mined[stf, mat] >= 0.10 * m.demand_material_total[stf, mat]

class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat):
        if stf < 2030:
            return pyomo.Constraint.Skip

        if mat not in CRMA_TARGET_MATERIALS or mat not in m.materials:
            return pyomo.Constraint.Skip

        # 25% Recycling (from End-of-Life Streams)
        return m.material_recycled[stf, mat] >= 0.25 * m.demand_material_total[stf, mat]


class crma_combined_independence_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat, target_quota):
        # Erst ab dem Zieljahr 2030 anwenden
        if stf < 2030:
            return pyomo.Constraint.Skip

        # Nur für strategische Materialien, die im Modell existieren
        if mat not in CRMA_TARGET_MATERIALS or mat not in m.materials:
            return pyomo.Constraint.Skip

        # Die Summe aus heimischem Bergbau und Sekundärrohstoffen (Recycling)
        domestic_supply = m.material_mined[stf, mat] + m.material_recycled[stf, mat]

        # Absolute Hürde (dynamisch durch Parameter übergeben)
        return domestic_supply >= target_quota * m.demand_material_total[stf, mat]


# ==============================================================================
# 4. APPLICATION LOGIC (The Setup Function)
# ==============================================================================
# ADDED crma_quota=0.35 TO THE FUNCTION ARGUMENTS
def apply_scenario_constraints(m, nzia_mode='strict', crma_mode='combined', crma_active=True, target_techs=None, crma_quota=0.35):
    if target_techs is None:
        target_techs = ['solarPV', 'windon', 'windoff', 'Batteries']

    print(f"\n--- Initializing Policy Constraints ---")

    # ---------------------------------------------------------
    # A. NZIA CONSTRAINTS
    # ---------------------------------------------------------
    strict_logic = nzia_strict_rule()
    m.nzia_strict_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech, m.stages,
        rule=lambda m, y, l, t, s: strict_logic.apply_rule(m, y, l, t, s, target_techs)
    )

    flex_logic = nzia_flex_rule()
    m.nzia_flex_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech,
        rule=lambda m, y, l, t: flex_logic.apply_rule(m, y, l, t, target_techs)
    )

    if nzia_mode == 'strict':
        m.nzia_strict_constraint.activate()
        m.nzia_flex_constraint.deactivate()
        print(f"✅ NZIA STRICT: Active (>=2030) for {target_techs}")
    elif nzia_mode == 'flex':
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.activate()
        print(f"✅ NZIA FLEX:   Active (>=2030) for {target_techs}")
    else:
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.deactivate()
        print("❌ NZIA:        Disabled")

    # ---------------------------------------------------------
    # B. CRMA CONSTRAINTS
    # ---------------------------------------------------------
    extraction_logic = eu_extraction_constraint()
    m.eu_extraction_constraint = pyomo.Constraint(
        m.stf, m.materials,
        rule=lambda m, y, mat: extraction_logic.apply_rule(m, y, mat)
    )

    recycling_logic = eu_recycling_constraint()
    m.eu_recycling_constraint = pyomo.Constraint(
        m.stf, m.materials,
        rule=lambda m, y, mat: recycling_logic.apply_rule(m, y, mat)
    )

    # 2. Instantiate the COMBINED rule (Dynamic >= target_quota Independence)
    combined_crma_logic = crma_combined_independence_constraint()
    m.eu_crma_combined_constraint = pyomo.Constraint(
        m.stf, m.materials,
        # PASS THE crma_quota VARIABLE HERE
        rule=lambda m, y, mat: combined_crma_logic.apply_rule(m, y, mat, crma_quota)
    )

    # 3. Activation Logic Loop based on runtime selection
    if not crma_active:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        m.eu_crma_combined_constraint.deactivate()
        print("❌ CRMA:        Disabled")

    elif crma_mode == 'separated':
        m.eu_extraction_constraint.activate()
        m.eu_recycling_constraint.activate()
        m.eu_crma_combined_constraint.deactivate()
        print("✅ CRMA SEPARATED: Active (>=2030) - Strict 10% Mining & 25% Recycling enforced separately.")

    elif crma_mode == 'combined':
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        m.eu_crma_combined_constraint.activate()
        # UPDATE PRINT STATEMENT TO SHOW CURRENT QUOTA
        print(f"✅ CRMA COMBINED:  Active (>=2030) - Joint (Mining + Recycling) >= {int(crma_quota*100)}% resilience pool.")

    print("-----------------------------------------\n")