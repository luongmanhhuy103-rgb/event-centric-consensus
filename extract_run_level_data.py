import csv
import os

def extract_accuracy_from_run(lines):
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

def parse_log_file(filename):
    """Đọc file log và trả về danh sách accuracy của từng run."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    runs = []
    current_run = []
    for line in lines:
        if line.startswith("NodeID"):
            if current_run:
                acc = extract_accuracy_from_run(current_run)
                runs.append(acc)
                current_run = []
        else:
            parts = line.split(',')
            if len(parts) >= 8:
                try:
                    int(parts[1].strip())
                    current_run.append(line)
                except:
                    pass
    if current_run:
        acc = extract_accuracy_from_run(current_run)
        runs.append(acc)
    return runs

def main():
    protocols = {
        'ours': 'all_runs_v3_fr{:.1f}.log',
        'tbcp': 'all_runs_tbcp_fr{:.1f}.log',
        'leach': 'all_runs_leach_fr{:.1f}.log'
    }
    destruction_levels = [0, 20, 40, 60]
    all_data = []
    run_counter = 1

    for proto, pattern in protocols.items():
        for lvl in destruction_levels:
            filename = pattern.format(lvl/100.0)
            if not os.path.exists(filename):
                print(f"File {filename} not found, skipping.")
                continue
            accs = parse_log_file(filename)
            print(f"{proto} at {lvl}%: {len(accs)} runs")
            for acc in accs:
                all_data.append([run_counter, lvl, proto, acc])
                run_counter += 1

    with open('run_level_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['run_id', 'destruction_pct', 'protocol', 'accuracy'])
        writer.writerows(all_data)

    print(f"✅ Đã xuất {len(all_data)} dòng dữ liệu vào run_level_data.csv")

if __name__ == "__main__":
    main()
