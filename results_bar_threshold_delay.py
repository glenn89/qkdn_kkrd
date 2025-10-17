import matplotlib.pyplot as plt
import numpy as np

# Threshold values excluding 11
thresholds = np.arange(11)

# Success data from the experiment excluding index 11
success_simple = np.array([132, 126, 119, 108, 97, 87, 80, 77, 76, 76, 76])
success_weighted = np.array([136, 135, 134, 134, 133, 123, 115, 110, 105, 100, 97])

# Plot configuration
x = thresholds
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, success_simple, width, label='Shortest path key relay', color='#FBBC05', zorder=0)
plt.bar(x + width/2, success_weighted, width, label='Weighted shortest path key relay', color='#EA7600', zorder=0)

plt.xlabel("Threshold ($th_{4}$)", fontsize=12)
plt.ylabel("Average delay (ms)", fontsize=12)
plt.xticks(thresholds, fontsize=12)
plt.yticks(fontsize=12)

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.grid(True, axis='x', linestyle='--', alpha=0.3)

# Place legend at the top center
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, frameon=False, fontsize=11)

plt.tight_layout()
plt.show()
