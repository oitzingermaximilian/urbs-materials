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

class ProcessingCapacitiesBuildoutRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        start_year = value(m.y0)
        build_time_lag = value(m.build_time[tech, stage])
        cutoff_year = stf - build_time_lag
        processing_init = m.processing_cap_init[stf, location, tech,stage]
        if cutoff_year < start_year:
            new_cap_sum = 0
        else:
            relevant_years = range(start_year, cutoff_year + 1)

            # Use sum() on the generator
            new_cap_sum = sum(
                m.capacity_new_factory[y, location, tech, stage]
                for y in relevant_years
            )

        debug_print(f"Year {stf}: Legacy={processing_init}, New_Active={new_cap_sum}")

        return m.capacity_total_factory[stf, location, tech, stage] == processing_init + new_cap_sum

class ProcessingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return(
            m.capacity_total_factory[stf, location, tech, stage]
            >= m.capacity_produced_output[stf, location, tech, stage]
        )

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
            m.capacity_imorted[stf, location, tech, stage] ==
            m.capacity_imported_flow[stf, location, tech, stage] +
            m.capacity_imported_storage[stf, location, tech, stage]
        )

class StockpileTotalRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        return (
            m.componenets_stockpilestf, location, tech, stage ==
            m.stock_domestic[stf, location, tech, stage] +
            m.stock_imported[stf, location, tech, stage]
        )
class StockpileDomesticRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if stf == value(m.y0):
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
        if stf == value(m.y0):
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

class SequentialProcessingRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if tech not in ['solarPV', 'Batteries']:
            return pyomo.Constraint.Skip
        if stage == 1:
            return pyomo.Constraint.Skip
        prev_stage = stage -1
        lhs = m.capacity_produced_output[stf, location, tech, stage]
        rhs = m.Supply[stf, location, tech, prev_stage]
        return lhs <= rhs

class ParallelAssemblyRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if tech not in ['windon','windoff']:
            return pyomo.Constraint.Skip
        final_stage = m.final_stage[tech]
        if stage == final_stage:
            return pyomo.Constraint.Skip

        lhs = m.capacity_produced_output[stf, location, tech, final_stage]
        rhs = m.Supply[stf, location, tech, stage]
        return lhs <= rhs


class InstallationSupplyLinkRule(AbstractConstraint):
    """
    Implements Eq 7.1: Final Installation = Supply of the Final Stage
    pi_new(y, l, k) = Q_supply(y, l, k, I_max)
    """

    def apply_rule(self, m, stf, location, tech):
        # 1. Retrieve the Final Stage Index for this technology
        # We access the parameter you defined in Option A
        # value() is important if you use the index for logic,
        # but for direct index access, Pyomo handles params automatically.
        # However, to be safe and clean:
        final_stage = value(m.final_stage_idx[tech])

        # 2. The Constraint
        # LHS: The capacity added to the energy system (Macro)
        lhs = m.capacity_ext_new[stf, location, tech]

        # RHS: The available supply of the finished good (Micro)
        rhs = m.Supply[stf, location, tech, final_stage]

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
        lhs = m.material_recycled[stf,material]
        rhs = sum(m.capacity_scrap_rec[stf, location, tech] * m.material_content[tech, material] * m.recycling_efficiency[tech,material]
        for location in m.location
        for tech in m.tech
        if (tech, material) in m.material_content
        )
        return lhs <= rhs

class MiningLimit(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        lhs = m.material_mining[stf, material]
        rhs = m.availability_mining[stf, material]
        return lhs <= rhs


class ElecNeedsProductionRule(AbstractConstraint):
    """
    Implements Eq 16: Calculates Annual Electricity Demand for a Technology
    Demand(y, l, k) = Sum_over_stages( Production(y,l,k,i) * EnergyIntensity(k,i) )
    """

    def apply_rule(self, m, t, stf, location, tech):
        # NOTE: 'stage' is NOT in the arguments.
        # We sum over all stages for this specific technology here.

        # 1. Calculate Total Annual Energy Required (e.g., MWh)
        annual_energy_mwh = sum(
            m.capacity_produced_output[stf, location, tech, stage] * m.energy_needs[tech, stage]
            for stage in m.stages
            # Safety check: ensure parameter exists for this combo
            if (tech, stage) in m.energy_needs
        )

        # 2. Link to the Demand Variable
        # Assuming m.demand_production is indexed [stf, location, tech]

        # If you specifically need Monthly Average Demand, keep the / 12
        # return m.demand_production[stf, location, tech] == annual_energy_mwh / 12

        # Standard Approach (Annual Total):
        return m.demand_production[t, stf, location, tech] == annual_energy_mwh / 12

# CAPEX
class CapexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # Sum over all Locations, Technologies, and Stages
        annual_investment = sum(
            m.capacity_new_factory[stf, location, tech, stage] * m.cost_capex[stf, location, tech, stage]
            for location in m.location
            for tech in m.tech
            for stage in m.stages
            # Safety check if parameter exists (optional depending on your data init)
            if (stf, location, tech, stage) in m.cost_capex
        )

        return m.cost_capex_total_extension[stf] == annual_investment
# OPEX
class OpexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # 1. Manufacturing Variable Costs (Labor, Utilities, O&M)
        # Summing over Location, Tech, Stage
        manufacturing_cost = sum(
            m.capacity_produced_output[stf, location, tech, stage] * m.cost_variable[stf, location, tech, stage]
            + m.cost_scrap[stf, location, tech]
            - m.PRICEREDUCTION_CAP_DEP_INV[stf, location, tech, stage]
            for location in m.location
            for tech in m.tech
            for stage in m.stages
            if (stf, location, tech, stage) in m.cost_variable
        )

        # 2. Raw Material Mining Costs
        # Summing over Materials (Global or Sum of Locations depending on your MiningLimit def)
        # Based on your MiningLimit rule, m.material_mining is indexed by [stf, material]
        mining_cost = sum(
            m.material_mining[stf, material] * m.cost_mining[stf, material]
            for material in m.materials
            if (stf, material) in m.cost_mining
        )

        return m.cost_opex_total_extension[stf] == manufacturing_cost + mining_cost
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


def apply_material_constraints(m):
    """
    Registers all constraints with the Pyomo model, grouped by their index requirements.
    """

    # ---------------------------------------------------------
    # GROUP 1: Full Detail Constraints
    # Indices: (stf, location, tech, stage)
    # ---------------------------------------------------------
    stage_constraints = [
        ProcessingCapacitiesBuildoutRule(),
        ProcessingCapacitiesOutputLimitRule(),
        CapacityProducedOutputCompositionRule(),
        CapacityImportedCompositionRule(),
        StockpileTotalRule(),
        StockpileDomesticRule(),
        StockpileImportedRule(),
        MaximumStockpileImportsRule(),
        SupplyCompositionRule(),
        SequentialProcessingRule(),
        ParallelAssemblyRule(),
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
            m.t, m.stf, m.location, m.tech,
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
    ]

    for constraint_obj in global_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf,
            rule=lambda m, y: constraint_obj.apply_rule(m, y)
        ))

    print("All stockpiling and manufacturing constraints registered successfully.")
