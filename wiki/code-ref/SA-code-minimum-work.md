# 最小功法：公式來源與應用

**method_id:** `minimum-work-method`
**涵蓋單元：** [[SA-U2-1]]
**分析哲學：** [[force-method-philosophy]]（力法思維）

## 理論基礎

最小功法基於 **Castigliano 定理**（能量方法）。核心思想：在靜不定結構中，多餘力的真實值應使**應變能最小**。這是力法在能量框架下的表現。

## 核心定理

### Castigliano 定理（位移形）

對於靜不定結構，若 $X_1, X_2, \ldots, X_d$ 為 $d$ 個多餘力，則真實值滿足：

$$\boxed{\frac{\partial U}{\partial X_i} = 0, \quad i = 1, 2, \ldots, d}$$

其中 $U$ 為**總應變能**：

$$U = U_0(P) + \sum_{i=1}^{d} X_i U_i(P) + \frac{1}{2}\sum_{i,j}^{d} X_i X_j U_{ij}$$

| 項 | 意義 |
|----|------|
| $U_0$ | 原載重 $P$ 獨自引起的應變能 |
| $U_i$ | 單位多餘力 $X_i = 1$ 引起的應變能 |
| $U_{ij}$ | 多餘力 $X_i, X_j$ 耦合項（由相互性 $U_{ij} = U_{ji}$） |

### 展開與求解

對 $X_i$ 求偏導：

$$\frac{\partial U}{\partial X_i} = U_i(P) + \sum_{j=1}^{d} X_j U_{ij} = 0$$

整理得：

$$\sum_{j=1}^{d} X_j U_{ij} = -U_i(P)$$

或**矩陣形式**：

$$[U]\{X\} = -\{U_0\}$$

## 應變能計算

### 彎曲應變能

$$U_{\text{bending}} = \int_L \frac{M^2}{2EI} dx$$

對於分段常截面的梁，若 $M(x)$ 在段內為多項式，可逐段積分或用梁表公式。

### 軸向應變能

$$U_{\text{axial}} = \int_L \frac{N^2}{2EA} dx$$

適用於桁架或有軸力的梁柱。

### 剪力與扭轉應變能

- **剪力**（平梁常忽略）：$U_{\text{shear}} = \int_L \frac{V^2}{2GA_s} dx$
- **扭轉**（平面結構通常無）：$U_{\text{torsion}} = \int_L \frac{T^2}{2GJ} dx$

**簡化**：多數題目只計彯曲，軸力與剪力可忽略。

## 標準求解步驟

### Step 1：選定多餘力

基本結構為靜定結構，多餘力數 = 超靜不定度 $d$。

### Step 2：列寫內力表達式

對**原載重** $P$：
$$M_0(x), N_0(x), \ldots$$

對**單位多餘力** $X_i = 1$：
$$m_i(x), n_i(x), \ldots$$

### Step 3：計算應變能

$$U_0 = \int_L \frac{M_0^2}{2EI} dx, \quad U_i = \int_L \frac{m_i^2}{2EI} dx, \quad U_{ij} = \int_L \frac{m_i \cdot m_j}{2EI} dx$$

### Step 4：建立最小功方程

$$\frac{\partial U}{\partial X_i} = 0 \implies \sum_{j=1}^{d} U_{ij} \cdot X_j = -U_i(P)$$

### Step 5：聯立求解

解線性方程組得多餘力 $X_1, X_2, \ldots, X_d$。

### Step 6：疊加求內力

$$M_{\text{total}} = M_0 + \sum_{i=1}^{d} X_i m_i$$

## 與諧合變位法的關係

最小功法與諧合變位法（虛功原理）在數學上等價：

| 最小功法 | 諧合變位法 |
|---------|-----------|
| $\frac{\partial U}{\partial X_i} = 0$ | $\delta_{i0} + \sum X_j \delta_{ij} = 0$ |
| 應變能 | 柔度係數 |

轉換關係：$\delta_{ij} = \frac{\partial^2 U}{\partial X_i \partial X_j}$

## 常見簡化

### 1. 純彯曲結構（忽略軸力）

$$U = \int \frac{M^2}{2EI} dx$$

代入最小功方程：

$$\sum_{j} X_j \int \frac{m_i m_j}{EI} dx = \int \frac{M_0 m_i}{EI} dx$$

### 2. 常截面梁

若 $EI = const$，可提取：

$$\sum_{j} X_j \int m_i m_j dx = \int M_0 m_i dx$$

（對應虛功法的柔度係數）

### 3. 特殊載重組合

多個獨立載重情況（如恆載 + 活載）：
$$U_{\text{total}} = U_{\text{dead}} + U_{\text{live}} + 2U_{\text{cross}}$$

求偏導後，多餘力對應總載重。

## 涉及題目

| 題號 | 年度 | 特點 |
|------|------|------|
| [[SA-2013-1]] | 2013 | 靜不定梁，純彯曲 |
| [[SA-2010-2]] | 2010 | 桁架 + 軸力應變能 |
| [[SA-2006-1]] | 2006 | 複合結構 |

## 參考資源

- [[SA-code-compatibility]]：等價的力法
- [[SA-code-unit-2]]：多餘力定義
