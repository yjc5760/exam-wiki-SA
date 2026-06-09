# 陷阱頁索引（wiki/traps/）

> 本目錄由 compile-all 從題目解析中萃取，記錄最常見的考試陷阱。
> **上次更新：** 2026-06-08

---

## 陷阱清單

| 陷阱 ID | 名稱 | 知識分類 | 危險係數 |
|--------|------|---------|:-------:|
| [T-BEAM-EFFECTIVE-WIDTH](T-BEAM-EFFECTIVE-WIDTH.md) | T形梁有效翼板寬計算陷阱 | RC-U1-1 | ★★★ |
| [BALANCED-RATIO-BOUNDARY](BALANCED-RATIO-BOUNDARY.md) | 平衡鋼筋比邊界與最大配筋率陷阱 | RC-U1-1 | ★★★ |
| [PHI-FACTOR-TRANSITION](PHI-FACTOR-TRANSITION.md) | 過渡區 φ 值計算陷阱 | RC-U1-1, RC-U1-2 | ★★★ |
| [COMPRESSION-STEEL-YIELDING](COMPRESSION-STEEL-YIELDING.md) | 壓力鋼筋未降伏判斷陷阱（雙筋梁） | RC-U1-1 | ★★★ |
| [SHEAR-CRITICAL-SECTION](SHEAR-CRITICAL-SECTION.md) | 剪力臨界斷面位置陷阱 | RC-U2-1 | ★★☆ |
| [TORSION-THRESHOLD](TORSION-THRESHOLD.md) | 扭力忽略門檻陷阱 | RC-U2-2 | ★★☆ |
| [DEFLECTION-EFFECTIVE-INERTIA](DEFLECTION-EFFECTIVE-INERTIA.md) | 有效慣性矩 Ie 計算陷阱 | RC-U3-1 | ★★☆ |
| [PUNCHING-SHEAR-CRITICAL](PUNCHING-SHEAR-CRITICAL.md) | 衝剪臨界斷面與公式陷阱 | RC-U3-2 | ★★☆ |
| [SEISMIC-BEAM-VE](SEISMIC-BEAM-VE.md) | 耐震梁設計剪力 Ve 計算陷阱 | RC-U3-3 | ★★★ |
| [JOINT-SHEAR-EFFECTIVE-AREA](JOINT-SHEAR-EFFECTIVE-AREA.md) | 梁柱接頭剪力有效面積計算陷阱 | RC-U3-3 | ★★★ |
| [LONG-COLUMN-SLENDERNESS](LONG-COLUMN-SLENDERNESS.md) | 細長柱判斷與放大彎矩法陷阱 | RC-U1-3 | ★★☆ |
| [PRESTRESS-LOSS-SEQUENCE](PRESTRESS-LOSS-SEQUENCE.md) | 預力損失順序與分類陷阱 | RC-U4-3 | ★★★ |
| [PRESTRESS-FPS-FORMULA](PRESTRESS-FPS-FORMULA.md) | 預力鋼腱極限應力 fps 公式選擇陷阱 | RC-U4-1 | ★★★ |

---

## 依危險係數

### ★★★ 高危陷阱（最常扣分）

- T形梁有效翼板寬 → 中性軸判斷連動
- φ 值過渡區 → 常被忽略，直接套 0.9
- 壓力鋼筋未降伏 → 直接假設降伏是大忌
- 耐震梁 Ve 用 Mpr → 用 Mn 是系統性錯誤
- 預力損失 → 先/後拉法混用
- fps 公式 → 有/無黏結混用

### ★★☆ 中危陷阱（考場易疏忽）

- 剪力臨界斷面 → 懸臂梁、倒T型梁特殊情況
- 扭力門檻 → Aoh vs. Acp 定義混淆
- 衝剪三公式 → 只用第三個公式
- 有效慣性矩 → 長期修正ξ值記錯、雙筋Icr漏項
- 細長柱判斷 → M1/M2正負號

---

*陷阱頁面由 Cowork 從解析中直接寫入，不走 ingest 流程。*
