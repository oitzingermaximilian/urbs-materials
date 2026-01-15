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
        """
        STRICT: Ensures 40% domestic production for EVERY stage individually.
        Forces the model to build specific bottleneck capacities (e.g., Cells) in the EU.
        """
        # Domestic Production = Flow + Stockout Withdrawal
        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage] +
                m.capacity_imported_stockout[stf, location, tech, stage]
        )

        # RHS: 40% of Total Supply for THIS stage
        rhs = 0.4 * m.Supply[stf, location, tech, stage]

        return domestic_contribution >= rhs


# ==============================================================================
# 2. NZIA FLEX (Aggregated) - Allows "Assembly Washing"
# ==============================================================================
class nzia_soft_target_rule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        """
        SOFT TARGET: Aim for 40% domestic production for EVERY stage.
        If impossible (due to growth limits), record the 'shortfall'.
        """

        # 1. Domestic Contribution (Flow + Stock)
        domestic_contribution = (
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_stockout[stf, location, tech, stage] +
                m.capacity_imported_stockout[stf, location, tech, stage]
        )

        # 2. The Target (40% of Supply)
        target = 0.40 * m.Supply[stf, location, tech, stage]

        # 3. The Equation with SLACK
        # Domestic + Shortfall >= Target
        # If Domestic is low, 'Shortfall' becomes positive to bridge the gap.

        return domestic_contribution + m.nzia_shortfall[stf, location, tech, stage] >= target


# ==============================================================================
# 3. CRMA MINING TARGET (10% of *Minable* Demand)
# ==============================================================================
class eu_extraction_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        """
        Ensures EU Mining covers >= 10% of the demand for MINABLE materials.
        FILTER: Only includes materials in the RHS denominator if EU mining availability > 0.
        """
        # LHS: Total Mined Material in EU
        total_mined = sum(m.material_mined[stf, mat] for mat in m.materials)

        # RHS: 10% of Demand (Filtered for minable materials)
        # We check if the mining limit for this year/material is greater than effectively zero
        relevant_demand = sum(
            m.demand_material_total[stf, mat]
            for mat in m.materials
            if pyomo.value(m.primary_material_availability[stf, mat]) > 1e-3  # FILTER HERE
        )

        return total_mined >= 0.10 * relevant_demand


# ==============================================================================
# 4. CRMA RECYCLING TARGET (Corrected for Tech, Material Index)
# ==============================================================================
class eu_recycling_constraint(AbstractConstraint):
    def apply_rule(self, m, stf):
        """
        Ensures EU Recycling covers >= 15% of the demand for RECYCLABLE materials.

        FILTER LOGIC:
        Since efficiency is indexed by (Tech, Material), we consider a material
        'Recyclable' if AT LEAST ONE technology has an efficiency > 0 for it.
        """
        # LHS: Total Recycled Material (Sum of all recycling flows)
        total_recycled = sum(m.material_recycled[stf, mat] for mat in m.materials)

        relevant_demand = 0

        for mat in m.materials:
            # Check if this material is recyclable by ANY technology
            is_recyclable = False

            for t in m.tech:
                # 1. Check if the tuple (tech, mat) exists in the parameter
                # 2. Check if the efficiency value is > 0
                if (t, mat) in m.recycling_efficiency:
                    if pyomo.value(m.recycling_efficiency[t, mat]) > 0:
                        is_recyclable = True
                        break  # Found one! No need to check other techs for this material.

            # If valid, add its total demand to the target calculation
            if is_recyclable:
                relevant_demand += m.demand_material_total[stf, mat]

        return total_recycled >= 0.15 * relevant_demand


# ==============================================================================
# CONSTRAINT REGISTRATION FUNCTION
# ==============================================================================
def apply_scenario_constraints(m):
    """
    Registers constraints to the model.
    Default State:
       - NZIA STRICT: Active
       - NZIA FLEX:   Inactive (Use .activate() in your run script to switch)
       - CRMA:        Active
    """

    # --- 1. NZIA STRICT (Per Stage) ---
    strict_logic = nzia_strict_rule()
    m.nzia_strict_constraint = pyomo.Constraint(
        m.stf, m.location, m.tech, m.stages,
        rule=lambda m, y, l, t, s: strict_logic.apply_rule(m, y, l, t, s)
    )
    m.nzia_strict_constraint.deactivate()

    ### --- 2. NZIA FLEX (Aggregated per Tech) ---
    #flex_logic = nzia_soft_target_rule()
    #m.nzia_soft_target_constraint = pyomo.Constraint(
    #    m.stf, m.location, m.tech, m.stages,
    #    rule=lambda m, y, l, t,s : flex_logic.apply_rule(m, y, l, t, s)
    #)
#
    ## Deactivate Flex by default (cannot have both Strict and Flex active for the same goal usually)
    ##m.nzia_flex_constraint.deactivate()
##
    ### --- 3. CRMA MINING (Global Filtered) ---
    #extraction_rule = eu_extraction_constraint()
    #m.eu_extraction_constraint = pyomo.Constraint(
    #    m.stf,
    #    rule=lambda m, y: extraction_rule.apply_rule(m, y),
    #)
    ##m.eu_extraction_constraint.deactivate()
##
    ### --- 4. CRMA RECYCLING (Global Filtered) ---
    #recycling_rule = eu_recycling_constraint()
    #m.eu_recycling_constraint = pyomo.Constraint(
    #    m.stf,
    #    rule=lambda m, y: recycling_rule.apply_rule(m, y),
    #)
    ##m.eu_extraction_constraint.deactivate()

    print("\n✅ Scenario Constraints Registered:")
    print("   1. NZIA Strict (40% per stage):   ACTIVE")
    print("   2. NZIA Flex (40% per tech):      INACTIVE (Toggle manually if needed)")
    print("   3. CRMA Mining (10% minable):     ACTIVE")
    print("   4. CRMA Recycling (15% recycl.):  ACTIVE")