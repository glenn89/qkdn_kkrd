import matplotlib.pyplot as plt

# Data
labels = [
    "Non-proactive key generation",
    "1-hop proactive key generation",
    "n-hop proactive key generation"
]

values = [497.1375, 113.0173, 79.5904]

colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

# Figure size
plt.figure(figsize=(12, 8))

# Bar plot
bars = plt.bar(labels, values, color=colors, width=0.48)

# Y-axis label
plt.ylabel("Average delay", fontsize=20)

# Axis tick font size
plt.xticks(fontsize=16)
plt.yticks(fontsize=18)

# Y-axis range and ticks
plt.ylim(0, 600)
plt.yticks(range(0, 601, 100), fontsize=18)

# Grid line
plt.grid(axis="y", linestyle="--", linewidth=1.2, alpha=0.6)
plt.gca().set_axisbelow(True)

# Value labels on top of bars
for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 10,
        f"{value:g}",
        ha="center",
        va="bottom",
        fontsize=20
    )

# Remove top and right spines
ax = plt.gca()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Make left and bottom axis lines thicker
ax.spines["left"].set_linewidth(1.5)
ax.spines["bottom"].set_linewidth(1.5)

# No title, no x-axis title
plt.xlabel("")

# Layout
plt.tight_layout()

# Save figure
plt.savefig("service_provision_bar_graph.png", dpi=300, bbox_inches="tight")

# Show figure
plt.show()