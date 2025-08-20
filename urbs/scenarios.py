
def scenario_min_min_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_min_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_min_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_min_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_min_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_min_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_avg_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_min_high_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_min_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_avg_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_avg_high_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_min_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 1000,
            "windoff": 1000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_avg_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 2500,
            "windoff": 2500,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_min_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_min_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 1508
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_avg_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_avg_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 6743
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_high_LNG_NZ(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_NZ" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1

def scenario_high_high_high_LNG_PF(data, data_urbsextensionv1):
    import pandas as pd  # Import pandas for NaN checking
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
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
            else:
                pro.loc[(stf, "EU27", "Biomass Plant"), "cap-up"] = 999999
                pro.loc[(stf, "EU27", "Coal Plant"), "cap-up"] = 53560
                pro.loc[(stf, "EU27", "Coal Lignite"), "cap-up"] = 43590
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "cap-up"] = 132230
                pro.loc[(stf, "EU27", "Gas Plant (CCGT)"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) LNG"), "min-fraction"] = 0
                pro.loc[(stf, "EU27", "Gas Plant (CCGT) CCUS"), "min-fraction"] = 0

    if "commodity" in data:
        co = data["commodity"]
        
        # LNG price data from 2024 to 2050 (27 values: indices 0-26)
        lng_prices_net_zero = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 19.48, 19.81, 20.14, 20.43,
            20.76, 21.12, 21.45, 21.81, 22.18, 22.41, 22.77, 23.15, 23.51, 23.89,
            24.27, 24.65, 25.07, 25.49, 25.87, 26.30, 26.74
        ]
        
        lng_prices_persisting_fossil = [
            19.15, 19.15, 19.15, 19.15, 19.15, 19.15, 20.45, 21.87, 23.34, 24.93,
            26.44, 28.39, 30.35, 32.33, 32.33, 32.33, 34.56, 36.93, 39.45, 42.12,
            44.95, 47.94, 51.10, 54.45, 57.99, 61.74, 65.71
        ]
        
        for stf in data["global_prop"].index.levels[0].tolist():
            # Piped Gas logic
            base_value = 319200000
            yearly_decrease_factor = 0.95948
            if stf == 2024:
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = base_value
            else:
                year_diff = stf - 2024
                reduced_value = base_value * (yearly_decrease_factor ** year_diff)
                co.loc[(stf, "EU27", "Piped Gas", "Stock"), "max"] = reduced_value
            
            # Set LNG prices based on year (2024-2050) and scenario type
            if 2024 <= stf <= 2050:
                year_index = int(stf - 2024)  # Convert to integer
                
                # Ensure year_index is within bounds
                if year_index < 0 or year_index >= 27:
                    continue
                
                if "LNG_PF" == "LNG_NZ":
                    lng_price = lng_prices_net_zero[year_index]
                else:  # LNG_PF
                    lng_price = lng_prices_persisting_fossil[year_index]
                
                # Update LNG Stock price only
                try:
                    # First, ensure the max value is not NaN
                    lng_key_with_space = (stf, "EU27", "LNG ", "Stock")
                    lng_key_without_space = (stf, "EU27", "LNG", "Stock")
                    
                    if lng_key_with_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_with_space, "max"]):
                            co.loc[lng_key_with_space, "max"] = float('inf')
                        co.loc[lng_key_with_space, "price"] = lng_price
                    elif lng_key_without_space in co.index:
                        # Ensure max is not NaN before setting price
                        if pd.isna(co.loc[lng_key_without_space, "max"]):
                            co.loc[lng_key_without_space, "max"] = float('inf')
                        co.loc[lng_key_without_space, "price"] = lng_price
                    else:
                        print(f"Warning: LNG Stock commodity not found for year {stf}")
                except KeyError:
                    # If the exact location doesn't exist, try alternative indexing
                    pass

    if "process-commodity" in data:
        proco = data["process-commodity"]
        for stf in data["global_prop"].index.levels[0].tolist():
            if stf == 2024:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205
            else:
                proco.loc[(stf, "Gas Plant (CCGT)", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT)", "CO2", "Out"), "ratio-min"] = 0.205
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "Piped Gas", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) CCUS", "CO2", "Out"), "ratio-min"] = 0.0205
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "LNG", "In"), "ratio-min"] = 1
                proco.loc[(stf, "Gas Plant (CCGT) LNG", "CO2", "Out"), "ratio-min"] = 0.205

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490,
            "windon": 5000,
            "windoff": 5000,
            "Batteries": 20608
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]
                    #print(f"Updated recycling cost for {tech} in {stf} to {new_costs[tech]} EUR/ton")
    return data, data_urbsextensionv1
