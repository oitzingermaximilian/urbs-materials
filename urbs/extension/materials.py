from abc import ABC, abstractmethod
import pyomo.core as pyomo
from pyomo.environ import value


class AbstractConstraint(ABC):
    @abstractmethod
    def apply_rule(self, m, *args):
        pass


# --- Helper to handle "All Combination" iteration safely ---
def check_valid_indices(m, tech, stage):
    """
    Returns True if the (tech, stage) pair is valid in the model sets.
    Used to safely skip invalid combinations when iterating over the full dense set.
    """
    return (tech, stage) in m.tech_stage_combinations


#################################################################################
# GROWTH CONSTRAINTS FOR PROCESSING AND SCRAP-PROCESSING
#################################################################################

class ProcessingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return (
                m.capacity_processing_total[stf, location, tech, stage]
                >= m.capacity_produced_output[stf, location, tech, stage]
        )


class ProcessingCapacitiesSizeRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        lhs = m.capacity_processing_total[stf, location, tech, stage]
        rhs = m.processing_cap_init[location, tech, stage] + \
              sum(m.processing_cap_new[y, location, tech, stage] for y in m.stf if y <= stf)
        return lhs == rhs


class ProcessingCapacityGrowthLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        # SCALING NOTE: Values are in GW (k-Universe)
        if stf == 2024:
            if tech in ["solarPV", "Batteries"]:
                max_capacity = 2.5
            else:
                max_capacity = 1.5
            return m.processing_cap_new[stf, location, tech, stage] <= max_capacity
        else:
            lhs = (m.processing_cap_new[stf, location, tech, stage] -
                   m.processing_cap_new[stf - 1, location, tech, stage])
            rhs = (m.processing_delta_grow[location, tech, stage] +
                   m.processing_avg_growth[location, tech, stage] * m.processing_cap_new[
                       stf - 1, location, tech, stage])
            return lhs <= rhs


# --- Scrap Handling Rules ---

class ScrapHandlingCapacitiesOutputLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        return m.capacity_scrap_handling_total[stf, location, tech] >= m.capacity_scrap_rec[stf, location, tech]


class ScrapHandlingCapacitiesSizeRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        lhs = m.capacity_scrap_handling_total[stf, location, tech]
        rhs = m.capacity_scrap_handling_init[location, tech] + sum(
            m.scraphandling_cap_new[y, location, tech] for y in m.stf if y <= stf)
        return lhs == rhs


class ScrapHandlingCapacityGrowthLimitRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # SCALING NOTE: Values in kton (k-Universe)
        if stf == 2024:
            max_capacity = 15.0 if tech in ["solarPV", "Batteries"] else 25.0
            return m.scraphandling_cap_new[stf, location, tech] <= max_capacity
        else:
            lhs = (m.scraphandling_cap_new[stf, location, tech] - m.scraphandling_cap_new[stf - 1, location, tech])
            rhs = (m.scraphandling_delta_grow[location, tech] + m.scraphandling_avg_growth[location, tech] *
                   m.scraphandling_cap_new[stf - 1, location, tech])
            return lhs <= rhs


##################################################################################
# COMPOSITION & STOCK RULES
##################################################################################

class CapacityProducedOutputCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return (m.capacity_produced_output[stf, location, tech, stage] ==
                m.capacity_produced_flow[stf, location, tech, stage] +
                m.capacity_produced_storage[stf, location, tech, stage])


class CapacityImportedCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return (m.capacity_imported[stf, location, tech, stage] ==
                m.capacity_imported_flow[stf, location, tech, stage] +
                m.capacity_imported_storage[stf, location, tech, stage])


class StockpileTotalRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return (m.components_stockpile[stf, location, tech, stage] ==
                m.stock_domestic[stf, location, tech, stage] +
                m.stock_imported[stf, location, tech, stage])


obsolescence_factor = 0.041


class StockpileDomesticRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        if stf == 2024:
            return (m.stock_domestic[stf, location, tech, stage] ==
                    m.stock_domestic_init[location, tech, stage] +
                    m.capacity_produced_storage[stf, location, tech, stage] -
                    m.capacity_produced_stockout[stf, location, tech, stage])
        else:
            return (m.stock_domestic[stf, location, tech, stage] ==
                    m.stock_domestic[stf - 1, location, tech, stage] * (1 - obsolescence_factor) +
                    m.capacity_produced_storage[stf, location, tech, stage] -
                    m.capacity_produced_stockout[stf, location, tech, stage])


class StockpileImportedRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        if stf == 2024:
            return (m.stock_imported[stf, location, tech, stage] ==
                    m.stock_imported_init[location, tech, stage] +
                    m.capacity_imported_storage[stf, location, tech, stage] -
                    m.capacity_imported_stockout[stf, location, tech, stage])
        else:
            return (m.stock_imported[stf, location, tech, stage] ==
                    m.stock_imported[stf - 1, location, tech, stage] * (1 - obsolescence_factor) +
                    m.capacity_imported_storage[stf, location, tech, stage] -
                    m.capacity_imported_stockout[stf, location, tech, stage])


class MaximumStockpileImportsRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return m.capacity_imported_storage[stf, location, tech, stage] <= 0.25 * m.capacity_imported[
            stf, location, tech, stage]


class MaximumStockpileDomesticRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        return m.capacity_produced_storage[stf, location, tech, stage] <= 0.25 * m.capacity_produced_output[
            stf, location, tech, stage]


class TurnoverStockImportsNewRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        valid_years = [2025, 2030, 2035, 2040, 2045]
        if stf not in valid_years:
            return pyomo.Constraint.Skip

        step_size = 5
        lhs = sum(m.capacity_imported_stockout[j, location, tech, stage]
                  for j in range(stf, stf + step_size)
                  if (j, location, tech, stage) in m.capacity_imported_stockout)

        rhs = (1 * (1 / step_size) * sum(m.stock_imported[j, location, tech, stage]
                                         for j in range(stf, stf + step_size)
                                         if (j, location, tech, stage) in m.stock_imported))
        return lhs >= rhs


class TurnoverStockDomesticNewRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        valid_years = [2025, 2030, 2035, 2040, 2045]
        if stf not in valid_years:
            return pyomo.Constraint.Skip

        step_size = 2
        lhs = sum(m.capacity_produced_stockout[j, location, tech, stage]
                  for j in range(stf, stf + step_size)
                  if (j, location, tech, stage) in m.capacity_produced_stockout)

        rhs = (1 * (1 / step_size) * sum(m.stock_domestic[j, location, tech, stage]
                                         for j in range(stf, stf + step_size)
                                         if (j, location, tech, stage) in m.stock_domestic))
        return lhs >= rhs


class SupplyCompositionRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        if not check_valid_indices(m, tech, stage): return pyomo.Constraint.Skip

        # CON: Supply Definition | Aggregates flow and stockout variables into total Supply
        return (m.Supply[stf, location, tech, stage] ==
                (m.capacity_produced_flow[stf, location, tech, stage] + m.capacity_produced_stockout[
                    stf, location, tech, stage]) +
                (m.capacity_imported_flow[stf, location, tech, stage] + m.capacity_imported_stockout[
                    stf, location, tech, stage]))


class ComponentBalanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, input_tech, input_stage):
        # NOTE: Supply exists for (input_tech, input_stage) which we assume is valid since it's passed here.
        # But we need to make sure we don't crash if it's invalid.
        if not check_valid_indices(m, input_tech, input_stage): return pyomo.Constraint.Skip

        supply = m.Supply[stf, location, input_tech, input_stage]

        # ROBUST SUMMATION: Iterate over the BOM MAP directly
        # This catches any consumer that is defined in the data, even if sets are wonky.
        demand = sum(
            m.capacity_produced_output[stf, location, consumer_tech, consumer_stage] * val

            for (consumer_tech, consumer_stage, i_tech, i_stage), val in m.bom_map.items()
            if i_tech == input_tech and i_stage == input_stage
            # Safety: ensure consumer is valid in the model variables
            if check_valid_indices(m, consumer_tech, consumer_stage)
        )
        return supply >= demand


class InstallationSupplyLinkRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        # 1. Retrieve the defined Final Stage for this tech
        try:
            # We assume m.final_stage uses the same casing as m.tech
            # If m.final_stage has 'SolarPV' but tech is 'solarPV', this lookup fails.

            # FAST FIX: Try direct lookup, then try case-insensitive fallback
            if tech in m.final_stage:
                final_s = value(m.final_stage[tech])
            else:
                # Fallback: Look for a key that matches case-insensitively
                # This is slow but safe for debugging
                found = False
                for k in m.final_stage:
                    if str(k).lower() == str(tech).lower():
                        final_s = value(m.final_stage[k])
                        found = True
                        break
                if not found:
                    return pyomo.Constraint.Skip

        except (ValueError, KeyError):
            return pyomo.Constraint.Skip

        # 2. Safety Check (The previous point of failure)
        # Instead of skipping silently if indices look wrong, we FORCE the constraint
        # if the variables exist.

        # Check if Supply variable exists for this (tech, final_s) combo
        # We assume 'EU27' and 2030 exist to test the key
        if (stf, location, tech, final_s) not in m.Supply:
            # OPTIONAL: Print warning only once
            if stf == 2030 and location == 'EU27':
                print(f"🚨 LINK BROKEN: Supply variable missing for {tech} - {final_s}")
            return pyomo.Constraint.Skip

        # 3. The Link Constraint
        # Installation (GW) == Supply of Final Stage (GW)
        return m.capacity_ext_new[stf, location, tech] == m.Supply[stf, location, tech, final_s]


class NewlyAddedBalanceLCOE(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        return m.balance_yearly_new_capacity[stf, location, tech] == sum(
            m.capacity_ext_new[stf, location, tech] * m.lf_solar[t, stf, location, tech] * m.hours[t]
            for t in m.timesteps_ext
        )


##################################################################################
# MATERIAL & ENERGY RULES
##################################################################################

class ProcessingOutputMaterialRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        # ROBUST SUMMATION: Iterate over the INTENSITY DICT directly.
        # This catches any intensity defined in Excel, ignoring set filters.

        # 1. Grab all valid (Tech, Stage) pairs for THIS material from the intensity dict
        relevant_keys = [
            (t, s, val) for (t, s, mat), val in m.material_intensity.items()
            if mat == material
        ]

        if not relevant_keys:
            return m.demand_material_total[stf, material] == 0

        total_demand = sum(
            m.capacity_produced_output[stf, location, t, s] * val

            for (t, s, val) in relevant_keys
            for location in m.location
            # Safety: Ensure variable exists before accessing
            if check_valid_indices(m, t, s)
        )

        return m.demand_material_total[stf, material] == total_demand


class MaterialDemandBalanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        return (m.demand_material_total[stf, material] ==
                m.material_imported[stf, material] +
                m.material_mined[stf, material] +
                m.material_recycled[stf, material])


class ScrapMaterialLinkageRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        lhs = m.material_recycled[stf, material]
        rhs = sum(
            m.capacity_scrap_rec[stf, location, tech] * (m.scrap_content[tech, material] / m.f_scrap[location, tech]) *
            m.recycling_efficiency[tech, material]
            for location in m.location
            for tech in m.tech
            if (tech, material) in m.scrap_content and m.f_scrap[location, tech] > 0
        )
        return lhs == rhs


class MiningLimit(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        lhs = m.material_mined[stf, material]
        rhs = (m.primary_material_availability[stf, material] * m.mining_energy_transission_share[stf, material] /
               m.mining_conversion_factor[stf, material])
        return lhs <= rhs


class LimitResourceExistanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        total_allowable_metal_stock = (
                m.initial_total_reserves[material]
                * m.mining_energy_transission_share[stf, material]
                * m.mining_conversion_factor[stf, material]
        )
        cumulative_mined = sum(m.material_mined[year, material] for year in m.stf if year <= stf)
        return m.remaining_reserves[stf, material] == total_allowable_metal_stock - cumulative_mined


class FactoryEnergyAnnualRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):
        total_gwh = sum(
            m.energy_needs[location, tech, stage] * m.capacity_produced_output[stf, location, tech, stage]
            for stage in m.stages
            if (location, tech, stage) in m.energy_needs
            # Safety check
            if check_valid_indices(m, tech, stage)
        )
        return m.FACTORY_ENERGY_ANNUAL[stf, location, tech] == total_gwh


class ElecNeedsProductionRule(AbstractConstraint):
    def apply_rule(self, m, tm, stf, location, tech):
        return m.demand_production[tm, stf, location, tech] == m.FACTORY_ENERGY_ANNUAL[stf, location, tech] / 12


##################################################################################
# GLOBAL COST RULES (k-Universe: k€)
##################################################################################

class CapexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j, i, n = 0.03, 0.071, 25
        stf_min, stf_end = min(m.stf), max(m.stf)
        f_inv = ((1 + j) ** (1 - (stf - stf_min)) * (i * (1 + i) ** n * ((1 + j) ** n - 1)) / (
                j * (1 + j) ** n * ((1 + i) ** n - 1)))
        op_time = (stf + n) - stf_end - 1
        f_over = 0
        if op_time > 0:
            f_over = ((1 + j) ** (1 - (stf - stf_min)) * (i * (1 + i) ** n * ((1 + j) ** op_time - 1)) / (
                    j * (1 + j) ** n * ((1 + i) ** n - 1)))

        gross = sum(
            m.processing_cap_new[stf, loc, tech, stage] * m.cost_capex[stf, loc, tech, stage] * (f_inv - f_over)
            for loc in m.location for (tech, stage) in m.tech_stage_combinations
        )

        savings = 0
        if hasattr(m, 'PRICEREDUCTION_ONETECH_TOTAL'):
            savings = sum(
                m.PRICEREDUCTION_ONETECH_TOTAL[stf, loc, tech, stage] * (f_inv - f_over)
                for loc in m.location
                for (tech, stage) in m.tech_stage_combinations
                if (stf, loc, tech, stage) in m.PRICEREDUCTION_ONETECH_TOTAL
            )
        return m.cost_capex_total_extension[stf] == gross - savings


class OpexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j, stf_min = 0.03, min(m.stf)
        f_cost = (1 + j) ** (1 - (stf - stf_min))
        total_opex = (
                sum(m.capacity_processing_total[stf, loc, tech, stage] * m.cost_fixed[stf, loc, tech, stage]
                    for loc in m.location for (tech, stage) in m.tech_stage_combinations) +
                sum(m.capacity_produced_output[stf, loc, tech, stage] * (m.cost_variable[stf, loc, tech, stage]
                +m.material_downstream_manufacturing_cost[stf, loc, tech,stage])
                    for loc in m.location for (tech, stage) in m.tech_stage_combinations) +
                sum(m.cost_electricity[stf] * m.FACTORY_ENERGY_ANNUAL[stf, loc, tech]
                    for loc in m.location for tech in m.tech) +
                sum(m.cost_scrap[stf, loc, tech] for loc in m.location for tech in m.tech) +
                sum(m.material_mined[stf, mat] * m.cost_mining[stf, mat] for mat in m.materials)
        )
        return m.cost_opex_total_extension[stf] == total_opex * f_cost


class TradeCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j, stf_min = 0.03, min(m.stf)
        f_cost = (1 + j) ** (1 - (stf - stf_min))
        total_trade = (
                sum(m.capacity_imported[stf, loc, tech, stage] * m.cost_import_part[stf, loc, tech, stage]
                    for loc in m.location for (tech, stage) in m.tech_stage_combinations) +
                sum(m.material_imported[stf, mat] * m.cost_import_material[stf, mat] for mat in m.materials)
        )
        return m.cost_trade_total_extension[stf] == total_trade * f_cost


class StockpileHoldingCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j, stf_min = 0.03, min(m.stf)
        f_cost = (1 + j) ** (1 - (stf - stf_min))
        HOLDING_COST = 27500  # k€/GW
        total_stock = sum(
            (m.stock_domestic[stf, loc, tech, stage] + m.stock_imported[stf, loc, tech, stage])
            for loc in m.location for (tech, stage) in m.tech_stage_combinations
        )
        return m.cost_stockpile_holding[stf] == total_stock * HOLDING_COST * f_cost


##################################################################################
# REGISTRATION
##################################################################################

def apply_material_constraints(m):
    # GROUP 1: (stf, location, tech, stage)
    # FIX: NOW ITERATING OVER ALL COMBINATIONS (tech, stages)
    # The 'check_valid_indices' helper in each rule prevents crashing on invalid combos.
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
        MaximumStockpileDomesticRule(),
        TurnoverStockDomesticNewRule(),
        TurnoverStockImportsNewRule(),
        SupplyCompositionRule(),
        ComponentBalanceRule(),
    ]
    for constraint_obj in stage_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech, m.stages,  # <--- DENSE ITERATION
            rule=lambda m, y, l, t, s: constraint_obj.apply_rule(m, y, l, t, s)
        ))

    # GROUP 2: (stf, location, tech)
    tech_constraints = [
        ScrapHandlingCapacitiesSizeRule(),
        ScrapHandlingCapacityGrowthLimitRule(),
        ScrapHandlingCapacitiesOutputLimitRule(),
        FactoryEnergyAnnualRule(),
        NewlyAddedBalanceLCOE(),
        InstallationSupplyLinkRule(),

    ]
    for constraint_obj in tech_constraints:
        name = constraint_obj.__class__.__name__
        setattr(m, name, pyomo.Constraint(
            m.stf, m.location, m.tech,
            rule=lambda m, y, l, k: constraint_obj.apply_rule(m, y, l, k)
        ))

    # GROUP 3: (t, stf, location, tech)
    setattr(m, "ElecNeedsProductionRule", pyomo.Constraint(
        m.timesteps_ext, m.stf, m.location, m.tech,
        rule=lambda m, t, y, l, k: m.demand_production[t, y, l, k] == m.FACTORY_ENERGY_ANNUAL[y, l, k] / 12
    ))

    # GROUP 4: (stf, material)
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

    # GROUP 5: Global / Cost Constraints
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

    print("✅ All manufacturing constraints registered successfully (Robust Mode).")