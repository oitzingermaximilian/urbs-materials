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

# Based on the 16% -> 24% growth over 10 years
obsolescence_factor = 0.041 # 4.1% per year https://www.ise.fraunhofer.de/en/publications/studies/photovoltaics-report.html page 9 of Photovoltaics report
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
                    m.stock_domestic[stf-1,location, tech, stage] *
                    (1 - obsolescence_factor) +
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
                    m.stock_imported[stf-1,location, tech, stage] *
                    (1 - obsolescence_factor) +
                    m.capacity_imported_storage[stf, location, tech, stage] -
                    m.capacity_imported_stockout[stf, location, tech, stage]
            )

class MaximumStockpileImportsRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        lhs = m.capacity_imported_storage[stf,location, tech, stage]
        rhs = 0.25 * m.capacity_imported[stf, location, tech, stage]
        return lhs <= rhs

class MaximumStockpileDomesticRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        lhs = m.capacity_produced_storage[stf,location, tech, stage]
        rhs = 0.25 * m.capacity_produced_output[stf, location, tech, stage]
        return lhs <= rhs


class TurnvoverStockImportsNewRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        valid_years = [2025, 2030, 2035, 2040, 2045]

        if stf not in valid_years:
            return pyomo.Constraint.Skip

        # --- Hardcoded Step Size ---
        step_size = 5

        # Calculate LHS (Outflows)
        lhs = sum(
            m.capacity_imported_stockout[j, location, tech, stage]
            for j in range(stf, stf + step_size)  # Range 2025 -> 2030
            if (j, location, tech, stage) in m.capacity_imported_stockout
        )

        # Calculate RHS (Average Stock * FT)
        rhs = (
                1
                * (1 / step_size)  # Averaging factor (1/5)
                * sum(
            m.stock_imported[j, location, tech, stage]
            for j in range(stf, stf + step_size)
            if (j, location, tech, stage) in m.stock_imported
        )
        )
        return lhs >= rhs


class TurnvoverStockDomesticNewRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech, stage):
        valid_years = [2025, 2030, 2035, 2040, 2045]

        if stf not in valid_years:
            return pyomo.Constraint.Skip

        # --- Hardcoded Step Size ---
        step_size = 2

        # Calculate LHS (Outflows)
        lhs = sum(
            m.capacity_produced_stockout[j, location, tech, stage]
            for j in range(stf, stf + step_size)
            if (j, location, tech, stage) in m.capacity_produced_stockout
        )

        # Calculate RHS (Average Stock * FT)
        rhs = (
                1
                * (1 / step_size)
                * sum(
            m.stock_domestic[j, location, tech, stage]
            for j in range(stf, stf + step_size)
            if (j, location, tech, stage) in m.stock_domestic
        )
        )
        return lhs >= rhs



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

class NewlyAddedBalanceLCOE(AbstractConstraint):
    def apply_rule(self, m, stf,location,tech):
        return m.balance_yearly_new_capacity[stf,location,tech] == sum(
                m.capacity_ext_new[stf, location, tech] * m.lf_solar[t, stf, location, tech]
               * m.hours[t]
                for t in m.timesteps_ext
            )



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
        # LHS: Actual Metal Mined (Useful/Refined Metal)
        lhs = m.material_mined[stf, material]

        # RHS: Global Capacity * Share * Efficiency
        # Meaning: "Global Ore Capacity" -> "Our Portion" -> "Useful Metal we can get"
        rhs = (
                m.primary_material_availability[stf, material]
                * m.mining_energy_transission_share[stf, material]
                / m.mining_conversion_factor[stf, material]  # <--- Applied here
        )

        return lhs <= rhs


class LimitResourceExistanceRule(AbstractConstraint):
    def apply_rule(self, m, stf, material):
        """
        Calculates remaining reserves based on the Total Allowable Budget (Initial * Share)
        minus everything we have mined so far.
        """

        # 1. Calculate the Total Recoverable Budget (In Useful Metal terms)
        # This represents the total amount of metal we are allowed to access over all time.
        # We apply the share and conversion factor to the INITIAL stock.
        total_allowable_metal_stock = (
                m.initial_total_reserves[material]
                * m.mining_energy_transission_share[stf, material]
                * m.mining_conversion_factor[stf, material]  # <--- Ore-to-Metal Efficiency
        )

        # 2. Calculate Cumulative Consumption up to the current year
        cumulative_mined = sum(
            m.material_mined[year, material]
            for year in m.stf
            if year <= stf
        )

        # 3. Define Remaining Reserves
        # Remaining = Total_Budget - Used_So_Far
        return m.remaining_reserves[stf, material] == total_allowable_metal_stock - cumulative_mined


# --- PART A: Calculate Annual Total (Complex, run ONCE per year) ---
class FactoryEnergyAnnualRule(AbstractConstraint):
    def apply_rule(self, m, stf, location, tech):

        # Filter: Only apply to techs that have production demand
        # (You might need a check here to skip non-manufacturing techs)

        total_mwh = 0

        for stage in m.stages:
            if (location, tech, stage) not in m.energy_needs:
                continue

            intensity = m.energy_needs[location, tech, stage]

            prod = m.capacity_produced_output[stf, location, tech, stage]
            total_mwh += intensity * prod

        return m.FACTORY_ENERGY_ANNUAL[stf, location, tech] == total_mwh


# --- PART B: Distribute to Grid (Simple, run MANY times) ---
class ElecNeedsProductionRule(AbstractConstraint):
    def apply_rule(self, m, tm, stf, location, tech):
        # Just link the variables. Very fast for solver.
        # Ensure '12' is correct!
        # If 'tm' is MONTHS: Divide by 12.
        # If 'tm' is HOURS: Divide by 8760 (to get constant MW power).

        return m.demand_production[tm, stf, location, tech] == m.FACTORY_ENERGY_ANNUAL[stf, location, tech] / 12

# CLONED URBS COST CALCULATION
class CapexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        # --- urbs Intertemporal Factors ---
        j = 0.03  # Social Discount Rate
        i = 0.071  # WACC (Interest Rate)
        n = 20    # Depreciation Period
        stf_min = min(m.stf)
        stf_end = max(m.stf) # In yearly model, end is just the final year

        # f_inv: Annuity + Discounting for the decision year
        f_inv = ((1 + j)**(1 - (stf - stf_min)) * (i * (1 + i)**n * ((1 + j)**n - 1)) /
                 (j * (1 + j)**n * ((1 + i)**n - 1)))

        # f_over: Rest value subtraction (if factory outlives the model)
        op_time = (stf + n) - stf_end - 1
        f_over = 0
        if op_time > 0:
            f_over = ((1 + j)**(1 - (stf - stf_min)) * (i * (1 + i)**n * ((1 + j)**op_time - 1)) /
                      (j * (1 + j)**n * ((1 + i)**n - 1)))

        # --- CALCULATION ---
        # 1. Gross Investment (Uses NEW capacity)
        gross = sum(
            m.processing_cap_new[stf, loc, tech, stage]
            * m.cost_capex[stf, loc, tech, stage]
            * (f_inv - f_over)
            for loc in m.location for tech in m.tech for stage in m.stages
            if (stf, loc, tech, stage) in m.processing_cap_new
        )

        # 2. Learning Rate Savings
        savings = 0
        if hasattr(m, 'PRICEREDUCTION_ONETECH_TOTAL'):
            savings = sum(
                m.PRICEREDUCTION_ONETECH_TOTAL[stf, loc, tech, stage]
                * (f_inv - f_over)
                for loc in m.location for tech in m.tech_one_tech for stage in m.stages_one_tech
                if (stf, loc, tech, stage) in m.PRICEREDUCTION_ONETECH_TOTAL
            )

        return m.cost_capex_total_extension[stf] == gross - savings


class OpexCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j = 0.03
        stf_min = min(m.stf)

        # In a yearly simulation, f_cost is just the discount factor for that year
        f_cost = (1 + j) ** (1 - (stf - stf_min))

        # Sum of all operational components for the extension
        # Fixed (Capacity) + Variable (Output) + Scrap + Mining
        total_opex = (
                sum(m.capacity_processing_total[stf, loc, tech, stage] * m.cost_fixed[stf, loc, tech, stage]
                    for loc in m.location for tech in m.tech for stage in m.stages) +
                sum(m.capacity_produced_output[stf, loc, tech, stage] * m.cost_variable[stf, loc, tech, stage]
                    for loc in m.location for tech in m.tech for stage in m.stages) +
                sum(m.cost_electricity[stf] * m.FACTORY_ENERGY_ANNUAL[stf, location, tech]
                    for location in m.location for tech in m.tech) +
                sum(m.cost_scrap[stf, loc, tech] for loc in m.location for tech in m.tech) +
                sum(m.material_mined[stf, mat] * m.cost_mining[stf, mat]  for mat in m.materials)
        )

        return m.cost_opex_total_extension[stf] == total_opex * f_cost


class TradeCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j = 0.03
        stf_min = min(m.stf)
        f_cost = (1 + j)**(1 - (stf - stf_min))

        total_trade = (
            sum(m.capacity_imported[stf, loc, tech, stage] * m.cost_import_part[stf, loc, tech, stage]
                for loc in m.location for tech in m.tech for stage in m.stages) +
            sum(m.material_imported[stf, mat] * m.cost_import_material[stf, mat] for mat in m.materials)
        )

        return m.cost_trade_total_extension[stf] == total_trade * f_cost
# Trade&Storage
class StockpileHoldingCostRule(AbstractConstraint):
    def apply_rule(self, m, stf):
        j = 0.03
        stf_min = min(m.stf)
        f_cost = (1 + j) ** (1 - (stf - stf_min))

        # Holding cost per unit (MW or kg) per year
        HOLDING_COST = 27500

        total_stock = sum(
            (m.stock_domestic[stf, loc, tech, stage] + m.stock_imported[stf, loc, tech, stage])
            for loc in m.location for tech in m.tech for stage in m.stages
        )

        return m.cost_stockpile_holding[stf] == total_stock * HOLDING_COST * f_cost

def apply_material_constraints(m):
    """
    Registers all constraints with the Pyomo model, grouped by their index requirements.
    """
    scrap_growth_constraints = [
        ScrapHandlingCapacitiesSizeRule(),
        ScrapHandlingCapacityGrowthLimitRule(),
        ScrapHandlingCapacitiesOutputLimitRule(),
        FactoryEnergyAnnualRule(),
        NewlyAddedBalanceLCOE()
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
        TurnvoverStockDomesticNewRule(),
        TurnvoverStockImportsNewRule(),
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
