import matplotlib.pyplot as plt
import numpy as np

# Threshold values excluding 11
thresholds = np.arange(10)

# Success data from the experiment excluding index 11
success_simple = np.array([4488.4, 4490.4, 4469.8, 4473.2, 4472.6, 4458.2, 4447.4, 4462.4, 4469.8, 4468.0])
success_weighted = np.array([4584.8, 4594.4, 4588.4, 4577.6, 4582.2, 4575.2, 4584.8, 4575.4, 4581.0, 4581.0])

# Plot configuration
x = thresholds
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, success_simple, width, label='Shortest path key relay', color='#FBBC05')
plt.bar(x + width/2, success_weighted, width, label='Weighted shortest path key relay', color='#EA7600')

plt.xlabel("Threshold ($th_{4}$)", fontsize=12)
plt.ylabel("The number of service provision", fontsize=12)
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
