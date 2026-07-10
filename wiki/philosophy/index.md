# 分析哲學索引（Layer 2）

> 本目錄收錄結構學靜不定分析的三大思維方式，說明「為何選這個方法」而非「如何算」（方法論細節見 `wiki/methods/`）。

| 思維 | 未知量 | 對應方法論 | 適合場景 |
|------|--------|-----------|---------|
| [力法思維](force-method-philosophy.md) | 多餘力 | [[minimum-work-method]]、[[compatibility-method]] | 靜不定度低（1–3個多餘力） |
| [位移法思維](displacement-method-philosophy.md) | 節點位移 | [[slope-deflection-method]]、[[moment-distribution-method]] | 自由度少，側移剛架 |
| [矩陣法思維](matrix-method-philosophy.md) | 節點位移（系統化） | [[matrix-displacement-method]] | 自由度多、不規則、需電腦化 |

## 選擇思維的第一個問題

拿到一道靜不定結構題，第一步不是選公式，而是問：**未知量該用「力」還是「位移」來描述比較少？**

- 多餘力少 → 力法思維（[[force-method-philosophy]]）
- 自由度少 → 位移法思維（[[displacement-method-philosophy]]）
- 自由度多且不規則 → 矩陣法思維（[[matrix-method-philosophy]]）

三種思維求出的答案必然一致，差別只在計算量與是否好手算，因此也常被用來互相驗算。
