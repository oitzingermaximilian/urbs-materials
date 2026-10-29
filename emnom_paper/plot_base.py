import os
import re
import ctypes
import shutil
import tempfile
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
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR / "result" / "results_server_201026"
if not BASE_DIR.exists():
    BASE_DIR = Path("result/results_server_201026")
SCENARIO = "LR4_nzia_40_crma_35_materials_base"
FILE_PATH = BASE_DIR / SCENARIO / f"{SCENARIO}.xlsx"
PLOT_OUTPUT_DIR = PROJECT_DIR / "plots" / "baseline" 

# ================= DISTINCT COLOR PALETTE =================
TECH_COLORS = {
    "Solar PV": "#E69F00",
    "Onshore Wind": "#66C2A5",
    "Offshore Wind": "#00876C",
    "Hydropower": "#0072B2",
    "Other RES": "#27AE60",
    "Nuclear": "#8E44AD",
    "Fossil": "#C0392B",
    "Fossil w/ CCS": "#922B21",
}

# ================= SORTIERUNG STACK =================
TECH_ORDER = [
    "Solar PV",
    "Onshore Wind",
    "Offshore Wind",
    "Hydropower",
    "Other RES",
    "Nuclear",
    "Fossil",
    "Fossil w/ CCS",
]

# ================= SORTIERUNG LEGENDE (2 Zeilen à 4 Einträge) =================
# Zeile 1: Solar PV, Onshore Wind, Offshore Wind, Hydropower
# Zeile 2: Other RES, Nuclear, Fossil, Fossil w/ CCS
LEGEND_ORDER = [
    "Solar PV",
    "Onshore Wind",
    "Offshore Wind",
    "Hydropower",
    "Other RES",
    "Nuclear",
    "Fossil",
    "Fossil w/ CCS",
]


# ================= HILFSFUNKTIONEN =================
def read_excel_safe(path, **kwargs):
    src = Path(path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Datei existiert nicht: {src}")

    tmp = Path(tempfile.gettempdir()) / f"plot_base_{src.name}"
    try:
        ok = ctypes.windll.kernel32.CopyFileW(str(src), str(tmp), False)
        if not ok:
            shutil.copy2(src, tmp)
    except Exception:
        shutil.copy2(src, tmp)

    try:
        df = pd.read_excel(tmp, **kwargs)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
    return df


def clean_technology_name(tech_name):
    if pd.isna(tech_name):
        return tech_name

    s = str(tech_name).strip()

    # Nuclear
    if s.lower().startswith("nuclear"):
        return "Nuclear"

    # Hydropower (merge RoR, pumped, and reservoir)
    if "hydro" in s.lower():
        return "Hydropower"

    # Solar PV
    if "solarpv" in s.lower() or s == "Solar PV":
        return "Solar PV"

    # Wind
    if "windon" in s.lower() or "onshore" in s.lower():
        return "Onshore Wind"
    if "windoff" in s.lower() or "offshore" in s.lower():
        return "Offshore Wind"

    # Other RES (Biomass)
    if "biomass" in s.lower() or "other res" in s.lower():
        return "Other RES"

    # Batteries (filtered out in load functions)
    if "batteries" in s.lower() or "battery" in s.lower():
        return "Batteries"

    # Fossil w/ CCS
    if "ccus" in s.lower() or "ccs" in s.lower():
        return "Fossil w/ CCS"

    # Everything else is unabated Fossil (Gas CCGT, Coal, Lignite, Oil, Other non-res)
    return "Fossil"


def get_color(tech):
    for key, color in TECH_COLORS.items():
        if key.lower() == tech.lower():
            return color
    return TECH_COLORS.get("Fossil", "#C0392B")


def sort_legend_handles(handles, labels, ncol=4):
    """
    Sorts handles and labels according to LEGEND_ORDER and reorders them
    into column-major order so that matplotlib's column-first filling
    renders row 1 and row 2 in the exact row-wise order requested:
      Row 1: Solar PV, Onshore Wind, Offshore Wind, Hydropower
      Row 2: Other RES, Nuclear, Fossil, Fossil w/ CCS
    """
    order_dict = {name: i for i, name in enumerate(LEGEND_ORDER)}
    hl_sorted = sorted(zip(handles, labels), key=lambda x: order_dict.get(x[1], 999))
    if not hl_sorted:
        return [], []

    n = len(hl_sorted)
    nrows = (n + ncol - 1) // ncol
    grid = [hl_sorted[r * ncol : (r + 1) * ncol] for r in range(nrows)]
    col_major = []
    for c in range(ncol):
        for r in range(nrows):
            if c < len(grid[r]):
                col_major.append(grid[r][c])

    return zip(*col_major)


# ================= DATEN LADEN =================
def load_baseline_generation(file_path, start_year=2025, end_year=2050):
    df_bal = read_excel_safe(file_path, sheet_name="extension_balance")
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


def load_capacity_data(file_path, start_year=2025, end_year=2050):
    df_proc = read_excel_safe(file_path, sheet_name="Process caps")
    df_proc.columns = df_proc.columns.str.lower()
    df_proc["stf"] = df_proc["stf"].ffill()
    df_proc["stf"] = pd.to_numeric(df_proc["stf"], errors="coerce")
    df_proc["cap_pro"] = pd.to_numeric(df_proc["cap_pro"], errors="coerce")

    df_proc["tech"] = df_proc["pro"].apply(clean_technology_name)
    df_proc = df_proc[["stf", "tech", "cap_pro"]].rename(columns={"cap_pro": "value"})

    df_ext = read_excel_safe(file_path, sheet_name="extension_only_totalcapacity")
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

    for t in TECH_ORDER:
        if t not in df_pivot.columns:
            df_pivot[t] = 0.0

    sorted_techs = [t for t in TECH_ORDER if t in df_pivot.columns]
    df_pivot = df_pivot[sorted_techs]
    years = df_pivot.index.astype(int)
    colors = [get_color(t) for t in df_pivot.columns]

    fig, ax = plt.subplots(figsize=(8.0, 4.5))

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
            if "CCS" in label or "CCUS" in label:
                stack.set_hatch("//")
    else:
        bottom = np.zeros(len(df_pivot))
        width = 0.55 if len(years) > 10 else 1.2
        for tech in df_pivot.columns:
            values = df_pivot[tech].values
            hatch_pattern = "//" if ("CCS" in tech or "CCUS" in tech) else None
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

    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if y in years]
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
    sorted_handles, sorted_labels = sort_legend_handles(raw_handles, raw_labels, ncol=4)

    ax.legend(
        sorted_handles,
        sorted_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        frameon=False,
        fontsize=8.5,
        columnspacing=1.5,
        handletextpad=0.4,
        handlelength=1.2,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOT_OUTPUT_DIR / output_filename
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"[OK] Erzeugungsplot ({chart_type.upper()}) gespeichert: {out_path}")


def plot_capacity_bar(
    df,
    ylabel="Installed Capacity (GW)",
    output_filename="Fig_Baseline_Capacity_Bar.pdf",
):
    df_pivot = df.pivot(index="stf", columns="tech", values="value").fillna(0)

    for t in TECH_ORDER:
        if t not in df_pivot.columns:
            df_pivot[t] = 0.0

    sorted_techs = [t for t in TECH_ORDER if t in df_pivot.columns]
    df_pivot = df_pivot[sorted_techs]
    years = df_pivot.index.astype(int)

    fig, ax = plt.subplots(figsize=(8.0, 4.5))

    bottom = np.zeros(len(df_pivot))
    width = 0.55 if len(years) > 10 else 1.2

    # 1. FORCE DATA INTO Z-ORDER = 1
    for tech in df_pivot.columns:
        values = df_pivot[tech].values
        hatch_pattern = "//" if ("CCS" in tech or "CCUS" in tech) else None

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

    xticks = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if y in years]
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
    sorted_handles, sorted_labels = sort_legend_handles(raw_handles, raw_labels, ncol=4)

    ax.legend(
        sorted_handles,
        sorted_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        frameon=False,
        fontsize=8.5,
        columnspacing=1.5,
        handletextpad=0.4,
        handlelength=1.2,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOT_OUTPUT_DIR / output_filename
    plt.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"[OK] Kapazitätsplot (BAR) gespeichert: {out_path}")


# ================= EXECUTION =================
if __name__ == "__main__":
    if not FILE_PATH.exists():
        print(f"[ERROR] Datei nicht gefunden: {FILE_PATH}\nBitte Pfad (BASE_DIR) prüfen.")
    else:
        df_gen = load_baseline_generation(FILE_PATH, start_year=2025, end_year=2050)
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

        df_cap = load_capacity_data(FILE_PATH, start_year=2025, end_year=2050)
        if not df_cap.empty:
            plot_capacity_bar(
                df_cap,
                ylabel="Installed Capacity (GW)",
                output_filename="Fig_Baseline_Capacity_Bar.pdf",
            )
