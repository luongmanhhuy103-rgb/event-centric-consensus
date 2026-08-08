import sys
import numpy as np

def parse_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    runs = []
    current = []
    for line in lines:
        if line.startswith("NodeID"):
            if current:
                runs.append(current)
            current = []
        else:
            current.append(line)
    if current:
        runs.append(current)
    return runs

def compute_accuracy(data, event_start=25, event_end=45):
    tp = fp = tn = fn = 0
    for line in data:
        parts = line.strip().split(',')
        if len(parts) == 8:
            try:
                step = int(parts[1])
                broadcast = parts[7] == 'True'
                in_event = event_start <= step <= event_end
                if in_event and broadcast:
                    tp += 1
                elif in_event and not broadcast:
                    fn += 1
                elif not in_event and broadcast:
                    fp += 1
                else:
                    tn += 1
            except:
                pass
    return (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0

print("=== Spoofing Attack Simulation ===")
print("Spoofing Rate | No Auth (mean±std) | With Auth (mean±std)")
print("------------- | ----------------- | -----------------")
for spoof in [0.0, 0.1, 0.2, 0.3]:
    # No auth
    filename_no = f"spoof_no_auth_{spoof}.log"
    try:
        runs_no = parse_log(filename_no)
        acc_no = [compute_accuracy(run) for run in runs_no]
        mean_no = np.mean(acc_no)*100
        std_no = np.std(acc_no)*100
    except:
        mean_no = 0
        std_no = 0
    
    # With auth
    filename_with = f"spoof_with_auth_{spoof}.log"
    try:
        runs_with = parse_log(filename_with)
        acc_with = [compute_accuracy(run) for run in runs_with]
        mean_with = np.mean(acc_with)*100
        std_with = np.std(acc_with)*100
    except:
        mean_with = 0
        std_with = 0
    
    print(f"{spoof*100:>11.0f}% | {mean_no:>6.2f} ± {std_no:>5.2f}% | {mean_with:>6.2f} ± {std_with:>5.2f}%")
