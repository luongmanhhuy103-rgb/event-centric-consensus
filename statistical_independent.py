import sys
import numpy as np
from scipy import stats

def load_csv(path):
    import csv
    data = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["destruction_pct"]), row["protocol"].strip().lower())
            data.setdefault(key, []).append(float(row["accuracy"]))
    return data

def bootstrap_ci_diff(a, b, n_boot=10000, ci=95):
    diffs = []
    for _ in range(n_boot):
        sample_a = np.random.choice(a, size=len(a), replace=True)
        sample_b = np.random.choice(b, size=len(b), replace=True)
        diffs.append(np.mean(sample_a) - np.mean(sample_b))
    lo = np.percentile(diffs, (100 - ci) / 2)
    hi = np.percentile(diffs, 100 - (100 - ci) / 2)
    return np.mean(diffs), lo, hi

def cohens_d(a, b):
    pooled_std = np.sqrt(((len(a)-1)*np.var(a, ddof=1) + (len(b)-1)*np.var(b, ddof=1)) / (len(a)+len(b)-2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(a) - np.mean(b)) / pooled_std

def analyze(data):
    levels = sorted(set(k[0] for k in data.keys()))
    pairs = [("ours", "tbcp"), ("ours", "leach")]

    print("=" * 90)
    print("BẢNG KIỂM ĐỊNH THỐNG KÊ (INDEPENDENT): Giao thức đề xuất vs Baseline")
    print("=" * 90)

    for lvl in levels:
        print(f"\n--- Mức phá hủy: {lvl}% ---")
        for proto_a, proto_b in pairs:
            key_a = (lvl, proto_a)
            key_b = (lvl, proto_b)
            if key_a not in data or key_b not in data:
                print(f"  [{proto_a} vs {proto_b}] Không đủ dữ liệu")
                continue
            a = np.array(data[key_a])
            b = np.array(data[key_b])
            n_a, n_b = len(a), len(b)
            if n_a < 2 or n_b < 2:
                print(f"  [{proto_a} vs {proto_b}] Không đủ dữ liệu (n_a={n_a}, n_b={n_b})")
                continue

            mean_diff, ci_lo, ci_hi = bootstrap_ci_diff(a, b)
            d = cohens_d(a, b)
            t_stat, p_ttest = stats.ttest_ind(a, b, equal_var=False)
            try:
                u_stat, p_mannwhitney = stats.mannwhitneyu(a, b, alternative='two-sided')
            except:
                p_mannwhitney = float("nan")

            sig_marker = "***" if p_ttest < 0.001 else ("**" if p_ttest < 0.01 else ("*" if p_ttest < 0.05 else "ns"))
            effect_label = "negligible" if abs(d) < 0.2 else ("small" if abs(d) < 0.5 else ("medium" if abs(d) < 0.8 else "large"))

            print(f"  [{proto_a} vs {proto_b}] n_a={n_a}, n_b={n_b}")
            print(f"    Mean diff        : {mean_diff:+.2f}% (95% Bootstrap CI: [{ci_lo:+.2f}, {ci_hi:+.2f}])")
            print(f"    Cohen's d        : {d:+.3f}  ({effect_label} effect)")
            print(f"    Welch's t-test   : t={t_stat:.3f}, p={p_ttest:.4f} {sig_marker}")
            print(f"    Mann-Whitney U   : p={p_mannwhitney:.4f}")

            if ci_lo < 0 < ci_hi:
                print(f"    >> CẢNH BÁO: Khoảng tin cậy chứa 0 → khác biệt KHÔNG có ý nghĩa thống kê")

    print("\n" + "=" * 90)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        print(f"Đang tải dữ liệu từ: {csv_path}")
        data = load_csv(csv_path)
    else:
        print("Vui lòng cung cấp file CSV: python3 statistical_independent.py run_level_data.csv")
        sys.exit(1)
    analyze(data)
