# P-M 互制圖計算法

**方法 ID：** pm-interaction-diagram
**知識分類：** 解題工具
**適用題型：** RC-U1-2 柱強度分析與設計、RC-U1-4 柱設計圖之應用

---

## 核心原理

RC 柱在軸力 $P_n$ 與彎矩 $M_n$ 同時作用下的強度，由「假設中性軸深度 $c$，依應變相容性求各鋼筋應力，再合力平衡得 $(P_n, M_n)$」逐點計算而成互制曲線。設計點 $(P_u, M_u)$ 必須落在設計強度曲線 $(\phi P_n, \phi M_n)$ 內側。

---

## 邊界條件／對應關係表

| 控制區 | 條件 | $\phi$（矩形箍） |
|--------|------|:---------------:|
| 壓力控制 | $\varepsilon_t \leq 0.002$ | 0.65 |
| 過渡區 | $0.002 < \varepsilon_t < 0.005$ | $0.65 + (\varepsilon_t - 0.002)\dfrac{0.25}{0.003}$ |
| 拉力控制 | $\varepsilon_t \geq 0.005$ | 0.90 |

純軸壓上限：

$$\phi P_{n,\max} = 0.80\,\phi\left[0.85 f'_c\,(A_g - A_{st}) + f_y A_{st}\right] \quad \text{（矩形箍）}$$

$$\phi P_{n,\max} = 0.85\,\phi\left[0.85 f'_c\,(A_g - A_{st}) + f_y A_{st}\right] \quad \text{（螺旋柱）}$$

---

## 步驟流程

### Point 1：純軸壓點（$e = 0$）

$$P_{n,\max} = 0.85 f'_c\,(A_g - A_{st}) + f_y A_{st}$$

設計值取 $\phi P_{n,\max}$（含 0.80 或 0.85 上限）。

### Point 2：平衡點（$\varepsilon_t = \varepsilon_y$）

$$c_b = \frac{6120}{6120 + f_y}\,d \quad \text{（kgf/cm}^2\text{）}, \quad a_b = \beta_1 c_b$$

$$C_c = 0.85 f'_c\,a_b\,b, \quad \varepsilon_{si} = 0.003\,\frac{c_b - d_i}{c_b}, \quad f_{si} = E_s\,\varepsilon_{si} \in [-f_y,\,f_y]$$

$$P_b = C_c + \sum f_{si} A_{si}, \quad M_b = C_c\!\left(\tfrac{h}{2} - \tfrac{a_b}{2}\right) + \sum f_{si} A_{si}\!\left(\tfrac{h}{2} - d_i\right)$$

### Point 3：純彎點（$P_n = 0$）

以 Whitney 應力塊法求 $M_n$，$\phi = 0.90$（若 $\varepsilon_t \geq 0.005$）。

### 任意中間點

假設 $c$ → 計算 $a$、各鋼筋 $f_{si}$ → 平衡求 $P_n$、$M_n$ → $e = M_n/P_n$。

---

## 常見陷阱

- 壓力筋在應力塊內（$d' < a$）須扣除混凝土面積：$F'_s = A'_s(f'_s - 0.85f'_c)$
- $\phi$ 值在過渡區需線性內插（$\varepsilon_t$ 0.002–0.005），不可直接用 0.65
- 純壓點有 0.80 / 0.85 的上限折減，不可忘記
- 配筋率限制：$0.01 \leq \rho_g \leq 0.08$

---

## 出現題目（使用本方法的考題，依 question_index 標籤核實）

| 題號 | 核心應用 |
|------|---------|
| [RC-2002-2](../problems/RC-2002-2.md) | 偏心受壓 $e=10$ cm，壓力控制 |
| [RC-2004-4](../problems/RC-2004-4.md) | 雙軸彎矩＋細長柱放大後驗算 |
| [RC-2005-1](../problems/RC-2005-1.md) | 矩形柱 P-M＋曲率延展比 |
| [RC-2008-2](../problems/RC-2008-2.md) | 拉力筋應變為零，三排配筋 |
| [RC-2010-1](../problems/RC-2010-1.md) | 圓形螺旋柱，降伏/極限軸力 |
| [RC-2011-1](../problems/RC-2011-1.md) | P-M 互制圖求算步驟（概念題） |
| [RC-2011-3](../problems/RC-2011-3.md) | 三排配筋，過渡區 $\phi$，韌性容量 |
| [RC-2015-1](../problems/RC-2015-1.md) | 方形柱，平衡點最大彎矩 |
| [RC-2017-1](../problems/RC-2017-1.md) | 加大柱，組合截面軸壓強度 |
| [RC-2019-2](../problems/RC-2019-2.md) | 壓力控制斷面，二次方程求中性軸 |
| [RC-2021-2](../problems/RC-2021-2.md) | 偏心距求解，中性軸已知逆推 |
| [RC-2024-3](../problems/RC-2024-3.md) | 拉力筋應變為零邊界 |
