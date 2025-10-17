import matplotlib.pyplot as plt
import numpy as np

# Scenario labels
scenarios = [
    "Remain key / distance",
    "Remain key",
    "Distance",
    # "Non-proactive key generation",
    # r"1-hop proactive key generation ($th_{1}=10$)",
    # r"N-hop proactive key generation ($th_{1}=10$, $th_{4}=10$)",
]

# Success and blocking data for each scenario
success_simple = np.array([76.337, 75.945, 75.1])
success_weighted = np.array([97.288, 100.634, 108.1])

# Calculate adjusted values: success + abs(blocking)

# X-axis methods
methods = ["Shortest path key relay", "Weighted shortest path key relay"]
x = np.arange(len(methods))

# Colors for each scenario
colors = ['#4E79A7', '#F28E2B', '#59A14F']

# Plot configuration
width = 0.2
plt.figure(figsize=(10, 6))

# # Plot hatched background bars (white face, colored edge)
# for i, color in enumerate(colors):
#     offset = (i - 1.5) * width
#     plt.bar(x + offset,
#             [adjusted_simple[i], adjusted_weighted[i]],
#             width, facecolor='white', edgecolor=color, hatch='///', zorder=0)

# Plot main success bars
bars = []
for i, color in enumerate(colors):
    offset = (i - 1.5) * width
    bar = plt.bar(x + offset,
                  [success_simple[i], success_weighted[i]],
                  width, color=color, label=scenarios[i], zorder=1)
    bars.append(bar)

# Annotate values inside the top of bars
font_size = 12
for bar_group in bars:
    for bar in bar_group:
        height = bar.get_height()
        # Place the text 2% below the bar top inside
        y_pos = height * 0.98
        plt.text(
            bar.get_x() + bar.get_width() / 2, y_pos,
            f"{height:.1f} ms", ha='center', va='top',
            fontsize=font_size, color='white', weight='bold', zorder=2
        )

center_offset = (-1.5 + (len(scenarios)-1)/2) * width
plt.xticks(x + center_offset, methods, fontsize=12)
# plt.ylabel("The number of service provision", fontsize=12)
plt.ylabel("Average delay (ms)", fontsize=12)

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.grid(True, axis='x', linestyle='--', alpha=0.3)

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=False, fontsize=12)
# plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.15),
#            ncol=2, frameon=False, fontsize=12)
plt.tight_layout()
plt.show()