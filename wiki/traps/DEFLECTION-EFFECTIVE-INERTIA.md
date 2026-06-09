# 有效慣性矩 Ie 計算陷阱

**陷阱 ID：** DEFLECTION-EFFECTIVE-INERTIA
**知識分類：** RC-U3-1
**危險係數：** ★★☆（中頻、高誤率）

---

## 陷阱描述

ACI 有效慣性矩法（Branson公式）計算撓度時，$M_a$（計算彎矩）的選取、
$I_{cr}$ 的計算，以及長期撓度修正係數 $\lambda$ 的應用，是高頻出錯點。

---

## Branson 公式

$$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \leq I_g$$

$$M_{cr} = \frac{f_r \cdot I_g}{y_t}, \quad f_r = 2\sqrt{f'_c} \text{ (kgf/cm²)} = 0.7\sqrt{f'_c} \text{ (MPa)}$$

---

## 開裂斷面慣性矩 $I_{cr}$

用**轉換斷面法**計算 $I_{cr}$（$n = E_s/E_c$）：

$$\text{中性軸位置：} \frac{b(kd)^2}{2} = n A_s (d - kd)$$

$$I_{cr} = \frac{b(kd)^3}{3} + n A_s (d - kd)^2$$

雙筋梁（考慮壓力鋼筋）：

$$\frac{b(kd)^2}{2} + (n-1)A'_s(kd - d') = n A_s(d - kd)$$

$$I_{cr} = \frac{b(kd)^3}{3} + (n-1)A'_s(kd-d')^2 + n A_s(d-kd)^2$$

---

## 長期撓度修正

$$\Delta_{long} = \lambda \cdot \Delta_i(DL)$$

$$\lambda = \frac{\xi}{1 + 50\rho'}, \quad \rho' = \frac{A'_s}{b \cdot d}$$

| 時間 | $\xi$ 值 |
|------|:--------:|
| 5年以上 | 2.0 |
| 1年 | 1.4 |
| 6個月 | 1.2 |
| 3個月 | 1.0 |

**總撓度：**
$$\Delta_{total} = \Delta_i(DL) \cdot (1 + \lambda) + \Delta_i(LL_\text{持續}) \cdot \lambda + \Delta_i(LL_\text{活動})$$

---

## 常見陷阱場景

| 陷阱 | 說明 |
|------|------|
| $M_a$ 的取法（懸臂梁 vs. 簡支梁） | 懸臂梁 $M_a$ 取固定端彎矩；連續梁取最大正/負彎矩分別計算 |
| 忽略雙筋梁壓力筋對 $I_{cr}$ 的貢獻 | $(n-1)A'_s$ 項常被遺漏 |
| $\lambda$ 中 $\rho'$ 的計算基準 | $\rho' = A'_s/(b \cdot d)$，用腹板寬 $b$ |
| T形梁的 $y_t$ 與 $I_g$ | $y_t$ 是中性軸到拉力最外側纖維距離，T形梁需計算形心位置 |
| 持續活載重比例 | 若活載重有部分是持續的（如書架），需分開計算長期和短期 |

---

## 出現題目

| 題號 | 說明 |
|------|------|
| [RC-2006-3](../problems/RC-2006-3.md) | 簡支梁即時撓度增量，有效慣性矩 Ie |
| [RC-2007-2](../problems/RC-2007-2.md) | 雙筋梁，即時撓度，長期撓度，λ修正 |
| [RC-2008-1](../problems/RC-2008-1.md) | 懸臂梁雙筋梁，長期撓度，有效慣性矩 Ie |
| [RC-2009-2](../problems/RC-2009-2.md) | 懸臂梁，即時撓度，裂縫斷面慣性矩 Icr |
| [RC-2018-3](../problems/RC-2018-3.md) | T形梁，負彎矩，裂縫控制 |
