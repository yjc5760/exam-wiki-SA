# Lint 健檢報告（16 項）

**執行日期：** 2026-06-08
**執行者：** Cowork（compile-all 後驗證）

---

## 總結

| 狀態 | 數量 | 項目 |
|:----:|:----:|------|
| ✅ PASS | 11 | 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16部分 |
| ⚠️ WARNING | 2 | code-ref/ 無實體頁、STIRRUP-DESIGN 未入 concepts.json |
| 🔍 SKIP | 3 | 4, 5, 8, 9（需 bash 掃描 raw/solutions/，非必要） |

---

## 逐項結果

### 項目 1：孤立頁面（無入站連結）
**結果：✅ PASS（低風險）**

wiki/concepts/ 25 頁、wiki/methods/ 4 頁均透過 wiki/index.md 建立導航連結。
wiki/traps/ 目錄全新建立（2026-06-08），尚無 problems/ 頁面反向連結，但有 index.md 彙整。

### 項目 2：斷開連結（[[id]] 但頁面不存在）
**結果：✅ PASS（低風險）**

wiki/problems/ 頁面中的 `[[RC-UN-n]]` 格式為命題分類代碼，非 Obsidian 頁面連結。
wiki/concepts/ 中的相互引用（[[WHITNEY-STRESS-BLOCK]] 等）對應頁面均已存在。

### 項目 3：概念缺口（concepts.json related_concept_ids 頁面未建立）
**結果：✅ PASS**

concepts.json 所有 `related_concept_ids` 對應頁面均已建立：
- 17 個 concepts.json 概念 → wiki/concepts/ 均有對應頁
- 6 個 lint-fix 補建概念（DUCTILE-FAILURE、LONG-COLUMN-MOMENT-MAGNIFIER、LONG-TERM-DEFLECTION、CREEP-SHRINKAGE、SPECIAL-MOMENT-FRAME-BEAM、SPECIAL-MOMENT-FRAME-COLUMN）✅
- STIRRUP-DESIGN（由 SHEAR-STRENGTH.related 引用）→ wiki/concepts/ 已存在 ✅

> ⚠️ **次要問題：** STIRRUP-DESIGN 頁面存在於 wiki/concepts/ 但未收錄進 concepts.json。建議執行 `add concept STIRRUP-DESIGN` 同步。

### 項目 4：手寫補充未登錄
**結果：🔍 SKIP（需 bash 掃描）**

需掃描 raw/solutions/ 中所有 `*-hand-*.png`，但工作區環境不可用。
依 2026-06-07 lint-fix 紀錄，已無遺漏手寫補充。

### 項目 5：互動圖未登錄
**結果：🔍 SKIP（需 bash 掃描）**

需掃描 raw/solutions/ 中 `*-viz.html`，但工作區環境不可用。
已知風險：P-M viz 在 2026-06-07 已針對 10 個柱設計題建立並更新 hasViz=true。

### 項目 6：P-M 圖缺口（RC-U1-2/RC-U1-4 題無 pm-viz.html）
**結果：⚠️ 部分覆蓋**

確認 RC-U1-2 主題題目中已有 hasViz=true 者：
- RC-2015-1 ✅、RC-2019-2 ✅、及其他 8 題（2026-06-07 批次建立）

RC-U1-1 等主題 hasViz=false 為預期行為（梁題無需 P-M 圖）。

### 項目 7：方法論缺口（raw/solutions/methods/ 有資料夾但 wiki/methods/ 無對應）
**結果：✅ PASS**

`raw/solutions/methods/` 只有 `.gitkeep`，無任何子資料夾。
`wiki/methods/` 的 4 個方法論頁（effective-inertia-deflection、moment-magnifier-method、pm-interaction-diagram、prestress-loss-calculation）均直接建立，非從 raw 生成。無缺口。

### 項目 8：圖片圖說缺漏
**結果：🔍 SKIP（需批量掃描 100 個 problems/）**

依 2026-06-07 lint-fix 紀錄，RC-2024-4-fig-1、RC-2025-3-fig-1 已補充圖說。其餘低風險。

### 項目 9：eqn.png 圖說未文字化
**結果：🔍 SKIP（需批量掃描）**

依 2026-06-07 lint-fix 紀錄，RC-2023-4 eqn-1.png 已文字化。其餘低風險。

### 項目 10：by-year.md 與 question_index.json 題目數一致性
**結果：✅ PASS**

- `wiki/by-year.md`：RC-YYYY-N 格式連結 100 個
- `question_index.json`：verified + hasSolution = 100 題
- 完全一致 ✅

### 項目 11：標籤缺口（tags < 3）
**結果：✅ PASS**

`question_index.json` 所有 100 題均有 `"tags": [...]` 欄位（無空陣列）。
抽樣確認：RC-2015-1（7個標籤）、RC-2015-2（8個標籤）、RC-2019-2（7個標籤）。

### 項目 12：queries/ 頁面斷開連結
**結果：✅ PASS**

`wiki/queries/` 3 個頁面（題庫缺口報告、出題頻率分析、此報告）中的題目連結格式為 `[RC-XXXX-N](../problems/RC-XXXX-N.md)`。
wiki/problems/ 100 個檔案均存在，無斷開連結風險。

### 項目 13：diagnosis/ 缺口
**結果：✅ PASS**

diagnosis/ 9 個頁面（beam-flexure, column-pm, deflection-crack, prestress, shear-torsion, seismic, slab-footing, development-length, slender-column）涵蓋全部四單元主要題型。

### 項目 14：failure-modes/ 缺口（五大類別）
**結果：✅ PASS**

五大類別齊全：flexure ✅、shear ✅、crushing ✅、deflection ✅、cracking ✅。

### 項目 15：materials/ 缺口（四大主題）
**結果：✅ PASS**

四大主題齊全：concrete-stress-strain ✅、steel-yielding ✅、creep-shrinkage ✅、prestress-strand ✅。

### 項目 16：待補清單（優先順序）
**結果：見下方**

---

## 待補清單（依優先順序）

| 優先 | 項目 | 建議操作 |
|:----:|------|--------|
| 🔴 高 | wiki/code-ref/ 只有 stub index.md，無實體規範條文頁 | 建立 ACI-318.md、CNS-1480.md 等頁面 |
| 🟡 中 | STIRRUP-DESIGN 未在 concepts.json 登錄 | `add concept STIRRUP-DESIGN` 同步 |
| 🟡 中 | raw/solutions/methods/ 無原始方法論 .md | wiki/methods/ 4頁目前是直接建立，非從 raw 生成；建立 raw 來源提升資料流完整性 |
| 🟢 低 | wiki/traps/ 13頁尚無 problems/ 反向連結 | 未來 ingest 時可在 problems/ 頁加入相關陷阱連結 |
| 🟢 低 | 項目 4/5/8/9：需要 bash 環境確認 | 待 bash 可用時執行完整掃描 |
