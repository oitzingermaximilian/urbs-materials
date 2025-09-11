
def scenario_min_min_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 9999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 9999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]

        # Piped Gas logic
        base_value = 319200000
        yearly_decrease_factor = 0.95948 #TEst with stable Gas supply

        # CO2 prices per year (€/t)
        co2_prices = {}

        # Linear interpolation from 65 in 2024 to 75 in 2030
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        # Fixed values from 2031 onward
        fixed_co2_prices = {
            2031: 81.3, 2032: 87.6, 2033: 93.9, 2034: 100.2, 2035: 106.5,
            2036: 112.8, 2037: 119.1, 2038: 125.4, 2039: 131.7, 2040: 138,
            2041: 228.5, 2042: 364.25, 2043: 466.0625, 2044: 500,
            2045: 500, 2046: 500, 2047: 500, 2048: 500, 2049: 500, 2050: 500
        }
        co2_prices.update(fixed_co2_prices)

        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas max
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

            # CO2 price update
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]
                print(f"Year {stf}: CO2 price set to {co2_prices[stf]:.2f} €/t")

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_min_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_min_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 838.7,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1258.05,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 4673.4,
            "windoff": 5563.4,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 7010.1,
            "windoff": 8345.15,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_min(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 1344.3
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_avg(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 60000
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2016.45
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_high(data, data_urbsextensionv1):
    import pandas as pd
    # Process updates
    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                pro.loc[(stf, "EU27", "Biomass Plant"), "inst-cap"] = 20420
                pro.loc[(stf, "EU27", "Coal Plant"), "inst-cap"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "inst-cap"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "inst-cap"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "inst-cap"] = 56670
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 9999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 9999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        base_value = 319200000
        yearly_decrease_factor = 0.95948
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value * (yearly_decrease_factor ** year_diff)

    # Process-commodity ratios
    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio"] = 0.205
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio"] = 0.0205
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio"] = 1
            proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio"] = 0.231

    # Recycling cost updates
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1677.4,
            "windon": 9346.8,
            "windoff": 11126.8,
            "Batteries": 2688.6
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1
