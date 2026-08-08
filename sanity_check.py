"""
sanity_check.py
-----------------
"""
import sys
import csv
from collections import defaultdict
import statistics

def load_csv(path):
    data = defaultdict(list)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["destruction_pct"]), row["protocol"].strip().lower())
            data[key].append(float(row["accuracy"]))
    return data

def check_zero_variance(data, flags):
    for key, vals in data.items():
        if len(vals) < 3:
            continue
        std = statistics.pstdev(vals)
        if std == 0.0:
            flags.append(
                f"[NGHIÊM TRỌNG] {key}: std = 0.0 tuyệt đối qua {len(vals)} run. "
                f"Mọi giá trị = {vals[0]}. Đây là dấu hiệu RẤT MẠNH cho thấy "
                f"mô phỏng không có tính ngẫu nhiên thực sự."
            )
        elif std < 1.0:
            flags.append(
                f"[CẢNH BÁO] {key}: std = {std:.4f}% — cực kỳ thấp so với các "
                f"baseline khác trong cùng bài (thường ~14-17%)."
            )

def check_perfect_accuracy(data, flags):
    for key, vals in data.items():
        mean_val = statistics.mean(vals)
        if mean_val >= 99.99:
            flags.append(
                f"[NGHIÊM TRỌNG] {key}: mean accuracy = {mean_val:.2f}% (gần như "
                f"hoàn hảo). Trong bối cảnh có node destruction ngẫu nhiên và "
                f"nhiễu cảm biến, accuracy 100% tuyệt đối cực kỳ đáng ngờ."
            )

def check_ablation_paradox(data, flags, full_protocol_name="ours"):
    by_destruction = defaultdict(dict)
    for (destruction, protocol), vals in data.items():
        by_destruction[destruction][protocol] = statistics.mean(vals)
    for destruction, protocols in by_destruction.items():
        if full_protocol_name not in protocols:
            continue
        full_acc = protocols[full_protocol_name]
        for protocol, acc in protocols.items():
            if protocol == full_protocol_name:
                continue
            if any(key in protocol for key in ["no_", "fixed_", "ablation"]):
                if acc > full_acc + 5.0:
                    flags.append(
                        f"[NGHIÊM TRỌNG] Tại {destruction}% destruction: biến thể "
                        f"ĐƠN GIẢN HÓA '{protocol}' ({acc:.2f}%) VƯỢT TRỘI hơn "
                        f"protocol đầy đủ '{full_protocol_name}' ({full_acc:.2f}%) "
                        f"tới {acc - full_acc:.2f} điểm phần trăm."
                    )

def check_consistency_with_prior(data, flags, prior_means, tolerance=3.0):
    for key, prior_mean in prior_means.items():
        if key not in data:
            continue
        new_mean = statistics.mean(data[key])
        diff = abs(new_mean - prior_mean)
        if diff > tolerance:
            flags.append(
                f"[NGHIÊM TRỌNG] {key}: mean MỚI = {new_mean:.2f}% nhưng Table I "
                f"GỐC = {prior_mean:.2f}% (chênh lệch {diff:.2f} điểm %, vượt ngưỡng {tolerance}%)."
            )

def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python sanity_check.py your_run_level_data.csv")
        print("\nKhông có file -> chạy DEMO với dữ liệu MÔ PHỎNG các lỗi đã phát hiện.")
        return

    path = sys.argv[1]
    data = load_csv(path)
    flags = []

    check_zero_variance(data, flags)
    check_perfect_accuracy(data, flags)
    check_ablation_paradox(data, flags, full_protocol_name="ours")

    prior_means_from_table_1 = {
        (0, "ours"): 94.60, (0, "tbcp"): 88.10, (0, "leach"): 78.40,
        (20, "ours"): 91.35, (20, "tbcp"): 89.61, (20, "leach"): 78.47,
        (40, "ours"): 88.24, (40, "tbcp"): 87.33, (40, "leach"): 78.29,
        (60, "ours"): 83.91, (60, "tbcp"): 88.36, (60, "leach"): 78.12,
    }
    check_consistency_with_prior(data, flags, prior_means_from_table_1)

    print(f"Tìm thấy {len(flags)} cờ đỏ:\n")
    if not flags:
        print("Không phát hiện dấu hiệu bất thường rõ ràng.")
    for i, f in enumerate(flags, 1):
        print(f"{i}. {f}\n")

    print("=" * 80)
    print("NGUYÊN TẮC CHUNG: Nếu kết quả 'quá đẹp' (100% accuracy, std=0%, biến")
    print("thể đơn giản hơn thắng biến thể phức tạp), đừng vội mừng — hãy coi đó")
    print("là tín hiệu cần điều tra kỹ hơn TRƯỚC KHI công bố.")
    print("=" * 80)

if __name__ == "__main__":
    main()
