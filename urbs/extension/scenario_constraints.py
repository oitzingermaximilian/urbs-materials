from abc import ABC, abstractmethod
import pyomo.environ as pyomo


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# ==============================================================================
# 1. NZIA STRICT (Per Stage) - No Loopholes
# ==============================================================================
class nzia_strict_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if tech not in ['SolarPV', 'solarPV']:
            return pyomo.Constraint.Skip

        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage]
        )
        rhs = 0.4 * m.Supply[stf, location, tech, stage]
        return domestic_contribution >= rhs


# ==============================================================================
# 2. NZIA FLEX (Aggregated) - Value Chain Averaging
# ==============================================================================
class nzia_flex_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
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
# 3. CRMA MINING (10% of Minable Demand)
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        total_mined = sum(m.material_mined[stf, mat] for mat in m.materials)

        relevant_demand = sum(
            m.demand_material_total[stf, mat]
            for mat in m.materials
            if pyomo.value(m.primary_material_availability[stf, mat]) > 1e-6
        )
        return total_mined >= 0.10 * relevant_demand


# ==============================================================================
# 4. CRMA RECYCLING (15% of Recyclable Demand)
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        total_recycled = sum(m.material_recycled[stf, mat] for mat in m.materials)

        relevant_demand = 0
        for mat in m.materials:
            is_recyclable = False
            for t in m.tech:
                if (t, mat) in m.recycling_efficiency:
                    if pyomo.value(m.recycling_efficiency[t, mat]) > 0:
                        is_recyclable = True
                        break

            if is_recyclable:
                relevant_demand += m.demand_material_total[stf, mat]

        return total_recycled >= 0.15 * relevant_demand


# ==============================================================================
# APPLICATION LOGIC (WITH FULL CONTROL)
# ==============================================================================

def apply_scenario_constraints(m, nzia_mode='strict', crma_active=True):
    """
    Registers scenario constraints with full toggle control.

    ARGUMENTS:
      m: The model instance.

      nzia_mode (str):
          - 'strict': Forces 40% domestic production for EVERY stage.
          - 'flex':   Forces 40% domestic production on AVERAGE.
          - 'none':   Disables NZIA targets.

      crma_active (bool):
          - True:  Enforces 10% Mining and 15% Recycling targets.
          - False: Disables CRMA targets completely.
    """
    print(f"\n--- Initializing Scenario Constraints ---")
    print(f"   Settings: NZIA='{nzia_mode.upper()}', CRMA={crma_active}")

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
        print("✅ NZIA STRICT: Active")
        print("❌ NZIA FLEX:   Inactive")

    elif nzia_mode == 'flex':
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.activate()
        print("❌ NZIA STRICT: Inactive")
        print("✅ NZIA FLEX:   Active")

    else:  # 'none' or unknown
        m.nzia_strict_constraint.deactivate()
        m.nzia_flex_constraint.deactivate()
        print("❌ NZIA:        All targets disabled")

    # 3. TOGGLE CRMA
    # ---------------------------------------------------------
    if crma_active:
        #m.eu_extraction_constraint.activate()
        m.eu_recycling_constraint.activate()
        print("✅ CRMA:        Active (Mining & Recycling)")
    else:
        m.eu_extraction_constraint.deactivate()
        m.eu_recycling_constraint.deactivate()
        print("❌ CRMA:        Disabled")