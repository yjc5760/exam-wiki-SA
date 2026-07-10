# 諧合變位法：公式來源與應用

**method_id:** `compatibility-method`
**涵蓋單元：** [[SA-U2-2]]
**分析哲學：** [[force-method-philosophy]]（力法思維）

## 理論基礎

諧合變位法（Method of Consistent Deformations, MCD）/ 柔度法（Flexibility Method）是力法的標準操作程序。核心：
1. 選定並移除多餘束制，得**靜定基本結構**
2. 利用「原結構與基本結構在多餘力作用點的變形應一致」建立**諧合方程**
3. 求解多餘力

## 核心公式

### 諧合條件（單一多餘力）

移除多餘束制後，基本結構在原載重與多餘力作用下，多餘力方向的位移應與原結構一致（即 = 0）：

$$\boxed{\delta_{10} + \delta_{11} X_1 = 0}$$

解得：
$$\boxed{X_1 = -\frac{\delta_{10}}{\delta_{11}}}$$

| 符號 | 定義 | 計算方法 |
|------|------|---------|
| $\delta_{10}$ | 基本結構在原載重 P 下，多餘力作用點沿多餘力方向的位移 | 虛功法：$\delta_{10} = \int \frac{m_0 M_0}{EI} dx$（$m_0$ = 多餘力為1時的內力） |
| $\delta_{11}$ | 基本結構在單位多餘力 $X_1=1$ 下，多餘力作用點的自柔度 | 虛功法：$\delta_{11} = \int \frac{m_1 m_1}{EI} dx$ |
| $X_1$ | 多餘力真實值 | 求解上式 |

### 多多餘力（$d \geq 2$）矩陣形式

$$\boxed{[\delta]\{X\} = -\{\Delta_0\}}$$

| 符號 | 說明 |
|------|------|
| $[\delta]$ | **柔度矩陣**（$d \times d$），$\delta_{ij} = \int \frac{m_i m_j}{EI} dx$；對稱矩陣 |
| $\{X\}$ | 多餘力向量（$d \times 1$） |
| $\{\Delta_0\}$ | 基本結構在原載重下各多餘力作用點的位移（$d \times 1$） |

**求解：**
$$\{X\} = -[\delta]^{-1}\{\Delta_0\}$$

### 虛功原理（計算柔度係數的工具）

對於彯曲：
$$\delta_{ij} = \int_L \frac{m_i(x) \cdot m_j(x)}{EI} dx$$

對於軸力：
$$\delta_{ij,\text{axial}} = \int_L \frac{n_i(x) \cdot n_j(x)}{EA} dx$$

總柔度：
$$\delta_{ij} = \delta_{ij,\text{bending}} + \delta_{ij,\text{axial}} + \ldots$$

## 標準求解步驟

### Step 1：判斷超靜不定度
$$d = r + c - 3 - j$$

（同靜定度判斷）

### Step 2：選擇基本結構

移除 $d$ 個多餘束制，使結構變為靜定。選擇原則：
- 基本結構應為**可計算的靜定結構**
- 避免選出機構（$d < 0$）
- 通常移除支承反力或切斷內鉸

### Step 3：建立內力表達式

**原載重 P 作用在基本結構下：**
$$M_0(x), N_0(x), \ldots \text{ (不含多餘力)}$$

**單位多餘力 $X_i = 1$ 作用在基本結構下：**
$$m_i(x), n_i(x), \ldots$$

### Step 4：計算柔度係數

$$\delta_{i0} = \int_L \frac{m_i(x) M_0(x)}{EI} dx, \quad \delta_{ij} = \int_L \frac{m_i(x) m_j(x)}{EI} dx$$

### Step 5：建立諧合方程

$$[\delta]\{X\} = -\{\Delta_0\}$$

其中 $\{\Delta_0\}$ 包含原載重效應（見下節）。

### Step 6：聯立求解

$$\{X\} = -[\delta]^{-1}\{\Delta_0\}$$

### Step 7：疊加求最終內力

$$M_{\text{final}} = M_0 + \sum_{i=1}^{d} X_i m_i$$

## 特殊效應與邊界修正

### 1. 支承沉陷（Settlement）

若多餘力作用點發生沉陷 $\Delta$（向下為正），則諧合方程右側補正：

$$\delta_{i0} + \sum_j X_j \delta_{ij} = -\Delta \quad \text{（若沉陷方向與假設反力方向同向）}$$

通常表示為：
$$[\delta]\{X\} = -\{\Delta_0\} - \{\Delta_{\text{settlement}}\}$$

### 2. 溫度變化

若構件升溫 $\Delta T$：
- **軸向位移**：$\Delta_x = \alpha \Delta T \cdot L$（$\alpha$ = 膨脹係數）
- **側向位移（梁）**：不均勻加熱時 $\Delta_y = \alpha \Delta T \cdot (h/L)$（$h$ = 梁高）
- 加入諧合方程右側

### 3. 製造誤差

構件製造時長度差 $\Delta L$（如預製件組裝）：
- **直接效應**：軸向位移 = $\Delta L$
- **間接效應**：引發額外彎矩（視同邊界位移）
- 代入諧合方程

### 4. 彈性支承（Elastic Support）

若支承為彈簧（勁度 $k$），則支承處的相對位移與反力成正比：

$$\text{位移} = \frac{R}{k}$$

修正柔度矩陣：
$$\delta_{11,\text{修}} = \int \frac{m_1^2}{EI} dx + \frac{1}{k}$$

## 與最小功法的對應

| 諧合變位法 | 最小功法 |
|-----------|---------|
| $[\delta]\{X\} = -\{\Delta_0\}$ | $[U]\{X\} = -\{U_0\}$ |
| 柔度矩陣 $\delta_{ij}$ | 應變能 $U_{ij}$ |
| 原載重位移 $\Delta_{i0}$ | 原載重應變能 $U_{i0}$ |

**數學等價性**：
$$\delta_{ij} = \frac{\partial^2 U}{\partial X_i \partial X_j}$$

## 涉及題目

| 題號 | 年度 | 特點 |
|------|------|------|
| [[SA-2023-2]] | 2023 | 靜不定桁架，軸力應變能 |
| [[SA-2019-3]] | 2019 | 連續梁，支承沉陷 |
| [[SA-2011-1]] | 2011 | 靜不定桁架，溫度 + 製造誤差 |

## 參考資源

- [[SA-code-minimum-work]]：能量等價形式
- [[SA-code-unit-2]]：多餘力與自由度定義
- [[wiki/failure-modes/公式應用]]：常見陷阱
