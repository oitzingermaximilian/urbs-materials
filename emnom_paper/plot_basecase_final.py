from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator, StrMethodFormatter

from plot_base import (
    FILE_PATH,
    load_baseline_generation,
    load_capacity_data,
    plot_capacity_bar,
    plot_electricity_generation,
)

MATERIAL_RECYCLING_COLOR = "#D6BA73"
AVAILABLE_MATERIAL_COLOR = "red"
CRMA_MATERIALS = [
    "aluminum",
    "copper",
    "silicon",
    "cobalt",
    "dysprosium",
    "gallium",
    "graphite",
    "lithium",
    "manganese",
    "neodymium",
    "nickel",
    "niobium",
    "praseodymium",
    "terbium",
    "titanium",
    "vanadium",
    "boron",
]


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR.parent / "Input_urbsextensionv1.xlsx"
OUTPUT_DIR = PROJECT_DIR / "plots" / "basecase_final"
MATERIALS_TO_PLOT = ["aluminum", "copper", "neodymium", "silicon"]
YEARS = np.arange(2025, 2051)

MATERIAL_COLORS = {
    "Imported": "#F5E0B7",
    "Mined": "#8BBF9F",
    "Recycled": "#D6BA73",
    "Demand": "red",
}


def load_basecase_minerals():
    df = pd.read_excel(FILE_PATH, sheet_name="minerals")
    df.columns = df.columns.str.lower()
    df["stf"] = pd.to_numeric(df["stf"].ffill(), errors="coerce")
    df["materials"] = df["materials"].astype(str).str.strip().str.lower()
    return df[df["stf"].between(2025, 2050)]


def plot_basecase_materials(df):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, squeeze=False)
    for axis, material in zip(axes.flat, MATERIALS_TO_PLOT):
        material_df = (
            df[df["materials"] == material]
            .set_index("stf")
            .reindex(YEARS)
            .fillna(0)
        )
        imported = material_df["material_imported"].values
        mined = material_df["material_mined"].values
        recycled = material_df["material_recycled"].values
        demand = imported + mined + recycled

        axis.stackplot(
            YEARS,
            imported,
            mined,
            recycled,
            colors=[
                MATERIAL_COLORS["Imported"],
                MATERIAL_COLORS["Mined"],
                MATERIAL_COLORS["Recycled"],
            ],
            edgecolor="black",
            linewidth=0.4,
        )
        axis.plot(
            YEARS,
            demand,
            color=MATERIAL_COLORS["Demand"],
            linewidth=1.6,
            label="Annual demand",
        )
        axis.set_title(material.capitalize())
        axis.set_xlim(2025, 2050)
        axis.set_xticks([2025, 2030, 2035, 2040, 2045, 2050])
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4))
        axis.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_axisbelow(True)

    handles = [
        plt.Line2D([], [], color=MATERIAL_COLORS["Demand"], lw=2, label="Annual demand"),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=MATERIAL_COLORS["Imported"], edgecolor="black",
            label="Imported",
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=MATERIAL_COLORS["Mined"], edgecolor="black",
            label="Mined",
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=MATERIAL_COLORS["Recycled"], edgecolor="black",
            label="Recycled",
        ),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True)
    fig.suptitle("LR4 Base Case Material Demand and Sourcing")
    fig.supxlabel("Year")
    fig.supylabel("Material quantity (kt)")
    fig.tight_layout(rect=(0.04, 0.08, 1, 0.95))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / "Fig_Basecase_Materials_Selected.pdf", bbox_inches="tight")
    plt.close(fig)


def _find_column(columns, candidates, description):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"Could not find {description} column. Available: {sorted(columns)}")


def _normalise_key(value):
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def _normalise_material(value):
    key = _normalise_key(value)
    return {"aluminium": "aluminum"}.get(key, key)


def load_material_intensities():
    intensity = pd.read_excel(INPUT_FILE, sheet_name="Material_Intensity")
    intensity.columns = (
        intensity.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    )
    tech_column = _find_column(
        intensity.columns, ["tech", "technology", "process"], "technology"
    )
    material_column = _find_column(
        intensity.columns, ["material", "materials", "mat"], "material"
    )
    value_column = _find_column(
        intensity.columns,
        ["intensity", "material_intensity", "value", "content"],
        "material intensity",
    )
    intensity = intensity.rename(
        columns={
            tech_column: "tech",
            material_column: "material",
            value_column: "intensity",
        }
    )
    intensity["tech"] = intensity["tech"].map(_normalise_key)
    intensity["material"] = intensity["material"].map(_normalise_material)
    intensity["intensity"] = pd.to_numeric(
        intensity["intensity"], errors="coerce"
    ).fillna(0)
    return (
        intensity[["tech", "material", "intensity"]]
        .query("intensity != 0")
        .groupby(["tech", "material"], as_index=False)["intensity"]
        .sum()
    )


def load_materials():
    materials = pd.read_excel(INPUT_FILE, sheet_name="Material_Intensity")
    materials.columns = (
        materials.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    )
    material_column = _find_column(
        materials.columns, ["material", "materials", "name"], "material list"
    )
    return (
        materials[material_column]
        .dropna()
        .astype(str)
        .map(_normalise_material)
        .drop_duplicates()
        .tolist()
    )


def calculate_material_scrap(df_scrap, df_minerals, df_intensity, materials):
    """Calculate annual scrap potential and recycled material by material."""
    scrap = df_scrap.copy()
    scrap.columns = scrap.columns.astype(str).str.strip().str.lower()
    tech_column = _find_column(
        scrap.columns, ["tech", "technology"], "scrap technology"
    )
    quantity_column = _find_column(
        scrap.columns, ["capacity_scrap_total"], "total scrap capacity"
    )
    scrap["stf"] = pd.to_numeric(scrap["stf"].ffill(), errors="coerce")
    scrap[tech_column] = scrap[tech_column].map(_normalise_key)
    scrap[quantity_column] = pd.to_numeric(
        scrap[quantity_column], errors="coerce"
    ).fillna(0)

    gross = scrap.merge(
        df_intensity,
        left_on=tech_column, right_on="tech",
        how="left",
    )
    gross["material"] = gross["material"].fillna("")
    gross["intensity"] = gross["intensity"].fillna(0)
    gross["available_material"] = gross[quantity_column] * gross["intensity"]
    gross = gross.groupby(["stf", "material"], as_index=False)[
        "available_material"
    ].sum()

    minerals = df_minerals.copy()
    minerals.columns = minerals.columns.astype(str).str.strip().str.lower()
    material_column = _find_column(
        minerals.columns, ["materials", "material"], "mineral material"
    )
    minerals["stf"] = pd.to_numeric(
        minerals["stf"].ffill(), errors="coerce"
    )
    minerals["material"] = minerals[material_column].map(_normalise_material)
    minerals["material_recycled"] = pd.to_numeric(
        minerals["material_recycled"], errors="coerce"
    ).fillna(0)
    recycled = (
        minerals.groupby(["stf", "material"], as_index=False)["material_recycled"]
        .sum()
    )

    years = np.arange(2025, 2051)
    materials = [material for material in materials if material]
    index = pd.MultiIndex.from_product(
        [years, materials], names=["stf", "material"]
    )
    result = (
        gross.set_index(["stf", "material"])
        .join(recycled.set_index(["stf", "material"]), how="outer")
        .reindex(index)
        .fillna(0)
        .reset_index()
    )
    return result


def plot_material_scrap(df_scrap, df_minerals, df_intensity, materials):
    materials = [material for material in materials if material in CRMA_MATERIALS]
    material_scrap = calculate_material_scrap(
        df_scrap, df_minerals, df_intensity, materials
    )
    plot_data = material_scrap[material_scrap["stf"].between(2025, 2050)]
    ncols = 2
    nrows = int(np.ceil(len(materials) / ncols))
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(13, max(3.5 * nrows, 4)), squeeze=False
    )
    axes = axes.flat
    for index, material in enumerate(materials):
        ax = axes[index]
        material_data = plot_data[plot_data["material"] == material]
        material_data = material_data.set_index("stf").reindex(YEARS).fillna(0)
        available = material_data["available_material"].values
        recycled = material_data["material_recycled"].values
        ax.stackplot(
            YEARS,
            available,
            recycled,
            alpha=0.18,
            colors=[AVAILABLE_MATERIAL_COLOR, MATERIAL_RECYCLING_COLOR],
            labels=["Cumulative Available Scrap", "Material Recycled"],
        )
        ax.plot(
            YEARS,
            available,
            color=AVAILABLE_MATERIAL_COLOR,
            linewidth=1.5,
            label="_nolegend_",
        )
        ax.set_title(material.capitalize())
        ax.set_xlim(2025, 2050)
        ax.set_xticks([2025, 2030, 2035, 2040, 2045, 2050])
        ax.set_ylabel("Material quantity (kt)")
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.legend(loc="upper left", fontsize=8, frameon=True)
    for ax in axes[len(materials):]:
        ax.set_visible(False)
    fig.suptitle("Cumulative Available Scrap and Material Recycling")
    fig.supxlabel("Year")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUTPUT_DIR / "Fig_Basecase_Material_Scrap_All_Materials.pdf",
        bbox_inches="tight",
    )
    plt.close(fig)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generation = load_baseline_generation(FILE_PATH, start_year=2025, end_year=2050)
    plot_electricity_generation(
        generation,
        chart_type="area",
        ylabel="Electricity Generated (TWh)",
        output_filename=str(OUTPUT_DIR / "Fig_Basecase_Electricity_Generation_Area.pdf"),
    )
    plot_electricity_generation(
        generation,
        chart_type="bar",
        ylabel="Electricity Generated (TWh)",
        output_filename=str(OUTPUT_DIR / "Fig_Basecase_Electricity_Generation_Bar.pdf"),
    )
    capacity = load_capacity_data(FILE_PATH, start_year=2025, end_year=2050)
    plot_capacity_bar(
        capacity,
        ylabel="Installed Capacity (GW)",
        output_filename=str(OUTPUT_DIR / "Fig_Basecase_Capacity_Bar.pdf"),
    )
    plot_basecase_materials(load_basecase_minerals())
    scrap = pd.read_excel(FILE_PATH, sheet_name="scrap")
    minerals = pd.read_excel(FILE_PATH, sheet_name="minerals")
    plot_material_scrap(
        scrap,
        minerals,
        load_material_intensities(),
        load_materials(),
    )
