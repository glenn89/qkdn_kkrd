import matplotlib.pyplot as plt
import numpy as np

# Data for thresholds 0 and 10
labels = ['shortest path key relay', 'weighted shortest key relay']
success_0 = [1306.8, 1318.8]
success_10 = [997.0, 1002.8]

# Plot with updated spacing between groups (0.3)
x = np.arange(len(labels)) * 0.3  # reduced spacing between groups
width = 0.1  # thinner bar width

fig, ax = plt.subplots(figsize=(7, 5))
bars_non = ax.bar(x - width/2, success_0, width, label='Non-proactive key relay', color='teal')
bars_pro = ax.bar(x + width/2, success_10, width, label='Proactive key relay', color='tomato')

# Annotate bars with values
for bar in bars_non + bars_pro:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

# Labels and axes
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel('The number of service provision')

# Move legend above plot
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2)

plt.tight_layout()
plt.show()
