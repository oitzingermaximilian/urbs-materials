
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
        yearly_decrease_factor = 0.95948 #Test with stable Gas supply

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
            2045: 600, 2046: 750, 2047: 900, 2048: 1000, 2049: 1000, 2050: 1000
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
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t >0:
                supim.loc[t,("EU27", "Hydro")] = 0.3375
                #print("SUPIM:", supim)
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
    # Commodity updates
    if "commodity" in data:
        co = data["commodity"]
        # CO2 prices per year (€/t)
        co2_prices = {}
        # Linear interpolation from 65 in 2024 to 75 in 2030
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)
        # Fixed values from 2031 onward
        fixed_co2_prices_seb = {
            2031: 81.3, 2032: 87.6, 2033: 93.9, 2034: 100.2, 2035: 106.5,
            2036: 112.8, 2037: 119.1, 2038: 125.4, 2039: 131.7, 2040: 138,
            2041: 228.5, 2042: 364.25, 2043: 466.0625, 2044: 500,
            2045: 500, 2046: 500, 2047: 500, 2048: 500, 2049: 500, 2050: 500
        }

        fixed_co2_prices_tyndp = {
            2024: 65.0,
            2025: 74.6667,
            2026: 84.3333,
            2027: 94.0,
            2028: 103.6667,
            2029: 113.3333,
            2030: 113.4,
            2031: 115.9,
            2032: 118.4,
            2033: 120.9,
            2034: 123.4,
            2035: 125.9,
            2036: 128.4,
            2037: 130.9,
            2038: 133.4,
            2039: 135.9,
            2040: 147.0,
            2041: 149.1,
            2042: 151.2,
            2043: 153.3,
            2044: 155.4,
            2045: 157.5,
            2046: 159.6,
            2047: 161.7,
            2048: 163.8,
            2049: 165.9,
            2050: 168.0
        }
        co2_prices.update(fixed_co2_prices_seb)
        for stf in data["global_prop"].index.levels[0].tolist():
            # CO2 price update
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]
                print(f"Year {stf}: CO2 price set to {co2_prices[stf]:.2f} €/t")
    if "demand" in data:
        demand = data["demand"]
        print("✅ Demand Columns",demand.columns)

        yearly_profile = [
            207658333.3, 218766666.7, 229875000, 240983333.3,
            252091666.7, 263208333.3, 255236445.9, 262008333.3,
            268783333.3, 275558333.3, 282333333.3, 289108333.3,
            295891666.7, 302666666.7, 309441666.7, 316216666.7,
            294534045.3, 304233333.3, 313933333.3, 323633333.3,
            333333333.3, 343033333.3, 352733333.3, 362433333.3,
            372133333.3, 381858333.3, 338580792.8,
        ]

        yearly_profile_with_electrolyser = [
            207658333.3,
            218941666.7,
            230225000,
            241500000,
            252775000,
            264058333.3,
            289000000,
            308500000,
            328000000,
            347500000,
            367000000,
            386500000,
            406000000,
            425500000,
            445000000,
            464583333.3,
            397916666.7,
            423166666.7,
            448416666.7,
            473666666.7,
            498916666.7,
            524166666.7,
            549416666.7,
            574666666.7,
            599916666.7,
            610166666.7,
            537083333.3
        ]

        years = range(2024, 2051)  # 2024–2050 inclusive
        for year, per_timestep in zip(years, yearly_profile_with_electrolyser):
            # update t = 1..12, leave t=0 untouched
            #demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep
            print("hi")


        #print("✅ Demand updated for EU27 Elec from 2024–2050")

    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375
                # print("SUPIM:", supim)
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

    if "process" in data:
        pro = data["process"]
        for stf in data["global_prop"].index.levels[0].tolist():
            pro.loc[(stf, "EU27", "Lignite Plant CCUS"), "cap-up"] = 0
            pro.loc[(stf, "EU27", "Coal Plant CCUS"), "cap-up"] = 0
            pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "cap-up"] = 0
            pro.loc[(stf, "EU27", "Biomass Plant"), "inv-cost"] = 3487.6605 * 1000
            pro.loc[(stf, "EU27", "Biomass Plant"), "var-cost"] = 2.2255

            # Min-fractions (capacity factors)
            pro.loc[(stf, "EU27", "Coal Plant"), "min-fraction"] = 0.50
            pro.loc[(stf, "EU27", "Lignite Plant"), "min-fraction"] = 0.6
            pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0.5
            pro.loc[(stf, "EU27", "Other non-res"), "min-fraction"] = 0.20
            pro.loc[(stf, "EU27", "Oil Plant"), "min-fraction"] = 0.15
            pro.loc[(stf, "EU27", "Coal Plant CCUS"), "min-fraction"] = 0.5
            pro.loc[(stf, "EU27", "Lignite Plant CCUS"), "min-fraction"] = 0.6
            pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0.50
            pro.loc[(stf, "EU27", "Nuclear Plant"), "min-fraction"] = 0.8
            pro.loc[(stf, "EU27", "Hydro (run-of-river)"), "min-fraction"] = 0
            pro.loc[(stf, "EU27", "Hydro (reservoir)"), "min-fraction"] = 0
            pro.loc[(stf, "EU27", "Biomass Plant"), "min-fraction"] = 0.7

    if "process_commodity" in data:
        proco = data["process_commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            mask = proco.index.get_level_values("support_timeframe") == stf
            proco.loc[mask, "ratio-min"] = proco.loc[mask, "ratio"]
            print("✅ proco - ratio-min updated from 2024–2050")

    return data, data_urbsextensionv1
