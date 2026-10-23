import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import concurrent.futures
import time

# ==========================================
# Setup matplotlib style
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

# ==========================================
# Define Scenario Space
# ==========================================
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR / "result" / "results_server_201026"

learning_rates = ["LR1", "LR4", "LR7"]
industry_names = [
    "nzia_0_crma_0",
    "nzia_15_crma_10",
    "nzia_30_crma_20",
    "nzia_40_crma_25",
    "nzia_50_crma_35",
]
material_names = [
    "materials_base",
    "materials_price_150",
    "materials_tier1_50_tier2_75_price_150",
    "materials_tier1_25_tier2_50_price_200",
]


# ==========================================
# Multi-Core Data Loader
# ==========================================
def process_scenario(args):
    lr, ind, mat, base_dir_str = args
    base_dir = Path(base_dir_str)
    scenario_name = f"{lr}_{ind}_{mat}"
    file_path = base_dir / scenario_name / f"{scenario_name}.xlsx"

    if not file_path.exists():
        return None, None, None, None, scenario_name, "File not found"

    try:
        sheets = pd.read_excel(
            file_path,
            sheet_name=[
                "production_elec_demand",
                "scrap",
                "scrap_processed",
                "minerals",
                "extension_balance",
            ],
            # engine="calamine" # Uncomment if you installed python-calamine for extreme speed
        )

        # 1. Induced Demand (Data is in GWh)
        df_elec = sheets["production_elec_demand"]
        df_elec["stf"] = df_elec["stf"].ffill()
        df_elec = df_elec.groupby("stf")["demand_production"].sum().reset_index()
        df_elec["LR"], df_elec["Industry"], df_elec["Material"] = lr, ind, mat

        # 2. Scrap & Recycling (Data is in kton)
        df_scrap = sheets["scrap"]
        df_scrap["stf"] = df_scrap["stf"].ffill()
        df_scrap = df_scrap.groupby("stf")["capacity_scrap_total"].sum().reset_index()

        df_rec = sheets["scrap_processed"]
        df_rec["stf"] = df_rec["stf"].ffill()
        df_rec = df_rec.groupby("stf")["capacity_scrap_rec"].sum().reset_index()

        df_valley = pd.merge(df_scrap, df_rec, on="stf", how="outer").fillna(0)
        df_valley["unprocessed_gap"] = (
            df_valley["capacity_scrap_total"] - df_valley["capacity_scrap_rec"]
        )
        df_valley["LR"], df_valley["Industry"], df_valley["Material"] = lr, ind, mat

        # 3. Minerals (Data is in kton)
        df_min = sheets["minerals"]
        df_min["stf"] = df_min["stf"].ffill()
        df_min = (
            df_min.groupby("stf")[
                ["material_imported", "material_mined", "material_recycled"]
            ]
            .sum()
            .reset_index()
        )
        df_min["LR"], df_min["Industry"], df_min["Material"] = lr, ind, mat

        # 4. Power Gen / CCUS Escape (Data is in GWh)
        df_bal = sheets["extension_balance"]
        df_bal.columns = df_bal.columns.str.lower()
        df_bal[["stf", "site"]] = df_bal[["stf", "site"]].ffill()
        df_bal["stf"] = pd.to_numeric(df_bal["stf"], errors="coerce")
        df_bal["value"] = pd.to_numeric(df_bal["value"], errors="coerce")
        df_bal = df_bal[df_bal["stf"].isin([2030, 2040, 2050])]

        def categorize_tech(process):
            p = str(process).lower()
            if "ccus" in p:
                return "Fossil + CCUS"
            if (
                "solar" in p
                or "wind" in p
                or "hydro" in p
                or "nuclear" in p
                or "biomass" in p
            ):
                return "Clean/RES"
            return "Other/Fossil Unabated"

        df_bal["tech_cat"] = df_bal["process"].apply(categorize_tech)
        df_gen = df_bal.groupby(["stf", "tech_cat"])["value"].sum().reset_index()
        df_gen["LR"], df_gen["Industry"], df_gen["Material"] = lr, ind, mat

        return df_elec, df_valley, df_min, df_gen, scenario_name, "Success"

    except Exception as e:
        return None, None, None, None, scenario_name, f"Error: {e}"


def get_data():
    scenarios = [
        (lr, ind, mat, str(BASE_DIR))
        for lr in learning_rates
        for ind in industry_names
        for mat in material_names
    ]
    all_elec, all_valley, all_min, all_gen = [], [], [], []

    print(f"Using all CPU cores to load {len(scenarios)} files...")
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_scenario, s): s for s in scenarios}
        for future in concurrent.futures.as_completed(futures):
            e, v, m, g, name, status = future.result()
            if status == "Success":
                all_elec.append(e)
                all_valley.append(v)
                all_min.append(m)
                all_gen.append(g)
            else:
                print(f"Skipped: {name} ({status})")

    print(f"Loaded in {round(time.time() - start, 1)} seconds.")
    return (
        pd.concat(all_elec, ignore_index=True),
        pd.concat(all_valley, ignore_index=True),
        pd.concat(all_min, ignore_index=True),
        pd.concat(all_gen, ignore_index=True),
    )

def process_single_capacity(args):
    """
    Top-level helper function for multi-processing.
    """
    import pandas as pd  # Ensure pandas is available in the worker process
    from pathlib import Path

    lr, ind, mat, base_dir_str = args
    base_dir = Path(base_dir_str)
    scenario_name = f"{lr}_{ind}_{mat}"
    file_path = base_dir / scenario_name / f"{scenario_name}.xlsx"

    if not file_path.exists():
        return None

    try:
        df = pd.read_excel(file_path, sheet_name="processing_capacities")

        # Forward fill just in case
        cols = ["stf", "location", "tech", "stages"]
        existing_cols = [c for c in cols if c in df.columns]
        df[existing_cols] = df[existing_cols].ffill()

        # Filter for relevant technologies and group up the total capacity
        df = df[df["tech"].isin(["solarPV", "windon", "windoff"])]
        df_agg = (
            df.groupby(["stf", "tech"])["capacity_processing_total"].sum().reset_index()
        )

        # Tag with scenario dimensions
        df_agg["LR"] = lr
        df_agg["Industry"] = ind
        df_agg["Material"] = mat

        return df_agg
    except Exception:
        return None


def load_processing_capacities_across_scenarios():
    """
    Loads the 'processing_capacities' sheet across all LR, Industry, and Material combinations.
    """
    scenarios = [
        (lr, ind, mat, str(BASE_DIR))
        for lr in learning_rates
        for ind in industry_names
        for mat in material_names
    ]

    print(f"Loading processing capacities from {len(scenarios)} scenarios...")
    start = time.time()

    all_data = []
    # Using ProcessPoolExecutor with the top-level function
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(process_single_capacity, scenarios):
            if result is not None:
                all_data.append(result)

    print(f"Loaded in {round(time.time() - start, 1)} seconds.")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()



def process_single_stage_capacity(args):
    """
    Top-level helper function for multi-processing. Extracts capacities by Stage.
    """
    import pandas as pd
    from pathlib import Path

    lr, ind, mat, base_dir_str = args
    base_dir = Path(base_dir_str)
    scenario_name = f"{lr}_{ind}_{mat}"
    file_path = base_dir / scenario_name / f"{scenario_name}.xlsx"

    if not file_path.exists():
        return None

    try:
        df = pd.read_excel(file_path, sheet_name="processing_capacities")

        # Forward fill just in case
        cols = ["stf", "location", "tech", "stages"]
        existing_cols = [c for c in cols if c in df.columns]
        df[existing_cols] = df[existing_cols].ffill()

        # Filter for relevant technologies
        df = df[df["tech"].isin(["solarPV", "windon", "windoff"])]

        # GROUP BY STAGES explicitly instead of just tech
        df_agg = (
            df.groupby(["stf", "tech", "stages"])["capacity_processing_total"]
            .sum()
            .reset_index()
        )

        # Tag with scenario dimensions
        df_agg["LR"] = lr
        df_agg["Industry"] = ind
        df_agg["Material"] = mat

        return df_agg
    except Exception:
        return None


def load_processing_capacities_by_stage():
    """
    Loads the 'processing_capacities' sheet across all scenarios, keeping stage granularity.
    """
    scenarios = [
        (lr, ind, mat, str(BASE_DIR))
        for lr in learning_rates
        for ind in industry_names
        for mat in material_names
    ]

    print(
        f"Loading stage-level processing capacities from {len(scenarios)} scenarios..."
    )
    start = time.time()

    all_data = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(process_single_stage_capacity, scenarios):
            if result is not None:
                all_data.append(result)

    print(f"Loaded in {round(time.time() - start, 1)} seconds.")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


def process_single_scrap_processed(args):
    """
    Top-level helper function for multi-processing. Extracts recovered scrap volumes.
    """
    import pandas as pd
    from pathlib import Path

    lr, ind, mat, base_dir_str = args
    base_dir = Path(base_dir_str)
    scenario_name = f"{lr}_{ind}_{mat}"
    file_path = base_dir / scenario_name / f"{scenario_name}.xlsx"

    if not file_path.exists():
        return None

    try:
        df = pd.read_excel(file_path, sheet_name="scrap_processed")

        # Forward fill formatting gaps
        cols = ["stf", "location", "tech"]
        existing_cols = [c for c in cols if c in df.columns]
        df[existing_cols] = df[existing_cols].ffill()

        # Filter for relevant technologies (Drop Batteries)
        df = df[df["tech"].isin(["solarPV", "windon", "windoff"])]

        # Group by Year and Tech to sum the capacity_scrap_rec
        df_agg = df.groupby(["stf", "tech"])["capacity_scrap_rec"].sum().reset_index()

        # Tag with scenario dimensions
        df_agg["LR"] = lr
        df_agg["Industry"] = ind
        df_agg["Material"] = mat

        return df_agg
    except Exception:
        return None


def load_scrap_processed_across_scenarios():
    """
    Loads the 'scrap_processed' sheet across all LR, Industry, and Material combinations.
    """
    scenarios = [
        (lr, ind, mat, str(BASE_DIR))
        for lr in learning_rates
        for ind in industry_names
        for mat in material_names
    ]

    print(f"Loading recovered scrap volumes from {len(scenarios)} scenarios...")
    start = time.time()

    all_data = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(process_single_scrap_processed, scenarios):
            if result is not None:
                all_data.append(result)

    print(f"Loaded in {round(time.time() - start, 1)} seconds.")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
# ==========================================
# COMPARATIVE PLOTTING FUNCTIONS
# ==========================================
def plot_scrap_processed_comprehensive(df):
    """
    Plots Recovered Scrap (kt) for Solar PV, Wind Onshore, and Wind Offshore
    across all Learning Rates, Industry constraints, and Material Prices.
    """
    print("Plotting Comprehensive Recovered Scrap Volumes...")

    # Filter to start from 2025
    df_plot = df[df["stf"] >= 2025].copy()

    # Clean up tech names for the plot labels
    tech_mapping = {
        "solarPV": "Solar PV",
        "windon": "Wind Onshore",
        "windoff": "Wind Offshore",
    }
    df_plot["tech_label"] = df_plot["tech"].map(tech_mapping)

    # Create FacetGrid: Columns = LRs, Rows = Technologies
    g = sns.relplot(
        data=df_plot,
        x="stf",
        y="capacity_scrap_rec",
        col="LR",
        row="tech_label",
        col_order=["LR1", "LR4", "LR7"],
        row_order=["Solar PV", "Wind Onshore", "Wind Offshore"],
        hue="Industry",
        style="Material",
        kind="line",
        height=3.5,  # Height of each individual subplot
        aspect=1.4,  # Width ratio
        markers=True,
        dashes=True,
        alpha=0.8,
        palette="viridis",
        facet_kws={"sharey": "row"},  # Ensures Wind/Solar get their own Y-axis scales
    )

    # Formatting and Labels
    g.set_axis_labels("Year", "Recovered Scrap (kt)")
    g.set_titles(col_template="Learning Rate: {col_name}", row_template="{row_name}")

    g.fig.suptitle(
        "Recovered Scrap Volumes vs. NZIA/CRMA Stringency and Material Prices",
        y=1.03,
        fontsize=18,
        weight="bold",
    )

    # Move legend outside the main grid
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1), frameon=False)

    # Save as High-Res Vector PDF
    out_file = "comp_scrap_processed_comprehensive.pdf"
    plt.savefig(out_file, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"   ✔ Comprehensive Recovered Scrap plot saved -> {out_file}")

def plot_induced_demand_comparison(df, target_lr="LR4", target_mat="materials_base"):
    """Compares Induced Electricity Demand across Industry Policy stringencies."""
    df_plot = df[(df["LR"] == target_lr) & (df["Material"] == target_mat)].copy()

    # FIX: Convert GWh to TWh for accurate axis labeling
    df_plot["demand_production_TWh"] = df_plot["demand_production"] / 1000

    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df_plot,
        x="stf",
        y="demand_production_TWh",
        hue="Industry",
        marker="o",
        palette="viridis",
    )
    plt.title(
        f"Induced Energy Demand vs. NZIA/CRMA Stringency\n({target_lr}, {target_mat})",
        fontsize=14,
    )
    plt.ylabel("Electricity Demand (TWh)")
    plt.xlabel("Year")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Policy Stringency", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("comp_1_induced_demand.png", dpi=300)
    plt.close()


def plot_valley_of_death_comparison(df, target_lr="LR4"):
    """Compares the unprocessed scrap gap between Base and Extreme material scenarios."""
    mats_to_compare = ["materials_base", "materials_tier1_25_tier2_50_price_200"]
    df_plot = df[
        (df["LR"] == target_lr)
        & (df["Material"].isin(mats_to_compare))
        & (df["Industry"] == "nzia_30_crma_20")
    ].copy()

    g = sns.FacetGrid(df_plot, col="Material", height=5, aspect=1.2)
    g.map(
        sns.lineplot,
        "stf",
        "capacity_scrap_total",
        color="red",
        label="Available Scrap",
    )
    g.map(
        sns.lineplot, "stf", "capacity_scrap_rec", color="green", label="Recycled Scrap"
    )
    g.map(
        sns.lineplot,
        "stf",
        "unprocessed_gap",
        color="black",
        linestyle="--",
        label="Valley of Death Gap",
    )

    # FIX: Label correctly as Kilotons (kton) instead of Capacity Equivalent
    g.set_axis_labels("Year", "Scrap Volume (kton)")
    g.set_titles("{col_name}")
    g.add_legend()
    g.fig.suptitle(
        f"Recycling Valley of Death: Base vs. Extreme Materials\n(Policy: NZIA 30, {target_lr})",
        y=1.05,
    )
    plt.savefig("comp_2_valley_of_death.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_sourcing_comparison(df, target_year=2050, target_lr="LR4"):
    """100% Stacked bar comparing Sourcing (Import/Mine/Recycle) across Industry Policies."""
    df_plot = df[
        (df["stf"] == target_year)
        & (df["LR"] == target_lr)
        & (df["Material"] == "materials_base")
    ].copy()

    # Calculate percentages (Works smoothly regardless of kton scale)
    df_plot["Total"] = (
        df_plot["material_imported"]
        + df_plot["material_mined"]
        + df_plot["material_recycled"]
    )
    for col in ["material_imported", "material_mined", "material_recycled"]:
        df_plot[f"{col}_pct"] = (df_plot[col] / df_plot["Total"]) * 100

    df_plot = df_plot.set_index("Industry")[
        ["material_imported_pct", "material_mined_pct", "material_recycled_pct"]
    ]

    ax = df_plot.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 6),
        color=["#1f77b4", "#ff7f0e", "#2ca02c"],
    )
    plt.title(
        f"Material Sourcing Mix in {target_year} Across Policy Stringency\n({target_lr}, Base Materials)",
        fontsize=14,
    )
    plt.ylabel("Share of Total Sourcing (%)")
    plt.xlabel("Industry Policy Stringency")
    plt.xticks(rotation=45, ha="right")
    plt.legend(
        ["Imported", "Mined (Domestic)", "Recycled"],
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.tight_layout()
    plt.savefig("comp_3_material_sourcing.png", dpi=300)
    plt.close()


def plot_ccus_escape_route(df, target_year=2050, target_lr="LR4"):
    """Shows how the share of Fossil+CCUS increases as Material Constraints get tighter."""
    df_plot = df[(df["stf"] == target_year) & (df["LR"] == target_lr)].copy()

    # Calculate Percentages (Works smoothly regardless of GWh scale)
    totals = (
        df_plot.groupby(["Industry", "Material"])["value"]
        .sum()
        .reset_index(name="Total")
    )
    df_plot = pd.merge(df_plot, totals, on=["Industry", "Material"])
    df_plot["pct"] = (df_plot["value"] / df_plot["Total"]) * 100

    # Filter just to Fossil + CCUS
    df_ccus = df_plot[df_plot["tech_cat"] == "Fossil + CCUS"].copy()

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_ccus, x="Industry", y="pct", hue="Material", palette="Reds")
    plt.title(
        f"The CCUS Escape Route in {target_year} ({target_lr})\nShare of Fossil+CCUS in Generation Mix",
        fontsize=14,
    )
    plt.ylabel("Share of Total Generation (%)")
    plt.xlabel("Industry Policy Stringency")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Material Constraints", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("comp_4_ccus_escape.png", dpi=300)
    plt.close()

def plot_induced_demand_comprehensive(df):
    """
    Compares Induced Electricity Demand across all Industry, Material, and LR scenarios.
    Generates subplots for each Learning Rate with shared Y-axes and saves as a vector PDF.
    Starts from the year 2025.
    """
    df_plot = df.copy()

    # Filter the data to start from 2025
    df_plot = df_plot[df_plot["stf"] >= 2025]

    # Convert GWh to TWh for accurate axis labeling
    df_plot["demand_production_TWh"] = df_plot["demand_production"] / 1000

    # sns.relplot automatically shares the y-axis across columns (cols) by default
    g = sns.relplot(
        data=df_plot,
        x="stf",
        y="demand_production_TWh",
        col="LR",
        col_order=["LR1", "LR4", "LR7"],  # Ensure logical progression
        hue="Industry",
        style="Material",
        kind="line",
        height=5,
        aspect=1.1,
        markers=True,
        dashes=True,
        alpha=0.8,
        palette="viridis",
    )

    # Labeling and Formatting
    g.set_axis_labels("Year", "Electricity Demand (TWh)")
    g.set_titles(col_template="Learning Rate: {col_name}")
    g.fig.suptitle(
        "Induced Energy Demand vs. NZIA/CRMA Stringency and Material Prices",
        y=1.05,
        fontsize=16,
    )

    # Adjust legend
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1), frameon=False)

    # Save as high-resolution vector PDF
    plt.savefig(
        "comp_1_induced_demand_comprehensive.pdf", format="pdf", bbox_inches="tight"
    )
    plt.close()

def plot_comprehensive_processing_capacities(df):
    """
    Plots Processing Capacities for Solar PV, Wind Onshore, and Wind Offshore
    across all Learning Rates, Industry constraints, and Material Prices.
    """
    print("Plotting Comprehensive Processing Capacities...")
    df_plot = df.copy()

    # Filter to start from 2025
    df_plot = df_plot[df_plot["stf"] >= 2025]

    # Clean up tech names for the plot labels
    tech_mapping = {
        "solarPV": "Solar PV",
        "windon": "Wind Onshore",
        "windoff": "Wind Offshore",
    }
    df_plot["tech_label"] = df_plot["tech"].map(tech_mapping)

    # Create a FacetGrid: Columns = LRs, Rows = Technologies
    g = sns.relplot(
        data=df_plot,
        x="stf",
        y="capacity_processing_total",
        col="LR",
        row="tech_label",
        col_order=["LR1", "LR4", "LR7"],
        row_order=["Solar PV", "Wind Onshore", "Wind Offshore"],
        hue="Industry",
        style="Material",
        kind="line",
        height=3.5,  # Height of each individual subplot
        aspect=1.4,  # Width ratio of each subplot
        markers=True,
        dashes=True,
        alpha=0.8,
        palette="viridis",
        facet_kws={
            "sharey": "row"
        },  # Shares Y-axis across LRs, but allows each Tech to have its own scale
    )

    # Formatting and Labels
    g.set_axis_labels("Year", "Processing Capacity (GW/yr)")
    g.set_titles(col_template="Learning Rate: {col_name}", row_template="{row_name}")

    g.fig.suptitle(
        "Installed Processing Capacities vs. NZIA/CRMA Stringency and Material Prices",
        y=1.03,
        fontsize=18,
        weight="bold",
    )

    # Move legend outside the main grid
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1), frameon=False)

    # Save as High-Res Vector PDF
    plt.savefig(
        "comp_processing_capacities_comprehensive.pdf",
        format="pdf",
        bbox_inches="tight",
    )
    plt.close()
    print("✔ Comprehensive Processing Capacities plot saved as PDF.")

def plot_stage_processing_capacities(df):
    """
    Plots Processing Capacities broken down by Stages.
    Generates a separate plot for Solar PV, Wind Onshore, and Wind Offshore.
    Strictly filters out irrelevant stages for each technology.
    """
    print("Plotting Processing Capacities by Stage...")

    # Filter to start from 2025
    df_plot = df[df["stf"] >= 2025].copy()

    tech_mapping = {
        "solarPV": "Solar PV",
        "windon": "Wind Onshore",
        "windoff": "Wind Offshore",
    }

    # Use the mapping you defined earlier to filter and order the rows
    tech_stage_map = {
        "solarPV": ["Polysilicon", "Wafer", "Cell", "Module"],
        "windon": ["BladeOn", "TowerOn", "NacelleOn"],
        "windoff": ["BladeOff", "TowerOff", "NacelleOff"],
    }

    # Loop through each technology and create a dedicated plot
    for tech_key, tech_name in tech_mapping.items():
        valid_stages = tech_stage_map.get(tech_key, [])

        # Strictly filter data for this tech AND its corresponding stages
        df_tech = df_plot[
            (df_plot["tech"] == tech_key) & (df_plot["stages"].isin(valid_stages))
        ]

        if df_tech.empty:
            print(f"   ⚠️ Skipping {tech_name}: No valid stage data found.")
            continue

        # Create FacetGrid: Columns = LRs, Rows = Stages
        g = sns.relplot(
            data=df_tech,
            x="stf",
            y="capacity_processing_total",
            col="LR",
            row="stages",
            col_order=["LR1", "LR4", "LR7"],
            row_order=valid_stages,  # Force correct supply chain order top-to-bottom
            hue="Industry",
            style="Material",
            kind="line",
            height=3.0,  # Slightly shorter height per row since there are more rows
            aspect=1.5,
            markers=True,
            dashes=True,
            alpha=0.8,
            palette="viridis",
            facet_kws={
                "sharey": "row"
            },  # Ensures same Y-axis scale across LRs for a specific stage
        )

        # Formatting
        g.set_axis_labels("Year", "Processing Capacity (GW/yr)")
        g.set_titles(col_template="LR: {col_name}", row_template="Stage: {row_name}")

        g.fig.suptitle(
            f"Processing Capacities by Stage: {tech_name}\nvs. NZIA/CRMA Stringency & Material Prices",
            y=1.03,
            fontsize=16,
            weight="bold",
        )

        # Move legend out of the way
        sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1), frameon=False)

        # Save specific tech plot
        out_file = f"comp_processing_stages_{tech_key}.pdf"
        plt.savefig(out_file, format="pdf", bbox_inches="tight")
        plt.close()
        print(f"   ✔ Saved {tech_name} stage comparison -> {out_file}")
# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    df_elec, df_valley, df_min, df_gen = get_data()

    if not df_elec.empty:
        print("Plotting Induced Demand Comparison...")
        plot_induced_demand_comparison(df_elec)

    if not df_valley.empty:
        print("Plotting Valley of Death Comparison...")
        plot_valley_of_death_comparison(df_valley)

    if not df_min.empty:
        print("Plotting Sourcing Comparison...")
        plot_sourcing_comparison(df_min)

    if not df_gen.empty:
        print("Plotting CCUS Escape Route...")
        plot_ccus_escape_route(df_gen)

    if not df_elec.empty:
        print("Plotting Comprehensive Induced Demand Comparison...")
        plot_induced_demand_comprehensive(df_elec)

    # Load and Plot the processing capacities
    df_proc_cap = load_processing_capacities_across_scenarios()

    if not df_proc_cap.empty:
        plot_comprehensive_processing_capacities(df_proc_cap)

    df_stage_caps = load_processing_capacities_by_stage()

    if not df_stage_caps.empty:
        plot_stage_processing_capacities(df_stage_caps)

    # Load and Plot the Recovered Scrap Volumes
    df_scrap_proc = load_scrap_processed_across_scenarios()

    if not df_scrap_proc.empty:
        plot_scrap_processed_comprehensive(df_scrap_proc)

    print("All comparison plots generated successfully.")
