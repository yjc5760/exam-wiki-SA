# 有效慣性矩撓度計算法

**方法 ID：** effective-inertia-deflection
**知識分類：** 解題工具
**適用題型：** RC-U3-1 梁工作性要求（撓度）
**適用規範：** ACI 318 §24.2.3–24.2.4（Branson 有效慣性矩法）

---

## 核心原理

RC 梁受力後部分開裂，有效慣性矩 $I_e$ 介於全斷面（未開裂）$I_g$ 與全開裂斷面 $I_{cr}$ 之間，依荷載彎矩 $M_a$ 與開裂彎矩 $M_{cr}$ 的比值插值（Branson 公式），反映梁實際的撓曲剛度。

---

## 邊界條件

- $I_e \leq I_g$（不可超過全斷面慣性矩）
- 若 $M_a \leq M_{cr}$：取 $I_e = I_g$（未開裂）
- 長期撓度：須乘以長期修正係數

---

## 步驟流程

**Step 1：開裂彎矩**

$$M_{cr} = \frac{f_r I_g}{y_t}, \quad f_r = 2\sqrt{f'_c} \text{ (kgf/cm}^2\text{)} \quad \text{或} \quad 0.7\sqrt{f'_c} \text{ (MPa)}$$

**Step 2：開裂斷面慣性矩 $I_{cr}$**

設中性軸深度 $kd$（單筋梁，忽略受拉混凝土）：

$$\frac{b(kd)^2}{2} = n A_s(d - kd), \quad n = \frac{E_s}{E_c}$$

$$I_{cr} = \frac{b(kd)^3}{3} + n A_s(d - kd)^2$$

（雙筋梁另加壓力筋慣性矩項：$(2n-1)A'_s(kd-d')^2$）

**Step 3：有效慣性矩（Branson 公式）**

$$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \leq I_g$$

**Step 4：即時撓度**

$$\Delta_i = \frac{K M_a L^2}{E_c I_e}$$

其中係數 $K$：均佈載重簡支梁 $K = 5/48$；均佈載重懸臂梁 $K = 1/8$；集中載重中點 $K = 1/12$。

**Step 5：長期（附加）撓度**

$$\Delta_{add} = \lambda \cdot \Delta_i(DL), \quad \lambda = \frac{\xi}{1 + 50\rho'}$$

| 時間 | $\xi$ |
|------|:-----:|
| ≥ 5 年 | 2.0 |
| 1 年 | 1.4 |
| 6 個月 | 1.2 |
| 3 個月 | 1.0 |

**Step 6：總撓度**

$$\Delta_{total} = \Delta_i(DL) \cdot (1 + \lambda) + \Delta_i(LL)$$

---

## 常見陷阱

- $I_{cr}$ 計算時雙筋梁需加壓力筋項（係數 $(2n-1)$ 而非 $n$，因混凝土已計算過）
- 長期修正 $\lambda$ 僅適用於靜載重（持續載重）部分，活載重取即時撓度
- $\rho'$ 取壓力筋比；無壓力筋時 $\rho' = 0 \Rightarrow \lambda = \xi$
- $I_e \leq I_g$；若 $M_a < M_{cr}$ 直接用 $I_g$

---

## 出現題目（使用本方法的考題，依 question_index 標籤核實）

| 題號 | 核心應用 |
|------|---------|
| [RC-2006-3](../problems/RC-2006-3.md) | 簡支梁集中活載重，即時撓度增量 |
| [RC-2007-2](../problems/RC-2007-2.md) | 雙筋梁即時＋長期撓度，λ 修正 |
| [RC-2008-1](../problems/RC-2008-1.md) | 懸臂雙筋梁長期撓度，轉換斷面法 |
| [RC-2009-2](../problems/RC-2009-2.md) | 懸臂梁 $I_{cr}$、曲率積分、雙段 EI 法 |
| [RC-2014-2](../problems/RC-2014-2.md) | 彎矩曲率三階段分析，開裂彎矩 |
