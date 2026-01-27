from abc import ABC, abstractmethod
import pyomo.environ as pyomo


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 1. NZIA STRICT (Per Stage) - Starts 2030
# ==============================================================================
class nzia_strict_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        # --- TIME CHECK: Skip years before 2030 ---
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
        # --- TIME CHECK: Skip years before 2030 ---
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
# 3. CRMA MINING (10% of Minable Demand) - Starts 2030
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        # --- TIME CHECK: Skip years before 2030 ---
        if stf < 2030:
            return pyomo.Constraint.Skip

        total_mined = sum(m.material_mined[stf, mat] for mat in m.materials)

        relevant_demand = sum(
            m.demand_material_total[stf, mat]
            for mat in m.materials
            if pyomo.value(m.primary_material_availability[stf, mat]) > 1e-6
        )
        return total_mined >= 0.10 * relevant_demand


# ==============================================================================
# 4. CRMA RECYCLING (15% of Recyclable Demand) - Starts 2030
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        # --- TIME CHECK: Skip years before 2030 ---
        if stf < 2030:
            return pyomo.Constraint.Skip

        total_recycled = sum(m.material_recycled[stf, mat] for mat in m.materials)

        relevant_demand = 0
        for mat in m.materials:
            is_recyclable = False
            for t in m.tech:
                # Check if tuple exists in recycling dict
                if (t, mat) in m.recycling_efficiency:
                    if pyomo.value(m.recycling_efficiency[t, mat]) > 0:
                        is_recyclable = True
                        break

            if is_recyclable:
                relevant_demand += m.demand_material_total[stf, mat]

        return total_recycled >= 0.15 * relevant_demand


# ==============================================================================
# APPLICATION LOGIC (No Changes Needed Here, Logic is inside Rules)
# ==============================================================================

def apply_scenario_constraints(m, nzia_mode='strict', crma_active=True):
    """
    Registers scenario constraints with full toggle control.
    Constraints will essentially be "dormant" (Skipped) until 2030.
    """
    print(f"\n--- Initializing Scenario Constraints ---")
    print(f"   Settings: NZIA='{nzia_mode.upper()}', CRMA={crma_active}")
    print("   Note: Targets only active for Years >= 2030.")

    # 1. CREATE ALL CONSTRAINTS (Always created, then toggled)
    # ---------------------------------------------------------

    # NZIA Strict
    strict_logic = nzia_strict_rule()
    m.nzia_strict_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech, m.stages,
        rule=lambda m, y, l, t, s: strict_logic.apply_rule(m, y, l, t, s)
    )

    # NZIA Flex
    flex_logic = nzia_flex_rule()
    m.nzia_flex_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech,
        rule=lambda m, y, l, t: flex_logic.apply_rule(m, y, l, t)
    )

    # CRMA Mining
    extraction_logic = eu_extraction_constraint()
    m.eu_extraction_constraint = pyomo.Constraint(
        m.stf,
        rule=lambda m, y: extraction_logic.apply_rule(m, y)
    )

    # CRMA Recycling
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
        print("❌ NZIA FLEX:   Inactive")

    elif nzia_mode == 'flex':
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.activate()
        print("❌ NZIA STRICT: Inactive")
        print("✅ NZIA FLEX:   Active (>=2030)")

    else:  # 'none' or unknown
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.deactivate()
        print("❌ NZIA:        All targets disabled")

    # 3. TOGGLE CRMA
    # ---------------------------------------------------------
    if crma_active:
        m.eu_extraction_constraint.activate()
        m.eu_recycling_constraint.activate()
        print("✅ CRMA:        Active (>=2030)")
    else:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        print("❌ CRMA:        Disabled")