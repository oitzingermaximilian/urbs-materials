from abc import ABC, abstractmethod
import pyomo.environ as pyomo

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Materials subject to CRMA Strategic Raw Material targets (Aggregated)
# Angepasst an die 25 spezifischen Commodities aus der Offshore/Onshore/PV-Liste
CRMA_TARGET_MATERIALS = [
    'aluminum', 'copper', 'silicon', 'cobalt', 'dysprosium', 'gallium',
    'graphite', 'lithium', 'manganese', 'neodymium', 'nickel', 'niobium',
    'praseodymium', 'terbium', 'titanium', 'vanadium', 'boron', #'silver','molybdenum'
]


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 1. NZIA STRICT (Per Stage) - Starts 2030
# ==============================================================================
class nzia_strict_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage, target_techs):
        if stf < 2030:
            return pyomo.Constraint.Skip

        # DYNAMISCHER CHECK: Gilt nur für die Technologien im Learning-Mode
        if tech not in target_techs:
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
    def apply_rule(self, m, stf, location, tech, target_techs):
        if stf < 2030:
            return pyomo.Constraint.Skip

        # DYNAMISCHER CHECK: Gilt nur für die Technologien im Learning-Mode
        if tech not in target_techs:
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
# 3. CRMA MINING (10% of TOTAL Demand over all Target Materials) - Starts 2030
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        if stf < 2030:
            return pyomo.Constraint.Skip

        # Aggregation über alle Ziel-Materialien (Gewicht in t/MW)
        total_mined = sum(m.material_mined[stf, mat] for mat in CRMA_TARGET_MATERIALS if mat in m.materials)
        total_demand = sum(m.demand_material_total[stf, mat] for mat in CRMA_TARGET_MATERIALS if mat in m.materials)

        return total_mined >= 0.10 * total_demand


# ==============================================================================
# 4. CRMA RECYCLING (15% of TOTAL Demand over all Target Materials) - Starts 2030
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        if stf < 2030:
            return pyomo.Constraint.Skip

        # Aggregation über alle Ziel-Materialien (Gewicht in t/MW)
        total_recycled = sum(m.material_recycled[stf, mat] for mat in CRMA_TARGET_MATERIALS if mat in m.materials)
        total_demand = sum(m.demand_material_total[stf, mat] for mat in CRMA_TARGET_MATERIALS if mat in m.materials)

        return total_recycled >= 0.15 * total_demand


# ==============================================================================
# APPLICATION LOGIC
# ==============================================================================
def apply_scenario_constraints(m, nzia_mode='strict', crma_active=True, target_techs=None):
    if target_techs is None:
        target_techs = ['solarPV']  # Fallback

    print(f"\n--- Initializing Scenario Constraints ---")
    print(f"   Settings: NZIA='{nzia_mode.upper()}', CRMA={crma_active}")
    print(f"   NZIA Target Techs: {target_techs}")
    print(f"   CRMA Target Materials (Aggregated sum): {len(CRMA_TARGET_MATERIALS)} materials")

    # 1. CREATE ALL CONSTRAINTS
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

    # CRMA Mining (Nur nach Zeit indiziert, da aggregiert)
    extraction_logic = eu_extraction_constraint()
    m.eu_extraction_constraint = pyomo.Constraint(
        m.stf,
        rule=lambda m, y: extraction_logic.apply_rule(m, y)
    )

    # CRMA Recycling (Nur nach Zeit indiziert, da aggregiert)
    recycling_logic = eu_recycling_constraint()
    m.eu_recycling_constraint = pyomo.Constraint(
        m.stf,
        rule=lambda m, y: recycling_logic.apply_rule(m, y)
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
        print(f"✅ CRMA:        Active (>=2030) - 10% Mining / 15% Recycling (Aggregated)")
    else:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        print("❌ CRMA:        Disabled")