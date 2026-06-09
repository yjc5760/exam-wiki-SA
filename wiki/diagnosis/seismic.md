# 題型診斷：韌性要求與耐震設計（RC-U3-3）

---

## 辨識關鍵字

`耐震` `韌性` `特殊矩形框架` `強柱弱梁` `塑鉸` `密箍區` `圍束箍筋` `接頭剪力` `可能彎矩強度` `Mpr` `Ve設計剪力` `Ash` `容量設計`

---

## 決策樹

```
看到「耐震設計」或「韌性」
    │
    ├─ 有「梁」「特殊矩形框架梁」
    │       → 確認密箍區範圍：lo = max(2h, ln/4, 450mm)（梁端）
    │         密箍間距：s ≤ min(d/4, 8db_min, 24db_tie, 300mm)
    │         設計剪力：Ve = (Mpr,l + Mpr,r)/ln ± wu·ln/2
    │                   Mpr 以 1.25fy 計算，φ=1.0
    │         Vc=0 條件：地震剪力 > 總設計剪力的 50% 且 Pu < 0.05Agf'c
    │         Concept: [[SEISMIC-DESIGN]], [[STRONG-COLUMN-WEAK-BEAM]]
    │
    ├─ 有「柱」「特殊矩形框架柱」「圍束箍筋」
    │       → 密箍區長度 lo = max(柱淨高/6, 最大斷面邊長, 450mm)
    │         Ash ≥ max(
    │           0.3·s·hc·f'c/fyh·(Ag/Ach - 1),
    │           0.09·s·hc·f'c/fyh
    │         )
    │         密箍區間距：s ≤ min(最小邊長/4, 6db_主筋, 14cm)
    │         Concept: [[SEISMIC-DESIGN]]
    │
    ├─ 有「接頭剪力」「梁柱接頭」「Vjh」「Aj」
    │       → 水平接頭剪力：Vjh = T_top + T_bot - Vcol
    │                       T = 1.25fy·As（用 Mpr）
    │         接頭強度：φVjh ≤ φγ√f'c·Aj
    │           γ = 3.2（內接頭，四面有梁圍束）
    │           γ = 2.4（邊接頭，三面圍束）
    │           γ = 1.6（角接頭，兩面圍束）
    │         Aj = 有效接頭面積（柱寬 × 有效深度）
    │         Concept: [[SEISMIC-DESIGN]]
    │
    ├─ 有「強柱弱梁」「ΣMnc」「ΣMnb」
    │       → 驗核：ΣMnc ≥ (6/5)·ΣMnb（節點處）
    │         Mnc 以當前軸力計算，需含軸力效應
    │         Concept: [[STRONG-COLUMN-WEAK-BEAM]]
    │
    └─ 有「曲率韌性」「φu/φy」「塑鉸長度」
            → φy = εy / [d(1-ky)]（轉換斷面法求 ky）
              φu = εcu / (c_u)（Whitney 應力塊求 c_u）
              μφ = φu/φy
              塑鉸長度 Lp ≈ 0.5h 或查規範
```

---

## 耐震設計核心公式速查

### 梁端設計剪力 Ve

$$V_e = \frac{M_{pr,l} + M_{pr,r}}{l_n} \pm \frac{w_u l_n}{2}$$

其中 $M_{pr}$ 以 $1.25 f_y$ 計算（$\phi=1.0$）。

### 柱圍束箍筋 Ash

$$A_{sh} \geq \max\!\left(0.3\, s\, h_c \frac{f'_c}{f_{yh}}\!\left(\frac{A_g}{A_{ch}}-1\right),\; 0.09\, s\, h_c \frac{f'_c}{f_{yh}}\right)$$

### 接頭剪力強度

$$\phi V_{jh} = \phi \gamma \sqrt{f'_c}\, A_j \quad (\phi=0.85)$$

---

## 常見陷阱

- **Mpr 必須以 1.25fy 計算**，φ=1.0（不是設計 Mn）
- **Vc=0 的判斷**：須同時滿足（1）地震剪力≥ Ve 的 50%，（2）Pu < 0.05Agf'c
- **lo 與 s 的公式**：梁和柱的密箍區定義不同，不可混用
- **接頭 γ 係數**：內/邊/角接頭不同，需依圍束梁數判斷
- **強柱弱梁的 6/5 係數**：台灣 ACI-318 規範要求，不是 1.0 也不是 1.2

---

## 相關 Methods / Concepts

- Concept: [[SEISMIC-DESIGN]] [[STRONG-COLUMN-WEAK-BEAM]] [[SHEAR-STRENGTH]]
- 歷屆題目（高頻）: RC-2025-2, RC-2022-4, RC-2019-3, RC-2018-2, RC-2016-2, RC-2013-2, RC-2012-2/3/4, RC-2009-1, RC-2005-3, RC-2004-3, RC-2003-3/4
