# RC 鋼筋混凝土設計與預力 知識庫

> **科目：** RC（結構工程技師高考第三科）
> **題庫：** 100 題（2002–2025 年）
> **格式：** RC-YYYY-N（例：RC-2015-1）
> **操作指令：** 見 CLAUDE-CODE.md　｜　**解題規範：** 見 CLAUDE-SOLVE.md

---

## 七層知識架構

本知識庫依以下七層組織所有知識：

| 層 | 目錄 | 維護者 | 說明 |
|----|------|:------:|------|
| Layer 1 | [concepts/](concepts/) · [problems/](problems/) | Cowork (ingest/compile) | 核心概念定義 + 題目解析 |
| Layer 2 | [philosophy/](philosophy/) | Cowork (compile-all) | 設計哲學（強度折減／韌性／耐震） |
| Layer 3 | [methods/](methods/) | Cowork (compile-all) | 解題方法論（P-M 互制／等效側力／損失計算） |
| Layer 4 | [diagnosis/](diagnosis/) | Cowork (直接存入) | 題型診斷決策樹 |
| Layer 5 | [failure-modes/](failure-modes/) | Cowork (直接存入) | 失敗模式（彎曲／剪力／壓碎／撓度／裂縫） |
| Layer 6 | [materials/](materials/) | Cowork (直接存入) | 材料行為（混凝土應力應變／鋼筋降伏／潛變收縮） |
| Layer 7 | [code-ref/](code-ref/) | Cowork (直接存入) | 規範條文對應（ACI 318／CNS 1480／耐震規範） |

---

## 概念頁快速導覽（24 個核心概念）

### 第一單元（RC-U1）：梁 / 柱設計

| 概念 ID | 概念名稱 | 分類 |
|---------|---------|------|
| [BALANCED-REINFORCEMENT-RATIO](concepts/BALANCED-REINFORCEMENT-RATIO.md) | 平衡鋼筋比 ρb | RC-U1-1 |
| [WHITNEY-STRESS-BLOCK](concepts/WHITNEY-STRESS-BLOCK.md) | Whitney 等值矩形應力塊 | RC-U1-1 |
| [BETA1-FACTOR](concepts/BETA1-FACTOR.md) | β1 係數（應力塊深度折減） | RC-U1-1 |
| [DUCTILE-FAILURE](concepts/DUCTILE-FAILURE.md) | 延性破壞（拉力控制破壞） | RC-U1-1 |
| [PM-INTERACTION-DIAGRAM](concepts/PM-INTERACTION-DIAGRAM.md) | P-M 互制圖 | RC-U1-2 |
| [BALANCED-POINT](concepts/BALANCED-POINT.md) | 平衡點（柱 P-M 圖） | RC-U1-2 |
| [LONG-COLUMN-MOMENT-MAGNIFIER](concepts/LONG-COLUMN-MOMENT-MAGNIFIER.md) | 長柱彎矩放大法（δns） | RC-U1-3 |

### 第二單元（RC-U2）：剪力 / 扭力 / 錨定

| 概念 ID | 概念名稱 | 分類 |
|---------|---------|------|
| [SHEAR-STRENGTH](concepts/SHEAR-STRENGTH.md) | RC 剪力強度 Vc + Vs | RC-U2-1 |
| [STIRRUP-DESIGN](concepts/STIRRUP-DESIGN.md) | 箍筋設計（剪力筋） | RC-U2-1 |
| [TORSION-DESIGN](concepts/TORSION-DESIGN.md) | RC 扭力強度設計（空間桁架類比） | RC-U2-2 |
| [DEVELOPMENT-LENGTH](concepts/DEVELOPMENT-LENGTH.md) | 鋼筋錨定長度 ld | RC-U2-3 |

### 第三單元（RC-U3）：工作性 / 版基 / 耐震

| 概念 ID | 概念名稱 | 分類 |
|---------|---------|------|
| [EFFECTIVE-MOMENT-OF-INERTIA](concepts/EFFECTIVE-MOMENT-OF-INERTIA.md) | 有效慣性矩 Ie（ACI 方法） | RC-U3-1 |
| [CRACKING-MOMENT](concepts/CRACKING-MOMENT.md) | 開裂彎矩 Mcr | RC-U3-1 |
| [LONG-TERM-DEFLECTION](concepts/LONG-TERM-DEFLECTION.md) | 長期撓度（潛變收縮修正） | RC-U3-1 |
| [CREEP-SHRINKAGE](concepts/CREEP-SHRINKAGE.md) | 潛變與收縮 | RC-U3-1 |
| [DEFLECTION-CONTROL](concepts/DEFLECTION-CONTROL.md) | 撓度控制（容許撓度） | RC-U3-1 |
| [CRACK-WIDTH](concepts/CRACK-WIDTH.md) | 裂縫寬度控制 | RC-U3-1 |
| [PUNCHING-SHEAR](concepts/PUNCHING-SHEAR.md) | 衝剪（雙向剪力） | RC-U3-2 |
| [SEISMIC-DESIGN](concepts/SEISMIC-DESIGN.md) | 耐震設計（能力設計法） | RC-U3-3 |
| [STRONG-COLUMN-WEAK-BEAM](concepts/STRONG-COLUMN-WEAK-BEAM.md) | 強柱弱梁 | RC-U3-3 |
| [SPECIAL-MOMENT-FRAME-BEAM](concepts/SPECIAL-MOMENT-FRAME-BEAM.md) | 特殊矩形框架梁（耐震梁） | RC-U3-3 |
| [SPECIAL-MOMENT-FRAME-COLUMN](concepts/SPECIAL-MOMENT-FRAME-COLUMN.md) | 特殊矩形框架柱（耐震柱） | RC-U3-3 |

### 第四單元（RC-U4）：預力

| 概念 ID | 概念名稱 | 分類 |
|---------|---------|------|
| [EFFECTIVE-PRESTRESS](concepts/EFFECTIVE-PRESTRESS.md) | 有效預力 Pe | RC-U4-1 |
| [PRESTRESS-LOSS](concepts/PRESTRESS-LOSS.md) | 預力損失 | RC-U4-3 |

---

## 題目依年份導覽

見 [by-year.md](by-year.md) — 完整 100 題依考年分類（2002–2025）。

---

## 第一單元（RC-U1）：梁/柱設計

### RC-U1-1 RC 梁彎矩強度分析與設計

* [RC-2002-4](problems/RC-2002-4.md) — 雙筋梁壓力筋恰好降伏邊界 β₁=0.80
* [RC-2004-2](problems/RC-2004-2.md) — 外伸梁 D 點跨中彎矩
* [RC-2005-2](problems/RC-2005-2.md) — T形梁最大拉力筋量 0.75ρb
* [RC-2007-1](problems/RC-2007-1.md) — T形梁設計有效翼板寬
* [RC-2011-2](problems/RC-2011-2.md) — T形梁平衡鋼筋量 NA 在腹板
* [RC-2014-1](problems/RC-2014-1.md) — 單筋矩形梁過筋梁應變相容
* [RC-2014-2](problems/RC-2014-2.md) — 彎矩曲率分析三階段
* [RC-2015-2](problems/RC-2015-2.md) — 雙筋梁曲率韌性 εt=0.004 限制
* [RC-2015-3](problems/RC-2015-3.md) — T型梁負彎矩雙筋梁腹板矩形等效
* [RC-2016-1](problems/RC-2016-1.md) — 兩端固定梁地震彎矩組合
* [RC-2019-1](problems/RC-2019-1.md) — 單筋梁過渡區 φ 值 Whitney 應力塊
* [RC-2020-1](problems/RC-2020-1.md) — T形梁有效翼板寬中性軸在翼板
* [RC-2021-1](problems/RC-2021-1.md) — T形梁最小撓曲鋼筋剪力設計
* [RC-2022-1](problems/RC-2022-1.md) — 雙筋梁壓力筋未降伏有效深度
* [RC-2022-2](problems/RC-2022-2.md) — 梁設計最經濟材料四組合比較
* [RC-2023-1](problems/RC-2023-1.md) — 曲率延展比降伏曲率極限曲率
* [RC-2023-2](problems/RC-2023-2.md) — T形梁雙筋梁壓力鋼筋未降伏
* [RC-2024-1](problems/RC-2024-1.md) — T形梁最大最小鋼筋量高強度鋼筋
* [RC-2024-2](problems/RC-2024-2.md) — 雙筋梁壓力鋼筋未降伏懸臂梁

### RC-U1-2 RC 柱強度分析與設計

* [RC-2002-2](problems/RC-2002-2.md) — 偏心受壓 P-M 互制 6-#9
* [RC-2004-4](problems/RC-2004-4.md) — 雙軸彎矩細長柱彎矩放大法
* [RC-2005-1](problems/RC-2005-1.md) — 矩形柱 P-M 互制曲率延展比
* [RC-2008-2](problems/RC-2008-2.md) — 方形柱 P-M 互制拉力鋼筋應變為零
* [RC-2010-1](problems/RC-2010-1.md) — 圓形螺旋柱降伏軸力極限軸力
* [RC-2011-1](problems/RC-2011-1.md) — P-M 互制圖求算步驟平衡點
* [RC-2011-3](problems/RC-2011-3.md) — 矩形柱 P-M 互制三排配筋
* [RC-2015-1](problems/RC-2015-1.md) — 方形柱 P-M 互制平衡點最大彎矩
* [RC-2017-1](problems/RC-2017-1.md) — 加大柱組合截面雙折線應力應變
* [RC-2019-2](problems/RC-2019-2.md) — 矩形柱 P-M 互制壓力控制斷面
* [RC-2021-2](problems/RC-2021-2.md) — 偏心距求解 P-M 互制中性軸已知逆推
* [RC-2024-3](problems/RC-2024-3.md) — 方形柱 P-M 互制拉力鋼筋應變為零

### RC-U1-3 細長柱

* [RC-2006-2](problems/RC-2006-2.md) — 無側移柱彎矩放大法 Cm 係數
* [RC-2016-3](problems/RC-2016-3.md) — 無側移構架放大彎矩法雙曲度

### RC-U1-4 柱設計圖之應用

*(相關內容見 RC-U1-2 柱設計題)*

---

## 第二單元（RC-U2）：剪力/扭力/錨定

### RC-U2-1 RC 剪力強度分析與設計

* [RC-2006-1](problems/RC-2006-1.md) — 懸臂梁雙筋梁壓力鋼筋未降伏剪力設計
* [RC-2009-3](problems/RC-2009-3.md) — 壓拉桿模式 STM 深梁
* [RC-2010-3](problems/RC-2010-3.md) — 軸力影響剪力開裂強度三種軸力比較
* [RC-2014-3](problems/RC-2014-3.md) — 臨界斷面 Vc 最大軸力影響等效彎矩 Mm
* [RC-2017-2](problems/RC-2017-2.md) — 加大柱介面剪力摩擦剪力法
* [RC-2020-2](problems/RC-2020-2.md) — 倒 T 型梁臨界斷面 d 偏移規則
* [RC-2023-3](problems/RC-2023-3.md) — 懸臂梁臨界斷面扭力忽略門檻

### RC-U2-2 RC 扭力強度設計

* [RC-2002-3](problems/RC-2002-3.md) — 扭力忽略門檻偏心均佈載重最大偏心量 e
* [RC-2008-3](problems/RC-2008-3.md) — 矩形梁純扭矩斷面適當性空間桁架類比
* [RC-2011-4](problems/RC-2011-4.md) — 矩形梁開裂扭矩扭矩剪力組合
* [RC-2013-3](problems/RC-2013-3.md) — 扭矩強度閉合箍筋空間桁架類比
* [RC-2018-1](problems/RC-2018-1.md) — 矩形梁扭矩剪力組合空間桁架類比
* [RC-2025-3](problems/RC-2025-3.md) — 扭矩強度縱向鋼筋驗核

### RC-U2-3 鋼筋錨定長度與斷點計算

* [RC-2003-2](problems/RC-2003-2.md) — 耐震柱搭接長度詳細計算法 Class B 搭接
* [RC-2010-2](problems/RC-2010-2.md) — 耐震柱縱向搭接 Class B 搭接拉力搭接

---

## 第三單元（RC-U3）：工作性/版基/耐震

### RC-U3-1 梁工作性要求（含撓度、裂縫）

* [RC-2005-4](problems/RC-2005-4.md) — 潛變潛變係數 Cc 長期變形
* [RC-2006-3](problems/RC-2006-3.md) — 簡支梁即時撓度增量有效慣性矩 Ie
* [RC-2007-2](problems/RC-2007-2.md) — 雙筋梁即時撓度長期撓度 λ 長期修正係數
* [RC-2008-1](problems/RC-2008-1.md) — 懸臂梁雙筋梁長期撓度有效慣性矩 Ie
* [RC-2009-2](problems/RC-2009-2.md) — 懸臂梁即時撓度降伏彎矩裂縫斷面慣性矩 Icr
* [RC-2018-3](problems/RC-2018-3.md) — T形梁負彎矩裂縫控制側面縱向表層鋼筋

### RC-U3-2 樓版與基腳設計

* [RC-2002-1](problems/RC-2002-1.md) — 雙向版角隅配筋邊梁角隅翹起效應
* [RC-2007-3](problems/RC-2007-3.md) — 獨立基腳正方形基腳因數化土壓
* [RC-2013-1](problems/RC-2013-1.md) — 單向版多跨連續版最小版厚 ACI 彎矩係數法
* [RC-2017-3](problems/RC-2017-3.md) — 方形基腳底版鋼筋設計穿孔剪力
* [RC-2020-3](problems/RC-2020-3.md) — 無梁版穿孔剪力雙向剪力內柱
* [RC-2021-3](problems/RC-2021-3.md) — 樁帽設計偏心載重基樁軸力雙向剪力
* [RC-2025-1](problems/RC-2025-1.md) — 獨立基腳穿孔剪力彎矩強度雙向剪力

### RC-U3-3 韌性要求與耐震設計

* [RC-2003-3](problems/RC-2003-3.md) — 梁柱接頭內部接頭水平剪力 Vjh
* [RC-2003-4](problems/RC-2003-4.md) — 剪力牆邊界構材水平垂直剪力筋
* [RC-2004-1](problems/RC-2004-1.md) — 混凝土品質判定耐震搭接 Class B 搭接
* [RC-2004-3](problems/RC-2004-3.md) — 耐震柱 Ash 公式圍束箍筋密箍區間距
* [RC-2005-3](problems/RC-2005-3.md) — 角柱接頭接頭剪力梁柱外接頭 Vjh
* [RC-2009-1](problems/RC-2009-1.md) — 耐震柱橫向鋼筋密箍區 lo 圍束箍筋
* [RC-2010-2](problems/RC-2010-2.md) — 耐震柱縱向搭接 Class B 搭接拉力搭接
* [RC-2012-2](problems/RC-2012-2.md) — 耐震梁特殊矩形框架梁可能彎矩強度 Mpr
* [RC-2012-3](problems/RC-2012-3.md) — 強柱弱梁塑鉸機構柱地震設計剪力
* [RC-2012-4](problems/RC-2012-4.md) — 梁柱外接頭接頭剪力角隅邊柱 Vjh
* [RC-2013-2](problems/RC-2013-2.md) — 特殊矩形柱耐震圍束箍筋密箍區 Ash 公式
* [RC-2016-2](problems/RC-2016-2.md) — 特殊矩形框架梁塑性鉸區可能彎矩強度 Mpr
* [RC-2018-2](problems/RC-2018-2.md) — 角柱接頭接頭剪力梁柱接頭 γ 係數
* [RC-2019-3](problems/RC-2019-3.md) — 橫膈版地震剪力抗剪鋼筋雙向版
* [RC-2022-4](problems/RC-2022-4.md) — 曲率韌性轉角韌性位移韌性塑鉸長度 Lp
* [RC-2025-2](problems/RC-2025-2.md) — 耐震梁特殊矩形框架梁可能彎矩強度 Mpr

---

## 第四單元（RC-U4）：預力

### RC-U4-1 預力梁斷面應力分析

* [RC-2003-1](problems/RC-2003-1.md) — 部分預力梁應變相容法非預力鋼絞線
* [RC-2004-5](problems/RC-2004-5.md) — 先拉法有黏結腱開裂彎矩 Mcr fps 公式
* [RC-2006-4](problems/RC-2006-4.md) — 後拉法組合 T 型斷面兩階段應力疊加
* [RC-2007-4](problems/RC-2007-4.md) — I 形橋梁組合 T 型斷面底纖維拉力控制
* [RC-2008-4](problems/RC-2008-4.md) — 後拉法組合 T 型斷面非組合梁承受 DL
* [RC-2009-4](problems/RC-2009-4.md) — 預力 RC 拉力桿混合斷面裂縫寬度 wmax
* [RC-2011-5](problems/RC-2011-5.md) — 後拉法有黏結腱合成斷面三斷面分析
* [RC-2012-1](problems/RC-2012-1.md) — 先拉法有黏結腱懸臂梁偏心方向判斷
* [RC-2013-4](problems/RC-2013-4.md) — 先拉法有黏結腱開裂彎矩 fps 公式
* [RC-2014-4](problems/RC-2014-4.md) — 預力梁斷面應力兩階段分析施加預力階段
* [RC-2018-4](problems/RC-2018-4.md) — 後拉法有黏結腱開裂彎矩極限彎矩
* [RC-2021-4](problems/RC-2021-4.md) — 預力 T 型梁組合斷面有效翼板寬最大活載重
* [RC-2023-4](problems/RC-2023-4.md) — 後拉法無握裹鋼絞線 fps 公式 L/dp 比值

### RC-U4-2 預力量與偏心量設計

* [RC-2010-4](problems/RC-2010-4.md) — 簡支預力梁偏心距限制四控制條件
* [RC-2015-4](problems/RC-2015-4.md) — 後拉法拋物線腱端部無偏心四控制條件
* [RC-2020-4](problems/RC-2020-4.md) — 預力連續梁一致腱二次彎矩等效載重法
* [RC-2024-4](problems/RC-2024-4.md) — 等效載重法拋物線腱次彎矩 C 線
* [RC-2025-4](problems/RC-2025-4.md) — 偏心距限制傳遞階段使用階段核心距

### RC-U4-3 預力損失

* [RC-2002-5](problems/RC-2002-5.md) — 後拉法摩擦損失連續梁兩端張拉
* [RC-2005-5](problems/RC-2005-5.md) — 直線型曲線型鋼腱等效載重法載重能力比較
* [RC-2016-4](problems/RC-2016-4.md) — 先拉法彈性縮短損失初施預力斷面應力分析
* [RC-2017-4](problems/RC-2017-4.md) — 論述題先拉法後拉法即時損失時間相關損失
* [RC-2019-4](problems/RC-2019-4.md) — 後拉法摩擦損失拋物線腱雙腱施拉

### RC-U4-4 預力梁剪力分析與設計

* [RC-2022-3](problems/RC-2022-3.md) — 預力梁腹剪裂縫 Vcw PCI 形梁垂直地震力
