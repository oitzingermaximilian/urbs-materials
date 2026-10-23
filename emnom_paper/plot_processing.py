import os
import math
from pathlib import Path
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib.ticker import (
    StrMethodFormatter,
    MultipleLocator,
    AutoMinorLocator,
    MaxNLocator,
)
import numpy as np
import pandas as pd
from scenario_config import (
    LEARNING_RATES,
    MATERIAL_SCENARIOS,
    scenario_file,
)

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
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR / "result" / "results_server_201026"

PLOT_OUTPUT_DIR = PROJECT_DIR / "plots/processing"

YEARS_TO_PLOT = [2030, 2035, 2040, 2045, 2050]
SHEET_NAME = "processing_capacities"

# Tech -> Stage mapping
TECH_STAGE_MAP = {
    "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
    "windon": ["BladeOn", "TowerOn", "NacelleOn"],
    "windoff": ["BladeOff", "TowerOff", "NacelleOff"],
}

SCENARIO_ORDER = ["LR1_Slow", "LR4_Base", "LR7_Fast"]

# UPDATED: High-Tech / Policy Palette
SCENARIO_COLORS = {
    "LR1_Slow": "#701A75",  # Deep Plum
    "LR4_Base": "#0F172A",  # Rich Slate
    "LR7_Fast": "#0284C7",  # Vibrant Azure
}

SCENARIO_LABELS = {
    "LR1_Slow": "LR1",
    "LR4_Base": "LR4",
    "LR7_Fast": "LR7",
}


# ================= DATEN LADEN =================
def load_processing_data(file_path):
    print(f"Lade Processing-Daten aus: {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    except ValueError:
        df = pd.read_excel(file_path, sheet_name="processing_capacity")

    df.columns = df.columns.str.lower()
    df["stf"] = df["stf"].ffill()
    if "location" in df.columns:
        df["location"] = df["location"].ffill()
    df["tech"] = df["tech"].ffill()

    df["tech"] = df["tech"].astype(str).str.strip()
    df["stages"] = df["stages"].astype(str).str.strip()

    df["stf"] = pd.to_numeric(df["stf"], errors="coerce")
    df["capacity_processing_total"] = pd.to_numeric(
        df["capacity_processing_total"], errors="coerce"
    )
    return df


def get_pivot_for_tech(df, tech, stages):
    df_tech = df[(df["tech"] == tech) & (df["stages"].isin(stages))]
    if df_tech.empty:
        return pd.DataFrame()
    df_pivot = df_tech.pivot_table(
        index="stf", columns="stages", values="capacity_processing_total", aggfunc="sum"
    ).fillna(0)
    for stage in stages:
        if stage not in df_pivot.columns:
            df_pivot[stage] = 0
    return df_pivot


# ================= OPTION 1: TRAJECTORY GRID =================
def create_trajectory_plot(
    tech_name,
    scenario_data,
    output_name,
    stages,
    output_dir=PLOT_OUTPUT_DIR,
    material_title=None,
    filename_suffix="",
):
    n_cols = len(stages)
    fig, axs = plt.subplots(1, n_cols, figsize=(2.5 * n_cols, 4), sharey=True)
    if n_cols == 1:
        axs = [axs]

    global_max = max([df.max().max() for df in scenario_data.values() if not df.empty])
    y_limit = global_max * 1.15 if global_max > 0 else 10

    for i, stage in enumerate(stages):
        ax = axs[i]

        for scen_key in SCENARIO_ORDER:
            df = scenario_data[scen_key]
            years = df.index.values
            vals = df[stage].values

            ls = "-" if scen_key == "LR4_Base" else "--"
            lw = 2.5 if scen_key == "LR4_Base" else 1.5

            ax.plot(
                years,
                vals,
                color=SCENARIO_COLORS[scen_key],
                linewidth=lw,
                linestyle=ls,
                zorder=3,
            )

        ax.set_title(stage, fontsize=12)
        ax.set_xlim(2025, 2050)
        ax.set_ylim(0, y_limit)

        # Ticks & Grid
        ax.grid(False)
        major_yticks = ax.yaxis.get_majorticklocs()
        for y in major_yticks:
            if 0 < y < y_limit:
                ax.axhline(
                    y, color="gray", linestyle="--", linewidth=0.6, alpha=0.5, zorder=0
                )

        ax.set_axisbelow(False)
        ax.tick_params(
            axis="both",
            which="major",
            direction="in",
            length=4,
            labelsize=9,
            top=True,
            right=True,
        )
        ax.xaxis.set_minor_locator(MultipleLocator(1))

        if i == 0:
            ax.set_ylabel("Capacity (GW/yr)", fontsize=11)
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    # Legend
    handles = [
        mlines.Line2D(
            [],
            [],
            color=SCENARIO_COLORS[k],
            lw=2.5 if k == "LR4_Base" else 1.5,
            ls="-" if k == "LR4_Base" else "--",
            label=SCENARIO_LABELS[k],
        )
        for k in SCENARIO_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        frameon=True,
        edgecolor="black",
    )

    if material_title:
        fig.suptitle(material_title, fontsize=14, y=1.02)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(
        output_dir / f"{output_name}_Option1_Trajectory{filename_suffix}.pdf",
        bbox_inches="tight",
    )
    plt.close()


# ================= OPTION 2: DUMBBELL / RANGE =================
def create_dumbbell_plot(
    tech_name,
    scenario_data,
    output_name,
    stages,
    output_dir=PLOT_OUTPUT_DIR,
    material_title=None,
    filename_suffix="",
):
    fig, ax = plt.subplots(figsize=(7.5, max(4, len(stages) * 1.5)))

    y_ticks, y_labels = [], []
    y_pos = 0

    # Iterate backwards so first stage is at the top
    for stage in reversed(stages):
        ax.text(
            -0.02,
            y_pos - 1,
            stage,
            transform=ax.get_yaxis_transform(),
            fontsize=12,
            ha="right",
            va="center",
        )

        for year in reversed(YEARS_TO_PLOT):
            v_slow = (
                scenario_data["LR1_Slow"].loc[year, stage]
                if year in scenario_data["LR1_Slow"].index
                else 0
            )
            v_base = (
                scenario_data["LR4_Base"].loc[year, stage]
                if year in scenario_data["LR4_Base"].index
                else 0
            )
            v_fast = (
                scenario_data["LR7_Fast"].loc[year, stage]
                if year in scenario_data["LR7_Fast"].index
                else 0
            )

            # Draw range line
            ax.plot(
                [v_slow, v_fast], [y_pos, y_pos], color="gray", linewidth=1.5, zorder=1
            )

            # Draw scenario dots
            ax.scatter(v_slow, y_pos, color=SCENARIO_COLORS["LR1_Slow"], s=80, zorder=2)
            ax.scatter(v_fast, y_pos, color=SCENARIO_COLORS["LR7_Fast"], s=80, zorder=2)
            ax.scatter(
                v_base,
                y_pos,
                color=SCENARIO_COLORS["LR4_Base"],
                s=100,
                edgecolors="white",
                linewidth=1.5,
                zorder=3,
            )

            y_ticks.append(y_pos)
            y_labels.append(str(year))
            y_pos -= 0.6
        y_pos -= 0.8  # Gap between stages

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=10)
    ax.set_xlabel("Capacity (GW/yr)", fontsize=11)

    ax.grid(False)
    ax.xaxis.grid(color="gray", linestyle="--", linewidth=0.6, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(
        axis="both", direction="in", length=4, labelsize=10, top=True, right=True
    )

    handles = [
        mlines.Line2D(
            [],
            [],
            color="w",
            marker="o",
            markerfacecolor=SCENARIO_COLORS[k],
            markeredgecolor="w" if k == "LR4_Base" else "none",
            markersize=10,
            label=SCENARIO_LABELS[k],
        )
        for k in SCENARIO_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        frameon=True,
        edgecolor="black",
    )

    if material_title:
        fig.suptitle(material_title, fontsize=14, y=1.02)

    plt.tight_layout()
    plt.savefig(
        output_dir / f"{output_name}_Option2_Dumbbell{filename_suffix}.pdf",
        bbox_inches="tight",
    )
    plt.close()


# ================= OPTION 3: CLUSTERED SNAPSHOTS =================
def create_clustered_bar_plot(
    tech_name,
    scenario_data,
    output_name,
    stages,
    output_dir=PLOT_OUTPUT_DIR,
    material_title=None,
    filename_suffix="",
):
    fig, ax = plt.subplots(figsize=(8.5, 5))

    stage_centers = np.arange(len(stages)) * 4
    year_offsets = [-1, 0, 1]
    scen_offsets = [-0.25, 0, 0.25]
    bar_width = 0.22

    for i, stage in enumerate(stages):
        for j, year in enumerate(YEARS_TO_PLOT):
            for k, scen_key in enumerate(SCENARIO_ORDER):
                x_pos = stage_centers[i] + year_offsets[j] + scen_offsets[k]
                val = (
                    scenario_data[scen_key].loc[year, stage]
                    if year in scenario_data[scen_key].index
                    else 0
                )

                ax.bar(
                    x_pos,
                    val,
                    width=bar_width,
                    color=SCENARIO_COLORS[scen_key],
                    edgecolor="black",
                    linewidth=0.5,
                    zorder=3,
                )

            # Year label below the cluster
            ax.text(
                stage_centers[i] + year_offsets[j],
                -ax.get_ylim()[1] * 0.05,
                str(year),
                ha="center",
                va="top",
                fontsize=8,
                rotation=45,
            )

    ax.set_xticks(stage_centers)
    ax.set_xticklabels(stages, fontsize=11)
    ax.set_ylabel("Capacity (GW/yr)", fontsize=11)

    ax.grid(False)
    major_yticks = ax.yaxis.get_majorticklocs()
    for y in major_yticks:
        if y > 0:
            ax.axhline(
                y, color="gray", linestyle="--", linewidth=0.6, alpha=0.5, zorder=0
            )

    ax.set_axisbelow(False)
    ax.tick_params(axis="y", direction="in", length=4, labelsize=10, right=True)
    ax.tick_params(axis="x", length=0)  # Hide x ticks, use text instead

    handles = [
        mpatches.Patch(
            facecolor=SCENARIO_COLORS[k], edgecolor="black", label=SCENARIO_LABELS[k]
        )
        for k in SCENARIO_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        frameon=True,
        edgecolor="black",
    )

    if material_title:
        fig.suptitle(material_title, fontsize=14, y=1.02)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    plt.savefig(
        output_dir / f"{output_name}_Option3_ClusteredBars{filename_suffix}.pdf",
        bbox_inches="tight",
    )
    plt.close()


# ================= EXECUTION =================
if __name__ == "__main__":
    for material in MATERIAL_SCENARIOS:
        files = [
            scenario_file(BASE_DIR, learning_rate, material)
            for learning_rate in LEARNING_RATES
        ]
        missing = [str(path) for path in files if not path.exists()]
        if missing:
            print(f"❌ Missing {material} scenario files: {', '.join(missing)}")
            continue

        loaded_data = [load_processing_data(path) for path in files]
        material_output_dir = PLOT_OUTPUT_DIR / material
        for tech, stages in TECH_STAGE_MAP.items():
            scenario_data_dict = {
                key: get_pivot_for_tech(data, tech, stages)
                for key, data in zip(
                    SCENARIO_ORDER,
                    loaded_data,
                )
            }
            if any(frame.empty for frame in scenario_data_dict.values()):
                print(f"   ⚠ Data incomplete for {material}/{tech}; skipping.")
                continue

            base_output_name = f"Fig_Processing_Capacities_{tech}"
            create_trajectory_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                material_title=material,
                filename_suffix="_WithMaterialTitle",
            )
            create_dumbbell_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                material_title=material,
                filename_suffix="_WithMaterialTitle",
            )
            create_clustered_bar_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                material_title=material,
                filename_suffix="_WithMaterialTitle",
            )
            create_trajectory_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                filename_suffix="_NoMaterialTitle",
            )
            create_dumbbell_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                filename_suffix="_NoMaterialTitle",
            )
            create_clustered_bar_plot(
                tech,
                scenario_data_dict,
                base_output_name,
                stages,
                material_output_dir,
                filename_suffix="_NoMaterialTitle",
            )

    print("\n✅ All processing-capacity layouts generated for every material scenario!")
