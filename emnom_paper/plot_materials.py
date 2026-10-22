import os
import math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import (
    StrMethodFormatter,
    MultipleLocator,
    AutoMinorLocator,
    MaxNLocator,
)
import numpy as np
import pandas as pd

# ==========================================
# Setup matplotlib style (Science / IEEE)
# ==========================================
plt.rcParams.update(
    {
        "text.usetex": False,
        "font.family": "serif",
        "pgf.rcfonts": False,
    }
)
try:
    plt.style.use(["science", "ieee", "no-latex"])
except Exception:
    pass

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ================= KONFIGURATION =================
BASE_DIR = Path("result/results_server_201026")
SCENARIO_LR4 = "LR4_nzia_40_crma_25_materials_base"
FILE_PATH = BASE_DIR / SCENARIO_LR4 / f"{SCENARIO_LR4}.xlsx"
PLOT_OUTPUT_DIR = Path("plots/materials")

# Column headers for our Scenarios
SCENARIOS = ["LR1", "LR4", "LR7"]

# CRMA Target Materials List
CRMA_TARGET_MATERIALS = [
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

# User-defined color palette
MAT_COLORS = {
    "Imported": "#F5E0B7",
    "Mined": "#8BBF9F",
    "Recycled": "#D6BA73",
    "Demand": "red",
}


# ================= DATEN LADEN & FILTERN =================
def load_minerals_data(file_path, start_year=2025, end_year=2040):
    print(f"Lade Mineralien-Daten aus: {file_path}")
    df = pd.read_excel(file_path, sheet_name="minerals")
    df.columns = df.columns.str.lower()

    df["stf"] = df["stf"].ffill()
    df["stf"] = pd.to_numeric(df["stf"], errors="coerce")
    df["materials"] = df["materials"].astype(str).str.strip().str.lower()
    df = df[(df["stf"] >= start_year) & (df["stf"] <= end_year)]
    return df


def determine_scale(max_value):
    if max_value > 1.0:
        return 1.0, "kt"
    elif max_value > 0.001:
        return 1000.0, "t"
    else:
        return 1000000.0, "kg"


# ================= MASSIVE MATRIX PLOTTING =================
def plot_materials_scenario_matrix(
    df_list, scenario_names, output_filename="Fig_Massive_Scenario_Matrix.pdf"
):
    print("\n📊 Generating Massive Matrix Plot...")

    # 1. Determine scaling based on the Baseline (LR4) data which is df_list[1]
    df_base = df_list[1]
    df_base = df_base[df_base["materials"].isin(CRMA_TARGET_MATERIALS)]

    mat_meta = []
    for mat in df_base["materials"].unique():
        df_mat = df_base[df_base["materials"] == mat]
        max_demand = (
            df_mat[["material_imported", "material_mined", "material_recycled"]]
            .sum(axis=1)
            .max()
        )
        multiplier, unit = determine_scale(max_demand)
        mat_meta.append({"name": mat, "multiplier": multiplier, "unit": unit})

    # Sort materials by Unit (kt -> t -> kg), then alphabetically
    unit_order = {"kt": 0, "t": 1, "kg": 2}
    sorted_materials = sorted(
        mat_meta, key=lambda m: (unit_order.get(m["unit"], 3), m["name"])
    )

    # 2. Setup Figure: Rows = Materials, Cols = Scenarios
    n_rows = len(sorted_materials)
    n_cols = len(scenario_names)

    # figsize height dynamically scales with the number of materials
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(14, 2.5 * n_rows), sharex=True, sharey="row"
    )

    target_years = [2025, 2030, 2035, 2040]
    all_years = np.arange(2025, 2041)

    # 3. Iterate through Grid
    for i, meta in enumerate(sorted_materials):
        mat_name = meta["name"]
        unit = meta["unit"]
        multiplier = meta["multiplier"]

        # Calculate maximum Y across ALL scenarios for this specific material row
        row_max_y = 0
        for df in df_list:
            df_mat = (
                df[df["materials"] == mat_name]
                .set_index("stf")
                .reindex(all_years)
                .fillna(0)
            )
            y_tot = (
                df_mat["material_imported"]
                + df_mat["material_mined"]
                + df_mat["material_recycled"]
            ) * multiplier
            row_max_y = max(row_max_y, y_tot.max())

        # Iterate over columns (scenarios)
        for j, (df_scen, scen_name) in enumerate(zip(df_list, scenario_names)):
            ax = axs[i, j]

            # Extract data
            df_mat = (
                df_scen[df_scen["materials"] == mat_name]
                .set_index("stf")
                .reindex(all_years)
                .fillna(0)
            )
            y_imp = df_mat["material_imported"].values * multiplier
            y_min = df_mat["material_mined"].values * multiplier
            y_rec = df_mat["material_recycled"].values * multiplier
            y_tot = y_imp + y_min + y_rec

            # Plot Stacked Area (Z-order = 1)
            ax.stackplot(
                all_years,
                y_imp,
                y_min,
                y_rec,
                labels=["Imported", "Mined", "Recycled"],
                colors=[
                    MAT_COLORS["Imported"],
                    MAT_COLORS["Mined"],
                    MAT_COLORS["Recycled"],
                ],
                edgecolor="black",
                linewidth=0.5,
                zorder=1,
            )

            # Plot Annual Demand Line (Z-order = 2)
            ax.plot(
                all_years, y_tot, color=MAT_COLORS["Demand"], linewidth=1.8, zorder=2
            )

            # Aesthetics & Limits
            ax.set_xlim(2025, 2040)
            if row_max_y > 0:
                ax.set_ylim(0, row_max_y * 1.15)

            # Grid & Layering
            ax.grid(False)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.1f}"))

            major_yticks = ax.yaxis.get_majorticklocs()
            for y in major_yticks:
                if 0 < y < (row_max_y * 1.15 if row_max_y > 0 else 1):
                    ax.axhline(
                        y,
                        color="gray",
                        linestyle="--",
                        linewidth=0.6,
                        alpha=0.4,
                        zorder=0,
                    )

            ax.set_axisbelow(False)
            ax.set_xticks(target_years)

            # Ticks formatting - Added labelrotation=45 to tilt the years
            ax.tick_params(
                axis="both",
                which="major",
                direction="in",
                length=4,
                labelsize=9,
                top=True,
                right=True,
            )
            ax.tick_params(axis="x", which="major", labelrotation=45)
            ax.tick_params(
                axis="both",
                which="minor",
                direction="in",
                length=2,
                top=True,
                right=True,
            )
            ax.xaxis.set_minor_locator(MultipleLocator(1))

            # Column Titles (Top Row only)
            if i == 0:
                ax.set_title(scen_name, fontsize=14, weight="bold", pad=15)

            # Row Titles (Leftmost Column only - Removed "Demand")
            if j == 0:
                ax.set_ylabel(
                    f"{mat_name.capitalize()}\n({unit})",
                    fontsize=11,
                    weight="bold",
                    labelpad=10,
                )

    # 4. Global Legend (At the bottom of the entire matrix)
    handles = [
        plt.Line2D([], [], color=MAT_COLORS["Demand"], lw=2, label="Annual Demand"),
        plt.Rectangle(
            (0, 0),
            1,
            1,
            facecolor=MAT_COLORS["Imported"],
            edgecolor="black",
            label="Imported",
        ),
        plt.Rectangle(
            (0, 0),
            1,
            1,
            facecolor=MAT_COLORS["Mined"],
            edgecolor="black",
            label="Mined",
        ),
        plt.Rectangle(
            (0, 0),
            1,
            1,
            facecolor=MAT_COLORS["Recycled"],
            edgecolor="black",
            label="Recycled",
        ),
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=True,
        facecolor="white",
        edgecolor="black",
        fontsize=12,
        bbox_to_anchor=(0.5, 0.005),
    )

    plt.tight_layout()
    # Adjust spacing: hspace handles space between rows, bottom handles space for legend
    plt.subplots_adjust(
        top=0.97, bottom=max(0.06, 0.6 / n_rows), hspace=0.15, wspace=0.08
    )

    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = PLOT_OUTPUT_DIR / output_filename
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"   ✔ Massive Matrix saved -> {out_file}")


# ================= EXECUTION =================
if __name__ == "__main__":
    if not FILE_PATH.exists():
        print(f"❌ Datei nicht gefunden: {FILE_PATH}\nBitte Pfad prüfen.")
    else:
        # Load the base dataframe
        df_base = load_minerals_data(FILE_PATH, start_year=2025, end_year=2040)

        if not df_base.empty:
            # Mock the 3 scenarios by duplicating the base df (Replace with actual data later)
            df_list = [df_base, df_base, df_base]

            plot_materials_scenario_matrix(df_list, SCENARIOS)
