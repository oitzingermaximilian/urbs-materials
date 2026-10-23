from pathlib import Path


LEARNING_RATES = ("LR1", "LR4", "LR7")
INDUSTRY_SCENARIO = "nzia_40_crma_25"

MATERIAL_LEVELS = (
    ("materials_base", 1.00, 1.00, 1.00),
    ("materials_price_150", 1.50, 1.00, 1.00),
    ("materials_tier1_50_tier2_75_price_150", 1.50, 0.50, 0.75),
    ("materials_tier1_25_tier2_50_price_200", 2.00, 0.25, 0.50),
)

MATERIAL_SCENARIOS = tuple(level[0] for level in MATERIAL_LEVELS)


def scenario_name(learning_rate, material):
    return f"{learning_rate}_{INDUSTRY_SCENARIO}_{material}"


def scenario_file(base_dir, learning_rate, material):
    name = scenario_name(learning_rate, material)
    return Path(base_dir) / name / f"{name}.xlsx"
