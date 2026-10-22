import os
import re
from pathlib import Path
import matplotlib.patches as mpatches
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
SCENARIO = "LR4_nzia_40_crma_25_materials_base"
FILE_PATH = BASE_DIR / SCENARIO / f"{SCENARIO}.xlsx"
PLOT_OUTPUT_DIR = Path("plots/baseline")

# ================= DISTINCT COLOR PALETTE =================
TECH_COLORS = {
    "Solar PV": "#E69F00",
    "Onshore Wind": "#66C2A5",
    "Offshore Wind": "#00876C",
    "Hydro (ror)": "#56B4E9",
    "Hydro (reservoir)": "#0072B2",
    "Nuclear": "#8E44AD",
    "Gas (CCGT)": "#C0392B",
    "Gas (CCGT) CCUS": "#922B21",
    "Biomass": "#27AE60",
    "Coal": "#333333",
    "Coal CCUS": "#595959",
    "Lignite": "#5D4037",
    "Lignite CCUS": "#3E2723",
    "Oil": "#78281F",
    "Other non-res": "#BDC3C7",
}

# ================= SORTIERUNG STACK =================
TECH_ORDER = [
    "Solar PV",
    "Onshore Wind",
    "Offshore Wind",
    "Hydro (ror)",
    "Hydro (reservoir)",
    "Nuclear",
    "Gas (CCGT)",
    "Gas (CCGT) CCUS",
    "Coal",
    "Coal CCUS",
    "Lignite",
    "Lignite CCUS",
    "Oil",
    "Biomass",
    "Other non-res",
]

# ================= SORTIERUNG LEGENDE (Spaltenweise) =================
LEGEND_ORDER = [
    "Solar PV",
    "Onshore Wind",
    "Offshore Wind",
    "Hydro (ror)",
    "Hydro (reservoir)",
    "Biomass",
    "Nuclear",
    "Gas (CCGT)",
    "Gas (CCGT) CCUS",
    "Oil",
    "Coal",
    "Coal CCUS",
    "Lignite",
    "Lignite CCUS",
    "Other non-res",
]


# ================= HILFSFUNKTIONEN =================
def clean_technology_name(tech_name):
    if pd.isna(tech_name):
        return tech_name

    cleaned = re.sub(r"_\d{4}$", "", str(tech_name))

    mapping = {
        "solarPV": "Solar PV",
        "windon": "Onshore Wind",
        "windoff": "Offshore Wind",
        "Hydro_(run-of-river)": "Hydro (ror)",
        "Hydro_(reservoir)": "Hydro (reservoir)",
        "Coal_Plant_CCUS": "Coal CCUS",
        "Gas_Plant_(CCGT)_CCUS": "Gas (CCGT) CCUS",
        "Biomass_Plant": "Biomass",
        "Coal_Plant": "Coal",
        "Gas_Plant_(CCGT)": "Gas (CCGT)",
        "Lignite_Plant": "Lignite",
        "Lignite_Plant_CCUS": "Lignite CCUS",
        "Nuclear_Plant": "Nuclear",
        "Oil_Plant": "Oil",
        "Other_non-res": "Other non-res",
    }

    if cleaned in mapping:
        return mapping[cleaned]

    return cleaned.replace("_", " ").strip()


def get_color(tech):
    for key, color in TECH_COLORS.items():
        if key.lower() == tech.lower():
            return color
    return TECH_COLORS["Other non-res"]


def sort_legend_handles(handles, labels):
    order_dict = {name: i for i, name in enumerate(LEGEND_ORDER)}
    hl_sorted = sorted(zip(handles, labels), key=lambda x: order_dict.get(x[1], 999))
    if not hl_sorted:
        return [], []
    return zip(*hl_sorted)


# ================= DATEN LADEN =================
def load_baseline_generation(file_path, start_year=2025, end_year=2040):
    df_bal = pd.read_excel(file_path, sheet_name="extension_balance")
    df_bal.columns = df_bal.columns.str.lower()
    df_bal[["stf", "process"]] = df_bal[["stf", "process"]].ffill()
    df_bal["stf"] = pd.to_numeric(df_bal["stf"], errors="coerce")
    df_bal["value"] = pd.to_numeric(df_bal["value"], errors="coerce")

    df_bal["tech"] = df_bal["process"].apply(clean_technology_name)

    mask = (
        (df_bal["stf"] >= start_year)
        & (df_bal["stf"] <= end_year)
        & (~df_bal["tech"].str.contains("Batteries", case=False, na=False))
    )
    df_gen = df_bal[mask].groupby(["stf", "tech"])["value"].sum().reset_index()
    df_gen["value_twh"] = df_gen["value"] / 1000.0
    return df_gen


def load_capacity_data(file_path, start_year=2025, end_year=2040):
    df_proc = pd.read_excel(file_path, sheet_name="Process caps")
    df_proc.columns = df_proc.columns.str.lower()
    df_proc["stf"] = df_proc["stf"].ffill()
    df_proc["stf"] = pd.to_numeric(df_proc["stf"], errors="coerce")
    df_proc["cap_pro"] = pd.to_numeric(df_proc["cap_pro"], errors="coerce")

    df_proc["tech"] = df_proc["pro"].apply(clean_technology_name)
    df_proc = df_proc[["stf", "tech", "cap_pro"]].rename(columns={"cap_pro": "value"})

    df_ext = pd.read_excel(file_path, sheet_name="extension_only_totalcapacity")
    df_ext.columns = df_ext.columns.str.lower()
    df_ext["stf"] = df_ext["stf"].ffill()
    df_ext["stf"] = pd.to_numeric(df_ext["stf"], errors="coerce")
    df_ext["capacity_ext"] = pd.to_numeric(df_ext["capacity_ext"], errors="coerce")

    df_ext["tech"] = df_ext["tech"].apply(clean_technology_name)
    df_ext = df_ext[["stf", "tech", "capacity_ext"]].rename(
        columns={"capacity_ext": "value"}
    )

    df_cap = pd.concat([df_proc, df_ext], ignore_index=True)

    mask = (
        (df_cap["stf"] >= start_year)
        & (df_cap["stf"] <= end_year)
        & (~df_cap["tech"].str.contains("Batteries", case=False, na=False))
    )
    df_cap_grouped = df_cap[mask].groupby(["stf", "tech"])["value"].sum().reset_index()
    return df_cap_grouped


# ================= PLOTTING =================
def plot_electricity_generation(
    df,
    chart_type="area",
    ylabel="Electricity Generated (TWh)",
    output_filename="Fig_Baseline_Electricity_Generation.pdf",
):
    df_pivot = df.pivot(index="stf", columns="tech", values="value_twh").fillna(0)

    sorted_techs = [t for t in TECH_ORDER if t in df_pivot.columns]
    for t in df_pivot.columns:
        if t not in sorted_techs:
            sorted_techs.append(t)

    df_pivot = df_pivot[sorted_techs]
    years = df_pivot.index.astype(int)
    colors = [get_color(t) for t in df_pivot.columns]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))

    # 1. FORCE DATA INTO Z-ORDER = 1
    if chart_type == "area":
        y_stacks = [df_pivot[t].values for t in df_pivot.columns]
        stacks = ax.stackplot(
            years,
            y_stacks,
            labels=df_pivot.columns,
            colors=colors,
            alpha=0.92,
            edgecolor="white",
            linewidth=0.3,
            zorder=1,  # Layer 1
        )
        ax.set_xlim(years.min(), years.max())
        for stack, label in zip(stacks, df_pivot.columns):
            if "CCUS" in label:
                stack.set_hatch("//")
    else:
        bottom = np.zeros(len(df_pivot))
        width = 0.55 if len(years) > 10 else 1.2
        for tech in df_pivot.columns:
            values = df_pivot[tech].values
            hatch_pattern = "//" if "CCUS" in tech else None
            ax.bar(
                years,
                values,
                bottom=bottom,
                label=tech,
                color=get_color(tech),
                edgecolor="black",
                linewidth=0.3,
                width=width,
                hatch=hatch_pattern,
                zorder=1,  # Layer 1
            )
            bottom += values
        ax.set_xlim(years.min() - 1.0, years.max() + 1.0)

    # Label Formatting
    ax.set_ylabel(ylabel, fontsize=12, labelpad=8)
    ax.set_xlabel(None)

    # Tick limits and scales
    ax.set_ylim(0, 4500)
    ax.set_yticks([1000, 2000, 3000, 4000])
    ax.set_yticklabels(["1,000", "2,000", "3,000", "4,000"])

    xticks = [y for y in [2025, 2030, 2035, 2040] if y in years]
    if not xticks:
        xticks = years.tolist()
    ax.set_xticks(xticks)

    # 2. BULLETPROOF TICKS/GRID FIX
    ax.grid(False)  # Turn off native buggy grid
    # Draw custom grid lines at Layer 0 (behind data)
    for y in [1000, 2000, 3000, 4000]:
        ax.axhline(y, color="gray", linestyle="--", linewidth=0.8, alpha=0.5, zorder=0)

    # Force ticks and spines to Layer 2.5 (above data)
    ax.set_axisbelow(False)

    # Configure inside-facing ticks
    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=4,
        top=True,
        right=True,
    )
    ax.tick_params(
        axis="both",
        which="minor",
        direction="in",
        length=2,
        top=True,
        right=True,
    )
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(500))
    # ==============================

    raw_handles, raw_labels = ax.get_legend_handles_labels()
    sorted_handles, sorted_labels = sort_legend_handles(raw_handles, raw_labels)

    ax.legend(
        sorted_handles,
        sorted_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=5,
        frameon=True,
        fontsize=8.5,
        framealpha=1.0,
        edgecolor="black",
        columnspacing=1.2,
        handlelength=1.4,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOT_OUTPUT_DIR / output_filename
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"✔ Erzeugungsplot ({chart_type.upper()}) gespeichert: {out_path}")


def plot_capacity_bar(
    df,
    ylabel="Installed Capacity (GW)",
    output_filename="Fig_Baseline_Capacity_Bar.pdf",
):
    df_pivot = df.pivot(index="stf", columns="tech", values="value").fillna(0)

    sorted_techs = [t for t in TECH_ORDER if t in df_pivot.columns]
    for t in df_pivot.columns:
        if t not in sorted_techs:
            sorted_techs.append(t)

    df_pivot = df_pivot[sorted_techs]
    years = df_pivot.index.astype(int)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))

    bottom = np.zeros(len(df_pivot))
    width = 0.55 if len(years) > 10 else 1.2

    # 1. FORCE DATA INTO Z-ORDER = 1
    for tech in df_pivot.columns:
        values = df_pivot[tech].values
        hatch_pattern = "//" if "CCUS" in tech else None

        ax.bar(
            years,
            values,
            bottom=bottom,
            label=tech,
            color=get_color(tech),
            edgecolor="black",
            linewidth=0.3,
            width=width,
            hatch=hatch_pattern,
            zorder=1,  # Layer 1
        )
        bottom += values

    ax.set_xlim(years.min() - 1.0, years.max() + 1.0)
    max_cap = bottom.max()
    ax.set_ylim(0, max_cap * 1.1)

    ax.set_ylabel(ylabel, fontsize=12, labelpad=8)
    ax.set_xlabel(None)

    # Create dynamic sensible ticks for capacity (e.g. 1000, 2000, 3000)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    xticks = [y for y in [2025, 2030, 2035, 2040] if y in years]
    if not xticks:
        xticks = years.tolist()
    ax.set_xticks(xticks)

    # 2. BULLETPROOF TICKS/GRID FIX
    ax.grid(False)  # Turn off native buggy grid
    # Draw custom grid lines dynamically at Layer 0 (behind data)
    major_yticks = ax.yaxis.get_majorticklocs()
    for y in major_yticks:
        if 0 < y < max_cap * 1.1:
            ax.axhline(
                y, color="gray", linestyle="--", linewidth=0.8, alpha=0.5, zorder=0
            )

    # Force ticks and spines to Layer 2.5 (above data)
    ax.set_axisbelow(False)

    # Configure inside-facing ticks
    ax.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=4,
        top=True,
        right=True,
    )
    ax.tick_params(
        axis="both",
        which="minor",
        direction="in",
        length=2,
        top=True,
        right=True,
    )
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    # ==============================

    raw_handles, raw_labels = ax.get_legend_handles_labels()
    sorted_handles, sorted_labels = sort_legend_handles(raw_handles, raw_labels)

    ax.legend(
        sorted_handles,
        sorted_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=5,
        frameon=True,
        fontsize=8.5,
        framealpha=1.0,
        edgecolor="black",
        columnspacing=1.2,
        handlelength=1.4,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOT_OUTPUT_DIR / output_filename
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"✔ Kapazitätsplot (BAR) gespeichert: {out_path}")


# ================= EXECUTION =================
if __name__ == "__main__":
    if not FILE_PATH.exists():
        print(f"❌ Datei nicht gefunden: {FILE_PATH}\nBitte Pfad (BASE_DIR) prüfen.")
    else:
        df_gen = load_baseline_generation(FILE_PATH, start_year=2025, end_year=2040)
        if not df_gen.empty:
            plot_electricity_generation(
                df_gen,
                chart_type="area",
                ylabel="Electricity Generated (TWh)",
                output_filename="Fig_Baseline_Electricity_Generation_Area.pdf",
            )
            plot_electricity_generation(
                df_gen,
                chart_type="bar",
                ylabel="Electricity Generated (TWh)",
                output_filename="Fig_Baseline_Electricity_Generation_Bar.pdf",
            )

        df_cap = load_capacity_data(FILE_PATH, start_year=2025, end_year=2040)
        if not df_cap.empty:
            plot_capacity_bar(
                df_cap,
                ylabel="Installed Capacity (GW)",
                output_filename="Fig_Baseline_Capacity_Bar.pdf",
            )
