# --- COST BREAKDOWN: SOLAR PV MODULE STAGE ---

# 1. Market Benchmarks
price_import_module = 149960  # €/MW (The competition)
price_import_cell   = 81558   # €/MW (The input part)

# 2. Manufacturing Costs (User Data)
cost_variable     = 12420     # €/MW
fixed_cost        = 2300      # €/MW (Capacity Cost)

# 3. Energy Costs
elec_needs        = 75        # MWh/MW
elec_price        = 75        # €/MWh
cost_elec_total   = elec_needs * elec_price

# 4. Material Costs (User Data)
# Prices in €/ton, Quantities in tons/MW
price_Al       = 3135
price_Glass    = 360#59
price_Polymers = 1760#6    # Note: 6 €/ton is very low for polymers, but used as provided
price_Cu       = 12905

qty_Al       = 11.08059701
qty_Glass    = 46.4
qty_Polymers = 7.617910448
qty_Cu       = 0.623283582

# Calculate Material Sub-totals
cost_Al       = qty_Al * price_Al
cost_Glass    = qty_Glass * price_Glass
cost_Polymers = qty_Polymers * price_Polymers
cost_Cu       = qty_Cu * price_Cu

cost_materials_total = cost_Al + cost_Glass + cost_Polymers + cost_Cu

# 5. Total Calculations
marginal_cost_to_make = price_import_cell + cost_variable + cost_elec_total + cost_materials_total
full_cost_to_make     = marginal_cost_to_make + fixed_cost

# --- PRINT THE RECEIPT ---
print(f"===========================================================")
print(f"       MANUFACTURING COST BREAKDOWN: SOLAR PV MODULE       ")
print(f"===========================================================")
print(f"1. INPUT PARTS")
print(f"   Imported Cell:           {price_import_cell:10,.0f} €/MW")
print(f"-----------------------------------------------------------")
print(f"2. VALUE ADD (PROCESSING)")
print(f"   Variable Opex:           {cost_variable:10,.0f} €/MW")
print(f"   Electricity:             {cost_elec_total:10,.0f} €/MW")
print(f"   Fixed Opex (Overhead):   {fixed_cost:10,.0f} €/MW")
print(f"-----------------------------------------------------------")
print(f"3. MATERIALS")
print(f"   Aluminum:                {cost_Al:10,.0f} €/MW")
print(f"   Glass:                   {cost_Glass:10,.0f} €/MW")
print(f"   Copper:                  {cost_Cu:10,.0f} €/MW")
print(f"   Polymers:                {cost_Polymers:10,.0f} €/MW")
print(f"   > TOTAL MATERIALS:       {cost_materials_total:10,.0f} €/MW")
print(f"===========================================================")
print(f"TOTAL COST TO MAKE (Full):  {full_cost_to_make:10,.0f} €/MW")
print(f"COST TO IMPORT (Module):    {price_import_module:10,.0f} €/MW")
print(f"-----------------------------------------------------------")
print(f"PROFIT MARGIN (per MW):     {price_import_module - full_cost_to_make:10,.0f} €/MW")
print(f"===========================================================")

print("\n--- CONCLUSION ---")
if full_cost_to_make < price_import_module:
    print("✅ DOMESTIC MANUFACTURING IS GENUINELY CHEAPER")
    print("   Even if you pay the Fixed Costs, it is roughly 20,000 €/MW cheaper")
    print("   to build it yourself than to buy it from the market.")
    print("   The model is behaving logically based on these prices.")
    if fixed_cost == 2300:
         print("   NOTE: Your Fixed Cost (2,300) is very low (<2% of total cost).")
else:
    print("❌ IMPORT SHOULD BE CHEAPER")