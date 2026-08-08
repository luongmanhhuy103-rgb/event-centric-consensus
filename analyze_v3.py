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
        return min(broadcast_steps) - event_start
    else:
        return None

for fr in [0.0, 0.2, 0.4, 0.6]:
    filename = f"all_runs_v3_fr{fr}.log"
    try:
        runs = parse_log(filename)
        if not runs:
            print(f"{filename}: No data found")
            continue
        
        metrics = []
        latencies = []
        for run in runs:
            p, r, f1, acc, tp, fp, tn, fn = compute_metrics_for_run(run)
            metrics.append((p, r, f1, acc))
            lat = get_latency(run)
            if lat is not None:
                latencies.append(lat)
        
        p_vals = [m[0] for m in metrics]
        r_vals = [m[1] for m in metrics]
        f1_vals = [m[2] for m in metrics]
        acc_vals = [m[3] for m in metrics]
        
        print(f"\n=== Failure Rate {fr*100:.0f}% ===")
        print(f"Number of runs: {len(runs)}")
        print(f"Precision: mean={np.mean(p_vals):.4f} ± {np.std(p_vals):.4f}")
        print(f"Recall:    mean={np.mean(r_vals):.4f} ± {np.std(r_vals):.4f}")
        print(f"F1:        mean={np.mean(f1_vals):.4f} ± {np.std(f1_vals):.4f}")
        print(f"Accuracy:  mean={np.mean(acc_vals):.4f} ± {np.std(acc_vals):.4f}")
        if latencies:
            print(f"Latency:   mean={np.mean(latencies):.2f} ± {np.std(latencies):.2f} steps")
        else:
            print("Latency: N/A")
    except FileNotFoundError:
        print(f"{filename}: File not found")
