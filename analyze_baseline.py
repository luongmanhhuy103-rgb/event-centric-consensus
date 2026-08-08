import sys
import numpy as np

def parse_log_baseline(filename):
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

def compute_metrics_for_run(data, event_start=25, event_end=45):
    tp = fp = tn = fn = 0
    for line in data:
        parts = line.strip().split(',')
        if len(parts) == 6:
            try:
                step = int(parts[1])
                broadcast = parts[5] == 'True'
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
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    return accuracy

for baseline in ['tbcp', 'leach']:
    print(f"\n=== Baseline: {baseline.upper()} ===")
    for fr in [0.0, 0.2, 0.4, 0.6]:
        filename = f"all_runs_{baseline}_fr{fr}.log"
        try:
            runs = parse_log_baseline(filename)
            accuracies = []
            for run in runs:
                acc = compute_metrics_for_run(run)
                accuracies.append(acc)
            print(f"Failure {fr*100:.0f}%: mean={np.mean(accuracies)*100:.2f}% ± {np.std(accuracies)*100:.2f}%")
        except FileNotFoundError:
            print(f"{filename}: Not found")
