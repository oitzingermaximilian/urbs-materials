
def scenario_min_min_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_min_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_min_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_avg_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_min_high_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 685.4,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_min_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_avg_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_avg_high_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 1720.584,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_min_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_avg_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_min(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 5309.74
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_avg(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 13327.455
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1

def scenario_high_high_high(data, data_urbsextensionv1):

    # ---------------- CO2 prices ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        for stf in range(2024, 2031):
            co2_prices[stf] = 65 + (stf - 2024) * (75 - 65) / (2030 - 2024)

        fixed_co2_prices_tyndp = {
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
            2050: 168.0,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

        co_2024 = co.xs(2024, level="support_timeframe", drop_level=False)
        stfs = data["global_prop"].index.levels[0].tolist()

        for stf in stfs:
            mask = co.index.get_level_values("support_timeframe") == stf
            aligned_max = (
                co_2024["max"]
                .droplevel("support_timeframe")
                .reindex(co.loc[mask].droplevel("support_timeframe").index)
            )
            co.loc[mask, "max"] = aligned_max.values

    # ---------------- Demand ----------------
    if "demand" in data:
        demand = data["demand"]
        yearly_profile = [
            207658333.3, 215588018.8, 223517704.2, 231447389.6,
            239377075.1, 247306760.5, 255236445.9, 260097649.0,
            264958852.1, 269820055.3, 274681258.3, 279542461.5,
            284403664.6, 289264867.8, 294126070.8, 298987274.0,
            294534045.3, 298734647.4, 302935249.6, 307135851.7,
            311336453.8, 315537055.9, 319737658.1, 323938260.2,
            328138862.3, 332339464.4, 338580792.8,
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        pro_2024 = pro.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = pro.index.get_level_values("support_timeframe") == stf
            aligned = (
                pro_2024["min-fraction"]
                .droplevel("support_timeframe")
                .reindex(pro.loc[mask].droplevel("support_timeframe").index)
            )
            pro.loc[mask, "min-fraction"] = aligned.values
            print("Target slice after:")
            print(pro.loc[mask, "min-fraction"].head())

    # ---------------- PROCESS_COMMODITY ----------------
    if "process_commodity" in data:
        proco = data["process_commodity"]
        proco_2024 = proco.xs(2024, level="support_timeframe", drop_level=False)

        for stf in data["global_prop"].index.levels[0]:
            mask = proco.index.get_level_values("support_timeframe") == stf
            aligned = (
                proco_2024["ratio"]
                .droplevel("support_timeframe")
                .reindex(proco.loc[mask].droplevel("support_timeframe").index)
            )
            proco.loc[mask, "ratio-min"] = aligned.values

    # ---------------- RECYCLING COST ----------------
    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        technologies = ["solarPV", "windon", "windoff", "Batteries"]
        location = "EU27"
        new_costs = {
            "solarPV": 5490.56,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 42531.04
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1
