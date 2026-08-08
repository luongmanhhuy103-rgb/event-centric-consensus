import sys
import numpy as np

def parse_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    runs = []
    current_run = []
    for line in lines:
        if line.startswith("NodeID"):
            if current_run:
                runs.append(current_run)
            current_run = []
        else:
            current_run.append(line)
    if current_run:
        runs.append(current_run)
    
    return runs

def compute_metrics_for_run(data, event_start=25, event_end=45):
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
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    return precision, recall, f1, accuracy, tp, fp, tn, fn

def get_latency(data, event_start=25):
    broadcast_steps = []
    for line in data:
        parts = line.strip().split(',')
        if len(parts) == 8:
            try:
                step = int(parts[1])
                broadcast = parts[7] == 'True'
                if broadcast and step >= event_start:
                    broadcast_steps.append(step)
            except:
                pass
    if broadcast_steps:
        first_broadcast = min(broadcast_steps)
        return first_broadcast - event_start
    else:
        return None

runs = parse_log('all_runs_v7.log')
if not runs:
    print("No data found.")
    sys.exit()

print(f"Total runs: {len(runs)}")
metrics = []
latencies = []

for i, run in enumerate(runs):
    p, r, f1, acc, tp, fp, tn, fn = compute_metrics_for_run(run)
    metrics.append((p, r, f1, acc))
    lat = get_latency(run)
    if lat is not None:
        latencies.append(lat)
    print(f"Run {i+1}: P={p:.3f}, R={r:.3f}, F1={f1:.3f}, Acc={acc:.3f}, Latency={lat} steps")

p_vals = [m[0] for m in metrics]
r_vals = [m[1] for m in metrics]
f1_vals = [m[2] for m in metrics]
acc_vals = [m[3] for m in metrics]

print("\n=== Summary Statistics ===")
print(f"Precision: mean={np.mean(p_vals):.4f} ± {np.std(p_vals):.4f}")
print(f"Recall:    mean={np.mean(r_vals):.4f} ± {np.std(r_vals):.4f}")
print(f"F1:        mean={np.mean(f1_vals):.4f} ± {np.std(f1_vals):.4f}")
print(f"Accuracy:  mean={np.mean(acc_vals):.4f} ± {np.std(acc_vals):.4f}")
if latencies:
    print(f"Latency:   mean={np.mean(latencies):.2f} ± {np.std(latencies):.2f} steps")
else:
    print("Latency: N/A")
