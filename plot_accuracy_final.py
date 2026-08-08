import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def extract_accuracy_from_log(filename):
    runs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    current_run = []
    for line in lines:
        line = line.strip()
        if line.startswith("NodeID"):
            if current_run:
                event_lines = []
                for l in current_run:
                    parts = l.split(',')
                    if len(parts) >= 8:
                        try:
                            step = int(parts[1])
                            if 25 <= step <= 45:
                                event_lines.append(l)
                        except:
                            pass
                if event_lines:
                    true_in_event = sum(1 for l in event_lines if l.split(',')[-1].strip() == 'True')
                    total_in_event = len(event_lines)
                    acc = true_in_event / total_in_event if total_in_event > 0 else 0
                    runs.append(acc * 100)
            current_run = []
        else:
            parts = line.split(',')
            if len(parts) >= 8:
                try:
                    current_run.append(line)
                except:
                    pass
    if current_run:
        event_lines = []
        for l in current_run:
            parts = l.split(',')
            if len(parts) >= 8:
                try:
                    step = int(parts[1])
                    if 25 <= step <= 45:
                        event_lines.append(l)
                except:
                    pass
        if event_lines:
            true_in_event = sum(1 for l in event_lines if l.split(',')[-1].strip() == 'True')
            total_in_event = len(event_lines)
            acc = true_in_event / total_in_event if total_in_event > 0 else 0
            runs.append(acc * 100)
    return runs

fr_values = [0.0, 0.2, 0.4, 0.6]
data_dict = {}
for fr in fr_values:
    filename = f"all_runs_v3_fr{fr}.log"
    try:
        accuracies = extract_accuracy_from_log(filename)
        data_dict[f"{int(fr*100)}%"] = accuracies
        print(f"Failure {int(fr*100)}%: {len(accuracies)} runs loaded.")
    except FileNotFoundError:
        print(f"File {filename} not found!")
        data_dict[f"{int(fr*100)}%"] = []

if not any(data_dict.values()):
    print("No data available. Please check the log files.")
else:
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    palette = sns.color_palette(COLOR_PALETTE, len(data_dict))
    ax = sns.boxplot(data=list(data_dict.values()), palette=palette, width=0.6)
    for patch in ax.artists:
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    for line in ax.lines:
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
    plt.close()
    print("Box plot saved as accuracy_boxplot.png")

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    palette = sns.color_palette(COLOR_PALETTE, len(data_dict))
    sns.stripplot(data=list(data_dict.values()), palette=palette,
                  jitter=0.2, size=8, alpha=0.8, edgecolor='black', linewidth=0.5)
    plt.xticks(range(len(data_dict)), list(data_dict.keys()), fontsize=12)
    plt.xlabel("Node Destruction (%)", fontsize=14)
    plt.ylabel("Accuracy (%)", fontsize=14)
    plt.title("Accuracy Distribution (Each Point = One Run)", fontsize=16)
    plt.ylim(0, 105)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig("accuracy_stripplot.png", dpi=300, bbox_inches='tight')
    plt.close()
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
    plt.close()
    print("Line plot saved as accuracy_lineplot.png")

    print("\n✅ Tất cả biểu đồ đã được tạo lại với bảng màu mới!")
