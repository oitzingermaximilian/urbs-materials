import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path
from matplotlib.colors import to_hex  # <-- Robust color conversion
from scipy.spatial import ConvexHull
import matplotlib.patches as mpatches
import seaborn as sns

def mwh_to_bcm(mwh):
    """
    Convert MWh to BCM using same basis as EU demand conversion in Sebs Paper:
    1 BCM = 35,315,000 MMBtu
    1 MWh = 3.412 MMBtu
    """
    mmbtu = mwh * 3.412
    bcm = mmbtu / 35_315_000
    return bcm

def lng_lineplot_range_comp_scenarios():
    """Plot LNG demand range (min/max envelope) for 2024-2050 horizon using new scenario tuples.
    Data directory structure:
      result/results_with_nzia/<LR>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
      result/results_without_nzia/<LR>/<rolling_2024_to_2050>/scenario_<price_scenario>.xlsx
    """
    output_dir = Path("scenario_comparison")
    output_dir.mkdir(exist_ok=True)
    rolling_horizon = "rolling_2024_to_2050"
    years_full = list(range(2024, 2051))

    # Define groups as before
    group_definitions = [
        {
            "label": "With NZIA",
            "variant": "results_with_nzia",
            "color": "#1f77b4",
            "alpha": 0.3,
            "hatch": None,
        },
        {
            "label": "Without NZIA",
            "variant": "results_without_nzia",
            "color": "#ff7f0e",
            "alpha": 0.3,
            "hatch": "//",
        },
    ]

    def load_group_data(base_variant, lr_code, scenarios):
        """Load LNG yearly BCM values for all scenarios in a group for a given LR."""
        years_full = list(range(2024, 2051))
        data_by_year = {y: [] for y in years_full}

        for scenario_name, scenario_obj in scenarios:
            file_path = (
                    Path(RESULTS_BASE_PATH)
                    / base_variant
                    / lr_code
                    / "rolling_2024_to_2050"
                    / f"scenario_{scenario_name}.xlsx"
            )
            if not file_path.exists():
                print(f"  Missing file: {file_path}")
                continue

            try:
                df = pd.read_excel(file_path, sheet_name="gas demand per block")
            except Exception as e:
                print(f"  Error reading {file_path}: {e}")
                continue

            df["blocks"] = df["blocks"].astype(str).str.strip()
            # Select only LNG blocks
            lng_df = df[df["blocks"].str.endswith("LNG") & df["stf"].between(2024, 2050)]
            if lng_df.empty:
                continue

            # Sum across all LNG blocks per year
            yearly = lng_df.groupby("stf")["gas_usage_block"].sum().reset_index()
            yearly["lng_bcm"] = yearly["gas_usage_block"].apply(mwh_to_bcm)

            for _, row in yearly.iterrows():
                year = int(row["stf"])
                if year in data_by_year:
                    data_by_year[year].append(row["lng_bcm"])

        return data_by_year

    print("Creating 2024-2050 LNG range plots for all scenarios...")
    for lr_code, lr_name in LEARNING_RATES.items():
        print(f"Processing LR {lr_code} ...")
        plt.figure(figsize=(14, 8))

        for group in group_definitions:
            print(f"  Group: {group['label']}")
            group_data = load_group_data(group["variant"], lr_code, scenarios)
            min_vals, max_vals = [], []
            any_nonzero = False

            for y in years_full:
                vals = group_data.get(y, [])
                if vals:
                    min_v, max_v = min(vals), max(vals)
                    if max_v > 0:
                        any_nonzero = True
                else:
                    min_v, max_v = 0, 0
                min_vals.append(min_v)
                max_vals.append(max_v)

            if any_nonzero:
                plt.fill_between(
                    years_full,
                    min_vals,
                    max_vals,
                    color=group["color"],
                    alpha=group["alpha"],
                    hatch=group["hatch"],
                    edgecolor=group["color"],
                    label=f"{group['label']} (Range)",
                )
                plt.plot(years_full, min_vals, color=group["color"], linestyle="--", linewidth=1.2, label=f"{group['label']} (Min)")
                plt.plot(years_full, max_vals, color=group["color"], linestyle="-", linewidth=2, label=f"{group['label']} (Max)")

                print(f"    {group['label']}: {min([v for v in min_vals if v > 0] or [0]):.2f} - {max(max_vals):.2f} BCM")
            else:
                print(f"    Skipped (no non-zero data): {group['label']}")

        plt.xlabel("Year")
        plt.ylabel("LNG Demand (BCM)")
        plt.title(f"LNG Demand Ranges 2024-2050 with/without NZIA\n{lr_name}")
        plt.xlim(2024, 2050)
        plt.grid(True, linestyle="--", alpha=0.6)

        handles, labels = plt.gca().get_legend_handles_labels()
        seen = set()
        dedup_handles, dedup_labels = [], []
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                dedup_handles.append(h)
                dedup_labels.append(l)
        plt.legend(dedup_handles, dedup_labels, bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
        plt.tight_layout()

        out_path = output_dir / f"lng_range_plot_scenarios_{lr_code}.png"
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {out_path}")

    print("✓ Completed LNG range plots for all scenarios!")
