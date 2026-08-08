import os
import glob
import numpy as np

def extract_accuracy_from_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    event_lines = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 8:
            try:
                step = int(parts[1].strip())
                if 25 <= step <= 45:
                    event_lines.append(line)
            except:
                pass
    
    if not event_lines:
        return 0.0
    
    true_count = sum(1 for l in event_lines if l.split(',')[-1].strip() == 'True')
    total = len(event_lines)
    return (true_count / total) * 100 if total > 0 else 0.0

fr_values = [0.0, 0.2, 0.4, 0.6]
results = {}

for fr in fr_values:
    pattern = f"all_runs_v3_fr{fr:.1f}.log"
    if not os.path.exists(pattern):
        print(f"File {pattern} not found!")
        continue
    
    with open(pattern, 'r') as f:
        content = f.read()
    
    runs = content.split("NodeID")
    accuracies = []
        lines = run.strip().split('\n')
        event_lines = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 8:
                try:
                    step = int(parts[1].strip())
                    if 25 <= step <= 45:
                        event_lines.append(line)
                except:
                    pass
        if event_lines:
            true_count = sum(1 for l in event_lines if l.split(',')[-1].strip() == 'True')
            total = len(event_lines)
            acc = (true_count / total) * 100 if total > 0 else 0
            accuracies.append(acc)
    
    if accuracies:
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies)
        results[f"{int(fr*100)}%"] = (mean_acc, std_acc, len(accuracies))
        print(f"{int(fr*100)}%: mean={mean_acc:.2f}%, std={std_acc:.2f}%, n={len(accuracies)} runs")
    else:
        print(f"{int(fr*100)}%: No data")

print("\n=== So sánh với Table I (gốc) ===")
table_i = {0: 94.60, 20: 91.35, 40: 88.24, 60: 83.91}
for fr, (mean, std, n) in results.items():
    key = int(fr[:-1])
    diff = abs(mean - table_i[key])
    print(f"{fr}: mean={mean:.2f}%, Table I={table_i[key]:.2f}%, diff={diff:.2f}%")
