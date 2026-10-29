import ctypes
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import (
    MaxNLocator,
    MultipleLocator,
    PercentFormatter,
    StrMethodFormatter,
)

from plot_base import (
    FILE_PATH,
    load_baseline_generation,
    load_capacity_data,
    plot_capacity_bar,
    plot_electricity_generation,
)

# Colors for Scrap and Recycling
UNUSED_SCRAP_COLOR = "#B0BEC5"
UTILIZED_SCRAP_COLOR = "#D6BA73"
TOTAL_SCRAP_LINE_COLOR = "#2C3E50"

# Colors for Material Demand and Sourcing
MATERIAL_COLORS = {
    "Imported": "#F5E0B7",
    "Mined": "#8BBF9F",
    "Recycled": "#D6BA73",
    "Demand": "red",
}

# Colors for Technology Supply Mix / Sourcing (from plot_tech_sourcing.py)
SUPPLY_MIX_COLORS = {
    "capacity_produced_flow": "#AA96DA",  # Soft Purple (Domestic Prod.)
    "capacity_produced_stockout": "#FCBAD3",  # Soft Pink (Domestic Stockpile)
    "Imported": "#FFFFD2",  # Pale Yellow (Imported)
}

SUPPLY_MIX_LABELS = {
    "capacity_produced_flow": "Domestic Prod.",
    "capacity_produced_stockout": "Domestic Stockpile",
    "Imported": "Imported",
}

TECH_STAGE_MAP = {
    "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
    "windon": ["BladeOn", "TowerOn", "NacelleOn"],
    "windoff": ["BladeOff", "TowerOff", "NacelleOff"],
}

TECH_DISPLAY_NAMES = {
    "solarPV": "Solar PV",
    "windon": "Onshore Wind",
    "windoff": "Offshore Wind",
}

STAGE_LABELS = {
    "Polysilicon": "Polysilicon",
    "Wafer": "Wafer",
    "Cell": "Cell",
    "Module": "Module",
    "BladeOn": "Blade",
    "TowerOn": "Tower",
    "NacelleOn": "Nacelle",
    "BladeOff": "Blade",
    "TowerOff": "Tower",
    "NacelleOff": "Nacelle",
}

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR.parent / "Input_urbsextensionv1.xlsx"
OUTPUT_DIR = PROJECT_DIR / "plots" / "basecase_final"
MATERIALS_TO_PLOT = ["aluminum", "copper", "neodymium", "silicon"]
YEARS = np.arange(2025, 2051)

# Grouping by quantities / units:
# - kt: aluminum, silicon, nickel, manganese, copper (multiplier = 1.0)
# - kg: terbium, vanadium, gallium, niobium, boron (multiplier = 1e6)
# - t (tons): all remaining CRMA materials (multiplier = 1e3)
KT_MATERIALS = ["aluminum", "copper", "manganese", "nickel", "silicon"]
T_MATERIALS = ["cobalt", "dysprosium", "graphite", "lithium", "neodymium", "praseodymium", "titanium"]
KG_MATERIALS = ["boron", "gallium", "niobium", "terbium", "vanadium"]

MATERIAL_UNITS = {
    # kt materials
    "aluminum": ("kt", 1.0),
    "silicon": ("kt", 1.0),
    "nickel": ("kt", 1.0),
    "manganese": ("kt", 1.0),
    "copper": ("kt", 1.0),
    # kg materials
    "terbium": ("kg", 1_000_000.0),
    "vanadium": ("kg", 1_000_000.0),
    "gallium": ("kg", 1_000_000.0),
    "niobium": ("kg", 1_000_000.0),
    "boron": ("kg", 1_000_000.0),
    # The rest in tons
    "cobalt": ("t", 1_000.0),
    "dysprosium": ("t", 1_000.0),
    "graphite": ("t", 1_000.0),
    "lithium": ("t", 1_000.0),
    "neodymium": ("t", 1_000.0),
    "praseodymium": ("t", 1_000.0),
    "titanium": ("t", 1_000.0),
}

CRMA_MATERIALS = list(MATERIAL_UNITS.keys())
UNIT_ORDER = {"kt": 0, "t": 1, "kg": 2}


def read_excel_safe(path, **kwargs):
    """Read an Excel file safely, even if it is currently locked by Excel."""
    try:
        return pd.read_excel(path, **kwargs)
    except PermissionError:
        path = Path(path).resolve()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            success = ctypes.windll.kernel32.CopyFileW(str(path), str(tmp_path), False)
            if not success:
                raise
            return pd.read_excel(tmp_path, **kwargs)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass


def sort_materials_by_unit(materials):
    """Sort materials by Unit (kt -> t -> kg), then alphabetically."""
    def sort_key(mat):
        unit, _ = MATERIAL_UNITS.get(mat, ("t", 1000.0))
        return (UNIT_ORDER.get(unit, 1), mat)
    return sorted(materials, key=sort_key)


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
        .replace("eu27.", "")
        .replace("eu27", "")
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def _normalise_material(value):
    key = _normalise_key(value)
    return {"aluminium": "aluminum"}.get(key, key)


# =====================================================================
# 1. MATERIAL INTENSITIES & FRACTIONS
# =====================================================================
def load_material_fractions():
    """
    Load material mass fractions per technology: scrap_content / f_scrap.
    scrap_content is in [t/MW] and f_scrap is in [t/MW], so the fraction is dimensionless.
    """
    tech_df = read_excel_safe(INPUT_FILE, sheet_name="Technologies")
    tech_df.columns = tech_df.columns.astype(str).str.strip().str.lower()
    tech_col = _find_column(tech_df.columns, ["technologies", "tech"], "technology")
    scrap_col = _find_column(tech_df.columns, ["scrap", "f_scrap"], "f_scrap")

    tech_scrap = tech_df[[tech_col, scrap_col]].dropna().copy()
    tech_scrap["tech"] = tech_scrap[tech_col].map(_normalise_key)
    tech_scrap["f_scrap"] = pd.to_numeric(tech_scrap[scrap_col], errors="coerce").fillna(0)
    scrap_dict = tech_scrap[tech_scrap["f_scrap"] > 0].set_index("tech")["f_scrap"].to_dict()

    mat_df = read_excel_safe(INPUT_FILE, sheet_name="Material_Intensity")
    mat_df.columns = mat_df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    t_col = _find_column(mat_df.columns, ["tech", "technology"], "technology")
    m_col = _find_column(mat_df.columns, ["material", "materials", "mat"], "material")
    c_col = _find_column(mat_df.columns, ["scrap_content", "intensity", "content"], "scrap content")

    mat_df["tech"] = mat_df[t_col].map(_normalise_key)
    mat_df["material"] = mat_df[m_col].map(_normalise_material)
    mat_df["scrap_content"] = pd.to_numeric(mat_df[c_col], errors="coerce").fillna(0)

    grouped = mat_df.groupby(["tech", "material"], as_index=False)["scrap_content"].sum()
    grouped["f_scrap"] = grouped["tech"].map(scrap_dict).fillna(0)

    fallback_sum = grouped.groupby("tech")["scrap_content"].transform("sum")
    grouped["f_scrap"] = np.where(grouped["f_scrap"] > 0, grouped["f_scrap"], fallback_sum)

    grouped["fraction"] = np.where(
        grouped["f_scrap"] > 0,
        grouped["scrap_content"] / grouped["f_scrap"],
        0.0,
    )
    return grouped[["tech", "material", "fraction"]]


def load_material_intensities():
    """Backward-compatible alias for load_material_fractions."""
    return load_material_fractions()


def load_materials():
    materials = read_excel_safe(INPUT_FILE, sheet_name="Material_Intensity")
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


# =====================================================================
# 2. MATERIAL DEMAND & SOURCING PLOTS
# =====================================================================
def load_basecase_minerals():
    df = read_excel_safe(FILE_PATH, sheet_name="minerals")
    df.columns = df.columns.str.lower()
    df["stf"] = pd.to_numeric(df["stf"].ffill(), errors="coerce")
    df["materials"] = df["materials"].astype(str).str.strip().str.lower()
    return df[df["stf"].between(2025, 2050)]


def plot_basecase_materials(df, start_year=2025, end_year=2050, suffix=""):
    """Plot 2x2 grid for selected materials (Aluminum, Copper, Neodymium, Silicon)."""
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, squeeze=False)
    for axis, material in zip(axes.flat, MATERIALS_TO_PLOT):
        unit, multiplier = MATERIAL_UNITS.get(material, ("kt", 1.0))
        material_df = (
            df[df["materials"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        imported = material_df["material_imported"].values * multiplier
        mined = material_df["material_mined"].values * multiplier
        recycled = material_df["material_recycled"].values * multiplier
        demand = imported + mined + recycled

        axis.stackplot(
            years,
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
            years,
            demand,
            color=MATERIAL_COLORS["Demand"],
            linewidth=1.6,
            label="Annual demand",
        )

        # Clean title without the unit, regular font weight
        axis.set_title(f"{material.capitalize()}", fontsize=16)

        # Local labels for both axes on every subplot
        axis.set_ylabel(f"Material Demand ({unit})", fontsize=16)

        axis.set_xlim(start_year, end_year)
        axis.set_xticks(xticks)
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4))
        axis.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_axisbelow(True)

        # Readable tick parameters without being bold
        axis.tick_params(axis="both", which="major", labelsize=12)

    handles = [
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
        plt.Line2D([], [], color=MATERIAL_COLORS["Demand"], lw=2, label="Annual demand")
    ]

    # Legend remains large and clean with no border
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=13)

    # Adjusted the layout rectangle to account for the legend at the bottom and lack of main title
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.98))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Materials_Selected{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_basecase_materials_unit_group(df, unit_label, materials_in_group, start_year=2025, end_year=2050, suffix=""):
    """Plot dedicated grid for materials sharing the same unit (kt, t, or kg) for Demand and Sourcing."""
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    n_mats = len(materials_in_group)
    if n_mats <= 4:
        ncols = 2
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (12, 4 * nrows)
    elif n_mats <= 6:
        ncols = 3
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (14, 3.8 * nrows)
    else:
        ncols = 4
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (16, 3.8 * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
    axes_flat = axes.flat

    for idx, material in enumerate(materials_in_group):
        ax = axes_flat[idx]
        unit, multiplier = MATERIAL_UNITS.get(material, (unit_label, 1.0))
        material_df = (
            df[df["materials"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        imported = material_df["material_imported"].values * multiplier
        mined = material_df["material_mined"].values * multiplier
        recycled = material_df["material_recycled"].values * multiplier
        demand = imported + mined + recycled

        ax.stackplot(
            years,
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
        ax.plot(
            years,
            demand,
            color=MATERIAL_COLORS["Demand"],
            linewidth=1.6,
            label="Annual demand",
        )
        ax.set_title(material.capitalize())
        ax.set_xlim(start_year, end_year)
        ax.set_xticks(xticks)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    for ax in axes_flat[n_mats:]:
        ax.set_visible(False)

    handles = [

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
        plt.Line2D([], [], color=MATERIAL_COLORS["Demand"], lw=2, label="Annual demand")
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, fontsize=10)
    fig.suptitle(f"Material Demand and Sourcing – {unit_label.upper()} Materials ({start_year}–{end_year})", fontsize=13)
    fig.supxlabel("Year")
    fig.supylabel(f"Material quantity ({unit_label})")
    fig.tight_layout(rect=(0.04, 0.08, 1, 0.95))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Materials_{unit_label}{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_basecase_materials_all(df, start_year=2025, end_year=2050, suffix=""):
    """Plot all 17 CRMA materials for Demand and Sourcing ordered by unit (kt -> t -> kg)."""
    sorted_materials = sort_materials_by_unit(CRMA_MATERIALS)
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    ncols = 3
    nrows = int(np.ceil(len(sorted_materials) / ncols))
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(15, max(3.0 * nrows, 4)), squeeze=False
    )
    axes_flat = axes.flat

    for idx, material in enumerate(sorted_materials):
        ax = axes_flat[idx]
        unit, multiplier = MATERIAL_UNITS.get(material, ("kt", 1.0))
        material_df = (
            df[df["materials"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        imported = material_df["material_imported"].values * multiplier
        mined = material_df["material_mined"].values * multiplier
        recycled = material_df["material_recycled"].values * multiplier
        demand = imported + mined + recycled

        ax.stackplot(
            years,
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
        ax.plot(
            years,
            demand,
            color=MATERIAL_COLORS["Demand"],
            linewidth=1.6,
            label="Annual demand",
        )
        ax.set_title(f"{material.capitalize()} ({unit})")
        ax.set_xlim(start_year, end_year)
        ax.set_xticks(xticks)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    for ax in axes_flat[len(sorted_materials):]:
        ax.set_visible(False)

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
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, fontsize=11)
    fig.suptitle(f"Material Demand and Sourcing across All CRMA Materials ({start_year}–{end_year})", fontsize=14)
    fig.supxlabel("Year", fontsize=12)
    fig.supylabel("Material quantity (scaled per material unit)", fontsize=12)
    fig.tight_layout(rect=(0.04, 0.05, 1, 0.96))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Materials_All_Materials{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


# =====================================================================
# 3. AVAILABLE SCRAP & RECYCLING (UTILIZED SCRAP) PLOTS
# =====================================================================
def calculate_material_scrap(df_scrap, df_minerals, df_fractions, materials, start_year=2025, end_year=2050):
    """
    Calculate annual unused scrap stockpile and recycled material (utilized scrap) by material in kt.

    - unused_scrap: capacity_scrap_total [kt of equipment] * material_fraction [dimensionless]
    - material_recycled: pulled directly from sheet 'minerals' [kt]
    - total_available: unused_scrap + material_recycled [kt]
    """
    scrap = df_scrap.copy()
    scrap.columns = scrap.columns.astype(str).str.strip().str.lower()
    tech_column = _find_column(
        scrap.columns, ["tech", "technology"], "scrap technology"
    )
    quantity_column = _find_column(
        scrap.columns, ["capacity_scrap_total"], "total scrap capacity"
    )
    scrap["stf"] = pd.to_numeric(scrap["stf"].ffill(), errors="coerce")
    scrap["tech"] = scrap[tech_column].map(_normalise_key)
    scrap[quantity_column] = pd.to_numeric(
        scrap[quantity_column], errors="coerce"
    ).fillna(0)

    merged = scrap.merge(df_fractions, on="tech", how="inner")
    merged["unused_scrap"] = merged[quantity_column] * merged["fraction"]
    unused = (
        merged.groupby(["stf", "material"], as_index=False)["unused_scrap"]
        .sum()
    )

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

    years = np.arange(start_year, end_year + 1)
    materials = [m for m in materials if m]
    index = pd.MultiIndex.from_product(
        [years, materials], names=["stf", "material"]
    )
    result = (
        unused.set_index(["stf", "material"])
        .join(recycled.set_index(["stf", "material"]), how="outer")
        .reindex(index)
        .fillna(0)
        .reset_index()
    )
    result["total_available"] = result["unused_scrap"] + result["material_recycled"]
    return result


def plot_material_scrap_selected(df_scrap, df_minerals, df_fractions, start_year=2025, end_year=2050, suffix=""):
    """Plot 2x2 grid for selected materials with respective units (Aluminum, Copper, Neodymium, Silicon)."""
    material_scrap = calculate_material_scrap(
        df_scrap, df_minerals, df_fractions, MATERIALS_TO_PLOT, start_year=start_year, end_year=end_year
    )
    plot_data = material_scrap[material_scrap["stf"].between(start_year, end_year)]
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, squeeze=False)
    for axis, material in zip(axes.flat, MATERIALS_TO_PLOT):
        unit, multiplier = MATERIAL_UNITS.get(material, ("kt", 1.0))
        mat_data = (
            plot_data[plot_data["material"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        unused = mat_data["unused_scrap"].values * multiplier
        utilized = mat_data["material_recycled"].values * multiplier
        total = mat_data["total_available"].values * multiplier

        axis.stackplot(
            years,
            unused,
            utilized,
            colors=[UNUSED_SCRAP_COLOR, UTILIZED_SCRAP_COLOR],
            labels=["Unused Scrap", "Utilized Scrap"],
            edgecolor="black",
            linewidth=0.3,
        )
        axis.plot(
            years,
            total,
            color=TOTAL_SCRAP_LINE_COLOR,
            linewidth=1.2,
            label="Total Available Scrap Pool",
        )

        # Clean title without the unit, regular font weight
        axis.set_title(f"{material.capitalize()}", fontsize=16)

        # Local labels for both axes on every subplot
        axis.set_ylabel(f"Scrap ({unit})", fontsize=16)

        axis.set_xlim(start_year, end_year)
        axis.set_xticks(xticks)
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4))
        axis.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_axisbelow(True)

        # Readable tick parameters without being bold
        axis.tick_params(axis="both", which="major", labelsize=12)

    # Reverted handles back to the original variables
    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UNUSED_SCRAP_COLOR, edgecolor="black",
            label="Unused Scrap",
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UTILIZED_SCRAP_COLOR, edgecolor="black",
            label="Utilized Scrap",
        ),
        plt.Line2D([], [], color=TOTAL_SCRAP_LINE_COLOR, lw=1.5, label="Total Available Scrap Pool"),
    ]

    # Legend remains large and clean with no border
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=13)

    # Adjusted the layout rectangle to account for the legend at the bottom
    fig.tight_layout(rect=(0.02, 0.08, 0.98, 0.98))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Material_Scrap_Selected{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_material_scrap_unit_group(df_scrap, df_minerals, df_fractions, unit_label, materials_in_group, start_year=2025, end_year=2050, suffix=""):
    """Plot a dedicated grid for materials sharing the same unit (kt, t, or kg)."""
    material_scrap = calculate_material_scrap(
        df_scrap, df_minerals, df_fractions, materials_in_group, start_year=start_year, end_year=end_year
    )
    plot_data = material_scrap[material_scrap["stf"].between(start_year, end_year)]
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    n_mats = len(materials_in_group)
    if n_mats <= 4:
        ncols = 2
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (12, 4 * nrows)
    elif n_mats <= 6:
        ncols = 3
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (14, 3.8 * nrows)
    else:
        ncols = 4
        nrows = int(np.ceil(n_mats / ncols))
        figsize = (16, 3.8 * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
    axes_flat = axes.flat

    for idx, material in enumerate(materials_in_group):
        ax = axes_flat[idx]
        unit, multiplier = MATERIAL_UNITS.get(material, (unit_label, 1.0))
        mat_data = (
            plot_data[plot_data["material"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        unused = mat_data["unused_scrap"].values * multiplier
        utilized = mat_data["material_recycled"].values * multiplier
        total = mat_data["total_available"].values * multiplier

        ax.stackplot(
            years,
            unused,
            utilized,
            colors=[UNUSED_SCRAP_COLOR, UTILIZED_SCRAP_COLOR],
            labels=["Unused Scrap", "Utilized Scrap"],
            edgecolor="black",
            linewidth=0.3,
        )
        ax.plot(
            years,
            total,
            color=TOTAL_SCRAP_LINE_COLOR,
            linewidth=1.2,
            label="Total Available Scrap Pool",
        )
        ax.set_title(material.capitalize())
        ax.set_xlim(start_year, end_year)
        ax.set_xticks(xticks)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    for ax in axes_flat[n_mats:]:
        ax.set_visible(False)

    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UNUSED_SCRAP_COLOR, edgecolor="black",
            label="Unused Scrap",
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UTILIZED_SCRAP_COLOR, edgecolor="black",
            label="Utilized Scrap",
        ),
        plt.Line2D([], [], color=TOTAL_SCRAP_LINE_COLOR, lw=1.5, label="Total Available Scrap Pool"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=True, fontsize=10)
    fig.suptitle(f"Cumulative Available Scrap and Recycling – {unit_label.upper()} Materials ({start_year}–{end_year})", fontsize=13)
    fig.supxlabel("Year")
    fig.supylabel(f"Material quantity ({unit_label})")
    fig.tight_layout(rect=(0.04, 0.08, 1, 0.95))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Material_Scrap_{unit_label}{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_material_scrap_all(df_scrap, df_minerals, df_fractions, materials, start_year=2025, end_year=2050, suffix=""):
    """Plot all CRMA materials ordered by unit (kt -> t -> kg) with properly scaled values."""
    crma_mats = [m for m in materials if m in CRMA_MATERIALS]
    sorted_materials = sort_materials_by_unit(crma_mats)

    material_scrap = calculate_material_scrap(
        df_scrap, df_minerals, df_fractions, sorted_materials, start_year=start_year, end_year=end_year
    )
    plot_data = material_scrap[material_scrap["stf"].between(start_year, end_year)]
    years = np.arange(start_year, end_year + 1)
    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]

    ncols = 3
    nrows = int(np.ceil(len(sorted_materials) / ncols))
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(15, max(3.0 * nrows, 4)), squeeze=False
    )
    axes_flat = axes.flat
    for idx, material in enumerate(sorted_materials):
        ax = axes_flat[idx]
        unit, multiplier = MATERIAL_UNITS.get(material, ("kt", 1.0))
        mat_data = (
            plot_data[plot_data["material"] == material]
            .set_index("stf")
            .reindex(years)
            .fillna(0)
        )
        unused = mat_data["unused_scrap"].values * multiplier
        utilized = mat_data["material_recycled"].values * multiplier
        total = mat_data["total_available"].values * multiplier

        ax.stackplot(
            years,
            unused,
            utilized,
            colors=[UNUSED_SCRAP_COLOR, UTILIZED_SCRAP_COLOR],
            labels=["Unused Scrap", "Utilized Scrap"],
            edgecolor="black",
            linewidth=0.3,
        )
        ax.plot(
            years,
            total,
            color=TOTAL_SCRAP_LINE_COLOR,
            linewidth=1.2,
            label="Total Available Scrap Pool",
        )
        ax.set_title(f"{material.capitalize()} ({unit})")
        ax.set_xlim(start_year, end_year)
        ax.set_xticks(xticks)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    for ax in axes_flat[len(sorted_materials):]:
        ax.set_visible(False)

    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UNUSED_SCRAP_COLOR, edgecolor="black",
            label="Unused Scrap",
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=UTILIZED_SCRAP_COLOR, edgecolor="black",
            label="Utilized Scrap",
        ),
        plt.Line2D([], [], color=TOTAL_SCRAP_LINE_COLOR, lw=1.5, label="Total Available Scrap Pool"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=True, fontsize=11)
    fig.suptitle(f"Cumulative Available Scrap and Recycling across CRMA Materials ({start_year}–{end_year})", fontsize=14)
    fig.supxlabel("Year", fontsize=12)
    fig.supylabel("Material quantity (scaled per material unit)", fontsize=12)
    fig.tight_layout(rect=(0.04, 0.05, 1, 0.96))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_Material_Scrap_All_Materials{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_material_scrap(df_scrap, df_minerals, df_fractions_or_intensity, materials=None, start_year=2025, end_year=2050, suffix=""):
    """
    Generate material scrap plots for selected key materials, unit groups (kt, t, kg), and all CRMA materials.
    """
    if not isinstance(df_fractions_or_intensity, pd.DataFrame) or "fraction" not in df_fractions_or_intensity.columns:
        df_fractions = load_material_fractions()
    else:
        df_fractions = df_fractions_or_intensity

    # 1. 2x2 Selected materials (Aluminum [kt], Copper [kt], Neodymium [t], Silicon [kt])
    plot_material_scrap_selected(df_scrap, df_minerals, df_fractions, start_year=start_year, end_year=end_year, suffix=suffix)

    # 2. Grouped plots by unit: kt, t, kg
    plot_material_scrap_unit_group(df_scrap, df_minerals, df_fractions, "kt", KT_MATERIALS, start_year=start_year, end_year=end_year, suffix=suffix)
    plot_material_scrap_unit_group(df_scrap, df_minerals, df_fractions, "t", T_MATERIALS, start_year=start_year, end_year=end_year, suffix=suffix)
    plot_material_scrap_unit_group(df_scrap, df_minerals, df_fractions, "kg", KG_MATERIALS, start_year=start_year, end_year=end_year, suffix=suffix)

    # 3. All CRMA materials matrix
    if materials is None:
        materials = load_materials()
    plot_material_scrap_all(df_scrap, df_minerals, df_fractions, materials, start_year=start_year, end_year=end_year, suffix=suffix)


# =====================================================================
# 4. SOURCING / SUPPLY MIX HELPER FUNCTION
# =====================================================================
def load_supply_mix_data(file_path):
    """Load and merge supply_mix, net_domestic_production, and net_domestic_stockout sheets."""

    def load_sheet(sheet_name, value_col_name):
        df = read_excel_safe(file_path, sheet_name=sheet_name)
        df.columns = df.columns.str.lower()
        df["stf"] = df["stf"].ffill()
        if "location" in df.columns:
            df["location"] = df["location"].ffill()
        df["tech"] = df["tech"].ffill()
        df["tech"] = df["tech"].astype(str).str.strip()
        df["stages"] = df["stages"].astype(str).str.strip()
        df["stf"] = pd.to_numeric(df["stf"], errors="coerce")
        keys = ["stf", "location", "tech", "stages"]
        val_col = [c for c in df.columns if c not in keys][0]
        df[val_col] = pd.to_numeric(df[val_col], errors="coerce").fillna(0)
        return df[["stf", "tech", "stages", val_col]].rename(columns={val_col: value_col_name})

    df_total = load_sheet("supply_mix", "Total")
    df_prod = load_sheet("net_domestic_production", "capacity_produced_flow")
    df_stock = load_sheet("net_domestic_stockout", "capacity_produced_stockout")

    merged = pd.merge(df_total, df_prod, on=["stf", "tech", "stages"], how="outer")
    merged = pd.merge(merged, df_stock, on=["stf", "tech", "stages"], how="outer").fillna(0)

    # Merge flow and stockout into a single Domestic Production variable
    merged["Domestic Production"] = merged["capacity_produced_flow"] + merged["capacity_produced_stockout"]

    # Calculate Imported as Total minus Domestic
    merged["Imported"] = (merged["Total"] - merged["Domestic Production"]).clip(lower=0)

    return merged


def plot_supply_mix_tech_periods(df_supply, tech, stages, suffix=""):
    """Plot a 2-row grid (Top: Absolute, Bottom: Relative 100%) for a single technology across its periods."""
    # Dropped 2046-2050 to avoid end-of-horizon effects
    period_labels = ["2025-2030", "2031-2035", "2036-2040", "2041-2045"]
    x_indices = np.arange(len(period_labels))
    bar_width = 0.6

    # 1. Helper function to map individual years to your specific periods
    def map_year_to_period(y):
        if 2025 <= y <= 2030:
            return "2025-2030"
        elif 2031 <= y <= 2035:
            return "2031-2035"
        elif 2036 <= y <= 2040:
            return "2036-2040"
        elif 2041 <= y <= 2045:
            return "2041-2045"
        # 2046 and beyond will return None and be filtered out
        return None

    # 2. Filter for tech, map years to periods, and SUM the data
    df_plot = df_supply[(df_supply["tech"] == tech) & (df_supply["stages"].isin(stages))].copy()
    df_plot["period"] = df_plot["stf"].apply(map_year_to_period)

    # Drop years outside our scope (including 2046-2050), then group by stage and period, and sum
    df_grouped = (
        df_plot.dropna(subset=["period"])
        .groupby(["stages", "period"])[["Domestic Production", "Imported"]]
        .sum()
        .reset_index()
    )

    n_stages = len(stages)
    ncols = n_stages
    nrows = 2
    figsize = (4.5 * ncols, 7.5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True, squeeze=False)
    tech_title = TECH_DISPLAY_NAMES.get(tech, tech)

    for col_idx, stage in enumerate(stages):
        ax_abs = axes[0, col_idx]
        ax_rel = axes[1, col_idx]

        # Extract summed data for this stage and enforce period order
        df_stage = (
            df_grouped[df_grouped["stages"] == stage]
            .set_index("period")
            .reindex(period_labels)
            .fillna(0)
        )

        dom = df_stage["Domestic Production"].values
        imp = df_stage["Imported"].values
        total = dom + imp

        # ==========================================
        # TOP ROW: Absolute Capacity (Summed)
        # ==========================================
        ax_abs.bar(
            x_indices, dom, width=bar_width,
            color=SUPPLY_MIX_COLORS.get("Domestic Production", "#AA96DA"),
            edgecolor="black", linewidth=0.5
        )
        ax_abs.bar(
            x_indices, imp, bottom=dom, width=bar_width,
            color=SUPPLY_MIX_COLORS.get("Imported", "#ff7f0e"),
            edgecolor="black", linewidth=0.5
        )

        stage_name = STAGE_LABELS.get(stage, stage)
        ax_abs.set_title(stage_name, fontsize=14)

        if col_idx == 0:
            ax_abs.set_ylabel("Capacity (GW)", fontsize=13)

        ax_abs.yaxis.set_major_locator(MaxNLocator(nbins=5))
        ax_abs.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
        ax_abs.grid(axis="y", linestyle="--", alpha=0.35)
        ax_abs.set_axisbelow(True)

        # ==========================================
        # BOTTOM ROW: Relative Share (%)
        # ==========================================
        pct_dom = np.zeros(len(period_labels))
        pct_imp = np.zeros(len(period_labels))

        for j in range(len(total)):
            if total[j] > 0:
                pct_dom[j] = (dom[j] / total[j]) * 100.0
                pct_imp[j] = (imp[j] / total[j]) * 100.0

        ax_rel.bar(
            x_indices, pct_dom, width=bar_width,
            color=SUPPLY_MIX_COLORS.get("Domestic Production", "#AA96DA"),
            edgecolor="black", linewidth=0.5
        )
        ax_rel.bar(
            x_indices, pct_imp, bottom=pct_dom, width=bar_width,
            color=SUPPLY_MIX_COLORS.get("Imported", "#ff7f0e"),
            edgecolor="black", linewidth=0.5
        )

        # NZIA Benchmark line
        ax_rel.axhline(40, color="red", linestyle="--", linewidth=1.8, zorder=5)

        if col_idx == 0:
            ax_rel.set_ylabel("% of Total Additions", fontsize=13)

        ax_rel.set_ylim(0, 100)
        ax_rel.yaxis.set_major_formatter(PercentFormatter())
        ax_rel.yaxis.set_major_locator(MultipleLocator(20))
        ax_rel.grid(axis="y", linestyle="--", alpha=0.35)
        ax_rel.set_axisbelow(True)

        # Bottom axis labels
        ax_rel.set_xticks(x_indices)
        ax_rel.set_xticklabels(period_labels, rotation=45, ha="right", fontsize=11)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS.get("Domestic Production", "#AA96DA"),
                      edgecolor="black", label="Domestic Production"),
        plt.Rectangle((0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS.get("Imported", "#ff7f0e"), edgecolor="black",
                      label="Imported"),
        plt.Line2D([0], [0], color="red", linestyle="--", linewidth=1.8, label="NZIA Benchmark")
    ]

    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=13)
    fig.tight_layout(rect=(0.02, 0.12, 0.98, 0.98))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_SupplyMix_Stacked_{tech}{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)

def plot_supply_mix_all_technologies(df_supply, start_year=2025, end_year=2050, suffix=""):
    """Plot combined AbsoluteBars for all three core technologies (solarPV, windon, windoff) in a unified layout."""
    years_to_plot = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]
    bar_width = 2.5

    # 3 rows: solarPV (4 stages), windon (3 stages), windoff (3 stages) -> 3 rows, 4 columns
    nrows = 3
    ncols = 4
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 11), squeeze=False)

    techs = [("solarPV", TECH_STAGE_MAP["solarPV"]),
             ("windon", TECH_STAGE_MAP["windon"]),
             ("windoff", TECH_STAGE_MAP["windoff"])]

    for row_idx, (tech, stages) in enumerate(techs):
        tech_title = TECH_DISPLAY_NAMES.get(tech, tech)
        for col_idx in range(ncols):
            ax = axes[row_idx, col_idx]
            if col_idx < len(stages):
                stage = stages[col_idx]
                df_stage = (
                    df_supply[(df_supply["tech"] == tech) & (df_supply["stages"] == stage)]
                    .set_index("stf")
                    .reindex(years_to_plot)
                    .fillna(0)
                )
                prod = df_stage["capacity_produced_flow"].values
                stock = df_stage["capacity_produced_stockout"].values
                imp = df_stage["Imported"].values

                ax.bar(
                    years_to_plot, prod, width=bar_width,
                    color=SUPPLY_MIX_COLORS["capacity_produced_flow"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )
                ax.bar(
                    years_to_plot, stock, bottom=prod, width=bar_width,
                    color=SUPPLY_MIX_COLORS["capacity_produced_stockout"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )
                ax.bar(
                    years_to_plot, imp, bottom=prod + stock, width=bar_width,
                    color=SUPPLY_MIX_COLORS["Imported"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )
                stage_name = STAGE_LABELS.get(stage, stage)
                ax.set_title(f"{tech_title}: {stage_name}", fontsize=11)
                ax.set_xlim(start_year - 2.5, end_year + 2.5)
                ax.set_xticks(years_to_plot)
                ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
                ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))
                ax.grid(axis="y", linestyle="--", alpha=0.35)
                ax.set_axisbelow(True)
                if col_idx == 0:
                    ax.set_ylabel("Capacity (GW)")
            else:
                ax.set_visible(False)

    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_flow"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_flow"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_stockout"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_stockout"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["Imported"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["Imported"],
        ),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=True, fontsize=11)
    fig.suptitle(f"Component Sourcing Mix (Supply Mix) Across Core Technologies ({start_year}–{end_year})", fontsize=14)
    fig.supxlabel("Year", fontsize=12)
    fig.tight_layout(rect=(0.03, 0.05, 1, 0.96))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_SupplyMix_AbsoluteBars_All{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_supply_mix_tech_100bars(df_supply, tech, stages, start_year=2025, end_year=2040, suffix="_2040"):
    """Plot 100% stacked bars with 40% benchmark line for a single technology across its stages."""
    years_to_plot = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]
    bar_width = 2.5

    n_stages = len(stages)
    if n_stages == 4:
        ncols = 2
        nrows = 2
        figsize = (12, 8)
    else:
        ncols = 3
        nrows = 1
        figsize = (14, 4.5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
    axes_flat = axes.flat

    tech_title = TECH_DISPLAY_NAMES.get(tech, tech)

    for idx, stage in enumerate(stages):
        ax = axes_flat[idx]
        df_stage = (
            df_supply[(df_supply["tech"] == tech) & (df_supply["stages"] == stage)]
            .set_index("stf")
            .reindex(years_to_plot)
            .fillna(0)
        )

        pct_prod = np.zeros(len(years_to_plot))
        pct_stock = np.zeros(len(years_to_plot))
        pct_imp = np.zeros(len(years_to_plot))

        for j, year in enumerate(years_to_plot):
            prod = df_stage.loc[year, "capacity_produced_flow"]
            stock = df_stage.loc[year, "capacity_produced_stockout"]
            imp = df_stage.loc[year, "Imported"]
            total = prod + stock + imp
            if total > 0:
                pct_prod[j] = (prod / total) * 100.0
                pct_stock[j] = (stock / total) * 100.0
                pct_imp[j] = (imp / total) * 100.0

        ax.bar(
            years_to_plot,
            pct_prod,
            width=bar_width,
            color=SUPPLY_MIX_COLORS["capacity_produced_flow"],
            edgecolor="black",
            linewidth=0.5,
            zorder=2,
            label=SUPPLY_MIX_LABELS["capacity_produced_flow"],
        )
        ax.bar(
            years_to_plot,
            pct_stock,
            bottom=pct_prod,
            width=bar_width,
            color=SUPPLY_MIX_COLORS["capacity_produced_stockout"],
            edgecolor="black",
            linewidth=0.5,
            zorder=2,
            label=SUPPLY_MIX_LABELS["capacity_produced_stockout"],
        )
        ax.bar(
            years_to_plot,
            pct_imp,
            bottom=pct_prod + pct_stock,
            width=bar_width,
            color=SUPPLY_MIX_COLORS["Imported"],
            edgecolor="black",
            linewidth=0.5,
            zorder=2,
            label=SUPPLY_MIX_LABELS["Imported"],
        )

        # 40% benchmark red dotted line
        ax.axhline(40, color="red", linestyle=":", linewidth=1.5, zorder=5, label="40% Benchmark")

        stage_name = STAGE_LABELS.get(stage, stage)
        ax.set_title(stage_name, fontsize=12)
        ax.set_xlim(start_year - 2.5, end_year + 2.5)
        ax.set_xticks(years_to_plot)
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.set_ylabel("Share (%)")
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_flow"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_flow"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_stockout"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_stockout"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["Imported"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["Imported"],
        ),
        plt.Line2D([0], [0], color="red", linestyle=":", linewidth=1.5, label="40% Benchmark"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, fontsize=10)
    fig.suptitle(f"{tech_title} Supply Mix Sourcing Shares (100% Stacked, {start_year}–{end_year})", fontsize=14)
    fig.supxlabel("Year", fontsize=12)
    fig.tight_layout(rect=(0.04, 0.08, 1, 0.95))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_SupplyMix_100Bars_{tech}{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


def plot_supply_mix_all_100bars(df_supply, start_year=2025, end_year=2040, suffix="_2040"):
    """Plot combined 100% stacked bars with 40% benchmark line for all three core technologies."""
    years_to_plot = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if start_year <= y <= end_year]
    bar_width = 2.5

    nrows = 3
    ncols = 4
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 11), squeeze=False)

    techs = [
        ("solarPV", TECH_STAGE_MAP["solarPV"]),
        ("windon", TECH_STAGE_MAP["windon"]),
        ("windoff", TECH_STAGE_MAP["windoff"]),
    ]

    for row_idx, (tech, stages) in enumerate(techs):
        tech_title = TECH_DISPLAY_NAMES.get(tech, tech)
        for col_idx in range(ncols):
            ax = axes[row_idx, col_idx]
            if col_idx < len(stages):
                stage = stages[col_idx]
                df_stage = (
                    df_supply[(df_supply["tech"] == tech) & (df_supply["stages"] == stage)]
                    .set_index("stf")
                    .reindex(years_to_plot)
                    .fillna(0)
                )

                pct_prod = np.zeros(len(years_to_plot))
                pct_stock = np.zeros(len(years_to_plot))
                pct_imp = np.zeros(len(years_to_plot))

                for j, year in enumerate(years_to_plot):
                    prod = df_stage.loc[year, "capacity_produced_flow"]
                    stock = df_stage.loc[year, "capacity_produced_stockout"]
                    imp = df_stage.loc[year, "Imported"]
                    total = prod + stock + imp
                    if total > 0:
                        pct_prod[j] = (prod / total) * 100.0
                        pct_stock[j] = (stock / total) * 100.0
                        pct_imp[j] = (imp / total) * 100.0

                ax.bar(
                    years_to_plot, pct_prod, width=bar_width,
                    color=SUPPLY_MIX_COLORS["capacity_produced_flow"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )
                ax.bar(
                    years_to_plot, pct_stock, bottom=pct_prod, width=bar_width,
                    color=SUPPLY_MIX_COLORS["capacity_produced_stockout"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )
                ax.bar(
                    years_to_plot, pct_imp, bottom=pct_prod + pct_stock, width=bar_width,
                    color=SUPPLY_MIX_COLORS["Imported"],
                    edgecolor="black", linewidth=0.5, zorder=2,
                )

                # 40% benchmark line
                ax.axhline(40, color="red", linestyle=":", linewidth=1.5, zorder=5)

                stage_name = STAGE_LABELS.get(stage, stage)
                ax.set_title(f"{tech_title}: {stage_name}", fontsize=11)
                ax.set_xlim(start_year - 2.5, end_year + 2.5)
                ax.set_xticks(years_to_plot)
                ax.set_ylim(0, 100)
                ax.yaxis.set_major_formatter(PercentFormatter())
                ax.yaxis.set_major_locator(MultipleLocator(20))
                ax.grid(axis="y", linestyle="--", alpha=0.35)
                ax.set_axisbelow(True)
                if col_idx == 0:
                    ax.set_ylabel("Share (%)")
            else:
                ax.set_visible(False)

    handles = [
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_flow"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_flow"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["capacity_produced_stockout"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["capacity_produced_stockout"],
        ),
        plt.Rectangle(
            (0, 0), 1, 1, facecolor=SUPPLY_MIX_COLORS["Imported"], edgecolor="black",
            label=SUPPLY_MIX_LABELS["Imported"],
        ),
        plt.Line2D([0], [0], color="red", linestyle=":", linewidth=1.5, label="40% Benchmark"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, fontsize=11)
    fig.suptitle(f"Component Sourcing Mix Shares (100% Stacked) Across Core Technologies ({start_year}–{end_year})", fontsize=14)
    fig.supxlabel("Year", fontsize=12)
    fig.tight_layout(rect=(0.03, 0.05, 1, 0.96))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"Fig_Basecase_SupplyMix_100Bars_All{suffix}.pdf"
    fig.savefig(OUTPUT_DIR / out_name, bbox_inches="tight")
    plt.close(fig)


# =====================================================================
# 5. MAIN EXECUTION PIPELINE
# =====================================================================
if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Electricity Generation & Capacity
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

    # 2. Material Demand & Sourcing Plots
    minerals_data = load_basecase_minerals()
    for end_yr, sfx in [(2050, ""), (2040, "_2040")]:
        plot_basecase_materials(minerals_data, start_year=2025, end_year=end_yr, suffix=sfx)
        plot_basecase_materials_unit_group(minerals_data, "kt", KT_MATERIALS, start_year=2025, end_year=end_yr, suffix=sfx)
        plot_basecase_materials_unit_group(minerals_data, "t", T_MATERIALS, start_year=2025, end_year=end_yr, suffix=sfx)
        plot_basecase_materials_unit_group(minerals_data, "kg", KG_MATERIALS, start_year=2025, end_year=end_yr, suffix=sfx)
        plot_basecase_materials_all(minerals_data, start_year=2025, end_year=end_yr, suffix=sfx)

    # 3. Available Scrap & Recycling (Utilized Scrap) Plots
    scrap = read_excel_safe(FILE_PATH, sheet_name="scrap")
    minerals = read_excel_safe(FILE_PATH, sheet_name="minerals")
    df_fractions = load_material_fractions()
    for end_yr, sfx in [(2050, ""), (2040, "_2040")]:
        plot_material_scrap(scrap, minerals, df_fractions, load_materials(), start_year=2025, end_year=end_yr, suffix=sfx)

    # 4. Component Sourcing Mix / Supply Mix (Exclusively until 2040 as requested)
    df_supply = load_supply_mix_data(FILE_PATH)
    for tech, stages in TECH_STAGE_MAP.items():
        # AbsoluteBars (GW)
        plot_supply_mix_tech_periods(df_supply, tech, stages,suffix="_2040")


    # Combined Multi-Panel Figures (All Technologies until 2040)
    #plot_supply_mix_all_technologies(df_supply, start_year=2025, end_year=2040, suffix="_2040")
    #plot_supply_mix_all_100bars(df_supply, start_year=2025, end_year=2040, suffix="_2040")

    print("All basecase final plots generated successfully in:", OUTPUT_DIR)
