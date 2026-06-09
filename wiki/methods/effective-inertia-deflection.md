# 有效慣性矩法（撓度計算）

**Method ID：** effective-inertia-deflection
**適用題型：** RC-U3-1 梁工作性要求（含撓度、裂縫）

## 概述

利用 ACI 有效慣性矩 Ie 計算 RC 梁服務載重下即時與長期撓度。

## 解題步驟

1. Step 1：計算開裂彎矩 Mcr = fr·Ig/yt（fr = 2√f'c）
2. Step 2：計算未開裂斷面慣性矩 Ig
3. Step 3：計算開裂斷面慣性矩 Icr（轉換斷面法）
4. Step 4：Ie = (Mcr/Ma)³·Ig + [1-(Mcr/Ma)³]·Icr
5. Step 5：即時撓度 δi = 5wL⁴/(384EcIe)（簡支）
6. Step 6：長期撓度修正 δlt = λ·δi（λ = ξ/(1+50ρ')）

## 常見陷阱

- ⚠️ Ie 不可超過 Ig（若 Ma < Mcr 直接用 Ig）
- ⚠️ ρ' 是壓力筋比，無壓力筋時 ρ'= 0 → λ = ξ
- ⚠️ ξ 值依持載時間：5年以上取 2.0

## 相關題目

[RC-2005-4](../problems/RC-2005-4.md) · [RC-2006-3](../problems/RC-2006-3.md) · [RC-2007-2](../problems/RC-2007-2.md) · [RC-2008-1](../problems/RC-2008-1.md) · [RC-2009-4](../problems/RC-2009-4.md) · [RC-2009-2](../problems/RC-2009-2.md) · [RC-2014-2](../problems/RC-2014-2.md) · [RC-2018-3](../problems/RC-2018-3.md)
