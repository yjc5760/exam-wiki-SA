# 方法論索引（Layer 3）

> 本目錄收錄結構學靜不定分析的四大解題方法論，對應命題大綱第二單元（SA-U2）。

| 方法 | method_id | 適用單元 | 未知量 | 本知識庫題數 |
|------|-----------|---------|--------|:---:|
| [最小功法／卡氏定理](minimum-work-method.md) | `minimum-work-method` | [[SA-U2-1]] | 多餘力 | 12 |
| [諧合變位法／柔度法](compatibility-method.md) | `compatibility-method` | [[SA-U2-2]] | 多餘力 | 7 |
| [傾角變位法](slope-deflection-method.md) | `slope-deflection-method` | [[SA-U2-3]] | 節點轉角、側移 | 13 |
| [矩陣位移法／直接勁度法](matrix-displacement-method.md) | `matrix-displacement-method` | [[SA-U2-4]] | 節點位移 | 12 |
| [彎矩分配法](moment-distribution-method.md) | `moment-distribution-method` | [[SA-U2-5]] | （迭代收斂，無需聯立） | 2 |

## 方法選擇準則

- **多餘力少（1–2 個）** → 最小功法或諧合變位法最直觀（見 [[force-method-philosophy]]）
- **側移剛架、自由度規則** → 傾角變位法或彎矩分配法（見 [[displacement-method-philosophy]]）
- **自由度多、需系統化/電腦化** → 矩陣位移法（見 [[matrix-method-philosophy]]）

四種方法本質上互為驗算工具：同一題常可用多種方法交叉驗證答案。
