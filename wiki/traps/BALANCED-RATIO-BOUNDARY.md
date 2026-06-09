# 平衡鋼筋比邊界與最大配筋率陷阱

**陷阱 ID：** BALANCED-RATIO-BOUNDARY
**知識分類：** RC-U1-1
**危險係數：** ★★★（高頻、高誤率）

---

## 陷阱描述

$\rho_b$（平衡鋼筋比）決定了設計的延性邊界。
最大配筋率（$\rho_{max}$）在**舊規範（0.75ρb）**與**新規範（ε_t ≥ 0.004）**之間有差異，
考試中必須確認題目適用哪個版本。

---

## 平衡鋼筋比公式（矩形梁）

$$\rho_b = \frac{0.85 \beta_1 f'_c}{f_y} \cdot \frac{6120}{6120 + f_y} \quad \text{（kgf/cm² 單位）}$$

$$\rho_b = \frac{0.85 \beta_1 f'_c}{f_y} \cdot \frac{600}{600 + f_y} \quad \text{（MPa 單位）}$$

---

## 最大鋼筋比（兩個版本）

| 規範版本 | 最大配筋控制 | 說明 |
|---------|------------|------|
| ACI 318-99 以前（舊） | $\rho_{max} = 0.75\rho_b$ | 直接限制配筋比上限 |
| ACI 318-02 以後（新） | $\varepsilon_t \geq 0.004$（拉力筋應變） | 以應變控制，確保最小延性 |

### 新規範 $\rho_{max}$ 對應值（矩形梁）

$$c_{max} = \frac{0.003}{0.003 + 0.004} \cdot d = \frac{3}{7} d$$

$$a_{max} = \beta_1 \cdot c_{max} = \frac{3\beta_1}{7} d$$

$$\rho_{max} = \frac{0.85 f'_c \cdot a_{max}}{f_y \cdot d} = \frac{0.85 f'_c}{f_y} \cdot \frac{3\beta_1}{7}$$

---

## T形梁的平衡鋼筋比

T形梁需分兩部分計算：翼板部分 + 腹板部分。

$$\rho_b^{(T)} = \frac{A_{sf}}{b_w d} + \rho_{bw} \cdot \frac{b_w}{b_w} $$

實際上：先求翼板所需鋼筋 $A_{sf} = 0.85f'_c(b_e-b_w)h_f/f_y$，再求腹板平衡 $A_{sw,b} = \rho_{bw} b_w d$，合計為 $A_{s,b}$。

---

## 最小鋼筋比

$$\rho_{min} = \max\left(\frac{0.8\sqrt{f'_c}}{f_y},\ \frac{14}{f_y}\right) \quad \text{（kgf/cm² 單位）}$$

$$\rho_{min} = \max\left(\frac{0.25\sqrt{f'_c}}{f_y},\ \frac{1.4}{f_y}\right) \quad \text{（MPa 單位）}$$

---

## 常見陷阱場景

| 陷阱 | 說明 |
|------|------|
| 舊式 0.75ρb 仍出現在某些考題中 | 確認題目附公式表的規範版本 |
| T形梁的 $\rho$ 計算基準 | $\rho = A_s / (b_w \cdot d)$，用腹板寬 $b_w$ 而非有效翼板寬 $b_e$ |
| $\varepsilon_t = 0.004$ 時 $\phi$ 值 | 此時在過渡區，$\phi \neq 0.9$，需插值 |
| 雙筋梁的最大配筋 | 壓力鋼筋存在時，可增加拉力筋量，但仍受 $\varepsilon_t \geq 0.004$ 控制 |

---

## 出現題目

| 題號 | 說明 |
|------|------|
| [RC-2015-2](../problems/RC-2015-2.md) | 雙筋梁，最大設計彎矩，εt=0.004限制 |
| [RC-2005-2](../problems/RC-2005-2.md) | T形梁，最大拉力筋量，0.75ρb |
| [RC-2011-2](../problems/RC-2011-2.md) | T形梁，平衡鋼筋量，NA在腹板 |
| [RC-2024-1](../problems/RC-2024-1.md) | T形梁，最大最小鋼筋量，高強度鋼筋 |
