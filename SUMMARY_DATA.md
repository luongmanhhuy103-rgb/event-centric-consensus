
| Destruction | Our Protocol | TB-CP | LEACH |
|---|---|---|---|
| 0% | 94.60 ± 17.27% | 88.10 ± 16.41% | 78.40 ± 14.31% |
| 20% | 91.35 ± 16.86% | 89.61 ± 16.51% | 78.47 ± 14.34% |
| 40% | 88.24 ± 16.32% | 87.33 ± 16.31% | 78.29 ± 14.34% |
| 60% | 83.91 ± 15.48% | 88.36 ± 16.99% | 78.12 ± 14.36% |

## 2. Statistical Significance (Ours vs TB-CP)
| Destruction | Mean diff | 95% CI | p-value | Cohen's d |
|---|---|---|---|---|
| 0% | +32.91% | [+28.37, +37.40] | 0.0000 | 2.552 |
| 20% | +9.14% | [+2.96, +15.21] | 0.0057 | 0.742 |
| 40% | +4.70% | [-3.47, +12.44] | 0.2537 | 0.298 |
| 60% | -23.10% | [-33.62, -12.43] | 0.0001 | -1.089 |

## 3. Fallback Mode (60% destruction)
- Accuracy: 100.0% (30/30 runs)

| Variant | 40% | 60% |
|---|---|---|
| Full Protocol | 88.24% | 83.91% |
| No Noise Score | 100.0% | 99.84% |
| Fixed Threshold | 100.0% | 93.33% |
| No HS-Trees | 100.0% | 93.33% |

## 5. θ_Adaptive Bound
- K_nominal = 10.0
- F_net ≤ 0.26 (lý thuyết an toàn)
- F_net = 0.6 (thực nghiệm) → vượt ngưỡng an toàn

| Nodes | Accuracy |
|---|---|
| 20 | 100.0% |
| 40 | 88.24% |
| 80 | 100.0% |
