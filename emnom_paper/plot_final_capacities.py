from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scenario_config import (
    LEARNING_RATES,
    MATERIAL_SCENARIOS,
    scenario_file,
)


PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR / "result" / "results_server_201026"
OUTPUT_DIR = PROJECT_DIR / "plots" / "final_capacities"

TECH_ORDER = ["solarPV", "windon", "windoff"]
TECH_LABELS = {
    "solarPV": "Solar PV",
    "windon": "Onshore Wind",
    "windoff": "Offshore Wind",
}
LR_COLORS = {
    "LR1": "#701A75",
    "LR4": "#0F172A",
    "LR7": "#0284C7",
}
MATERIAL_MARKERS = {
    "materials_base": "o",
    "materials_price_150": "s",
    "materials_tier1_50_tier2_75_price_150": "^",
    "materials_tier1_25_tier2_50_price_200": "D",
}
GENERATION_COLORS = {
    "solarPV": "#E69F00",
    "windon": "#66C2A5",
    "windoff": "#00876C",
}


def load_final_capacity_data():
    rows = []
    for material in MATERIAL_SCENARIOS:
        for learning_rate in LEARNING_RATES:
            file_path = scenario_file(BASE_DIR, learning_rate, material)
            if not file_path.exists():
                print(f"Missing scenario file: {file_path}")
                continue

            df = pd.read_excel(
                file_path,
                sheet_name="extension_only_totalcapacity",
            )
            df.columns = df.columns.str.lower()
            required_columns = {"stf", "tech", "capacity_ext"}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                raise ValueError(
                    f"{file_path} is missing columns: {sorted(missing_columns)}"
                )

            df["stf"] = pd.to_numeric(df["stf"].ffill(), errors="coerce")
            df["capacity_ext"] = pd.to_numeric(
                df["capacity_ext"], errors="coerce"
            ).fillna(0)
            df["tech"] = df["tech"].ffill().astype(str).str.strip()

            capacity_by_year = (
                df[
                    (df["stf"].between(2030, 2050))
                    & (df["tech"].isin(TECH_ORDER))
                ]
                .groupby(["stf", "tech"], as_index=False)["capacity_ext"]
                .sum()
            )

            for _, row in capacity_by_year.iterrows():
                rows.append(
                    {
                        "Learning Rate": learning_rate,
                        "Material Scenario": material,
                        "Technology": row["tech"],
                        "Technology Label": TECH_LABELS[row["tech"]],
                        "Year": int(row["stf"]),
                        "Capacity": row["capacity_ext"],
                    }
                )

    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError("No final capacity data was loaded.")
    return result


def plot_final_capacities(
    df,
    value_column="Capacity",
    ylabel="Capacity",
    title="Extension Capacities Across All Scenarios, 2030-2050",
    output_filename="Fig_Final_Capacities_Boxplot_2030_2050.pdf",
):
    years = list(range(2030, 2051))
    fig, axes = plt.subplots(
        len(TECH_ORDER),
        1,
        figsize=(12, 11),
        sharex=True,
        squeeze=False,
    )
    for axis, technology in zip(axes.flat, TECH_ORDER):
        technology_df = df[df["Technology"] == technology]
        sns.boxplot(
            data=technology_df,
            x="Year",
            y=value_column,
            order=years,
            color="white",
            linewidth=1.0,
            fliersize=0,
            ax=axis,
        )

        for learning_rate in LEARNING_RATES:
            for material in MATERIAL_SCENARIOS:
                subset = technology_df[
                    (technology_df["Learning Rate"] == learning_rate)
                    & (technology_df["Material Scenario"] == material)
                ]
                x_positions = [
                    years.index(year) - 0.18
                    + (LEARNING_RATES.index(learning_rate) * 0.18)
                    for year in subset["Year"]
                ]
                axis.scatter(
                    x_positions,
                    subset[value_column],
                    s=28,
                    color=LR_COLORS[learning_rate],
                    marker=MATERIAL_MARKERS[material],
                    edgecolor="black",
                    linewidth=0.4,
                    alpha=0.85,
                    label=f"{learning_rate} - {material}",
                    zorder=3,
                )

        axis.set_title(TECH_LABELS[technology])
        axis.set_ylabel(ylabel)
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_axisbelow(True)
        axis.tick_params(axis="x", labelrotation=45)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    unique_legend = dict(zip(labels, handles))
    fig.legend(
        unique_legend.values(),
        unique_legend.keys(),
        title="Learning rate - material scenario",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=True,
        fontsize=8,
    )
    axes[-1, 0].set_xlabel("Year")
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0, 0.84, 0.96))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved final-capacity boxplot -> {output_path}")


def load_generation_mix_data():
    rows = []
    for material in MATERIAL_SCENARIOS:
        for learning_rate in LEARNING_RATES:
            file_path = scenario_file(BASE_DIR, learning_rate, material)
            if not file_path.exists():
                print(f"Missing scenario file: {file_path}")
                continue

            df = pd.read_excel(file_path, sheet_name="extension_balance")
            df.columns = df.columns.str.lower()
            required_columns = {"stf", "process", "value"}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                raise ValueError(
                    f"{file_path} is missing columns: {sorted(missing_columns)}"
                )

            df["stf"] = pd.to_numeric(df["stf"].ffill(), errors="coerce")
            # extension_balance values are in GWh; plots and summary tables use TWh.
            df["value"] = (
                pd.to_numeric(df["value"], errors="coerce").fillna(0) / 1000
            )
            df["process"] = df["process"].ffill().astype(str).str.lower()

            def technology(process):
                if "solarpv" in process or "solar" in process:
                    return "solarPV"
                if "windon" in process:
                    return "windon"
                if "windoff" in process:
                    return "windoff"
                return None

            df["Technology"] = df["process"].map(technology)
            df = df[
                df["stf"].between(2030, 2050)
                & df["Technology"].notna()
            ]
            grouped = (
                df.groupby(["stf", "Technology"], as_index=False)["value"]
                .sum()
                .rename(columns={"stf": "Year", "value": "Generation"})
            )
            grouped["Learning Rate"] = learning_rate
            grouped["Material Scenario"] = material
            rows.extend(grouped.to_dict("records"))

    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError("No generation-mix data was loaded.")
    return result


def plot_generation_comparison(df, deviation=False):
    years = list(range(2030, 2051))
    fig, axes = plt.subplots(
        len(TECH_ORDER),
        1,
        figsize=(12, 14),
        sharex=True,
        squeeze=False,
    )

    baseline = df[
        (df["Learning Rate"] == "LR4")
        & (df["Material Scenario"] == "materials_base")
    ][["Year", "Technology", "Generation"]].rename(
        columns={"Generation": "Baseline Generation"}
    )
    comparison_data = df.merge(
        baseline,
        on=["Year", "Technology"],
        how="left",
        validate="many_to_one",
    )
    if comparison_data["Baseline Generation"].isna().any():
        raise RuntimeError("Missing LR4 materials_base generation baseline data.")
    if (comparison_data["Baseline Generation"] == 0).any():
        raise RuntimeError(
            "Cannot calculate generation deviation from a zero baseline."
        )
    comparison_data["Deviation"] = (
        (comparison_data["Generation"] - comparison_data["Baseline Generation"])
        / comparison_data["Baseline Generation"]
        * 100
    )
    value_column = "Deviation" if deviation else "Generation"

    for axis, technology in zip(axes.flat, TECH_ORDER):
        technology_df = comparison_data[
            comparison_data["Technology"] == technology
        ]
        sns.boxplot(
            data=technology_df,
            x="Year",
            y=value_column,
            order=years,
            color="white",
            linewidth=1.0,
            fliersize=0,
            ax=axis,
        )
        for learning_rate in LEARNING_RATES:
            for material in MATERIAL_SCENARIOS:
                subset = technology_df[
                    (technology_df["Learning Rate"] == learning_rate)
                    & (technology_df["Material Scenario"] == material)
                ]
                x_positions = [
                    years.index(year) - 0.18
                    + (LEARNING_RATES.index(learning_rate) * 0.18)
                    for year in subset["Year"]
                ]
                axis.scatter(
                    x_positions,
                    subset[value_column],
                    s=28,
                    color=LR_COLORS[learning_rate],
                    marker=MATERIAL_MARKERS[material],
                    edgecolor="black",
                    linewidth=0.4,
                    alpha=0.85,
                    label=f"{learning_rate} - {material}",
                    zorder=3,
                )
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(TECH_LABELS[technology])
        axis.set_ylabel(
            "Deviation from LR4 materials_base (%)"
            if deviation
            else "Generated electricity (TWh)"
        )
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        axis.set_axisbelow(True)
        axis.tick_params(axis="x", labelrotation=45)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    unique_legend = dict(zip(labels, handles))
    fig.legend(
        unique_legend.values(),
        unique_legend.keys(),
        title="Learning rate - material scenario",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=True,
        fontsize=8,
    )
    combined = (
        comparison_data.groupby(
            ["Year", "Learning Rate", "Material Scenario"], as_index=False
        )[["Generation", "Baseline Generation"]]
        .sum()
    )
    combined["Deviation"] = (
        (combined["Generation"] - combined["Baseline Generation"])
        / combined["Baseline Generation"]
        * 100
    )
    scenario_keys = ["Learning Rate", "Material Scenario"]
    summary = combined.groupby(scenario_keys).agg(
        generated_mean=("Generation", "mean"),
        deviation_mean=("Deviation", "mean"),
    ).reset_index()
    for year in [2030, 2040, 2050]:
        year_values = combined[combined["Year"] == year][
            scenario_keys + ["Generation", "Deviation"]
        ].rename(
            columns={
                "Generation": f"generated_{year}",
                "Deviation": f"deviation_{year}",
            }
        )
        summary = summary.merge(year_values, on=scenario_keys, how="left")
    summary["Scenario"] = (
        summary["Learning Rate"] + " / " + summary["Material Scenario"]
    )
    if deviation:
        title = "Electricity Generation Deviation from LR4 materials_base, 2030-2050"
        filename = "Fig_Generation_Deviation_Boxplot_2030_2050.pdf"
    else:
        title = "Generated Electricity Across Scenarios, 2030-2050"
        filename = "Fig_Generation_Absolute_Boxplot_2030_2050.pdf"

    axes[-1, 0].set_xlabel("Year")
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0, 0.84, 0.96))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved generation comparison plot -> {output_path}")
    return summary


def save_generation_summary_table(summary, output_filename, deviation=False):
    """Save the combined-generation benchmark table as a readable standalone PDF."""
    columns = ["Scenario", "2030", "2040", "2050", "Mean"]
    rows = []
    for _, row in summary.iterrows():
        if deviation:
            values = [
                row["Scenario"],
                f"{row['deviation_2030']:+.1f}%",
                f"{row['deviation_2040']:+.1f}%",
                f"{row['deviation_2050']:+.1f}%",
                f"{row['deviation_mean']:+.1f}%",
            ]
        else:
            values = [
                row["Scenario"],
                f"{row['generated_2030']:,.1f}",
                f"{row['generated_2040']:,.1f}",
                f"{row['generated_2050']:,.1f}",
                f"{row['generated_mean']:,.1f}",
            ]
        rows.append(values)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="center",
        loc="center",
        bbox=(0, 0, 1, 0.85),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    unit = "%" if deviation else "TWh"
    ax.set_title(
        "Combined Solar PV + Onshore Wind + Offshore Wind\n"
        f"Scenario benchmark table ({unit})",
        pad=20,
    )
    fig.savefig(OUTPUT_DIR / output_filename, format="pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    capacity_data = load_final_capacity_data()
    plot_final_capacities(capacity_data)

    baseline = capacity_data[
        (capacity_data["Learning Rate"] == "LR4")
        & (capacity_data["Material Scenario"] == "materials_base")
    ][["Year", "Technology", "Capacity"]].rename(
        columns={"Capacity": "Baseline Capacity"}
    )
    deviation_data = capacity_data.merge(
        baseline,
        on=["Year", "Technology"],
        how="left",
        validate="many_to_one",
    )
    if deviation_data["Baseline Capacity"].isna().any():
        raise RuntimeError("Missing LR4 materials_base baseline data.")
    if (deviation_data["Baseline Capacity"] == 0).any():
        raise RuntimeError(
            "Cannot calculate percentage deviation from a zero baseline capacity."
        )
    deviation_data["Deviation"] = (
        (deviation_data["Capacity"] - deviation_data["Baseline Capacity"])
        / deviation_data["Baseline Capacity"]
        * 100
    )
    plot_final_capacities(
        deviation_data,
        value_column="Deviation",
        ylabel="Deviation from LR4 materials_base (%)",
        title=(
            "Extension Capacity Deviation from LR4 materials_base, "
            "2030-2050"
        ),
        output_filename="Fig_Final_Capacities_Deviation_Boxplot_2030_2050.pdf",
    )
    generation_data = load_generation_mix_data()
    absolute_summary = plot_generation_comparison(
        generation_data, deviation=False
    )
    deviation_summary = plot_generation_comparison(
        generation_data, deviation=True
    )
    save_generation_summary_table(
        absolute_summary,
        "Fig_Generation_Combined_Summary_Table_TWh.pdf",
        deviation=False,
    )
    save_generation_summary_table(
        deviation_summary,
        "Fig_Generation_Combined_Summary_Table_Deviation.pdf",
        deviation=True,
    )
