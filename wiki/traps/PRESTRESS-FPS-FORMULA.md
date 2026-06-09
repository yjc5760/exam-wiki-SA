# 預力鋼腱極限應力 fps 公式選擇陷阱

**陷阱 ID：** PRESTRESS-FPS-FORMULA
**知識分類：** RC-U4-1
**危險係數：** ★★★（高頻、高誤率）

---

## 陷阱描述

預力梁計算撓曲強度時，$f_{ps}$ 的計算方式取決於**鋼腱有無黏結（bonded vs. unbonded）**。
考生最常犯的錯誤是：混用有黏結與無握裹的公式。

---

## 公式對照

### 有黏結鋼腱（Bonded Tendons）

ACI 318 §25.5.3（台灣慣用近似式）：

$$f_{ps} = f_{pu}\left(1 - \frac{\gamma_p}{\beta_1}\left(\rho_p \frac{f_{pu}}{f'_c} + \frac{d}{d_p}(\omega - \omega')\right)\right)$$

其中 $\gamma_p = 0.28$（低鬆弛鋼絞線，$f_{py}/f_{pu} \geq 0.90$）

簡化記憶：$\omega_p = \rho_p f_{ps}/f'_c \leq 0.36\beta_1$（延性驗核）

### 無握裹鋼腱（Unbonded Tendons）

$$f_{ps} = f_{se} + 70 + \frac{f'_c}{100\rho_p} \leq \min(f_{py},\ f_{se}+420)$$

（$f_{se}$、$f_{py}$ 單位：MPa；或同等 kgf/cm² 換算）

另外對於無握裹腱，$L/d_p$ 比值決定公式的形式（短跨用不同修正）。

---

## 判斷流程

```
讀題 → 確認「有黏結腱（bonded）」或「無握裹腱（unbonded）」
     ↓
有黏結：用 γp/(β₁) 近似式 → 需反覆迭代（fps 出現在兩邊）
無握裹：直接代入 fse + 70 + ... 公式（一次計算）
     ↓
最終驗核：ωp = ρp·fps/f'c ≤ 0.36β₁（延性控制）
```

---

## 常見陷阱場景

| 陷阱 | 說明 |
|------|------|
| 忘記 $\beta_1$ 折減 | $\gamma_p/\beta_1$ 的 $\beta_1$ 常被遺漏 |
| 無握裹腱用有黏結公式 | 無握裹腱的 $f_{ps}$ 遠小於有黏結腱 |
| 忘記 $\omega'$（壓力鋼筋） | 若同時有壓力非預力筋，需在公式中扣除 $\omega'$ |
| $d$ vs. $d_p$ | 公式中的 $d$ 是非預力鋼筋深度，$d_p$ 是預力腱深度 |
| 開裂彎矩 $M_{cr}$ 計算 | $M_{cr}$ 用彈性方法（$f = P/A \pm Pe \cdot y/I \pm M \cdot y/I$），而非 Whitney |

---

## 出現題目

| 題號 | 說明 |
|------|------|
| [RC-2004-5](../problems/RC-2004-5.md) | 先拉法有黏結腱，fps 公式，ωp 延性驗核 |
| [RC-2013-4](../problems/RC-2013-4.md) | 先拉法有黏結腱，開裂彎矩，fps 公式 |
| [RC-2018-4](../problems/RC-2018-4.md) | 後拉法有黏結腱，開裂彎矩，極限彎矩，fps 選擇 |
| [RC-2023-4](../problems/RC-2023-4.md) | 後拉法無握裹鋼絞線，L/dp比值，fps公式 |
