import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from matplotlib.lines import Line2D
from pathlib import Path
import math
import argparse

# ================= FORMATTING =================
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

BASE_DIR = r"../../result/urbs-LR4-20260531T0833"
OUTPUT_DIR = os.path.join("", "minerals_sourcing")

MATERIAL_GROUPS = {
    "Solar PV Only": ["silicon"],
    "Crossover (Solar & Wind)": ["aluminum", "copper"],
    "Wind Only": [
        "boron",
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
    ],
}

CRMA_TARGET_MATERIALS = []
for grp, mats in MATERIAL_GROUPS.items():
    CRMA_TARGET_MATERIALS.extend(mats)

QUOTAS = [5, 10, 15, 20, 25, 30, 35]

BINS = {
    "2024-2025": [2024, 2025],
    "2026-2030": [2026, 2027, 2028, 2029, 2030],
    "2031-2035": [2031, 2032, 2033, 2034, 2035],
    "2036-2040": [2036, 2037, 2038, 2039, 2040],
}

# --- BAR CHART SETTINGS ---
components = ["Mined", "Recycled"]
bar_colors = ["#A8D8EA", "#AA96DA"]
imports_color = "#FFFFD2"
FS_TICK = 20
FS_AXIS = 22
FS_WINDOW_LABEL = 20
FS_LEGEND_1ROW = 18
FIXED_MARGINS = dict(top=0.82, bottom=0.12, left=0.15, right=0.95)
Y_LABEL_COORDS = (-0.11, 0.5)
LEGEND_Y_POS = 1.05

# --- RADAR CHART SETTINGS ---
marginal_quotas = [35, 30, 25, 20, 15, 10, 5]
cmap = plt.cm.get_cmap("viridis", len(marginal_quotas))
RADAR_COLORS = {q: cmap(marginal_quotas.index(q)) for q in QUOTAS}


def load_mineral_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, sheet_name="minerals")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    cols_to_fill = ["stf", "materials", "tech", "location"]
    existing_cols = [c for c in cols_to_fill if c in df.columns]
    df[existing_cols] = df[existing_cols].ffill()

    if "tech" in df.columns:
        df = df[df["tech"].astype(str).str.contains("solar|wind", case=False, na=False)]

    mat_col = "materials" if "materials" in df.columns else "material"
    df = df[df[mat_col].isin(CRMA_TARGET_MATERIALS)].copy()

    results = {}
    for mat in CRMA_TARGET_MATERIALS:
        df_mat = df[df[mat_col] == mat]

        def get_series(col_name):
            if col_name in df_mat.columns:
                return df_mat.groupby("stf")[col_name].sum()
            return pd.Series(dtype=float)

        results[mat] = {
            "mined": get_series("material_mined"),
            "recycled": get_series("material_recycled"),
            "imported": get_series("material_imported"),
            "demand": get_series("demand_material_total"),
        }
    return results


def catmull_rom_spline_1d(y, n_interp=50):
    N = len(y)
    y_smooth = []
    for i in range(N):
        p0 = y[(i - 1) % N]
        p1 = y[i]
        p2 = y[(i + 1) % N]
        p3 = y[(i + 2) % N]

        for t in np.linspace(0, 1, n_interp, endpoint=False):
            val = 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * (t**2)
                + (-p0 + 3 * p1 - 3 * p2 + p3) * (t**3)
            )
            y_smooth.append(val)

    y_smooth.append(y_smooth[0])
    return np.array(y_smooth)


def get_theta_smooth(N, n_interp=50):
    theta = []
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    for i in range(N):
        start = angles[i]
        end = angles[(i + 1) % N] if i < N - 1 else 2 * np.pi
        for t in np.linspace(0, 1, n_interp, endpoint=False):
            theta.append(start + (end - start) * t)
    theta.append(theta[0])
    return np.array(theta)


def create_clustered_bar_charts(scenario_data, output_dir):
    base_patches = [
        mpatches.Patch(facecolor=fc, edgecolor="black", label=lab)
        for fc, lab in zip(bar_colors, components)
    ]
    imports_patch = mpatches.Patch(
        facecolor=imports_color, edgecolor="black", label="Imports"
    )
    legend_handles = base_patches + [imports_patch]

    windows = list(BINS.keys())
    x_base = np.arange(len(windows))

    max_clusters = len(QUOTAS)
    total_width = 0.8
    gap = 0.02
    width = (total_width - (max_clusters - 1) * gap) / max_clusters

    for mat in CRMA_TARGET_MATERIALS:
        mat_has_demand = any(
            scenario_data[q][mat]["demand"].sum() > 1e-6 for q in scenario_data
        )
        if not mat_has_demand:
            continue

        print(f"📊 Plotting clustered bar chart for {mat.capitalize()}...")

        fig, ax = plt.subplots(figsize=(12, 7))
        fig.subplots_adjust(**FIXED_MARGINS)

        offset_trans_rel = mtransforms.ScaledTranslation(
            0, 20 / 72, fig.dpi_scale_trans
        )
        text_trans_rel = ax.transData + offset_trans_rel

        for i, win_name in enumerate(windows):
            years = BINS[win_name]
            start_offset = (
                -(max_clusters * width + (max_clusters - 1) * gap) / 2 + width / 2
            )

            for j, q in enumerate(QUOTAS):
                x_pos = x_base[i] + start_offset + j * (width + gap)

                if q not in scenario_data:
                    continue

                mat_data = scenario_data[q][mat]
                mined = mat_data["mined"].reindex(years).fillna(0).sum()
                recycled = mat_data["recycled"].reindex(years).fillna(0).sum()
                imported = mat_data["imported"].reindex(years).fillna(0).sum()
                total = mined + recycled + imported
                denom = total if total > 1e-6 else 1

                ax.bar(
                    x_pos,
                    1,
                    width=width,
                    facecolor=imports_color,
                    edgecolor="black",
                    linewidth=0.8,
                    zorder=0,
                )

                bottom = 0
                for comp, color in zip(["mined", "recycled"], bar_colors):
                    val = mined if comp == "mined" else recycled
                    frac = val / denom
                    ax.bar(
                        x_pos,
                        frac,
                        width=width,
                        bottom=bottom,
                        facecolor=color,
                        edgecolor="black",
                        linewidth=0.8,
                        zorder=1,
                    )
                    bottom += frac

                font_size = max(6, min(16, 80 / max_clusters))
                ax.text(
                    x_pos,
                    0.95,
                    f"{q}%",
                    ha="center",
                    va="bottom",
                    rotation=90,
                    fontsize=font_size,
                    transform=text_trans_rel,
                )

        ax.set_xticks(x_base)
        ax.set_xticklabels(windows, fontsize=FS_WINDOW_LABEL)
        ax.tick_params(axis="y", labelsize=FS_TICK)

        ax.set_ylim(0, 1.15)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{int(y * 100)}%"))
        ax.set_ylabel("Share of Total Supply", fontsize=FS_AXIS)
        ax.yaxis.set_label_coords(*Y_LABEL_COORDS)
        ax.grid(axis="y", alpha=0.3)

        ax.legend(
            handles=legend_handles,
            fontsize=FS_LEGEND_1ROW,
            frameon=True,
            loc="lower center",
            bbox_to_anchor=(0.5, LEGEND_Y_POS),
            ncol=3,
            borderaxespad=0,
        )

        # Determine group to save in subfolder
        mat_group = "Unknown"
        for grp, mats in MATERIAL_GROUPS.items():
            if mat in mats:
                mat_group = grp
                break

        group_dir = os.path.join(
            output_dir, mat_group.replace(" & ", "_").replace(" ", "_")
        )
        Path(group_dir).mkdir(parents=True, exist_ok=True)

        out_file = os.path.join(group_dir, f"{mat}_clustered_sourcing.png")
        fig.savefig(out_file, dpi=500)
        plt.close(fig)


def create_radar_grid(scenario_data, output_dir):
    active_mats = []
    for mat in CRMA_TARGET_MATERIALS:
        has_demand = False
        for q in scenario_data:
            if scenario_data[q][mat]["demand"].sum() > 1e-6:
                has_demand = True
                break
        if has_demand:
            active_mats.append(mat)

    if not active_mats:
        return

    print(f"📊 Building unified Radar Grid for {len(active_mats)} materials...")

    n_cols = 4
    n_rows = math.ceil(len(active_mats) / n_cols)

    fig = plt.figure(figsize=(4.5 * n_cols, 4.5 * n_rows))
    # Increased hspace so titles and labels don't collide. Removed suptitle entirely.
    fig.subplots_adjust(hspace=0.55, wspace=0.3, top=0.95, bottom=0.1)

    windows = list(BINS.keys())
    # Shorten year labels: "2024-2025" -> "24-25"
    windows_short = [w.replace("20", "", 2) for w in windows]

    theta_viz = np.linspace(0, 2 * np.pi, len(windows), endpoint=False)
    theta_smooth = get_theta_smooth(len(windows), n_interp=50)

    for idx, mat in enumerate(active_mats):
        ax = fig.add_subplot(n_rows, n_cols, idx + 1, polar=True)

        mat_group = "Unknown"
        for grp, mats in MATERIAL_GROUPS.items():
            if mat in mats:
                mat_group = grp
                break

        # Closer padding so it stays attached to its radar chart and away from the one above
        ax.set_title(
            f"{mat.capitalize()}\n({mat_group})", weight="bold", fontsize=14, pad=10
        )

        for q in QUOTAS:
            if q not in scenario_data:
                continue

            mat_data = scenario_data[q][mat]
            mined_s = mat_data["mined"]
            recycled_s = mat_data["recycled"]
            imported_s = mat_data["imported"]

            values = []
            for win_name in windows:
                years = BINS[win_name]
                mined = mined_s.reindex(years).fillna(0).sum()
                recycled = recycled_s.reindex(years).fillna(0).sum()
                imported = imported_s.reindex(years).fillna(0).sum()
                total = mined + recycled + imported

                if total > 1e-6:
                    dom_share = (mined + recycled) / total
                else:
                    dom_share = 0
                values.append(dom_share)

            values_smooth = catmull_rom_spline_1d(values, n_interp=50)
            ax.plot(
                theta_smooth,
                values_smooth,
                color=RADAR_COLORS[q],
                linewidth=2.5,
                alpha=0.9,
                label=f"S{q}",
            )

        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])

        # Only show percentage labels on the very first subplot
        if idx == 0:
            ax.set_yticklabels(["25%", "50%", "75%", "100%"], color="#777777", size=9)
        else:
            ax.set_yticklabels([])

        ax.set_xticks(theta_viz)
        # Normal weight (not bold) for year labels
        ax.set_xticklabels(windows_short, fontsize=11, weight="normal")
        ax.tick_params(pad=8)

        ax.spines["polar"].set_color("#888888")
        ax.spines["polar"].set_linewidth(1.5)
        ax.grid(color="#DDDDDD", linestyle="-", linewidth=1)

    handles = [
        Line2D([0], [0], color=RADAR_COLORS[q], lw=2.5, label=f"S{q}") for q in QUOTAS
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=len(QUOTAS),
        fontsize=14,
        frameon=False,
        bbox_to_anchor=(0.5, 0.02),
    )

    out_file = os.path.join(output_dir, "Domestic_Sourcing_Radar_Grid.png")
    plt.savefig(out_file, dpi=400, bbox_inches="tight")
    print(f"   ✔ Saved Radar Grid -> {out_file}")
    plt.close(fig)


def create_individual_radars(scenario_data, output_dir):
    individual_dir = os.path.join(output_dir, "individual_radars")
    Path(individual_dir).mkdir(parents=True, exist_ok=True)
    print(f"📊 Building individual Radars...")

    windows = list(BINS.keys())
    theta_viz = np.linspace(0, 2 * np.pi, len(windows), endpoint=False)
    theta_smooth = get_theta_smooth(len(windows), n_interp=50)

    for mat in CRMA_TARGET_MATERIALS:
        has_demand = False
        for q in scenario_data:
            if scenario_data[q][mat]["demand"].sum() > 1e-6:
                has_demand = True
                break
        if not has_demand:
            continue

        fig = plt.figure(figsize=(6, 6))
        fig.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.15)
        ax = fig.add_subplot(111, polar=True)
        ax.set_title(mat.capitalize(), weight="bold", fontsize=18, pad=20)

        for q in QUOTAS:
            if q not in scenario_data:
                continue

            mat_data = scenario_data[q][mat]
            mined_s = mat_data["mined"]
            recycled_s = mat_data["recycled"]
            imported_s = mat_data["imported"]

            values = []
            for win_name in windows:
                years = BINS[win_name]
                mined = mined_s.reindex(years).fillna(0).sum()
                recycled = recycled_s.reindex(years).fillna(0).sum()
                imported = imported_s.reindex(years).fillna(0).sum()
                total = mined + recycled + imported

                if total > 1e-6:
                    dom_share = (mined + recycled) / total
                else:
                    dom_share = 0
                values.append(dom_share)

            values_smooth = catmull_rom_spline_1d(values, n_interp=50)
            ax.plot(
                theta_smooth,
                values_smooth,
                color=RADAR_COLORS[q],
                linewidth=2.5,
                alpha=0.9,
                label=f"S{q}",
            )

        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_xticks(theta_viz)

        # Add labels ONLY for aluminum
        if mat.lower() == "aluminum":
            ax.set_yticklabels(
                ["25%", "50%", "75%", "100%"], color="#555555", size=11, weight="bold"
            )
            ax.set_xticklabels(windows, fontsize=13, weight="bold")
        else:
            ax.set_yticklabels([])
            ax.set_xticklabels([])

        ax.tick_params(pad=28)

        ax.spines["polar"].set_color("#888888")
        ax.spines["polar"].set_linewidth(1.5)
        ax.grid(color="#DDDDDD", linestyle="-", linewidth=1)

        out_file = os.path.join(individual_dir, f"{mat}_radar.png")
        plt.savefig(out_file, dpi=400, transparent=True)
        plt.close(fig)

    # Create standalone legend
    fig_leg = plt.figure(figsize=(8, 1))
    handles = [
        Line2D([0], [0], color=RADAR_COLORS[q], lw=3, label=f"S{q}") for q in QUOTAS
    ]
    fig_leg.legend(
        handles=handles, loc="center", ncol=len(QUOTAS), fontsize=14, frameon=True
    )
    leg_file = os.path.join(individual_dir, "legend.png")
    fig_leg.savefig(leg_file, dpi=400, bbox_inches="tight", transparent=True)
    plt.close(fig_leg)

    print(f"   ✔ Saved individual radars -> {individual_dir}")


def create_selected_examples_grid(scenario_data, output_dir):
    print(
        f"📊 Building Selected Examples Grid (Aluminum, Copper, Neodymium, Silicon)..."
    )

    mats_to_plot = ["aluminum", "copper", "neodymium", "silicon"]

    # 2x2 grid
    fig = plt.figure(figsize=(10, 9.5))
    fig.subplots_adjust(hspace=0.15, wspace=0.1, top=0.92, bottom=0.1)

    windows = list(BINS.keys())
    theta_viz = np.linspace(0, 2 * np.pi, len(windows), endpoint=False)
    theta_smooth = get_theta_smooth(len(windows), n_interp=50)

    for idx, mat in enumerate(mats_to_plot):
        ax = fig.add_subplot(2, 2, idx + 1, polar=True)
        ax.set_title(mat.capitalize(), weight="bold", fontsize=18, pad=12)

        for q in QUOTAS:
            if q not in scenario_data:
                continue

            mat_data = scenario_data[q][mat]
            mined_s = mat_data["mined"]
            recycled_s = mat_data["recycled"]
            imported_s = mat_data["imported"]

            values = []
            for win_name in windows:
                years = BINS[win_name]
                mined = mined_s.reindex(years).fillna(0).sum()
                recycled = recycled_s.reindex(years).fillna(0).sum()
                imported = imported_s.reindex(years).fillna(0).sum()
                total = mined + recycled + imported

                if total > 1e-6:
                    dom_share = (mined + recycled) / total
                else:
                    dom_share = 0
                values.append(dom_share)

            values_smooth = catmull_rom_spline_1d(values, n_interp=50)
            ax.plot(
                theta_smooth,
                values_smooth,
                color=RADAR_COLORS[q],
                linewidth=2.5,
                alpha=0.9,
                label=f"S{q}",
            )

        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_xticks(theta_viz)

        windows_short = [f"P{i + 1}" for i in range(len(windows))]

        # Apply P1-P4 to ALL plots to maintain consistency
        ax.set_xticklabels(windows_short, fontsize=14, weight="bold")

        # Add percentage labels visually ONLY for aluminum
        if mat.lower() == "aluminum":
            ax.set_yticklabels(
                ["25%", "50%", "75%", "100%"], color="black", size=11, weight="bold"
            )
        else:
            ax.set_yticklabels([])

        # Move P1-P4 inside the 100% mark so circles can expand
        ax.tick_params(axis="x", pad=-20)

        ax.spines["polar"].set_color("#888888")
        ax.spines["polar"].set_linewidth(1.5)
        ax.grid(color="#DDDDDD", linestyle="-", linewidth=1)

    # Add legend at the bottom
    handles = [
        Line2D([0], [0], color=RADAR_COLORS[q], lw=3, label=f"S{q}") for q in QUOTAS
    ]
    leg = fig.legend(
        handles=handles,
        loc="lower center",
        ncol=len(QUOTAS),
        fontsize=15,
        frameon=True,
        bbox_to_anchor=(0.5, 0.01),
    )
    leg.get_frame().set_edgecolor("black")
    leg.get_frame().set_linewidth(1.5)

    individual_dir = os.path.join(output_dir, "individual_radars")
    Path(individual_dir).mkdir(parents=True, exist_ok=True)
    out_file = os.path.join(individual_dir, "Selected_Examples_Grid.png")

    plt.savefig(out_file, dpi=400, bbox_inches="tight", transparent=False)
    plt.close(fig)
    print(f"   ✔ Saved Selected Examples Grid -> {out_file}")


def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    print(f"Loading data for all CRMA scenarios...")
    scenario_data = {}
    for q in QUOTAS:
        folder_name = f"scenario_solar_recycling_low_crma_{q}"
        file_name = f"{folder_name}.xlsx"
        file_path = os.path.join(BASE_DIR, folder_name, file_name)
        res = load_mineral_data(file_path)
        if res is not None:
            scenario_data[q] = res

    if not scenario_data:
        print("❌ No data loaded. Exiting.")
        return

    parser = argparse.ArgumentParser(
        description="Plot CRMA sourcing radars and bar charts"
    )
    parser.add_argument(
        "--only-examples",
        action="store_true",
        help="Only plot the 2x2 Selected Examples Grid",
    )
    args = parser.parse_args()

    if args.only_examples:
        create_selected_examples_grid(scenario_data, OUTPUT_DIR)
    else:
        create_clustered_bar_charts(scenario_data, OUTPUT_DIR)
        create_radar_grid(scenario_data, OUTPUT_DIR)
        create_individual_radars(scenario_data, OUTPUT_DIR)
        create_selected_examples_grid(scenario_data, OUTPUT_DIR)


if __name__ == "__main__":
    main()
