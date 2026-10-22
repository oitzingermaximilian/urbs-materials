import os
import math
from pathlib import Path
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.ticker import (
    StrMethodFormatter,
    MultipleLocator,
    MaxNLocator,
    PercentFormatter,
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

PLOT_OUTPUT_DIR = Path("plots/supply_mix")

YEARS_TO_PLOT = [2025, 2030, 2035, 2040]

TECH_STAGE_MAP = {
    "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
    "windon": ["BladeOn", "TowerOn", "NacelleOn"],
    "windoff": ["BladeOff", "TowerOff", "NacelleOff"],
}

SCENARIO_ORDER = ["LR1_Slow", "LR4_Base", "LR7_Fast"]
SCENARIO_LABELS = {
    "LR1_Slow": "LR1 (Slow)",
    "LR4_Base": "LR4 (Base)",
    "LR7_Fast": "LR7 (Fast)",
}

# UPDATED COLORS FOR 3 COMPONENTS
MIX_COLORS = {
    "capacity_produced_flow": "#AA96DA",  # Soft Purple (Manufactured)
    "capacity_produced_stockout": "#FCBAD3",  # Soft Pink (Stockpile Withdrawals)
    "Imported": "#FFFFD2",  # Pale Yellow
}

MIX_LABELS = {
    "capacity_produced_flow": "Domestic Prod.",
    "capacity_produced_stockout": "Domestic Stockpile",
    "Imported": "Imported",
}


# ================= DATEN LADEN & MERGEN =================
def load_and_merge_supply_data(file_path):
    print(f"Lade Supply-Daten aus: {file_path}")

    def load_sheet(sheet_name, value_col_name):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
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
        df[val_col] = df[val_col].apply(lambda x: 0 if abs(x) < 1e-6 else x)
        return df[["stf", "tech", "stages", val_col]].rename(
            columns={val_col: value_col_name}
        )

    df_total = load_sheet("supply_mix", "Total")
    df_prod = load_sheet("net_domestic_production", "capacity_produced_flow")
    df_stock = load_sheet("net_domestic_stockout", "capacity_produced_stockout")

    df_merged = pd.merge(df_total, df_prod, on=["stf", "tech", "stages"], how="outer")
    df_merged = pd.merge(
        df_merged, df_stock, on=["stf", "tech", "stages"], how="outer"
    ).fillna(0)

    df_merged["Imported"] = (
        df_merged["Total"]
        - df_merged["capacity_produced_flow"]
        - df_merged["capacity_produced_stockout"]
    )
    df_merged["Imported"] = df_merged["Imported"].apply(lambda x: x if x > 0 else 0)

    return df_merged


# ================= HILFSFUNKTIONEN =================
def generate_smooth_curve(x0, x1, y0, y1, steps=50):
    x = np.linspace(x0, x1, steps)
    t = (x - x0) / (x1 - x0)
    curve = (1 - np.cos(t * np.pi)) / 2
    y = y0 + (y1 - y0) * curve
    return x, y


def format_grid_axes(ax, is_100_pct=True, max_y=None):
    ax.grid(False)
    if is_100_pct:
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax.yaxis.set_major_locator(MultipleLocator(50))
        for y in [25, 50, 75, 100]:
            ax.axhline(
                y, color="gray", linestyle="--", linewidth=0.5, alpha=0.3, zorder=0
            )
    else:
        if max_y and max_y > 0:
            ax.set_ylim(0, max_y * 1.15)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
            major_yticks = ax.yaxis.get_majorticklocs()
            for y in major_yticks:
                if 0 < y < max_y * 1.15:
                    ax.axhline(
                        y,
                        color="gray",
                        linestyle="--",
                        linewidth=0.5,
                        alpha=0.3,
                        zorder=0,
                    )

    ax.set_axisbelow(False)
    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=3.5,
        labelsize=9,
        top=True,
        right=True,
    )
    ax.set_xlim(min(YEARS_TO_PLOT) - 1, max(YEARS_TO_PLOT) + 1)
    ax.set_xticks(YEARS_TO_PLOT)
    ax.set_xticklabels([str(y) for y in YEARS_TO_PLOT], rotation=45)
    ax.xaxis.set_minor_locator(MultipleLocator(1))


# ================= PLOTTING FUNCTIONS =================


def plot_supply_alluvial_matrix(
    tech_name, scenario_dict, stages, output_dir=PLOT_OUTPUT_DIR
):
    n_rows = len(stages)
    n_cols = len(SCENARIO_ORDER)
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(3 * n_cols, 2.5 * n_rows), sharex=True, sharey=True
    )

    if n_rows == 1 and n_cols == 1:
        axs = np.array([[axs]])
    elif n_rows == 1:
        axs = axs[np.newaxis, :]
    elif n_cols == 1:
        axs = axs[:, np.newaxis]

    bar_width = 1.0

    for r, stage in enumerate(stages):
        for c, scen_key in enumerate(SCENARIO_ORDER):
            ax = axs[r, c]
            df = scenario_dict[scen_key]
            df_stage = (
                df[(df["tech"] == tech_name) & (df["stages"] == stage)]
                .set_index("stf")
                .reindex(YEARS_TO_PLOT)
                .fillna(0)
            )

            pct_prod = np.zeros(len(YEARS_TO_PLOT))
            pct_stock = np.zeros(len(YEARS_TO_PLOT))
            pct_imp = np.zeros(len(YEARS_TO_PLOT))

            for j, year in enumerate(YEARS_TO_PLOT):
                prod = df_stage.loc[year, "capacity_produced_flow"]
                stock = df_stage.loc[year, "capacity_produced_stockout"]
                imp = df_stage.loc[year, "Imported"]
                total = prod + stock + imp
                if total > 0:
                    pct_prod[j] = (prod / total) * 100
                    pct_stock[j] = (stock / total) * 100
                    pct_imp[j] = (imp / total) * 100

            # Draw smooth flows for 3 layers
            for j in range(len(YEARS_TO_PLOT) - 1):
                x_start = YEARS_TO_PLOT[j] + bar_width / 2
                x_end = YEARS_TO_PLOT[j + 1] - bar_width / 2

                x_flow, curve_prod = generate_smooth_curve(
                    x_start, x_end, pct_prod[j], pct_prod[j + 1]
                )
                ax.fill_between(
                    x_flow,
                    np.zeros_like(curve_prod),
                    curve_prod,
                    color=MIX_COLORS["capacity_produced_flow"],
                    alpha=0.35,
                    edgecolor="none",
                )

                x_flow, curve_stock = generate_smooth_curve(
                    x_start,
                    x_end,
                    pct_prod[j] + pct_stock[j],
                    pct_prod[j + 1] + pct_stock[j + 1],
                )
                ax.fill_between(
                    x_flow,
                    curve_prod,
                    curve_stock,
                    color=MIX_COLORS["capacity_produced_stockout"],
                    alpha=0.35,
                    edgecolor="none",
                )

                ax.fill_between(
                    x_flow,
                    curve_stock,
                    np.ones_like(curve_stock) * 100,
                    color=MIX_COLORS["Imported"],
                    alpha=0.35,
                    edgecolor="none",
                )

            # Draw solid bars
            for j, year in enumerate(YEARS_TO_PLOT):
                if pct_prod[j] > 0 or pct_stock[j] > 0 or pct_imp[j] > 0:
                    bottom = 0
                    ax.bar(
                        year,
                        pct_prod[j],
                        bottom=bottom,
                        width=bar_width,
                        color=MIX_COLORS["capacity_produced_flow"],
                        edgecolor="black",
                        linewidth=0.5,
                        zorder=3,
                    )
                    if pct_prod[j] > 8:
                        ax.text(
                            year,
                            bottom + pct_prod[j] / 2,
                            f"{pct_prod[j]:.0f}%",
                            ha="center",
                            va="center",
                            color="black",
                            fontsize=9,
                            fontweight="bold",
                            zorder=4,
                        )
                    bottom += pct_prod[j]

                    ax.bar(
                        year,
                        pct_stock[j],
                        bottom=bottom,
                        width=bar_width,
                        color=MIX_COLORS["capacity_produced_stockout"],
                        edgecolor="black",
                        linewidth=0.5,
                        zorder=3,
                    )
                    if pct_stock[j] > 8:
                        ax.text(
                            year,
                            bottom + pct_stock[j] / 2,
                            f"{pct_stock[j]:.0f}%",
                            ha="center",
                            va="center",
                            color="black",
                            fontsize=9,
                            fontweight="bold",
                            zorder=4,
                        )
                    bottom += pct_stock[j]

                    ax.bar(
                        year,
                        pct_imp[j],
                        bottom=bottom,
                        width=bar_width,
                        color=MIX_COLORS["Imported"],
                        edgecolor="black",
                        linewidth=0.5,
                        zorder=3,
                    )
                    if pct_imp[j] > 8:
                        ax.text(
                            year,
                            bottom + pct_imp[j] / 2,
                            f"{pct_imp[j]:.0f}%",
                            ha="center",
                            va="center",
                            color="black",
                            fontsize=9,
                            fontweight="bold",
                            zorder=4,
                        )

            format_grid_axes(ax, is_100_pct=True)

            if r == 0:
                ax.set_title(
                    SCENARIO_LABELS[scen_key], fontweight="bold", fontsize=12, pad=8
                )
            if c == 0:
                ax.set_ylabel(
                    f"{stage}\nMix (%)", fontsize=10, fontweight="bold", labelpad=8
                )

            if r < n_rows - 1:
                ax.tick_params(axis="x", labelbottom=False)

    handles = [
        mpatches.Patch(facecolor=MIX_COLORS[k], edgecolor="black", label=MIX_LABELS[k])
        for k in MIX_COLORS.keys()
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        frameon=True,
        edgecolor="black",
        fontsize=11,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=max(0.12, 0.4 / n_rows), hspace=0.15, wspace=0.1)

    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(
        output_dir / f"Fig_Matrix_Alluvial_{tech_name}.pdf", bbox_inches="tight"
    )
    plt.close()


def plot_supply_100bars_matrix(
    tech_name, scenario_dict, stages, output_dir=PLOT_OUTPUT_DIR
):
    n_rows = len(stages)
    n_cols = len(SCENARIO_ORDER)
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(3 * n_cols, 2.5 * n_rows), sharex=True, sharey=True
    )

    if n_rows == 1 and n_cols == 1:
        axs = np.array([[axs]])
    elif n_rows == 1:
        axs = axs[np.newaxis, :]
    elif n_cols == 1:
        axs = axs[:, np.newaxis]

    bar_width = 2.5

    for r, stage in enumerate(stages):
        for c, scen_key in enumerate(SCENARIO_ORDER):
            ax = axs[r, c]
            df = scenario_dict[scen_key]
            df_stage = (
                df[(df["tech"] == tech_name) & (df["stages"] == stage)]
                .set_index("stf")
                .reindex(YEARS_TO_PLOT)
                .fillna(0)
            )

            pct_prod = np.zeros(len(YEARS_TO_PLOT))
            pct_stock = np.zeros(len(YEARS_TO_PLOT))
            pct_imp = np.zeros(len(YEARS_TO_PLOT))

            for j, year in enumerate(YEARS_TO_PLOT):
                prod = df_stage.loc[year, "capacity_produced_flow"]
                stock = df_stage.loc[year, "capacity_produced_stockout"]
                imp = df_stage.loc[year, "Imported"]
                total = prod + stock + imp
                if total > 0:
                    pct_prod[j] = (prod / total) * 100
                    pct_stock[j] = (stock / total) * 100
                    pct_imp[j] = (imp / total) * 100

            ax.bar(
                YEARS_TO_PLOT,
                pct_prod,
                width=bar_width,
                color=MIX_COLORS["capacity_produced_flow"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )
            ax.bar(
                YEARS_TO_PLOT,
                pct_stock,
                bottom=pct_prod,
                width=bar_width,
                color=MIX_COLORS["capacity_produced_stockout"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )
            ax.bar(
                YEARS_TO_PLOT,
                pct_imp,
                bottom=pct_prod + pct_stock,
                width=bar_width,
                color=MIX_COLORS["Imported"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )

            format_grid_axes(ax, is_100_pct=True)

            if r == 0:
                ax.set_title(
                    SCENARIO_LABELS[scen_key], fontweight="bold", fontsize=12, pad=8
                )
            if c == 0:
                ax.set_ylabel(
                    f"{stage}\nMix (%)", fontsize=10, fontweight="bold", labelpad=8
                )

            if r < n_rows - 1:
                ax.tick_params(axis="x", labelbottom=False)

    handles = [
        mpatches.Patch(facecolor=MIX_COLORS[k], edgecolor="black", label=MIX_LABELS[k])
        for k in MIX_COLORS.keys()
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        frameon=True,
        edgecolor="black",
        fontsize=11,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=max(0.12, 0.4 / n_rows), hspace=0.15, wspace=0.1)

    plt.savefig(output_dir / f"Fig_Matrix_100Bars_{tech_name}.pdf", bbox_inches="tight")
    plt.close()


def plot_supply_absolute_bars_matrix(
    tech_name, scenario_dict, stages, output_dir=PLOT_OUTPUT_DIR
):
    n_rows = len(stages)
    n_cols = len(SCENARIO_ORDER)
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(3 * n_cols, 2.5 * n_rows), sharex=True, sharey="row"
    )

    if n_rows == 1 and n_cols == 1:
        axs = np.array([[axs]])
    elif n_rows == 1:
        axs = axs[np.newaxis, :]
    elif n_cols == 1:
        axs = axs[:, np.newaxis]

    bar_width = 2.5

    row_max_y = {}
    for stage in stages:
        max_y = 0
        for scen in SCENARIO_ORDER:
            df = scenario_dict[scen]
            df_stage = (
                df[(df["tech"] == tech_name) & (df["stages"] == stage)]
                .set_index("stf")
                .reindex(YEARS_TO_PLOT)
                .fillna(0)
            )
            tot = (
                df_stage["capacity_produced_flow"]
                + df_stage["capacity_produced_stockout"]
                + df_stage["Imported"]
            )
            max_y = max(max_y, tot.max())
        row_max_y[stage] = max_y

    for r, stage in enumerate(stages):
        for c, scen_key in enumerate(SCENARIO_ORDER):
            ax = axs[r, c]
            df = scenario_dict[scen_key]
            df_stage = (
                df[(df["tech"] == tech_name) & (df["stages"] == stage)]
                .set_index("stf")
                .reindex(YEARS_TO_PLOT)
                .fillna(0)
            )

            prod = df_stage["capacity_produced_flow"].values
            stock = df_stage["capacity_produced_stockout"].values
            imp = df_stage["Imported"].values

            ax.bar(
                YEARS_TO_PLOT,
                prod,
                width=bar_width,
                color=MIX_COLORS["capacity_produced_flow"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )
            ax.bar(
                YEARS_TO_PLOT,
                stock,
                bottom=prod,
                width=bar_width,
                color=MIX_COLORS["capacity_produced_stockout"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )
            ax.bar(
                YEARS_TO_PLOT,
                imp,
                bottom=prod + stock,
                width=bar_width,
                color=MIX_COLORS["Imported"],
                edgecolor="black",
                linewidth=0.5,
                zorder=2,
            )

            format_grid_axes(ax, is_100_pct=False, max_y=row_max_y[stage])

            if r == 0:
                ax.set_title(
                    SCENARIO_LABELS[scen_key], fontweight="bold", fontsize=12, pad=8
                )
            if c == 0:
                ax.set_ylabel(
                    f"{stage}\nCap (GW)", fontsize=10, fontweight="bold", labelpad=8
                )

            if r < n_rows - 1:
                ax.tick_params(axis="x", labelbottom=False)

    handles = [
        mpatches.Patch(facecolor=MIX_COLORS[k], edgecolor="black", label=MIX_LABELS[k])
        for k in MIX_COLORS.keys()
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        frameon=True,
        edgecolor="black",
        fontsize=11,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=max(0.12, 0.4 / n_rows), hspace=0.15, wspace=0.15)

    plt.savefig(
        output_dir / f"Fig_Matrix_AbsoluteBars_{tech_name}.pdf", bbox_inches="tight"
    )
    plt.close()


def plot_supply_100area_matrix(
    tech_name, scenario_dict, stages, output_dir=PLOT_OUTPUT_DIR
):
    n_rows = len(stages)
    n_cols = len(SCENARIO_ORDER)
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(3 * n_cols, 2.5 * n_rows), sharex=True, sharey=True
    )

    if n_rows == 1 and n_cols == 1:
        axs = np.array([[axs]])
    elif n_rows == 1:
        axs = axs[np.newaxis, :]
    elif n_cols == 1:
        axs = axs[:, np.newaxis]

    for r, stage in enumerate(stages):
        for c, scen_key in enumerate(SCENARIO_ORDER):
            ax = axs[r, c]
            df = scenario_dict[scen_key]
            df_stage = (
                df[(df["tech"] == tech_name) & (df["stages"] == stage)]
                .set_index("stf")
                .reindex(YEARS_TO_PLOT)
                .fillna(0)
            )

            pct_prod = np.zeros(len(YEARS_TO_PLOT))
            pct_stock = np.zeros(len(YEARS_TO_PLOT))
            pct_imp = np.zeros(len(YEARS_TO_PLOT))

            for j, year in enumerate(YEARS_TO_PLOT):
                prod = df_stage.loc[year, "capacity_produced_flow"]
                stock = df_stage.loc[year, "capacity_produced_stockout"]
                imp = df_stage.loc[year, "Imported"]
                total = prod + stock + imp
                if total > 0:
                    pct_prod[j] = (prod / total) * 100
                    pct_stock[j] = (stock / total) * 100
                    pct_imp[j] = (imp / total) * 100

            ax.stackplot(
                YEARS_TO_PLOT,
                pct_prod,
                pct_stock,
                pct_imp,
                labels=MIX_LABELS.values(),
                colors=[
                    MIX_COLORS["capacity_produced_flow"],
                    MIX_COLORS["capacity_produced_stockout"],
                    MIX_COLORS["Imported"],
                ],
                edgecolor="white",
                linewidth=0.5,
                alpha=0.9,
                zorder=1,
            )

            format_grid_axes(ax, is_100_pct=True)

            if r == 0:
                ax.set_title(
                    SCENARIO_LABELS[scen_key], fontweight="bold", fontsize=12, pad=8
                )
            if c == 0:
                ax.set_ylabel(
                    f"{stage}\nMix (%)", fontsize=10, fontweight="bold", labelpad=8
                )

            if r < n_rows - 1:
                ax.tick_params(axis="x", labelbottom=False)

    handles = [
        mpatches.Patch(facecolor=MIX_COLORS[k], edgecolor="black", label=MIX_LABELS[k])
        for k in MIX_COLORS.keys()
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=3,
        frameon=True,
        edgecolor="black",
        fontsize=11,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=max(0.12, 0.4 / n_rows), hspace=0.15, wspace=0.1)

    plt.savefig(output_dir / f"Fig_Matrix_100Area_{tech_name}.pdf", bbox_inches="tight")
    plt.close()


# ================= EXECUTION =================
if __name__ == "__main__":
    if not FILE_PATH.exists():
        print(f"❌ Datei nicht gefunden: {FILE_PATH}\nBitte Pfad prüfen.")
    else:
        df_base = load_and_merge_supply_data(FILE_PATH)

        # ---------------------------------------------------------
        # MOCK DATA SCENARIOS FOR ALL THREE COMPONENTS
        # ---------------------------------------------------------
        df_lr1 = df_base.copy()
        df_lr7 = df_base.copy()

        # LR1 (Slow): Shift towards imports, shrink domestic
        df_lr1["Imported"] = df_lr1["Imported"] * 1.30
        df_lr1["capacity_produced_flow"] = df_lr1["capacity_produced_flow"] * 0.70
        df_lr1["capacity_produced_stockout"] = (
            df_lr1["capacity_produced_stockout"] * 0.80
        )

        # LR7 (Fast): Shift towards domestic, shrink imports
        df_lr7["Imported"] = df_lr7["Imported"] * 0.70
        df_lr7["capacity_produced_flow"] = df_lr7["capacity_produced_flow"] * 1.30
        df_lr7["capacity_produced_stockout"] = (
            df_lr7["capacity_produced_stockout"] * 1.10
        )
        # ---------------------------------------------------------

        scenario_data_dict = {
            "LR1_Slow": df_lr1,
            "LR4_Base": df_base,
            "LR7_Fast": df_lr7,
        }

        for tech, stages in TECH_STAGE_MAP.items():
            print(f"\n📊 Generating Scenario Supply Mix matrices for {tech}...")

            plot_supply_alluvial_matrix(tech, scenario_data_dict, stages)
            plot_supply_100bars_matrix(tech, scenario_data_dict, stages)
            plot_supply_absolute_bars_matrix(tech, scenario_data_dict, stages)
            plot_supply_100area_matrix(tech, scenario_data_dict, stages)

        print(
            "\n✅ All Supply Mix Matrix visualizations successfully generated in plots/supply_mix!"
        )
