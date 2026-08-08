import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import re

# "viridis", "plasma", "Set2", "Dark2", "tab10"

def extract_accuracy_from_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    runs = []
    current_run = []
    for line in lines:
        if line.startswith("NodeID"):
            if current_run:
                event_lines = [l for l in current_run if 25 <= int(l.split(',')[1]) <= 45]
                if event_lines:
                    true_in_event = sum(1 for l in event_lines if l.strip().split(',')[-1] == 'True')
                    total_in_event = len(event_lines)
                    accuracy = true_in_event / total_in_event if total_in_event > 0 else 0
                    runs.append(accuracy * 100)
            current_run = []
        else:
            current_run.append(line)
    if current_run:
        event_lines = [l for l in current_run if 25 <= int(l.split(',')[1]) <= 45]
        if event_lines:
            true_in_event = sum(1 for l in event_lines if l.strip().split(',')[-1] == 'True')
            total_in_event = len(event_lines)
            accuracy = true_in_event / total_in_event if total_in_event > 0 else 0
            runs.append(accuracy * 100)
    return runs

fr_values = [0.0, 0.2, 0.4, 0.6]
data_dict = {}
for fr in fr_values:
    filename = f"all_runs_v3_fr{fr}.log"
    try:
        accuracies = extract_accuracy_from_log(filename)
        data_dict[f"{int(fr*100)}%"] = accuracies
    except FileNotFoundError:
        print(f"File {filename} not found!")
        data_dict[f"{int(fr*100)}%"] = []

plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

palette = sns.color_palette(COLOR_PALETTE, len(data_dict))

box = sns.boxplot(data=list(data_dict.values()), palette=palette, width=0.6)

for patch in box.artists:
    patch.set_edgecolor('black')
    patch.set_linewidth(1.5)

for line in box.lines:
    line.set_color('black')
    line.set_linewidth(1.5)

plt.xticks(range(len(data_dict)), list(data_dict.keys()), fontsize=12)
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Detection Accuracy Distribution Across 30 Independent Runs", fontsize=16)
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("accuracy_boxplot.png", dpi=300, bbox_inches='tight')
plt.show()
print("Box plot saved as accuracy_boxplot.png")

plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

palette = sns.color_palette(COLOR_PALETTE, len(data_dict))

sns.stripplot(data=list(data_dict.values()), palette=palette, 
              jitter=0.2, size=8, alpha=0.7, edgecolor='black', linewidth=0.5)

plt.xticks(range(len(data_dict)), list(data_dict.keys()), fontsize=12)
plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Accuracy Distribution (Each Point = One Run)", fontsize=16)
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("accuracy_stripplot.png", dpi=300, bbox_inches='tight')
plt.show()
print("Strip plot saved as accuracy_stripplot.png")

means = [np.mean(v) for v in data_dict.values()]
stds = [np.std(v) for v in data_dict.values()]
x_ticks = list(data_dict.keys())

plt.figure(figsize=(8, 5))

plt.errorbar(x_ticks, means, yerr=stds, fmt='o-', 
             capsize=6, color='#D62728', ecolor='#2C3E50', 
             markersize=10, linewidth=2.5, capthick=2)

plt.fill_between(range(len(x_ticks)), 
                 [m - s for m, s in zip(means, stds)],
                 [m + s for m, s in zip(means, stds)],
                 alpha=0.2, color='#D62728')

plt.xlabel("Node Destruction (%)", fontsize=14)
plt.ylabel("Accuracy (%)", fontsize=14)
plt.title("Mean Accuracy vs. Node Destruction", fontsize=16)
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("accuracy_lineplot.png", dpi=300, bbox_inches='tight')
plt.show()
print("Line plot saved as accuracy_lineplot.png")

print("\n✅ Tất cả biểu đồ đã được tạo lại với bảng màu mới!")
