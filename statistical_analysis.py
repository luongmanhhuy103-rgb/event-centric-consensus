import sys
import numpy as np
from scipy import stats

RNG = np.random.default_rng(42)

def load_csv(path):
    import csv
    data = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["destruction_pct"]), row["protocol"].strip().lower())
            data.setdefault(key, []).append(
                (int(row["run_id"]), float(row["accuracy"]))
            )
    return data

def align_by_run_id(records_a, records_b):
    dict_a = dict(records_a)
    dict_b = dict(records_b)
    common_ids = sorted(set(dict_a) & set(dict_b))
    if len(common_ids) == 0:
        return None, None, 0
    x = np.array([dict_a[i] for i in common_ids])
    y = np.array([dict_b[i] for i in common_ids])
    return x, y, len(common_ids)

def cohens_d_paired(x, y):
    diff = x - y
    if diff.std(ddof=1) == 0:
        return 0.0
    return diff.mean() / diff.std(ddof=1)

def bootstrap_ci_mean_diff(x, y, n_boot=10000, ci=95):
    diffs = x - y
    n = len(diffs)
    boot_means = np.empty(n_boot)
    for b in range(n_boot):
        sample = RNG.choice(diffs, size=n, replace=True)
        boot_means[b] = sample.mean()
    lo = np.percentile(boot_means, (100 - ci) / 2)
    hi = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return diffs.mean(), lo, hi

def analyze(data):
    levels = sorted(set(k[0] for k in data.keys()))
    pairs = [("ours", "tbcp"), ("ours", "leach")]

    print("=" * 90)
    print("BẢNG KIỂM ĐỊNH THỐNG KÊ: Giao thức đề xuất vs Baseline")
    print("=" * 90)

    for lvl in levels:
        print(f"\n--- Mức phá hủy: {lvl}% ---")
        for proto_a, proto_b in pairs:
            key_a = (lvl, proto_a)
            key_b = (lvl, proto_b)
            if key_a not in data or key_b not in data:
                print(f"  [{proto_a} vs {proto_b}] Không đủ dữ liệu")
                continue
            x, y, n = align_by_run_id(data[key_a], data[key_b])
            if n < 2:
                print(f"  [{proto_a} vs {proto_b}] Không đủ dữ liệu ghép cặp (n={n})")
                continue

            mean_diff, ci_lo, ci_hi = bootstrap_ci_mean_diff(x, y)
            d = cohens_d_paired(x, y)
            t_stat, p_ttest = stats.ttest_rel(x, y)
            try:
                w_stat, p_wilcoxon = stats.wilcoxon(x, y)
            except ValueError:
                p_wilcoxon = float("nan")

            sig_marker = "***" if p_ttest < 0.001 else ("**" if p_ttest < 0.01 else ("*" if p_ttest < 0.05 else "ns"))
            effect_label = "negligible" if abs(d) < 0.2 else ("small" if abs(d) < 0.5 else ("medium" if abs(d) < 0.8 else "large"))

            print(f"  [{proto_a} vs {proto_b}] n={n}")
            print(f"    Mean diff        : {mean_diff:+.2f}% (95% Bootstrap CI: [{ci_lo:+.2f}, {ci_hi:+.2f}])")
            print(f"    Cohen's d        : {d:+.3f}  ({effect_label} effect)")
            print(f"    Paired t-test    : t={t_stat:.3f}, p={p_ttest:.4f} {sig_marker}")
            print(f"    Wilcoxon signed  : p={p_wilcoxon:.4f}")

            if ci_lo < 0 < ci_hi:
                print(f"    >> CẢNH BÁO: Khoảng tin cậy chứa 0 → khác biệt KHÔNG có ý nghĩa thống kê")

    print("\n" + "=" * 90)
    print("HƯỚNG DẪN TRÍCH DẪN VÀO BÀI BÁO:")
    print("=" * 90)
    print("""
Thay vì viết: "our protocol achieves X% vs Y% for baseline"
Hãy viết dạng:
    "At [level]% destruction, the proposed protocol showed a mean accuracy
    improvement of [diff]% over [baseline] (95% CI: [lo, hi], paired t-test
    p = [p], Cohen's d = [d] [effect])."

Nếu p > 0.05 hoặc CI chứa 0: báo cáo trung thực rằng khác biệt
không có ý nghĩa thống kê.
""")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        print(f"Đang tải dữ liệu từ: {csv_path}")
        data = load_csv(csv_path)
    else:
        print("Vui lòng cung cấp file CSV: python3 statistical_analysis.py run_level_data.csv")
        sys.exit(1)
    analyze(data)
