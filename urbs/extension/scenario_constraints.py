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

        # DYNAMIC GEOLOGY CHECK (Prevents Infeasibility for elements like Rare Earths)
        # Sums the reserves across all locations for this material
        total_availability = sum(
            pyomo.value(m.primary_material_availability[stf, loc, mat])
            for loc in m.location
            if (stf, loc, mat) in m.primary_material_availability
        )

        # Geology Exception (EUR-Lex): No physical reserves = No quota applied
        if total_availability <= 0:
            return pyomo.Constraint.Skip

        return m.material_mined[stf, mat] >= 0.10 * m.demand_material_total[stf, mat]

class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf, mat):
        if stf < 2030:
            return pyomo.Constraint.Skip

        if mat not in CRMA_TARGET_MATERIALS or mat not in m.materials:
            return pyomo.Constraint.Skip

        # 25% Recycling (from End-of-Life Streams)
        return m.material_recycled[stf, mat] >= 0.25 * m.demand_material_total[stf, mat]


# ==============================================================================
# 4. APPLICATION LOGIC (The Setup Function)
# ==============================================================================
def apply_scenario_constraints(m, nzia_mode='strict', crma_active=True, target_techs=None):
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

    if crma_active:
        m.eu_extraction_constraint.activate()
        m.eu_recycling_constraint.activate()
        print("✅ CRMA:        Active (>=2030) - 10% Mining (Dynamic) / 40% Processing / 25% Recycling")
    else:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        print("❌ CRMA:        Disabled")

    print("-----------------------------------------\n")