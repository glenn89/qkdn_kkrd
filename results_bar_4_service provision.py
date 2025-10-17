import matplotlib.pyplot as plt
import numpy as np

# Scenario labels
scenarios = [
    "Non-proactive key generation",
    r"1-hop proactive key generation ($th_{1}=10$, $th_{4}=8$)",
    r"1-hop proactive key generation ($th_{1}=10$, $th_{4}=9$)",
    r"1-hop proactive key generation ($th_{1}=10$, $th_{4}=10$)"
]

# Success data for each scenario
success_simple = np.array([4673.4, 4345.6, 4106., 4070.2])
success_weighted = np.array([4799.2, 4797.8, 4584.8, 4122.8])
# Blocking data
blocking_simple = np.array([-61.8, -98.6, -368.2, -786.4])
blocking_weighted = np.array([-57.4, -58.8, -271.8, -733.8])

# Calculate adjusted (success + abs(blocking))
adjusted_simple = success_simple + np.abs(blocking_simple)
adjusted_weighted = success_weighted + np.abs(blocking_weighted)

# X-axis methods
methods = ["Shortest path key relay", "Weighted shortest path key relay"]
x = np.arange(len(methods))

# Colors for each scenario
colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2']

# Plot
width = 0.2
plt.figure(figsize=(10, 6))

# Hatched background bars
for i, color in enumerate(colors):
    offset = (i - 1.5) * width
    plt.bar(x + offset, [adjusted_simple[i], adjusted_weighted[i]],
            width, facecolor='white', edgecolor=color, hatch='///', zorder=0)

# Main bars
bars = []
for i, color in enumerate(colors):
    offset = (i - 1.5) * width
    bar = plt.bar(x + offset, [success_simple[i], success_weighted[i]],
                  width, color=color, label=scenarios[i], zorder=1)
    bars.append(bar)

# Annotate inside top
for bar_group in bars:
    for bar in bar_group:
        h = bar.get_height()
        plt.text(bar.get_x()+bar.get_width()/2, h*0.98,
                 f"{h:.1f}", ha='center', va='top',
                 fontsize=9, color='white', weight='bold', zorder=2)

plt.xticks(x, methods, fontsize=10)
plt.ylabel("The number of service provision", fontsize=12)

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.grid(True, axis='x', linestyle='--', alpha=0.3)

plt.legend(loc='upper center', bbox_to_anchor=(0.5,1.12),
           ncol=2, frameon=False, fontsize=9)
plt.tight_layout()
plt.show()