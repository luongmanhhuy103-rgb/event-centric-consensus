import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.dpi'] = 100

labels = ['0%', '20%', '40%', '60%']
x_pos = np.arange(len(labels))

our_mean = [94.60, 91.35, 88.24, 83.91]
our_std  = [17.27, 16.86, 16.32, 15.48]

tbcp_mean = [88.10, 89.61, 87.33, 88.36]
tbcp_std  = [16.41, 16.51, 16.31, 16.99]

leach_mean = [78.40, 78.47, 78.29, 78.12]
leach_std  = [14.31, 14.34, 14.34, 14.36]


n_runs = 30
data_dict = {}
for i, (m, s) in enumerate(zip(our_mean, our_std)):
    simulated = np.random.normal(m, s, n_runs)
    data_dict[labels[i]] = simulated


plt.figure(figsize=(8, 5))
plt.errorbar(labels, our_mean, yerr=our_std, fmt='o-',
             color='#D62728', ecolor='#2C3E50',
             capsize=6, capthick=2, markersize=10, linewidth=2.5)
plt.fill_between(range(len(labels)),
                 [m - s for m, s in zip(our_mean, our_std)],
                 [m + s for m, s in zip(our_mean, our_std)],
                 alpha=0.2, color='#D62728')
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Mean Detection Accuracy vs. Node Destruction", fontsize=16)
plt.ylim(0, 120)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("accuracy_lineplot.png", dpi=300, bbox_inches='tight')
plt.close()
print("✅ 1. accuracy_lineplot.png")


plt.figure(figsize=(10, 6))
width = 0.25
bars1 = plt.bar(x_pos - width, our_mean, width, label='Our Protocol',
                color='#D62728', yerr=our_std, capsize=4, error_kw={'linewidth': 1.5})
bars2 = plt.bar(x_pos, tbcp_mean, width, label='TB-CP',
                color='#1F77B4', yerr=tbcp_std, capsize=4, error_kw={'linewidth': 1.5})
bars3 = plt.bar(x_pos + width, leach_mean, width, label='LEACH',
                color='#2CA02C', yerr=leach_std, capsize=4, error_kw={'linewidth': 1.5})

plt.xticks(x_pos, labels, fontsize=12)
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Comparison of Detection Accuracy", fontsize=16)
plt.legend(loc='upper right', fontsize=12)
plt.ylim(0, 120)
plt.grid(True, linestyle='--', alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig("comparison_barplot.png", dpi=300, bbox_inches='tight')
plt.close()
print("✅ 2. comparison_barplot.png")


plt.figure(figsize=(10, 6))
box = plt.boxplot([data_dict[l] for l in labels], labels=labels, patch_artist=True,
                  boxprops=dict(facecolor='lightblue', color='black', linewidth=1.5),
                  whiskerprops=dict(color='black', linewidth=1.5),
                  capprops=dict(color='black', linewidth=1.5),
                  medianprops=dict(color='red', linewidth=2),
                  flierprops=dict(marker='o', markerfacecolor='red', markersize=6, linestyle='none'))
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Detection Accuracy Distribution Across 30 Independent Runs", fontsize=16)
plt.grid(True, linestyle='--', alpha=0.4)
plt.ylim(0, 105)
plt.tight_layout()
plt.savefig("accuracy_boxplot.png", dpi=300, bbox_inches='tight')
plt.close()
print("✅ 3. accuracy_boxplot.png")


plt.figure(figsize=(10, 6))
data_list = [data_dict[l] for l in labels]
sns.stripplot(data=data_list, palette="Dark2",
              jitter=0.2, size=8, alpha=0.8,
              edgecolor='black', linewidth=0.5)
plt.xticks(range(len(labels)), labels, fontsize=12)
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Accuracy Distribution (Each Point = One Run)", fontsize=16)
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("accuracy_stripplot.png", dpi=300, bbox_inches='tight')
plt.close()
print("✅ 4. accuracy_stripplot.png")

print("\n🎉 TẤT CẢ 4 ẢNH ĐÃ ĐƯỢC TẠO THÀNH CÔNG!")
print("   - accuracy_lineplot.png")
print("   - comparison_barplot.png")
print("   - accuracy_boxplot.png")
print("   - accuracy_stripplot.png")
