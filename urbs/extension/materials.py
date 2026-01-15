from abc import ABC, abstractmethod

import pyomo.core as pyomo
from pyomo.environ import value


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, stf, location, tech, stage):
        pass


DEBUG = False  # Set to False to disable all debug prints


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

#################################################################################
# GROWTH CONSTRAINTS FOR PROCESSING AND SCRAP-PROCESSING
#################################################################################

class ProcessingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return(
            m.capacity_processing_total[stf, location, tech, stage]
            >= m.capacity_produced_output[stf, location, tech, stage]
        )

class ProcessingCapacitiesSizeRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        lhs = m.capacity_processing_total[stf, location, tech, stage]
        rhs = m.processing_cap_init[location, tech, stage] + sum(m.processing_cap_new[y, location, tech, stage] for y in m.stf if y <= stf)
        return lhs == rhs

class ProcessingCapacityGrowthLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if stf == 2024:
            if tech in ["solarPV", "Batteries"]:
                max_capacity = 2500  # 2.5 GW limit for renewable technologies
            else:
                max_capacity = 1500  # 1.5 GW limit for other technologies
            return m.processing_cap_new[stf, location, tech, stage] <= max_capacity
        else:
            lhs =(
                m.processing_cap_new[stf, location, tech, stage]
                - m.processing_cap_new[stf-1, location, tech, stage]
            )
            rhs =(
                m.processing_delta_grow[location, tech, stage]
                + m.processing_avg_growth[location, tech, stage]
                *m.processing_cap_new[stf-1, location, tech, stage]
            )
            return lhs <= rhs

#--------------------------------------------------------------------------------#
class ScrapHandlingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        return(
            m.capacity_scrap_handling_total[stf, location, tech]
            >= m.capacity_scrap_rec[stf, location, tech]
        )

class ScrapHandlingCapacitiesSizeRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lhs = m.capacity_scrap_handling_total[stf, location, tech]
        rhs = m.capacity_scrap_handling_init[location, tech] + sum(m.scraphandling_cap_new[y, location, tech] for y in m.stf if y <= stf)
        return lhs == rhs

class ScrapHandlingCapacityGrowthLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        if stf == 2024:
            if tech in ["solarPV", "Batteries"]:
                max_capacity = 15000  # 2.5 GW limit for renewable technologies
            else:
                max_capacity = 25000  # 1.5 GW limit for other technologies
            return m.scraphandling_cap_new[stf, location, tech] <= max_capacity
        else:
            lhs =(
                m.scraphandling_cap_new[stf, location, tech]
                - m.scraphandling_cap_new[stf-1, location, tech]
            )
            rhs =(
                m.scraphandling_delta_grow[location, tech]
                + m.scraphandling_avg_growth[location, tech]
                *m.scraphandling_cap_new[stf-1, location, tech]
            )
            return lhs <= rhs

##################################################################################

class CapacityProducedOutputCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return(
            m.capacity_produced_output[stf, location, tech, stage] ==
            m.capacity_produced_flow[stf, location, tech, stage] +
            m.capacity_produced_storage[stf, location, tech, stage]
        )

class CapacityImportedCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return(
            m.capacity_imported[stf, location, tech, stage] ==
            m.capacity_imported_flow[stf, location, tech, stage] +
            m.capacity_imported_storage[stf, location, tech, stage]
        )

class StockpileTotalRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return (
            m.components_stockpile[stf, location, tech, stage] ==
            m.stock_domestic[stf, location, tech, stage] +
            m.stock_imported[stf, location, tech, stage]
        )
class StockpileDomesticRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if stf == 2024:
            return (
                    m.stock_domestic[stf, location, tech, stage] ==
                    m.stock_domestic_init[location, tech, stage] +
                    m.capacity_produced_storage[stf, location, tech, stage] -
                    m.capacity_produced_stockout[stf, location, tech, stage]
            )
        else:
            return (
                    m.stock_domestic[stf, location, tech, stage] ==
                    m.stock_domestic[stf-1,location, tech, stage] +
                    m.capacity_produced_storage[stf, location, tech, stage] -
                    m.capacity_produced_stockout[stf, location, tech, stage]
            )

class StockpileImportedRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if stf == 2024:
            return (
                    m.stock_imported[stf, location, tech, stage] ==
                    m.stock_imported_init[location, tech, stage] +
                    m.capacity_imported_storage[stf, location, tech, stage] -
                    m.capacity_imported_stockout[stf, location, tech, stage]
            )
        else:
            return (
                    m.stock_imported[stf, location, tech, stage] ==
                    m.stock_imported[stf-1,location, tech, stage] +
                    m.capacity_imported_storage[stf, location, tech, stage] -
                    m.capacity_imported_stockout[stf, location, tech, stage]
            )

class MaximumStockpileImportsRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        lhs = m.capacity_imported_storage[stf,location, tech, stage]
        rhs = 0.5 * m.capacity_imported[stf, location, tech, stage]
        return lhs <= rhs



class SupplyCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return(
                m.Supply[stf, location, tech, stage] ==
                (m.capacity_produced_flow[stf, location, tech, stage] + m.capacity_produced_stockout[stf, location, tech, stage])+
                (m.capacity_imported_flow[stf,location,tech,stage]+ m.capacity_imported_stockout[stf,location,tech,stage])
        )


class ComponentBalanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, input_tech, input_stage):
        supply = m.Supply[stf, location, input_tech, input_stage]

        demand = sum(
            m.capacity_produced_output[stf, location, consumer_tech, consumer_stage]
            * m.bom_map[consumer_tech, consumer_stage, input_tech, input_stage]  # <--- UPDATED NAME

            for consumer_tech in m.tech
            for consumer_stage in m.stages
            # Check against the new name:
            if (consumer_tech, consumer_stage, input_tech, input_stage) in m.bom_map
        )

        return supply >= demand


class InstallationSupplyLinkRule(AbstractConstraint):
    """
    Links the Manufacturing Model to the Energy Model.
    Capacity Added (MW) == Supply of Final Stage (MW)
    """
    def apply_rule(self, m, stf, location, tech):
        # 1. Retrieve the Final Stage Name
        # We wrap this in a try-block in case the parameter is missing or empty
        try:
            final_stage = value(m.final_stage[tech])
        except (ValueError, KeyError):
            print(f"⚠️ SKIPPING {tech}: No final_stage_idx defined!")
            return pyomo.Constraint.Skip

        # 2. Define the sides of the equation
        lhs = m.capacity_ext_new[stf, location, tech] # Or m.capacity_ext_new depending on your var name
        rhs = m.Supply[stf, location, tech, final_stage]

        # --- DEBUG PRINT ---
        # This will print once for every (stf, location, tech) combo during model build
        #print(f"LINKING: {tech} (Loc: {location})")
        #print(f"   -> Final Stage Identified: '{final_stage}'")
        #print(f"   -> Constraint: {lhs.name} == {rhs.name}")
        #print("-" * 30)
        # -------------------

        return lhs == rhs


# Materials

class ProcessingOutputMaterialRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        # We sum over all locations, technologies, and stages
        # that actually consume this material.

        total_demand = sum(
            m.capacity_produced_output[stf, location, tech, stage] * m.material_intensity[tech, stage, material]

            for location in m.location
            for tech in m.tech
            for stage in m.stages
            # Check if this specific combo uses the material to avoid KeyErrors
            if (tech, stage, material) in m.material_intensity
        )

        return m.demand_material_total[stf, material] == total_demand

class MaterialDemandBalanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        return(
            m.demand_material_total[stf, material] == m.material_imported[stf,material] + m.material_mined[stf,material] + m.material_recycled[stf,material]
        )


class ScrapMaterialLinkageRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        # LHS: Total Pure Material Recovered (e.g., Tons of Copper)
        lhs = m.material_recycled[stf, material]

        # RHS: Sum of (Scrap Mass Processed * Material Content % * Efficiency)
        # Unit check: [Tons Scrap] * [Tons Mat / Tons Scrap] * [%] = [Tons Mat]
        rhs = sum(
            m.capacity_scrap_rec[stf, location, tech]
            * ( m.scrap_content[tech, material] / m.f_scrap[location, tech])  # <--- Ensure this matches your data index!
            * m.recycling_efficiency[tech, material]

            for location in m.location
            for tech in m.tech
            if (tech, material) in m.scrap_content
        )

        # Use Equality (==) to define the conversion strictly
        return lhs == rhs

class MiningLimit(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        # LHS: Actual Metal Mined
        lhs = m.material_mined[stf, material]
        rhs = m.primary_material_availability[stf, material]
        return lhs <= rhs

class LimitResourceExistanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        # Get the previous time step

        if stf == 2024:
            # Initial condition: First year reserves = Total Initial - Mined this year
            return m.remaining_reserves[stf, material] == \
                m.initial_total_reserves[material] - m.material_mined[stf, material]
        else:
            # Recursive step: Current = Previous - Mined this year
            return m.remaining_reserves[stf, material] == \
                m.remaining_reserves[stf-1, material] - m.material_mined[stf, material]

class ElecNeedsProductionRule(AbstractConstraint):
    """
    Implements Eq 16: Calculates Annual Electricity Demand for a Technology
    Demand(y, l, k) = Sum_over_stages( Production(y,l,k,i) * EnergyIntensity(k,i) )
    """

    def apply_rule(self, m, tm, stf, location, tech):
        # NOTE: 'stage' is NOT in the arguments.
        # We sum over all stages for this specific technology here.

        # 1. Calculate Total Annual Energy Required (e.g., MWh)
        annual_energy_mwh = sum(
            m.energy_needs[location, tech, stage] * m.capacity_produced_output[stf, location, tech, stage] #* m.auxiliary_product_BD_q[stf, location, tech, stage, n] * m.P_sec_relative[n]
            #for n in m.nsteps_sec
            # <--- Use 3 keys here
            for stage in m.stages
            # Check for the 3-item tuple:
            if (location, tech, stage) in m.energy_needs
        )

        # 2. Build the constraint expression and print it
        expr = m.demand_production[tm, stf, location, tech] == annual_energy_mwh / 12
        #print(f"ElecNeedsProductionRule constraint for (t={tm}, stf={stf}, loc={location}, tech={tech}): {expr}")
        return expr

# CAPEX
class CapexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # Calculate gross cost and subtract the total calculated savings
        annual_investment = sum(
            (m.processing_cap_new[stf, loc, tech, stage] * m.cost_capex[stf, loc, tech, stage])
            - m.PRICEREDUCTION_CAP_DEP_INV[stf, loc, tech, stage]
            for loc in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, loc, tech, stage) in m.cost_capex
        )

        return m.cost_capex_total_extension[stf] == annual_investment
# OPEX
class OpexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # --- A. Manufacturing Costs ---

        # 1. Fixed Costs (Applied to Installed Capacity)
        # Unit: [MW_capacity] * [EUR/MW/yr]
        manufacturing_fixed = sum(
            m.capacity_processing_total[stf, location, tech, stage]
            * m.cost_fixed[stf, location, tech, stage]

            for location in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, location, tech, stage) in m.cost_fixed
        )

        # 2. Variable Costs (Applied to Production Output)
        # Unit: [MW_output] * [EUR/MW_output]
        # Note: 'cost_variable' should include Labor + Materials (Consumables).
        # Electricity is usually excluded here if modeled as physical demand elsewhere.
        manufacturing_variable = sum(
            m.capacity_produced_output[stf, location, tech, stage]
            * m.cost_variable[stf, location, tech, stage]

            for location in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, location, tech, stage) in m.cost_variable
        )
        # 3. Scrap & Recycling Adjustments (If applicable)
        scrap_costs = sum(
            m.cost_scrap[stf, location, tech]

            for location in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, location, tech) in m.cost_scrap
        )

        # --- B. Mining Costs (Virgin Material Extraction) ---
        mining_cost = sum(
            m.material_mined[stf, material] * m.cost_mining[stf, material]
            for material in m.materials
            if (stf, material) in m.cost_mining
        )

        penalty_cost = sum(m.nzia_shortfall[stf, location, tech, stage] * 500_000_000
                          for location in m.location
                           for tech in m.tech
                           for stage in m.stages)

        # --- Total Equation ---
        return m.cost_opex_total_extension[stf] == (
                manufacturing_fixed +
                manufacturing_variable +
                scrap_costs +
                mining_cost
                +penalty_cost
        )
# Trade&Storage
class TradeCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # 1. Component Imports (e.g., Solar Cells, Wafers)
        component_import_cost = sum(
            m.capacity_imported[stf, location, tech, stage] * m.cost_import_part[stf, location, tech, stage]
            for location in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, location, tech, stage) in m.cost_import_part
        )

        # 2. Raw Material Imports (e.g., Lithium, Silicon)
        # Assuming m.material_imported is indexed [stf, material] per your Balance Rule
        material_import_cost = sum(
            m.material_imported[stf, material] * m.cost_import_material[stf, material]
            for material in m.materials
            if (stf, material) in m.cost_import_material
        )

        return m.cost_trade_total_extension[stf] == component_import_cost + material_import_cost


class StockpileHoldingCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # --- DUMMY COST PARAMETER ---
        # Set this high enough to be noticeable, but not infinite.
        # e.g., 5-10% of your production cost.
        # If your production cost is ~100, try 10.
        HOLDING_COST_PER_UNIT = 10

        # Sum of all items currently sitting in stock
        total_holding_cost = sum(
            (m.stock_domestic[stf, location, tech, stage] +
             m.stock_imported[stf, location, tech, stage])
            * HOLDING_COST_PER_UNIT

            for location in m.location
            for tech in m.tech
            for stage in m.stages
        )

        return m.cost_stockpile_holding[stf] == total_holding_cost
def apply_material_constraints(m):
    """
    Registers all constraints with the Pyomo model, grouped by their index requirements.
    """
    scrap_growth_constraints = [
        ScrapHandlingCapacitiesSizeRule(),
        ScrapHandlingCapacityGrowthLimitRule(),
        ScrapHandlingCapacitiesOutputLimitRule(),
    ]

    for constraint_obj in scrap_growth_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech,
            rule=lambda m, y, l, k: constraint_obj.apply_rule(m, y, l, k)
        ))
    # ---------------------------------------------------------
    # GROUP 1: Full Detail Constraints
    # Indices: (stf, location, tech, stage)
    # ---------------------------------------------------------
    stage_constraints = [
        ProcessingCapacitiesSizeRule(),
        ProcessingCapacityGrowthLimitRule(),
        ProcessingCapacitiesOutputLimitRule(),
        CapacityProducedOutputCompositionRule(),
        CapacityImportedCompositionRule(),
        StockpileTotalRule(),
        StockpileDomesticRule(),
        StockpileImportedRule(),
        MaximumStockpileImportsRule(),
        SupplyCompositionRule(),
        ComponentBalanceRule(),

    ]

    for constraint_obj in stage_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech, m.stages,
            rule=lambda m, y, l, k, i: constraint_obj.apply_rule(m, y, l, k, i)
        ))

    # ---------------------------------------------------------
    # GROUP 2: Technology Aggregate Constraints
    # Indices: (stf, location, tech)
    # ---------------------------------------------------------
    tech_constraints = [
        InstallationSupplyLinkRule(),
    ]

    for constraint_obj in tech_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech,
            rule=lambda m, y, l, k: constraint_obj.apply_rule(m, y, l, k)
        ))

    # ---------------------------------------------------------
    # GROUP 3: High-Resolution Time Constraints
    # Indices: (t, stf, location, tech)
    # NOTE: Checks your ElecNeedsProductionRule which uses 't'
    # ---------------------------------------------------------
    high_res_constraints = [
        ElecNeedsProductionRule(),
    ]

    for constraint_obj in high_res_constraints:
        name = constraint_obj.__class__.__name__
        # Assuming 'm.t' is your time-step set (e.g., months or hours)
        setattr(m, name, pyomo.Constraint(
            m.timesteps_ext, m.stf, m.location, m.tech,
            rule=lambda m, t, y, l, k: constraint_obj.apply_rule(m, t, y, l, k)
        ))

    # ---------------------------------------------------------
    # GROUP 4: Material Constraints
    # Indices: (stf, material)
    # ---------------------------------------------------------
    material_constraints = [
        ProcessingOutputMaterialRule(),
        MaterialDemandBalanceRule(),
        ScrapMaterialLinkageRule(),
        MiningLimit(),
        LimitResourceExistanceRule(),
    ]

    for constraint_obj in material_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.materials,
            rule=lambda m, y, mat: constraint_obj.apply_rule(m, y, mat)
        ))

    # ---------------------------------------------------------
    # GROUP 5: Global / Cost Constraints
    # Indices: (stf)
    # ---------------------------------------------------------
    global_constraints = [
        CapexCostRule(),
        OpexCostRule(),
        TradeCostRule(),
        StockpileHoldingCostRule()
    ]

    for constraint_obj in global_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf,
            rule=lambda m, y: constraint_obj.apply_rule(m, y)
        ))

    print("All stockpiling and manufacturing constraints registered successfully.")
