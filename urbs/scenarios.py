#IEW SCENARIO FUNCTIONS FOR URBS

# IEW SCENARIO FUNCTIONS FOR URBS - FIXED FOR NUMERICAL STABILITY

def scenario_solar_recycling_low(data, data_urbsextensionv1):
    """
    Scenario: Low SolarPV Recycling Cost (Converted to M€/t)
    """
    _apply_standard_background_data(data)

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: 685.4 EUR/t -> kEUR/kt
        solar_recycling_price = 685.4

        for stf in range(2024, 2051):
            key = (stf, location, "solarPV")
            if key in recyclingcost:
                recyclingcost[key] = solar_recycling_price

    return data, data_urbsextensionv1


def scenario_solar_recycling_medium(data, data_urbsextensionv1):
    """
    Scenario: Medium SolarPV Recycling Cost (Converted to M€/t)
    """
    _apply_standard_background_data(data)

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: 1720.584 EUR/t -> kEUR/t
        solar_recycling_price = 1720.584

        for stf in range(2024, 2051):
            key = (stf, location, "solarPV")
            if key in recyclingcost:
                recyclingcost[key] = solar_recycling_price

    return data, data_urbsextensionv1


def scenario_solar_recycling_high(data, data_urbsextensionv1):
    """
    Scenario: High SolarPV Recycling Cost (Converted to M€/t)
    """
    _apply_standard_background_data(data)

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: 5490.56 EUR/t -> kEUR/kt
        solar_recycling_price = 5490.56

        for stf in range(2024, 2051):
            key = (stf, location, "solarPV")
            if key in recyclingcost:
                recyclingcost[key] = solar_recycling_price

    return data, data_urbsextensionv1


def _apply_standard_background_data(data):
    """
    Helper function to apply background data in GW and M€ units.
    """
    # ---------------- CO2 prices (Scale to M€/t) ----------------
    if "commodity" in data:
        co = data["commodity"]
        co2_prices = {}
        # Linear increase 2024-2030 (Scale to M€/t by multiplying with 1e-3)
        # Note: In the GW-M€ universe, commodity prices use a 1e-3 shift
        # relative to the raw input to stay consistent.
        for stf in range(2024, 2031):
            co2_prices[stf] = (65 + (stf - 2024) * (75 - 65) / (2030 - 2024)) * 1e-3

        fixed_co2_prices_tyndp = {
            2031: 115.9 * 1e-3, 2032: 118.4 * 1e-3, 2033: 120.9 * 1e-3,
            2034: 123.4 * 1e-3, 2035: 125.9 * 1e-3, 2036: 128.4 * 1e-3,
            2037: 130.9 * 1e-3, 2038: 133.4 * 1e-3, 2039: 135.9 * 1e-3,
            2040: 147.0 * 1e-3, 2041: 149.1 * 1e-3, 2042: 151.2 * 1e-3,
            2043: 153.3 * 1e-3, 2044: 155.4 * 1e-3, 2045: 157.5 * 1e-3,
            2046: 159.6 * 1e-3, 2047: 161.7 * 1e-3, 2048: 163.8 * 1e-3,
            2049: 165.9 * 1e-3, 2050: 168.0 * 1e-3,
        }
        co2_prices.update(fixed_co2_prices_tyndp)

        for stf in data["global_prop"].index.levels[0].tolist():
            if stf in co2_prices:
                co.loc[(stf, "EU27", "CO2", "Env"), "price"] = co2_prices[stf]

    # ---------------- Demand (Scale MW to GW) ----------------
    if "demand" in data:
        demand = data["demand"]
        demand = demand.astype(float)

        # FIXED: All values multiplied by 1e-3 (MWh -> GWh)
        yearly_profile = [
            v * 1e-3 for v in [
                207658333.3, 215588018.8, 223517704.2, 231447389.6, 239377075.1,
                247306760.5, 255236445.9, 260097649.0, 264958852.1, 269820055.3,
                274681258.3, 279542461.5, 284403664.6, 289264867.8, 294126070.8,
                298987274.0, 294534045.3, 298734647.4, 302935249.6, 307135851.7,
                311336453.8, 315537055.9, 319737658.1, 323938260.2, 328138862.3,
                332339464.4, 338580792.8,
            ]
        ]
        years = range(2024, 2051)
        for year, per_timestep in zip(years, yearly_profile):
            demand.loc[(float(year), slice(1, 12)), ("EU27", "Elec")] = per_timestep

        data["demand"] = demand

    # ---------------- SUPIM ----------------
    if "supim" in data:
        supim = data["supim"]
        # Hydro value remains small, but ensure units are GW if original was MW
        # If 0.33 was already GW, leave it. If it was MW, use 0.33 * 1e-3.
        for t in data["global_prop"].index.levels[0].tolist():
            if t > 0:
                supim.loc[t, ("EU27", "Hydro")] = 0.3375

    # ---------------- PROCESS (WACC and Fractions) ----------------
    if "process" in data:
        pro = data["process"]
        pro["wacc"] = 0
        # No scaling needed for WACC or min-fraction (dimensionless)

    # ---------------- PROCESS_COMMODITY (Ratios) ----------------
    if "process_commodity" in data:
        # Note: Input.py already scales material ratios to Tons/GW.
        # Here we just ensure ratio-min matches.
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




# OLD SCENARIOS


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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 5309.74,
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
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 13327.455,
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
        # yearly_profile = [
        #    207658333.3, 218941666.7, 230225000.0, 241500000.0,
        #    252775000.0, 264058333.3, 289000000.0, 299891666.7,
        #    310783333.3, 321675000.0, 332566666.7, 343458333.3,
        #    354350000.0, 365241666.7, 376133333.3, 387025000.0,
        #    397916666.7, 411833333.4, 425750000.0, 439666666.7,
        #    453583333.3, 467500000.0, 481416666.7, 495333333.3,
        #    509250000.0, 523166666.6, 537083333.3,
        # ] #This is the Profile with electrolyser Demand

        yearly_profile = [
            207658333.3,
            215588018.8,
            223517704.2,
            231447389.6,
            239377075.1,
            247306760.5,
            255236445.9,
            260097649.0,
            264958852.1,
            269820055.3,
            274681258.3,
            279542461.5,
            284403664.6,
            289264867.8,
            294126070.8,
            298987274.0,
            294534045.3,
            298734647.4,
            302935249.6,
            307135851.7,
            311336453.8,
            315537055.9,
            319737658.1,
            323938260.2,
            328138862.3,
            332339464.4,
            338580792.8,
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
            "Batteries": 42531.04,
        }
        for stf in range(2024, 2051):
            for tech in technologies:
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = new_costs[tech]

    return data, data_urbsextensionv1
