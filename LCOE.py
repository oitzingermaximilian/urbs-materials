import pandas as pd

def calculate_solar_pv_costs_explicit_energy():
    # --- 1. USER CONFIGURABLE INPUTS ---

    # [INPUT] Electricity Price in €/MWh
    # To hit your target of $0.06/W (approx $60k/MW total energy cost),
    # with ~400 MWh total demand and 1.10 Exchange rate, we need ~136 €/MWh.
    electricity_price_eur_mwh = 74.06

    # Exchange Rate (EUR to USD)
    exchange_rate = 1

    # Material Prices (USD/kg)
    prices_usd = {
        'Glass': 0.59,
        'Polymers': 6.00,
        'Ag': 2500,
        'Si': 2.48,
        'Al': 3135/1000,
        'Cu': 12905/1000
    }

    # Manufacturing Data
    # energy_mwh: Energy demand per MW of production
    # other_opex_usd: Non-energy operational costs (Labor, overhead) in USD
    manufacturing_specs = {
        'Polysilicon': {'energy_mwh': 160, 'other_opex_usd': 4669},
        'Wafer': {'energy_mwh': 130, 'other_opex_usd': 7912},
        'Cell': {'energy_mwh': 80, 'other_opex_usd': 23184},
        'Module': {'energy_mwh': 30, 'other_opex_usd': 14720}
    }

    # Material Intensity (kg per MW) - UPDATED WITH USER WEIGHTS
    intensities = {
        'Polysilicon': {
            'Si': 3047.16  # Precision Update (was 3803)
        },
        'Wafer': {
            # Still mostly energy/consumables, no main BOM change
        },
        'Cell': {
            'Ag': 20.78,  # Silver Paste
            'Al': 207.76  # New: Aluminium for Cell rear contact (0.3% weight)
        },
        'Module': {
            'Al': 11080.60,  # Frame (16% weight)
            'Glass': 46400,  # Glass (67% weight)
            'Polymers': 7617.91,  # Encapsulant/Backsheet (11% weight)
            'Cu': 554.03  # Ribbon Copper Content (0.8% weight)
        }
    }

    # Market Reference Prices (USD per MW)
    market_prices_usd = {
        'Cell': 82800,
        'Module': 170200
    }

    # --- 2. CALCULATION LOGIC ---

    def calculate_stage_cost(stage_name):
        specs = manufacturing_specs[stage_name]

        # A. Energy Cost Calculation (Price x Quantity)
        # Formula: (MWh * €/MWh) * Exchange Rate
        energy_cost_usd = (specs['energy_mwh'] * electricity_price_eur_mwh) * exchange_rate

        # B. Other OPEX
        opex_cost_usd = specs['other_opex_usd']

        # C. Material Cost
        mat_cost_usd = 0
        stage_materials = intensities.get(stage_name, {})
        for mat, qty in stage_materials.items():
            mat_cost_usd += qty * prices_usd[mat]

        return mat_cost_usd, energy_cost_usd, opex_cost_usd

    # --- 3. BUILD RESULTS ---

    # Calculate costs for all EU stages
    total_mat = 0
    total_energy = 0
    total_opex = 0

    print(f"{'Stage':<12} | {'Energy (MWh)':<12} | {'Elec Cost ($)':<15} | {'Mat Cost ($)':<15} | {'Total ($)':<15}")
    print("-" * 75)

    for stage in manufacturing_specs:
        m, e, o = calculate_stage_cost(stage)
        total_mat += m
        total_energy += e
        total_opex += o

        energy_demand = manufacturing_specs[stage]['energy_mwh']
        total_stage = m + e + o
        print(f"{stage:<12} | {energy_demand:<12} | {e:<15,.0f} | {m:<15,.0f} | {total_stage:<15,.0f}")

    grand_total_usd = total_mat + total_energy + total_opex

    print("-" * 75)
    print(
        f"{'TOTAL':<12} | {sum(d['energy_mwh'] for d in manufacturing_specs.values()):<12} | {total_energy:<15,.0f} | {total_mat:<15,.0f} | {grand_total_usd:<15,.0f}")

    # --- 4. FINAL SCENARIO SUMMARY ---
    cost_imported = market_prices_usd['Module']
    cost_hybrid = market_prices_usd['Cell'] + sum(calculate_stage_cost('Module'))

    print("\n--- FINAL SCENARIOS ($/W) ---")
    print(f"Electricity Input: €{electricity_price_eur_mwh}/MWh")
    print(f"Electricity Cost Share: ${total_energy / 1_000_000:.3f}/W (Target: $0.060)")
    print(f"1. Fully Imported:      ${cost_imported / 1e6:.3f}/W")
    print(f"2. Hybrid (EU Module):  ${cost_hybrid / 1e6:.3f}/W")
    print(f"3. Fully EU Produced:   ${grand_total_usd / 1e6:.3f}/W")


# Run
calculate_solar_pv_costs_explicit_energy()