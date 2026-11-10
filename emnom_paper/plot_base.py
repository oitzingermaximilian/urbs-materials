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
try:
    import scienceplots
    plt.style.use(["science", "ieee", "no-latex"])
except Exception:
    pass

plt.rcParams.update(
    {
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "pgf.rcfonts": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

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
    "Other RES": "#7F8C8D",
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


def safe_savefig(fig_or_plt, out_path, **kwargs):
    """Save figure safely on Windows / OneDrive by removing stale placeholders."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        try:
            p.unlink()
        except Exception:
            pass
    fig_or_plt.savefig(p, **kwargs)


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


def filter_active_capacity(df_cap, df_gen, min_gen_twh=1e-4):
    """
    Filters capacity data so that only actively generating/contributing
    technologies are plotted. If a technology generates zero (or <= min_gen_twh)
    in a given year, its capacity is set to 0.0.
    """
    df_merged = pd.merge(
        df_cap,
        df_gen[["stf", "tech", "value_twh"]],
        on=["stf", "tech"],
        how="left",
    )
    df_merged["value_twh"] = df_merged["value_twh"].fillna(0.0)
    df_filtered = df_merged.copy()
    df_filtered.loc[df_filtered["value_twh"] <= min_gen_twh, "value"] = 0.0
    return df_filtered[["stf", "tech", "value"]]


def load_capacity_data(
    file_path, start_year=2025, end_year=2050, df_gen=None, active_only=False
):
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

    if active_only:
        if df_gen is None:
            df_gen = load_baseline_generation(file_path, start_year=start_year, end_year=end_year)
        df_cap_grouped = filter_active_capacity(df_cap_grouped, df_gen)

    return df_cap_grouped

# ================= PLOTTING =================
def plot_electricity_generation(
    df,
    chart_type="area",
    ylabel="Electricity generated (TWh)",
    output_filename="Fig_Baseline_Electricity_Generation.pdf",
    label_size=14,
    tick_size=11,
    legend_size=11.5,
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
    ax.set_ylabel(ylabel, fontsize=label_size, labelpad=8)
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
        labelsize=tick_size,
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
        bbox_to_anchor=(0.5, -0.16),
        ncol=4,
        frameon=False,
        fontsize=legend_size,
        columnspacing=1.2,
        handletextpad=0.4,
        handlelength=1.2,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(output_filename) if Path(output_filename).is_absolute() else PLOT_OUTPUT_DIR / output_filename
    safe_savefig(plt, out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"[OK] Erzeugungsplot ({chart_type.upper()}) gespeichert: {out_path}")


def plot_capacity_bar(
    df,
    df_gen=None,
    only_active=False,
    ylabel="Active generation capacity (GW)",
    output_filename="Fig_Baseline_Capacity_Bar.pdf",
    label_size=14,
    tick_size=11,
    legend_size=11.5,
):
    if only_active and df_gen is not None:
        df = filter_active_capacity(df, df_gen)

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

    ax.set_ylabel(ylabel, fontsize=label_size, labelpad=8)
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
        labelsize=tick_size,
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
        bbox_to_anchor=(0.5, -0.16),
        ncol=4,
        frameon=False,
        fontsize=legend_size,
        columnspacing=1.2,
        handletextpad=0.4,
        handlelength=1.2,
    )

    plt.tight_layout()
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(output_filename) if Path(output_filename).is_absolute() else PLOT_OUTPUT_DIR / output_filename
    safe_savefig(plt, out_path, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"[OK] Kapazitätsplot (BAR) gespeichert: {out_path}")


def plot_combined_capacity_and_generation(
    df_cap,
    df_gen,
    only_active_cap=True,
    chart_type_cap="bar",
    chart_type_gen="area",
    ylabel_cap="Active generation capacity (GW)",
    ylabel_gen="Electricity generated (TWh)",
    title_cap="a)",
    title_gen="b)",
    output_filename="Fig_Baseline_Capacity_and_Generation_Combined.pdf",
    label_size=15,
    tick_size=12,
    legend_size=12,
    title_size=14,
    figsize=(8.5, 7.6),
):
    """
    Plots Active generation capacity (a) and Electricity generated (b) stacked vertically
    (2 rows x 1 column) with a unified shared legend at the bottom to save vertical space.
    If only_active_cap is True, capacity with no generation in that year is set to 0.
    """
    if only_active_cap and df_gen is not None:
        df_cap = filter_active_capacity(df_cap, df_gen)

    fig, (ax_cap, ax_gen) = plt.subplots(2, 1, figsize=figsize)

    # ================= 1. CAPACITY SUBPLOT (a) =================
    df_cap_pivot = df_cap.pivot(index="stf", columns="tech", values="value").fillna(0)
    for t in TECH_ORDER:
        if t not in df_cap_pivot.columns:
            df_cap_pivot[t] = 0.0

    sorted_techs_cap = [t for t in TECH_ORDER if t in df_cap_pivot.columns]
    df_cap_pivot = df_cap_pivot[sorted_techs_cap]
    years_cap = df_cap_pivot.index.astype(int)

    if chart_type_cap == "area":
        y_stacks_cap = [df_cap_pivot[t].values for t in df_cap_pivot.columns]
        colors_cap = [get_color(t) for t in df_cap_pivot.columns]
        stacks_cap = ax_cap.stackplot(
            years_cap,
            y_stacks_cap,
            labels=df_cap_pivot.columns,
            colors=colors_cap,
            alpha=0.92,
            edgecolor="white",
            linewidth=0.3,
            zorder=1,
        )
        ax_cap.set_xlim(years_cap.min(), years_cap.max())
        for stack, label in zip(stacks_cap, df_cap_pivot.columns):
            if "CCS" in label or "CCUS" in label:
                stack.set_hatch("//")
        max_cap = sum(y_stacks_cap).max()
    else:
        bottom_cap = np.zeros(len(df_cap_pivot))
        width_cap = 0.55 if len(years_cap) > 10 else 1.2
        for tech in df_cap_pivot.columns:
            values = df_cap_pivot[tech].values
            hatch_pattern = "//" if ("CCS" in tech or "CCUS" in tech) else None
            ax_cap.bar(
                years_cap,
                values,
                bottom=bottom_cap,
                label=tech,
                color=get_color(tech),
                edgecolor="black",
                linewidth=0.3,
                width=width_cap,
                hatch=hatch_pattern,
                zorder=1,
            )
            bottom_cap += values
        ax_cap.set_xlim(years_cap.min() - 0.8, years_cap.max() + 0.8)
        max_cap = bottom_cap.max()

    ax_cap.set_ylim(0, max_cap * 1.1)
    ax_cap.set_ylabel(ylabel_cap, fontsize=label_size, labelpad=8)
    ax_cap.set_xlabel(None)
    if title_cap:
        ax_cap.set_title(title_cap, fontsize=title_size, loc="center", fontweight="normal", pad=6)

    ax_cap.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax_cap.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    xticks_cap = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if y in years_cap]
    if not xticks_cap:
        xticks_cap = years_cap.tolist()
    ax_cap.set_xticks(xticks_cap)

    ax_cap.grid(False)
    for y in ax_cap.yaxis.get_majorticklocs():
        if 0 < y < max_cap * 1.1:
            ax_cap.axhline(
                y, color="gray", linestyle="--", linewidth=0.8, alpha=0.5, zorder=0
            )

    ax_cap.set_axisbelow(False)
    ax_cap.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=4,
        top=True,
        right=True,
        labelsize=tick_size,
    )
    ax_cap.tick_params(
        axis="both",
        which="minor",
        direction="in",
        length=2,
        top=True,
        right=True,
    )
    ax_cap.xaxis.set_minor_locator(MultipleLocator(1))
    ax_cap.yaxis.set_minor_locator(AutoMinorLocator(2))

    # ================= 2. GENERATION SUBPLOT (b) =================
    df_gen_pivot = df_gen.pivot(index="stf", columns="tech", values="value_twh").fillna(0)
    for t in TECH_ORDER:
        if t not in df_gen_pivot.columns:
            df_gen_pivot[t] = 0.0

    sorted_techs_gen = [t for t in TECH_ORDER if t in df_gen_pivot.columns]
    df_gen_pivot = df_gen_pivot[sorted_techs_gen]
    years_gen = df_gen_pivot.index.astype(int)
    colors_gen = [get_color(t) for t in df_gen_pivot.columns]

    if chart_type_gen == "area":
        y_stacks_gen = [df_gen_pivot[t].values for t in df_gen_pivot.columns]
        stacks_gen = ax_gen.stackplot(
            years_gen,
            y_stacks_gen,
            labels=df_gen_pivot.columns,
            colors=colors_gen,
            alpha=0.92,
            edgecolor="white",
            linewidth=0.3,
            zorder=1,
        )
        ax_gen.set_xlim(years_gen.min(), years_gen.max())
        for stack, label in zip(stacks_gen, df_gen_pivot.columns):
            if "CCS" in label or "CCUS" in label:
                stack.set_hatch("//")
    else:
        bottom_gen = np.zeros(len(df_gen_pivot))
        width_gen = 0.55 if len(years_gen) > 10 else 1.2
        for tech in df_gen_pivot.columns:
            values = df_gen_pivot[tech].values
            hatch_pattern = "//" if ("CCS" in tech or "CCUS" in tech) else None
            ax_gen.bar(
                years_gen,
                values,
                bottom=bottom_gen,
                label=tech,
                color=get_color(tech),
                edgecolor="black",
                linewidth=0.3,
                width=width_gen,
                hatch=hatch_pattern,
                zorder=1,
            )
            bottom_gen += values
        ax_gen.set_xlim(years_gen.min() - 0.8, years_gen.max() + 0.8)

    ax_gen.set_ylabel(ylabel_gen, fontsize=label_size, labelpad=8)
    ax_gen.set_xlabel(None)
    if title_gen:
        ax_gen.set_title(title_gen, fontsize=title_size, loc="center", fontweight="normal", pad=6)

    ax_gen.set_ylim(0, 4500)
    ax_gen.set_yticks([1000, 2000, 3000, 4000])
    ax_gen.set_yticklabels(["1,000", "2,000", "3,000", "4,000"])

    xticks_gen = [y for y in [2025, 2030, 2035, 2040, 2045, 2050] if y in years_gen]
    if not xticks_gen:
        xticks_gen = years_gen.tolist()
    ax_gen.set_xticks(xticks_gen)

    ax_gen.grid(False)
    for y in [1000, 2000, 3000, 4000]:
        ax_gen.axhline(y, color="gray", linestyle="--", linewidth=0.8, alpha=0.5, zorder=0)

    ax_gen.set_axisbelow(False)
    ax_gen.tick_params(
        axis="both",
        which="major",
        direction="in",
        length=4,
        top=True,
        right=True,
        labelsize=tick_size,
    )
    ax_gen.tick_params(
        axis="both",
        which="minor",
        direction="in",
        length=2,
        top=True,
        right=True,
    )
    ax_gen.xaxis.set_minor_locator(MultipleLocator(1))
    ax_gen.yaxis.set_minor_locator(MultipleLocator(500))

    # ================= 3. UNIFIED SHARED LEGEND =================
    raw_handles, raw_labels = ax_cap.get_legend_handles_labels()
    sorted_handles, sorted_labels = sort_legend_handles(raw_handles, raw_labels, ncol=4)

    fig.legend(
        sorted_handles,
        sorted_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.01),
        ncol=4,
        frameon=False,
        fontsize=legend_size,
        columnspacing=1.3,
        handletextpad=0.4,
        handlelength=1.2,
    )

    plt.tight_layout(rect=(0.0, 0.08, 1.0, 1.0))
    PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(output_filename) if Path(output_filename).is_absolute() else PLOT_OUTPUT_DIR / output_filename
    fmt = out_path.suffix.lstrip(".").lower() if out_path.suffix else "pdf"
    safe_savefig(plt, out_path, format=fmt, bbox_inches="tight", dpi=300 if fmt == "png" else None)
    plt.close()
    print(f"[OK] Kombinierter Plot (a: {chart_type_cap.upper()}, b: {chart_type_gen.upper()}) gespeichert: {out_path}")


# ================= EXECUTION =================
if __name__ == "__main__":
    if not FILE_PATH.exists():
        print(f"[ERROR] Datei nicht gefunden: {FILE_PATH}\nBitte Pfad (BASE_DIR) prüfen.")
    else:
        df_gen = load_baseline_generation(FILE_PATH, start_year=2025, end_year=2050)
        df_cap = load_capacity_data(FILE_PATH, start_year=2025, end_year=2050)

        if not df_gen.empty:
            plot_electricity_generation(
                df_gen,
                chart_type="area",
                ylabel="Electricity generated (TWh)",
                output_filename="Fig_Baseline_Electricity_Generation_Area.pdf",
            )
            plot_electricity_generation(
                df_gen,
                chart_type="bar",
                ylabel="Electricity generated (TWh)",
                output_filename="Fig_Baseline_Electricity_Generation_Bar.pdf",
            )

        if not df_cap.empty:
            plot_capacity_bar(
                df_cap,
                df_gen=df_gen,
                only_active=True,
                ylabel="Active generation capacity (GW)",
                output_filename="Fig_Baseline_Capacity_Bar.pdf",
            )

        if not df_gen.empty and not df_cap.empty:
            plot_combined_capacity_and_generation(
                df_cap,
                df_gen,
                only_active_cap=True,
                chart_type_cap="bar",
                chart_type_gen="area",
                ylabel_cap="Active generation capacity (GW)",
                ylabel_gen="Electricity generated (TWh)",
                title_cap="a)",
                title_gen="b)",
                output_filename="Fig_Baseline_Capacity_and_Generation_Combined.pdf",
            )
