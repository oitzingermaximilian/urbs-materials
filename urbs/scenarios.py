# IEW SCENARIO FUNCTIONS FOR URBS
import numpy as np
# IEW SCENARIO FUNCTIONS FOR URBS - FIXED FOR NUMERICAL STABILITY


def scenario_solar_recycling_low(data, data_urbsextensionv1):
    """
    Scenario: Low Recycling Cost (Converted to M€/t)
    """

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: kEUR/kt
        new_costs = {
            "solarPV": 685.4,
            "windon": 1982.15,
            "windoff": 3462.33,
            "Batteries": 5309.74,
        }

        for stf in range(2024, 2051):
            for tech, price in new_costs.items():
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = price

    return data, data_urbsextensionv1


def scenario_solar_recycling_medium(data, data_urbsextensionv1):
    """
    Scenario: Medium Recycling Cost (Converted to M€/t)
    """

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: kEUR/kt
        new_costs = {
            "solarPV": 1720.584,
            "windon": 4975.2,
            "windoff": 8690.45,
            "Batteries": 13327.455,
        }

        for stf in range(2024, 2051):
            for tech, price in new_costs.items():
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = price

    return data, data_urbsextensionv1


def scenario_solar_recycling_high(data, data_urbsextensionv1):
    """
    Scenario: High Recycling Cost (Converted to M€/t)
    """

    if "recyclingcost_dict" in data_urbsextensionv1:
        recyclingcost = data_urbsextensionv1["recyclingcost_dict"]
        location = "EU27"

        # FIXED: kEUR/kt
        new_costs = {
            "solarPV": 5490.56,
            "windon": 15877,
            "windoff": 27733.28,
            "Batteries": 42531.04,
        }

        for stf in range(2024, 2051):
            for tech, price in new_costs.items():
                key = (stf, location, tech)
                if key in recyclingcost:
                    recyclingcost[key] = price

    return data, data_urbsextensionv1


base_scenarios = [
    ("low", scenario_solar_recycling_low),
    ("medium", scenario_solar_recycling_medium),
    ("high", scenario_solar_recycling_high),
]

# 2. Define the quotas (0.05, 0.10, ... 0.35)
quotas_to_test = np.arange(0.05, 0.40, 0.05)

# 3. Automatically generate the combined scenarios!
scenarios = []


# Factory function to avoid Python's late-binding loop issue
def create_combined_scenario(base_func, target_quota):
    def custom_scenario(data, data_urbsextensionv1):
        # Apply the base price logic
        d, d_ext = base_func(data, data_urbsextensionv1)

        # Inject the CRMA quota as a parameter into the dictionary
        d_ext["crma_quota"] = target_quota
        return d, d_ext

    return custom_scenario


# Build the master list
for name, func in base_scenarios:
    for q in quotas_to_test:
        quota_percent = int(round(q * 100))
        scen_name = f"scenario_solar_recycling_{name}_crma_{quota_percent}"

        # Add the dynamically created scenario to our list
        scenarios.append((scen_name, create_combined_scenario(func, q)))
