# 第二單元：靜不定結構分析方法

**命題大綱：** [[SA-U2]] 靜不定結構的五種解法
**涵蓋主題：** 最小功法、諧合變位法、傾角變位法、矩陣位移法、彎矩分配法

## 核心公式對比表

### 1. 通用基礎公式

#### 超靜不定度與自由度

| 項目 | 公式／說明 |
|------|-----------|
| 超靜不定度（力法基礎） | $d = r + c - 3 - j$ |
| 自由度（位移法基礎） | $DOF = 3j - (r+c)$；或結構層面計 $DOF = 3\text{(樓層數)} - \text{(邊界約束數)}$ |
| 側移自由度（側向位移） | 剛架 DOF - 軸向位移 DOF（取決於支承配置） |

#### 能量原理

| 原理 | 公式 | 應用場景 |
|------|------|---------|
| 虛功原理 | $\delta = \int_L \frac{m(x) \cdot M(x)}{EI} dx + \int_L \frac{n(x) \cdot N(x)}{EA} dx + \ldots$ | 求位移、支反力 |
| Castigliano 定理 | $\delta_i = \frac{\partial U}{\partial P_i}$（$U$ = 應變能） | 求位移、反力 |
| 相互定理（Reciprocal） | $\delta_{ij} = \delta_{ji}$（$\delta_{ij}$ = P_i作用下j點位移） | 驗算、簡化計算 |

### 2. 最小功法與諧合變位法（力法）

#### 核心思想
- 選定**多餘力** $X_1, X_2, \ldots, X_d$（$d$ = 超靜不定度）
- 移除對應束制得**靜定基本結構**
- 根據**諧合條件**建立方程求多餘力

#### 諧合條件（Compatibility）

**單一多餘力（$d=1$）：**

$$\delta_{10} + \delta_{11} X_1 = 0 \implies X_1 = -\frac{\delta_{10}}{\delta_{11}}$$

| 符號 | 定義 | 計算方法 |
|------|------|---------|
| $\delta_{10}$ | 移除多餘力後，原載重作用下「多餘力作用點」的位移 | 虛功法：$\delta_{10} = \int \frac{m_0 \cdot M_0}{EI} dx$（$m_0$ = 多餘力為1時的內力） |
| $\delta_{11}$ | 多餘力 $X_1=1$ 時，多餘力作用點的「自柔度」 | 虛功法：$\delta_{11} = \int \frac{m_1 \cdot m_1}{EI} dx$ |
| $X_1$ | 多餘力真實值 | 求解上式 |

**多多餘力（$d \geq 2$）矩陣形式：**

$$[\delta]\{X\} = -\{\Delta_0\}$$

其中 $[\delta]$ 為柔度矩陣，$\delta_{ij} = \int \frac{m_i \cdot m_j}{EI} dx$

#### 特殊效應的諧合方程修正

| 效應 | 修正項 |
|------|--------|
| 支承沉陷（下沉 $\Delta x$） | 在諧合方程右側加上 $\Delta_x$（沉陷方向與假設反力方向一致時為正） |
| 溫度變化（$\Delta T$） | 軸向位移 $= \alpha \Delta T \cdot L$；側向位移（梁）$= \alpha \Delta T \cdot h / L$（$h$ = 梁高）；加入右側 |
| 製造誤差（長度差 $\Delta L$） | 軸向：直接加 $\Delta L$；轉角：等效力矩 $= 6EI \Delta L / L^2$ |
| 彈性支承（彈簧常數 $k$） | 多餘力作用下支承位移 $= X_1 / k$，加入柔度矩陣：$\delta_{11} = \int \frac{m_1^2}{EI} dx + \frac{1}{k}$ |

#### 最小功法專用

**Castigliano 定理（位移形）：** 

若結構有多餘力 $X_i$，則
$$\frac{\partial U}{\partial X_i} = 0 \quad \text{(最小應變能條件)}$$

其中 $U = U_0 + \sum X_i U_i + \frac{1}{2}\sum X_i X_j \delta_{ij}$

展開後得諧合方程，與虛功法等效。

### 3. 傾角變位法（位移法）

#### 核心未知量
- **節點轉角** $\theta_i$
- **側移** $\delta$（各層側向位移）
- 假設桿軸不變形（無軸向變形 or 軸向變形忽略）

#### 桿端彎矩公式（標準形）

$$M_{ij} = \frac{2EI}{L}\big(2\theta_i + \theta_j - 3\psi\big) + M^F_{ij}
= \frac{4EI}{L}\theta_i + \frac{2EI}{L}\theta_j - \frac{6EI}{L^2}\Delta + M^F_{ij}$$

其中：
- $4EI/L$：轉角勁度（i 端轉角 $\theta_i=1$、遠端固定時 i 端彎矩）
- $2EI/L$：轉角耦合項（j 端轉角 $\theta_j=1$ 時傳到 i 端的彎矩 ⟹ 傳遞係數 $C=1/2$）
- $M^F_{ij}$：固端彎矩（兩端固定時跨內載重造成的端彎矩）
- $-6EI/L^2 \cdot \Delta = -6EI/L \cdot \psi$：側移項。$\Delta$ 為兩端**垂直於桿軸**的相對位移，$\psi = \Delta/L$

**⭐ 建議記憶形式（把 $\psi$ 併入 $\theta$）：**

$$M_{ij} = \frac{2EI}{L}\Big[\,2(\theta_i - \psi) + (\theta_j - \psi)\,\Big] + M^F_{ij}$$

彎矩只認「桿端切線<u>相對於弦</u>的角度」。那個 $-3\psi$ 其實是 $-2\psi-\psi$，
是兩個 $\theta$ 各自扣掉弦轉動的結果，不必背；且 $\psi$ 的係數必然等於兩個 $\theta$ 係數之和（$3=2+1$）。

**剛體檢查（10 秒抓符號錯）：** 令 $\theta_i=\theta_j=\psi=\alpha$、無跨內載重，應得 $M_{ij}=0$。
若不為零，符號一定錯（最常見是把 $-3\psi$ 寫成 $+3\psi$）。

#### 側移剛架的額外方程：層剪力平衡

第 $k$ 層的層剪力平衡：

$$\sum V_k = H_k \quad (\text{該層外加水平力})$$

柱**無**跨內載重時，由單柱自由體取矩：

$$|V| = \frac{|M_{ij} + M_{ji}|}{L}\qquad(\text{方向由自由體圖決定})$$

以位移表示（與矩陣法對應時使用）：

$$V = -\frac{6EI}{L^2}(\theta_i + \theta_j) + \frac{12EI}{L^3}\Delta + V^0_{ij}$$

其中 $V^0_{ij}$ 為兩端固定時跨內載重造成的固端剪力。

> ⚠️ **兩項符號必須相反。** 剛體檢查：令 $\theta_i=\theta_j=\alpha$、$\Delta=\alpha L$，
> 應得 $V = -\frac{12EI\alpha}{L^2} + \frac{12EI\alpha}{L^2} = 0$。若兩項同號，此檢查會失敗。
>
> ⚠️ **柱上有跨內載重時 $|V| = |M_{ij}+M_{ji}|/L$ 不成立**，必須另畫自由體推導（見 [[SA-2017-3]]）。
>
> **斜桿／非正交幾何／柱有集中力時，改用虛功法建側移方程：**
> $\sum(\text{外力} \times \text{虛位移}) = \sum (M_{ij}+M_{ji})\,\delta\psi_{ij}$。
> $\delta\psi_{ij}$ 在寫方程式時已算過，直接重用，不必再做一次幾何分解。

#### 勁度與修正

| 情況 | 有效勁度 | 說明 |
|------|--------|------|
| 標準桿（兩端剛接、遠端固定） | $4EI/L$ | 無修正；傳遞係數 $C=1/2$ |
| **遠端鉸接** | $3EI/L$（**減 25%**） | 原因是「遠端不再提供**轉動約束**」，故近端變軟。<br>**不是**「遠端轉角為零」—— 恰好相反，遠端鉸接時 $\theta_j$ 最大，只是彎矩為零。<br>修正式：$M_{ij} = \frac{3EI}{L}(\theta_i-\psi) + \big(M^F_{ij}-\tfrac12 M^F_{ji}\big)$，**式中無 $\theta_j$** |
| 對稱結構＋**對稱**載重（跨對稱軸的桿） | $2EI/L$（減半） | $\theta_j = -\theta_i$ ⟹ $(2\theta_i-\theta_i)=\theta_i$；且 $\Delta = 0$ |
| 對稱結構＋**反對稱**載重（跨對稱軸的桿） | $6EI/L$（1.5 倍） | $\theta_j = +\theta_i$ ⟹ $(2\theta_i+\theta_i)=3\theta_i$；且 $\Delta \ne 0$ |
| 兩端皆無轉角、僅側移（剛性構件夾住的柱） | $M=\frac{6EI}{L^2}\Delta$、$V=\frac{12EI}{L^3}\Delta$ | 短柱效應：$V \propto 1/L^3$（見 [[SA-2006-4]]） |
| 非均勻斷面 | $M_{ij}=S_{ij}\frac{EI_0}{L}(\theta_i+C_{ji}\theta_j)-(\text{側移項})+\bar M^F_{ij}$ | 均勻梁是 $S=4$、$C=1/2$ 的特例；須重新推導（見 [[SA-2025-3]]） |

> ⚠️ **名稱陷阱：**「對稱載重」給的是**反號**的轉角，「反對稱載重」給的才是**同號**的轉角。
> 名稱說的是載重與變形形狀的對稱性，不是轉角數值的正負。
> 不要背這兩個數字，直接把轉角關係代進 $\frac{2EI}{L}(2\theta_i+\theta_j)$ 即可，三秒鐘且不會記反。

#### 固端彎矩（FEM）與修正規則

| 載重 | $M^F_{ij}$（左端） | $M^F_{ji}$（右端） |
|------|------|------|
| 滿跨均佈 $w$ | $-wL^2/12$ | $+wL^2/12$ |
| 中央集中 $P$ | $-PL/8$ | $+PL/8$ |
| 任意位置集中 $P$（距 i 為 $a$、距 j 為 $b$） | $-Pab^2/L^2$ | $+Pa^2b/L^2$ |
| 三角形分佈（i 端 0 → j 端 $w$） | $-wL^2/30$ | $+wL^2/20$ |

**遠端鉸接的修正規則（一條吃下所有特例）：**

$$\bar M^F_{ij} = M^F_{ij} - \tfrac12 M^F_{ji}$$

驗證：滿跨均佈 $wL^2/12 \to wL^2/8$；中央集中 $PL/8 \to 3PL/16$。
**修正後必然變大**（遠端不能承擔彎矩，載重效應全推給近端）。算出變小就是符號寫反。

> **節點載重不進 FEM。** 作用在剛節點的力沒有跨內位置 ⟹ FEM $=0$；
> 也不進節點彎矩平衡（$\sum M=0$ 只加彎矩）；**只**進側移方程。見 [[SA-2017-3]]。

> **完整原理、圖解與手算範例：** 見 [SA-U2-3 觀念講義](../../study/lecture-SA-U2-3.html)
> 與 [SA-U2-3 題型診斷](../diagnosis/SA-U2-3.md)；本法專頁見 [[SA-code-slope-deflection]]。

### 4. 矩陣位移法（直接勁度法）

#### 核心方程

$$[K]\{\Delta\} = \{F\}$$

| 符號 | 含義 |
|------|------|
| $[K]$ | 全結構剛度矩陣（global stiffness matrix）|
| $\{\Delta\}$ | 節點位移向量 |
| $\{F\}$ | 節點外力向量（包含集中力、力矩） |

#### 桿件局部剛度矩陣（1個桿，2個節點i,j，3 DOF/節點）

假設桿i-j，方向沿x軸，則局部坐標下 6×6 矩陣：

$$[k]_{\text{local}} = \begin{bmatrix} 
EA/L & 0 & 0 & -EA/L & 0 & 0 \\
0 & 12EI/L^3 & 6EI/L^2 & 0 & -12EI/L^3 & 6EI/L^2 \\
0 & 6EI/L^2 & 4EI/L & 0 & -6EI/L^2 & 2EI/L \\
-EA/L & 0 & 0 & EA/L & 0 & 0 \\
0 & -12EI/L^3 & -6EI/L^2 & 0 & 12EI/L^3 & -6EI/L^2 \\
0 & 6EI/L^2 & 2EI/L & 0 & -6EI/L^2 & 4EI/L 
\end{bmatrix}$$

#### 組合與邊界條件施加

1. 為每條桿建立局部剛度矩陣
2. 坐標轉換至全局坐標
3. 按節點編號組合成全結構 $[K]$
4. 施加邊界條件（固定DOF對應的行列刪除）
5. 求解 $\{\Delta\} = [K]^{-1}\{F\}$
6. 逐桿計算內力

### 5. 彎矩分配法（迭代法）

#### 核心參數

| 參數 | 符號 | 計算公式 | 說明 |
|------|------|---------|------|
| 勁度 | $K_{ij}$ | $4EI/L$（遠端固定）；$3EI/L$（遠端鉸接） | 轉角單位變化時的彎矩 |
| 分配因子 | $DF_{ij}$ | $K_{ij} / \sum K$ | 節點 $i$ 的不平衡彎矩分配給各桿的比例 |
| 傳遞因子 | $COF$ | $1/2$（遠端固定）；$0$（遠端鉸接） | 分配至節點 $i$ 的彎矩傳遞至遠端的比例 |

#### 迭代步驟

1. **計算 FEM**：各桿在載重下的固端彎矩
2. **計算 DF**：$DF_{ij} = K_{ij} / \sum_k K_{ik}$
3. **初始化**：所有節點暫假設為固定（所有轉角 = 0）
4. **逐節點分配**：
   - 計算不平衡彎矩 $U_i = \sum M_{FEM}$（匯聚於節點i的所有末端彎矩）
   - 分配：$M_{\text{dist},ij} = -DF_{ij} \cdot U_i$（負號表示抵銷不平衡）
   - 傳遞：$M_{\text{carry},ji} = COF \cdot M_{\text{dist},ij}$
5. **重複迭代**：直至每個節點的不平衡彎矩 < 允許精度（通常 0.01 kN-m）
6. **計算最終彎矩**：$M_{final,ij} = M_{FEM} + \sum(\text{分配}) + \sum(\text{傳遞})$

#### 對稱性簡化

對稱結構可取半結構分析。跨對稱軸的桿件，其有效勁度依**載重**的對稱性而不同：

| 載重 | 跨對稱軸桿的轉角關係 | 有效勁度 |
|------|------------------|---------|
| **對稱** | $\theta_{\text{far}} = -\theta_{\text{near}}$ | $K = 2EI/L$（減半） |
| **反對稱** | $\theta_{\text{far}} = +\theta_{\text{near}}$ | $K = 6EI/L$（1.5 倍） |

分配因子須依修正後的勁度重算；跨對稱軸的桿不再需要傳遞（遠端由對稱性決定）。

## 涉及題目統計

依 `raw/json/question_index.json` 的 `primaryTopicId` 統計（2026-07-26 重新核對）。
第二單元主分類共 **46 題**（全科 96 題）：

| 子項 | 方法 | 主分類題數 | 代表題目 |
|------|------|:---------:|---------|
| SA-U2-1 | 最小功法 | 12 | [[SA-2006-1]], [[SA-2013-2]], [[SA-2022-1]] |
| SA-U2-2 | 諧合變位法 | 7 | [[SA-2002-3]], [[SA-2011-1]], [[SA-2023-2]] |
| SA-U2-3 | 傾角變位法 | 13 | [[SA-2017-3]], [[SA-2022-2]], [[SA-2024-4]] |
| SA-U2-4 | 矩陣位移法 | 12 | [[SA-2012-4]], [[SA-2019-4]], [[SA-2025-4]] |
| SA-U2-5 | 彎矩分配法 | 2 | [[SA-2003-1]], [[SA-2006-3]] |

> ⚠️ **勘誤（2026-07-26）：** 原表的「代表題目」多處題號不屬於該子項 ——
> 最小功法列 [[SA-2013-1]]（實為 SA-U1-2 桁架三鉸拱）與 SA-2010-2；
> 傾角變位法列 SA-2017-2（實為 SA-U2-1）與 SA-2009-2；
> 矩陣位移法列 SA-2019-2、[[SA-2016-1]]、[[SA-2012-1]]（後兩題實為 SA-U1-2）。
> 題數（12／7／13／12／2）本身正確，已保留並補上子項代號。

## 參考資源

- 結構學第二單元命題大綱：見 `CLAUDE.md`「命題大綱分類」
- 各方法專頁：[SA-code-minimum-work](SA-code-minimum-work.md)、[SA-code-compatibility](SA-code-compatibility.md)、[**SA-code-slope-deflection**](SA-code-slope-deflection.md)、[SA-code-matrix-displacement](SA-code-matrix-displacement.md)、[SA-code-moment-distribution](SA-code-moment-distribution.md)
- 題型診斷：[SA-U2-1](../diagnosis/SA-U2-1.md)、[SA-U2-2](../diagnosis/SA-U2-2.md)、[**SA-U2-3**](../diagnosis/SA-U2-3.md)、[SA-U2-4](../diagnosis/SA-U2-4.md)、[SA-U2-5](../diagnosis/SA-U2-5.md)
- 觀念講義：[lecture-SA-U2-3](../../study/lecture-SA-U2-3.html)（[PDF](../../study/lecture-SA-U2-3.pdf)）
- 相關哲學思維：[force-method-philosophy](../philosophy/force-method-philosophy.md)、[displacement-method-philosophy](../philosophy/displacement-method-philosophy.md)、[matrix-method-philosophy](../philosophy/matrix-method-philosophy.md)
- 相關失敗模式：[符號錯誤](../failure-modes/符號錯誤.md)、[公式應用](../failure-modes/公式應用.md)、[收斂問題](../failure-modes/收斂問題.md)
