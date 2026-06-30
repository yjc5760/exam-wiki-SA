# exam-wiki-RC — 操作指令手冊（Runbook）

> **適用環境：** Cowork（直接在對話中說出指令即可）
> **不適用：** 此檔案不需要 Claude Code 終端機；Cowork 承接所有指令
> **格式與命名規範：** 見 CLAUDE-SPEC.md

---

## 指令索引

### 📦 wiki 編譯與維護

| 指令 | 觸發語句 | 用途 |
|------|---------|------|
| [INGEST](#ingest) | `ingest RC-XXXX-N` | 將一道已驗證題目寫入 wiki |
| [COMPILE-ALL](#compile-all) | `compile all` | 從零初始化整個 wiki |
| [LINT](#lint) | `lint wiki` | 健檢 wiki 完整性（16 項） |
| [STATUS](#status) | `status` | 查看驗證進度與統計 |
| [REINDEX](#reindex) | `reindex` | 掃描 solutions/，修正 hasSolution 不一致 |
| [ADD-CONCEPT](#add-concept) | `add concept [概念名]` | 新增概念到 concepts.json |
| [ADD-METHOD](#add-method) | `add method [方法名]` | 新增解題方法論頁面 |
| [REFRESH-DASHBOARD](#refresh-dashboard) | `更新儀表板資料` | 從 question_index.json 重新生成 dashboard-data.js |

### 📊 備考分析類

| 指令 | 觸發語句 | 用途 |
|------|---------|------|
| [FREQUENCY](#frequency) | `frequency` | 統計各考點歷年出現次數 |
| [ANALYZE](#analyze) | `analyze YYYY` | 分析某年考卷考點分布 |
| [PREDICT](#predict) | `predict` | 推測今年最可能出現的考點 |
| [STUDY](#study) | `study RC-UN` | 彙整某單元所有題目與重點 |

### 🔍 查詢快捷類

| 指令 | 觸發語句 | 用途 |
|------|---------|------|
| [FIND](#find) | `find [關鍵字]` | 快速搜尋含某關鍵字的題目 |
| [RELATED](#related) | `related RC-XXXX-N` | 找出與某題考點相似的其他題目 |
| [UNVERIFIED](#unverified) | `unverified` | 列出所有有解析但尚未驗證的題目 |
| [QUERY](#query) | 直接提問 | 自由查詢知識庫 |

---

## INGEST

**觸發語句：** `ingest RC-2018-1`（Cowork 直接執行）

**前置檢查（強制）：**
```
1. 讀取 raw/json/question_index.json
2. 找到 moduleId = "RC-2018-1" 的條目
3. 檢查 verificationStatus：
   - "verified"     → 繼續執行
   - "unverified"   → 停止，提示：「請人工驗證後將狀態改為 verified」
   - "needs-review" → 停止，提示：「此題標記為需複查，請確認後再 ingest」
```

**執行步驟：**
```
1. 讀取 raw/solutions/RC-XXXX-N/RC-XXXX-N.md
2. 讀取 raw/json/question_index.json 中該題的完整條目
   → 取得 primaryTopicId、secondaryTopicIds、designMethod、tags、hasViz
3. 掃描 raw/solutions/RC-XXXX-N/ 下的所有附屬檔案：
   → *-fig-*.png、*-chart-*.png、*-eqn-*.png（靜態截圖）
   → *-hand-*.png（手寫補充）
   → *-pm-viz.html、*-sfd-bmd-viz.html 等（互動圖）
4. 建立或更新 wiki/problems/RC-XXXX-N.md
5. 從 .md 萃取涉及的概念 → 更新 wiki/concepts/ 相關頁面的「出現題目」表格
6. 從 .md 萃取涉及的陷阱 → 更新 wiki/traps/ 相關頁面的「出現題目」表格
7. 更新 wiki/index.md（主分類和副分類下都加入此題連結）
8. 更新 wiki/by-year.md（對應年份加入此題）
9. 在 wiki/log.md 追加紀錄
```

**錯誤更正流程：**
```
① 對 Cowork 說：「將 RC-XXXX-N 的 verificationStatus 改為 needs-review」
② 對 Cowork 說：在 raw/solutions/RC-XXXX-N/RC-XXXX-N.md 末尾補充更正說明
③ 人工重新驗算確認後：「將 RC-XXXX-N 的 verificationStatus 改回 verified」
④ 對 Cowork 說：ingest RC-XXXX-N
```

---

## COMPILE-ALL

**觸發語句：** `compile all`（Cowork 直接執行）

**執行步驟：**
```
1. 讀取 raw/json/concepts.json → 生成 wiki/concepts/[id].md
2. 讀取 raw/solutions/methods/ → 生成 wiki/methods/[method-id].md
3. 讀取 raw/json/question_index.json
   → 只處理 verificationStatus = "verified" 的題目
   → 生成 wiki/problems/[moduleId].md
4. 生成 wiki/index.md（依 RC 命題大綱分類）
5. 生成 wiki/by-year.md（依考年分類）
6. 建立 wiki/queries/（若不存在）
7. 【注意】以下五個目錄不由 compile-all 生成，勿覆蓋：
   wiki/diagnosis/ · wiki/failure-modes/ · wiki/materials/ · wiki/code-ref/ · wiki/queries/
8. 在 wiki/log.md 追加 compile-all 紀錄
```

---

## LINT

**觸發語句：** `lint wiki`（Cowork 直接執行）

**檢查項目：**
```
1.  孤立頁面（無任何其他頁面連結）
2.  斷開連結（[[id]] 但對應頁面不存在）
3.  概念缺口（concepts.json 有 related_concept_ids 但頁面未建立）
4.  手寫補充未登錄（raw/solutions/ 有 hand-*.png 但 problems/ 頁面未標注）
5.  圖形未登錄（raw/solutions/ 有 *-viz.html 但 problems/ 頁面無圖形區塊）
6.  P-M 圖缺口（RC-U1-2/RC-U1-4 柱設計題目但無 pm-viz.html）
7.  方法論缺口（raw/solutions/methods/ 有資料夾但 wiki/methods/ 無對應頁面）
8.  圖片圖說缺漏（.md 中有 ![...](*.png) 但下方無 *圖說：* 的題目）
9.  eqn.png 圖說未文字化（有 *-eqn.png 但圖說未包含公式 LaTeX）
10. by-year.md 與 question_index.json 的題目數是否一致
11. 標籤缺口：hasSolution=true 但 tags 少於 3 個的題目
12. queries/ 頁面中的斷開連結
13. diagnosis/ 缺口（wiki/index.md 列出的題型但 diagnosis/ 無對應頁面）
14. failure-modes/ 缺口（五大類別頁面是否齊全：彎曲/剪力/壓碎/撓度/裂縫）
15. materials/ 缺口（四大主題頁面是否齊全）
16. 輸出待補清單，依優先順序排列
```

---

## STATUS

**觸發語句：** `status`（Cowork 直接執行）

**輸出格式：**
```
讀取 raw/json/question_index.json，輸出：

驗證進度：X / 總題數
✅ verified   (X題)：[列出題號]
⚠️ needs-review (X題)：[列出題號]
❌ unverified (X題)：[依年份分組列出]

solutions/ 已有解析但未驗證：[列出題號]
已 verified 但尚無 solutions/ 資料夾：[列出題號]

標籤統計（前10常見標籤）：
[標籤] : X 題
```

---

## REINDEX

**觸發語句：** `reindex`（Cowork 直接執行）

**用途：** 當 `raw/solutions/` 下的資料夾與 `question_index.json` 的 `hasSolution` 欄位不一致時（如手動新增了資料夾但忘記更新索引），用此指令自動修正。

**執行步驟：**
```
1. 掃描 raw/solutions/ 下所有子資料夾（格式：RC-YYYY-N）
2. 對每個資料夾，確認是否有對應的 .md 主解析檔
3. 與 question_index.json 比對 hasSolution 欄位：
   - 資料夾存在且有 .md → hasSolution 應為 true
   - 資料夾不存在或無 .md → hasSolution 應為 false
4. 輸出差異報告，詢問是否修正
5. 確認後批次更新 question_index.json
```

---

## ADD-CONCEPT

**觸發語句：** `add concept [概念名]`（例：`add concept 開裂彎矩`）

**用途：** 在 `raw/json/concepts.json` 新增一個概念條目，並建立對應的 `wiki/concepts/[id].md`。

**執行步驟：**
```
1. 詢問概念的基本資訊：
   - concept_id（建議格式：RC-C-XXX）
   - 中文名稱、英文名稱
   - 所屬單元（RC-UN-n）
   - 簡短定義（1-2句）
   - 相關概念 related_concept_ids（可留空）
2. 寫入 raw/json/concepts.json
3. 建立 wiki/concepts/[id].md（含定義、公式、相關題目表格）
4. 在 wiki/log.md 追加紀錄
```

---

## ADD-METHOD

**觸發語句：** `add method [方法名]`（例：`add method Whitney應力塊法`）

**用途：** 在 `raw/solutions/methods/` 新增一個解題方法論文件，並建立 `wiki/methods/[id].md`。

**執行步驟：**
```
1. 詢問方法論基本資訊：
   - method_id（建議格式：RC-M-XXX）
   - 適用題型、適用規範條文
   - 核心公式、步驟摘要
2. 建立 raw/solutions/methods/[method_id]/[method_id].md
3. 建立 wiki/methods/[method_id].md
4. 在 wiki/log.md 追加紀錄
```

---

## REFRESH-DASHBOARD

**觸發語句：** `更新儀表板資料`（Cowork 直接執行）

**用途：** `dashboard.html`（資料夾根目錄的離線儀表板）讀取 `dashboard-data.js` 顯示題庫。當 `question_index.json` 變動（新增題目、改標籤）後，需重新生成快照。

**執行步驟：**
```
1. 讀取 raw/json/question_index.json 全部條目
2. 轉換為精簡陣列格式寫入 dashboard-data.js：
   [moduleId, primaryTopicId縮寫(去RC-前綴), secondaryTopicIds縮寫, designMethod, viz檔名前綴陣列, tags]
   - viz 前綴：掃描 raw/solutions/RC-XXXX-N/ 下 *-viz.html，
     取檔名中 moduleId 與 -viz.html 之間的字段（如 pm、section）
   - ⚠ PDF 補充筆記（*.pdf）不納入 dashboard-data.js；
     dashboard.html 透過「📎 掃描補充 PDF」按鈕以 File System Access API 即時掃描
3. 讀取 `raw/json/syllabus_taxonomy.json`，提取出 `subject.id === "RC"` 的分類樹，並自動轉換成 `window.RC_TOPICS` 與 `window.RC_UNITS` 寫入 `dashboard-data.js` 中。
4. 在 wiki/log.md 追加紀錄
注意：dashboard.html 本身不需改動；僅當需求變更時才修改 UI。
```

**補充說明：補充筆記 PDF**
- 使用者可將任意 `.pdf` 檔案放入 `raw/solutions/RC-YYYY-N/` 資料夾
- dashboard.html 題庫瀏覽頁有工具列按鈕「📎 掃描補充 PDF」
  - 首次點擊：觸發 File System Access API 授權視窗，選取專案根目錄後自動掃描
  - 有 PDF 的題目卡片會出現「📎 補充筆記 PDF」按鈕；無 PDF 者不顯示
  - 掃描結果快取於頁面記憶體，重新授權後可重新掃描（按鈕文字顯示找到的 PDF 題目數）
- REFRESH-DASHBOARD 不需掃描 PDF，無需更新 dashboard-data.js

---

## FREQUENCY

**觸發語句：** `frequency`（Cowork 直接執行）

**用途：** 統計各 topicId（命題考點）在歷年考題中的出現次數，協助識別高頻考點、準備備考重點。

**輸出格式：**
```
讀取 question_index.json 所有條目，統計 primaryTopicId 與 secondaryTopicIds：

【高頻考點 Top 10】
RC-U1-1 RC 梁彎矩強度分析與設計：X 題（主：X 題，副：X 題）
RC-U2-1 RC 剪力強度分析與設計：X 題
...

【各單元命題比例】
RC-U1（梁/柱基本）：XX%
RC-U2（剪力/扭力/錨定）：XX%
RC-U3（工作性）：XX%
RC-U4（預力）：XX%

【近5年趨勢】：[逐年考點列表]
```

---

## ANALYZE

**觸發語句：** `analyze YYYY`（例：`analyze 2018`）

**用途：** 深度分析某一年考卷的四道題目，輸出考點覆蓋、難度評估、與歷年的異同。

**輸出格式：**
```
【RC-YYYY 考卷分析】

題號 | 主考點      | 副考點    | 設計法 | 難度 | 解析狀態
-----|------------|----------|--------|------|--------
1   | RC-U2-2 扭力 | RC-U2-1 | USD   | ★★★  | ✅ verified
...

【本年特色】：...
【與前一年比較】：...
【建議複習重點】：...
```

---

## PREDICT

**觸發語句：** `predict`（Cowork 直接執行）

**用途：** 根據歷年出題頻率與近年趨勢，推測今年（或下次考試）最可能出現的考點組合。

**執行步驟：**
```
1. 讀取 question_index.json 所有條目
2. 計算各 topicId 近10年、近5年、近3年的出題頻率
3. 找出「長期未考但高頻」的考點（潛在補考點）
4. 找出「連續出現」的高頻考點（持續重點）
5. 考慮四題的搭配慣例（通常各單元各一題）
6. 輸出預測報告與建議複習清單
```

---

## STUDY

**觸發語句：**
- `study RC-U2`（單元層級，Cowork 直接執行）
- `study RC-U1-1`（子項層級深度複習，Cowork 直接執行）

**用途：** 彙整某單元／子項所有考題、重點公式、常見陷阱，產生帶圖表的互動 HTML 複習導覽頁面，存入 `study/` 目錄。

**輸出格式：帶圖表的自含 HTML 檔案**（非純 Markdown，需使用 KaTeX 渲染公式）

### 單元層級（study RC-UN）頁面結構（六區塊）：
```
① 總覽（KPI 卡片 + 子項頻率橫條圖）
  - 4 個 KPI 卡：總題數、佔全科比例、排名、近6年出題率
  - 子項卡片（4個，點擊可過濾題目清單）
  - Canvas 橫向頻率條圖

② 年度熱力圖
  - 熱力格（每格=1年，深色=多題）
  - Canvas 年度堆疊長條圖（各子項不同顏色）

③ 考題清單（互動篩選）
  - 篩選按鈕（全部 + 各子項）
  - 每題顯示：題號/年度、題型摘要、關鍵 tags（前5個）、解析/互動圖/驗證狀態 icon
  - 【重要】點擊題號或標題時，必須以 `<a href="../index.html#md=raw/solutions/RC-XXXX-N/RC-XXXX-N.md&t=RC-XXXX-N" target="_blank">` 格式連結至 markdown 渲染器，確保公式能透過 KaTeX 呈現，且相對路徑的附圖（png）與補充檔（pdf）皆可正常載入。

④ 核心公式速查（KaTeX 渲染）
  - 每個子項一張公式卡，含主要計算公式與注意事項

⑤ 高頻陷阱 Top 8
  - 標色區分子項、附說明

⑥ 備考優先序
  - 表格：優先順序、掌握目標、備考要點
  - 整合備考策略說明框
```

### 子項層級（study RC-UN-n）頁面結構（七區塊）：
```
① 命題分析（KPI + 題型分類卡 + 年度堆疊長條圖 + 題型圓餅圖）
② 截面圖解（SVG 結構圖：三種梁型 / 柱型等）
③ 解題流程圖（SVG 決策樹）
④ 核心公式速查（KaTeX 分題型公式卡 + φ 值速查表）
⑤ 考題清單（互動篩選，依題型分色）
⑥ 高頻陷阱（考古題歸納，依題型標色）
⑦ 互動計算器（輸入截面參數 → 即時計算並繪製應變圖）
```

**資料來源：** `raw/json/question_index.json`（從中統計各子項題數、年度分布、tags）

**命名規則：**
- 單元層級：`study/study-RC-UN.html`（例：`study/study-RC-U1.html`）
- 子項層級：`study/study-RC-UN-n.html`（例：`study/study-RC-U1-1.html`）

---

## FIND

**觸發語句：** `find [關鍵字]`（例：`find 接頭剪力`、`find Whitney`）

**用途：** 快速搜尋 `raw/solutions/` 下所有 .md 檔案及 `question_index.json`，找出含有特定關鍵字的題目。

**輸出格式：**
```
搜尋「接頭剪力」，找到 X 筆結果：

RC-XXXX-N：[題型摘要]（出現位置：標題/tags/解析內容）
...
```

---

## RELATED

**觸發語句：** `related RC-XXXX-N`（例：`related RC-2018-2`）

**用途：** 根據 primaryTopicId、secondaryTopicIds、tags 的重疊程度，找出與指定題目最相關的其他題目，方便集中練習同類題型。

**輸出格式：**
```
【與 RC-XXXX-N 相關的題目】（依相似度排序）

★★★ RC-YYYY-N：[共同考點] [共同標籤X個]
★★☆ RC-YYYY-N：...
★☆☆ RC-YYYY-N：...
```

---

## UNVERIFIED

**觸發語句：** `unverified`（Cowork 直接執行）

**用途：** STATUS 指令的快捷版，只列出「已有解析但尚未驗算」的題目，方便追蹤待辦清單。

**輸出格式：**
```
【待驗算題目清單】（hasSolution=true 且 verificationStatus=unverified）

RC-2018-1：扭矩剪力箍筋設計
RC-2018-2：角柱接頭剪力強度
RC-2018-3：T形梁裂縫控制
RC-2018-4：後拉法預力梁
...

共 X 題待驗算。驗算完成後說：「將 RC-XXXX-N 的 verificationStatus 改為 verified」
```

---

## QUERY

**觸發語句：** 直接提問（自由格式）

**範例：**
- 「哪些題目考到 β₁ 折減？」
- 「RC-U4 預力共出了幾題？」
- 「2015 到 2020 年有哪些題目考剪力設計？」

查詢結果可存入 `wiki/queries/` 供日後參考（告訴 Cowork「請存檔」即可）。

---

## CHANGELOG

| 日期 | 變更 | 原因 |
|------|------|------|
| 2026-05-29 | 初版：設計為 Claude Code 終端機指令 | 原始三層架構設計 |
| 2026-06-04 | 全面改寫：所有指令改由 Cowork 直接執行 | 知識庫全程在 Cowork 運行，無獨立終端機環境 |
| 2026-06-04 | 新增 REINDEX、ADD-CONCEPT、ADD-METHOD、FREQUENCY、ANALYZE、PREDICT、STUDY、FIND、RELATED、UNVERIFIED 共 10 個指令 | 擴充備考分析與查詢快捷功能 |
| 2026-06-30 | 更新 STUDY 指令規格：考題連結必須指向 `raw/solutions/` 原始檔 | 確保 index.html#md 渲染引擎能正確讀取相對路徑的圖片與 PDF 附檔 |
