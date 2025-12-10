import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------- Set font for LNG plots only -----------------
plt.rcParams["font.family"] = "Arial"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# Optional: default font size for these plots
plt.rcParams["font.size"] = 8

print("Current font family:", plt.rcParams["font.family"])
fig, ax = plt.subplots(figsize=(9, 4))
years = range(2025, 2035)
data = pd.read_excel("D:/für Max/Value_For_LNG_Plot2.xlsx", index_col="Year")
data = data.loc[2025:2035]

ax.plot(
    data.index,
    data["LTC"],
    color="#1B3C53",
    linewidth=2,
    linestyle="solid",
    label="Contractual LNG",
    zorder=3,
    marker="o",
)

ax.plot(
    data.index,
    data["Base_Case"],
    color="#F5A04E",
    linewidth=2,
    linestyle="solid",
    label="Current Policies",
    zorder=4,
    marker="o",
)

ax.plot(
    data.index,
    data["Maximum_Across_Scenarios"],
    color="#5459AC",
    linewidth=1.6,
    linestyle="--",
    label="Max. NZIA",
    zorder=3,
    marker="o",
)

ax.plot(
    data.index,
    data["Minimum_Across_Scenario"],
    color="#05A5D2",
    linewidth=1.6,
    linestyle="--",
    label="Base Case",
    zorder=2,
    marker="o",
)

ax.plot(
    data.index,
    data["Best_Case"],
    color="#007E6E",
    linewidth=1.5,
    linestyle="--",
    label="Optimistic",
    zorder=3,
    marker="o",
)

leg = ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, 1),
    ncol=5,
    frameon=True,
    handlelength=1.25,
    handletextpad=0.5,
    fontsize=12,
)
leg._legend_box.align = "left"
leg.get_frame().set_edgecolor("black")
ax.set_xlim([2024.5, 2036])
ax.set_xticks([2025, 2030, 2035])
ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8)
ax.tick_params(axis="x", labelsize=13)
ax.tick_params(axis="y", labelsize=13)
ax.set_ylabel("LNG Demand and Supply (bcm)", fontsize=13)
plt.tight_layout()
fig.savefig("LNG_Plot_Revised.pdf", dpi=1000)

###############################################################################

years = np.arange(2025, 2036)
data = pd.read_excel("D:/für Max/Value_For_LNG_Plot2.xlsx", index_col="Year")
data = data.loc[2025:2035]

data_max_increase = data["Max_Increase"]
data_min_increase = data["Min_Increase"]


fig, ax = plt.subplots(figsize=(9, 4))
width = 0.4

# Plot grouped bars
ax.bar(
    years - width / 2,
    data_min_increase,
    width=width,
    label="Minimum increase",
    color="#67B2D8",
    zorder=2,
)
ax.bar(
    years + width / 2,
    data_max_increase,
    width=width,
    label="Maximum increase",
    color="#E67E22",
    zorder=2,
)

for rects in ax.containers:
    ax.bar_label(rects, padding=1, fontsize=10, fmt="%.1f")

ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8, zorder=-2)
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=12)

ax.set_ylabel("Demand Increase in LNG (bcm)", fontsize=13)

ax.set_xticks(years)
leg = ax.legend(
    loc="upper left",
    bbox_to_anchor=(0.0, 1),
    ncol=1,
    frameon=True,
    handlelength=1.25,
    handletextpad=0.5,
    fontsize=12,
)
leg._legend_box.align = "left"
leg.get_frame().set_edgecolor("black")
ax.set_ylim([0, 21.5])

plt.tight_layout()
fig.savefig("Relative_Increase_LNG_BCM.png", dpi=400)

###############################################################################

fig, ax = plt.subplots(figsize=(9, 4))

Buffer_Base = data["Buffer_Base"]
ax.plot(
    years,
    Buffer_Base,
    label="Current policies",
    color="#222222",
    lw=2,
    zorder=4,
    marker="o",
    ls="dotted",
)

Buffer_Min = data["Buffer_Min"]
ax.plot(years, Buffer_Min, color="#57595B", lw=1, zorder=3)

Buffer_Max = data["Buffer_Max"]
ax.plot(years, Buffer_Max, color="#57595B", lw=1, zorder=3)

ax.fill_between(
    years, Buffer_Max, 0, color="#6DC3BB", zorder=2, label="Maximum increase"
)
ax.fill_between(
    years, Buffer_Max, Buffer_Min, color="#F2AEBB", zorder=2, label="Minimum increase"
)
# fill_between(x, y1, y2=0, where=None, interpolate=False, step=None, *, data=None, **kwargs)[source]

ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8, zorder=-2)
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=12)

ax.set_ylabel("Gap to Contractual LNG Supply (bcm)", fontsize=13)

ax.set_xticks(years)
leg = ax.legend(
    loc="lower right",
    bbox_to_anchor=(1, 0),
    ncol=1,
    frameon=True,
    handlelength=2,
    handletextpad=0.5,
    fontsize=12,
)
leg._legend_box.align = "left"
leg.get_frame().set_edgecolor("black")
ax.set_ylim([0, 75])

plt.tight_layout()
fig.savefig("Buffer_LNG_BCM.png", dpi=400)


#     # ----------------------------------------------------------------------
#     # 2. CUMULATIVE PERCENTAGE DEVIATION BOXPLOT (no outliers shown)
#     # ----------------------------------------------------------------------
#     base_cumulative = load_lng(base_file, years).cumsum()
#     nzia_cumulative = [load_lng(f, years).cumsum() for f in nzia_files]

#     # prepare DataFrame where each column is one scenario cumulative series
#     # if nzia_cumulative empty, handle gracefully
#     if nzia_cumulative:
#         data = pd.DataFrame({i: s for i, s in enumerate(nzia_cumulative)}).T
#         # pct_dev: columns for target years (we want distribution across scenarios)
#         pct_dev = pd.DataFrame({
#             y: 100 * (data[y] - base_cumulative[y]) / base_cumulative[y]
#             for y in target_years
#         })
#     else:
#         pct_dev = pd.DataFrame({y: pd.Series(dtype=float) for y in target_years})

#     plt.figure(figsize=(9, 5))
#     ax = plt.gca()
#     positions = np.arange(len(target_years))
#     box_data = [pct_dev[y].dropna() for y in target_years]

#     # draw boxplot without fliers/outliers (showfliers=False)
#     median_color = "#1F78B4"
#     median_linewidth = 2.0
#     bp = ax.boxplot(
#         box_data, positions=positions, widths=0.35, patch_artist=True,
#         showfliers=False,  # hide outliers
#         boxprops=dict(facecolor="#A6CEE3", alpha=0.75, linewidth=1.2),
#         medianprops=dict(color=median_color, linewidth=median_linewidth),
#         whiskerprops=dict(color="#666666", linestyle="--", linewidth=1.2),
#         capprops=dict(color="#666666", linewidth=1.2),
#         flierprops=dict(marker='o', markersize=4, markeredgecolor='none')  # not shown since showfliers=False
#     )

#     # Formatting for readability (larger fonts etc.)
#     ax.set_title("Cumulative LNG demand – Compared to current policies",
#                  fontsize=12, weight="bold")
#     ax.set_xlabel("Year", fontsize=10)
#     ax.set_ylabel("Deviation from base [%]", fontsize=10)
#     ax.set_xticks(positions)
#     ax.set_xticklabels(target_years, fontsize=10)
#     ax.grid(axis="y", linestyle=":", color="0.8", linewidth=0.8)

#     ax.tick_params(axis="x", labelsize=10)
#     ax.tick_params(axis="y", labelsize=10)

#     # Draw thin dashed horizontal lines from each median to the y-axis (no numeric text)
#     # Use the same color and thickness as the median, with slightly lower alpha
#     # We'll draw from the left axis limit to the box x position.
#     x_left = ax.get_xlim()[0]  # left axis coordinate
#     for i, med_line in enumerate(bp.get('medians', [])):
#         # median line y data; average the y-values to get a single median y
#         ydata = med_line.get_ydata()
#         if len(ydata) == 0:
#             continue
#         median_val = float(np.mean(ydata))

#         # horizontal dashed line from left axis to the box position using median style
#         ax.plot([x_left, positions[i]], [median_val, median_val],
#                 color=median_color, linestyle="--", linewidth=median_linewidth, alpha=0.65, zorder=2)

#         # small tick at the y-axis to indicate the median point (no numeric label)
#         ax.plot([x_left], [median_val], marker='|', markersize=14,
#                 color=median_color, markeredgewidth=1.6, alpha=0.9, zorder=3)

#     plt.tight_layout()
#     plt.savefig(out_path / "lng_cumulative_pct_deviation.pdf", dpi=600, bbox_inches="tight")
#     plt.show()
#     print("✔ LNG cumulative deviation plot saved")
