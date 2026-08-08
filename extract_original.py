import os
import numpy as np

def extract_accuracy_from_log(filename):
    with open(filename, 'r') as f:
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
    
    return accuracies

fr_values = [0.0, 0.2, 0.4, 0.6]
table_i = {0: 94.60, 20: 91.35, 40: 88.24, 60: 83.91}

print("=== DỮ LIỆU TỪ LOG GỐC (Cooja thật) ===\n")

for fr in fr_values:
    filename = f"all_runs_fr{int(fr*100)}.log"
    if not os.path.exists(filename):
        print(f"File {filename} không tồn tại!")
        continue
    
    accuracies = extract_accuracy_from_log(filename)
    if accuracies:
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies)
        n = len(accuracies)
        key = int(fr*100)
        diff = abs(mean_acc - table_i[key])
        print(f"{key}%: mean={mean_acc:.2f}%, std={std_acc:.2f}%, n={n} runs")
        print(f"   Table I={table_i[key]:.2f}%, diff={diff:.2f}%")
        print(f"   {'✅ KHỚP' if diff < 1.0 else '⚠️ KHÔNG KHỚP'}")
        print()
    else:
        print(f"{int(fr*100)}%: Không có dữ liệu")
