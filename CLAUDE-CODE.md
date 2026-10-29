# exam-wiki-SA — 操作指令手冊（Runbook）

> **適用環境：** Cowork（直接在對話中說出指令即可）
> **不適用：** 此檔案不需要 Claude Code 終端機；Cowork 承接所有指令
> **格式與命名規範：** 見 CLAUDE-SPEC.md

---

## 指令索引

### 📦 wiki 編譯與維護

| 指令 | 觸發語句 | 用途 |
|------|---------|------|
| [INGEST](#ingest) | `ingest SA-XXXX-N` | 將一道已驗證題目寫入 wiki |
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
| [STUDY](#study) | `study SA-UN` | 彙整某單元所有題目與重點 |

### 🔍 查詢快捷類

| 指令 | 觸發語句 | 用途 |
|------|---------|------|
| [FIND](#find) | `find [關鍵字]` | 快速搜尋含某關鍵字的題目 |
| [RELATED](#related) | `related SA-XXXX-N` | 找出與某題考點相似的其他題目 |
| [UNVERIFIED](#unverified) | `unverified` | 列出所有有解析但尚未驗證的題目 |
| [QUERY](#query) | 直接提問 | 自由查詢知識庫 |

---

## INGEST

**觸發語句：** `ingest SA-2018-1`（Cowork 直接執行）

**前置檢查（強制）：**
```
1. 讀取 raw/json/question_index.json
2. 找到 moduleId = "SA-2018-1" 的條目
3. 檢查 verificationStatus：
   - "verified"     → 繼續執行
   - "unverified"   → 停止，提示：「請人工驗證後將狀態改為 verified」
   - "needs-review" → 停止，提示：「此題標記為需複查，請確認後再 ingest」
```

**執行步驟：**
```
1. 讀取 raw/solutions/SA-XXXX-N/SA-XXXX-N.md
2. 讀取 raw/json/question_index.json 中該題的完整條目
   → 取得 primaryTopicId、secondaryTopicIds、tags、hasViz
3. 掃描 raw/solutions/SA-XXXX-N/ 下的所有附屬檔案：
   → *-fig-*.png、*-chart-*.png、*-eqn-*.png（靜態截圖）
   → *-hand-*.png（手寫補充）
   → *-sfd-bmd-viz.html、*-influence-line-viz.html 等（互動圖）
4. 建立或更新 wiki/problems/SA-XXXX-N.md
5. 從 .md 萃取涉及的概念 → 更新 wiki/concepts/ 相關頁面的「出現題目」表格
6. 從 .md 萃取涉及的陷阱 → 更新 wiki/traps/ 相關頁面的「出現題目」表格
7. 更新 wiki/index.md（主分類和副分類下都加入此題連結）
8. 更新 wiki/by-year.md（對應年份加入此題）
9. 在 wiki/log.md 追加紀錄
```

**錯誤更正流程：**
```
① 對 Cowork 說：「將 SA-XXXX-N 的 verificationStatus 改為 needs-review」
② 對 Cowork 說：在 raw/solutions/SA-XXXX-N/SA-XXXX-N.md 末尾補充更正說明
③ 人工重新驗算確認後：「將 SA-XXXX-N 的 verificationStatus 改回 verified」
④ 對 Cowork 說：ingest SA-XXXX-N
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
4. 生成 wiki/index.md（依 SA 命題大綱分類）
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
6.  SFD/BMD 圖缺口（SA-U1-2 靜定結構分析題目但要求繪圖卻無 sfd-bmd-viz.html）
7.  方法論缺口（raw/solutions/methods/ 有資料夾但 wiki/methods/ 無對應頁面）
8.  圖片圖說缺漏（.md 中有 ![...](*.png) 但下方無 *圖說：* 的題目）
9.  eqn.png 圖說未文字化（有 *-eqn.png 但圖說未包含公式 LaTeX）
10. by-year.md 與 question_index.json 的題目數是否一致
11. 標籤缺口：hasSolution=true 但 tags 少於 3 個的題目
12. queries/ 頁面中的斷開連結
13. diagnosis/ 缺口（wiki/index.md 列出的題型但 diagnosis/ 無對應頁面）
14. failure-modes/ 缺口（主要類別頁面是否齊全：符號錯誤/邊界條件/自由度/公式應用/收斂問題）
15. materials/ 缺口（材料特性主題頁面是否齊全）
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

**用途：** 當 `raw/solutions/` 下的資料夾與 `question_index.json` 的 `hasSolution` 欄位不一致時，用此指令自動修正。

**執行步驟：**
```
1. 掃描 raw/solutions/ 下所有子資料夾（格式：SA-YYYY-N）
2. 對每個資料夾，確認是否有對應的 .md 主解析檔
3. 與 question_index.json 比對 hasSolution 欄位：
   - 資料夾存在且有 .md → hasSolution 應為 true
   - 資料夾不存在或無 .md → hasSolution 應為 false
4. 輸出差異報告，詢問是否修正
5. 確認後批次更新 question_index.json
```

---

## ADD-CONCEPT

**觸發語句：** `add concept [概念名]`（例：`add concept 彎矩分配法分配因子`）

**用途：** 在 `raw/json/concepts.json` 新增一個概念條目，並建立對應的 `wiki/concepts/[id].md`。

**執行步驟：**
```
1. 詢問概念的基本資訊：
   - concept_id（建議格式：SA-C-XXX）
   - 中文名稱、英文名稱
   - 所屬單元（SA-UN-n）
   - 簡短定義（1-2句）
   - 相關概念 related_concept_ids（可留空）
2. 寫入 raw/json/concepts.json
3. 建立 wiki/concepts/[id].md（含定義、公式、相關題目表格）
4. 在 wiki/log.md 追加紀錄
```

---

## ADD-METHOD

**觸發語句：** `add method [方法名]`（例：`add method 傾角變位法`）

**用途：** 在 `raw/solutions/methods/` 新增一個解題方法論文件，並建立 `wiki/methods/[id].md`。

**執行步驟：**
```
1. 詢問方法論基本資訊：
   - method_id（建議格式：SA-M-XXX）
   - 適用題型、適用單元
   - 核心公式、步驟摘要
2. 建立 raw/solutions/methods/[method_id]/[method_id].md
3. 建立 wiki/methods/[method_id].md
4. 在 wiki/log.md 追加紀錄
```

---

**修正既有方法論的公式錯誤（FIX-METHOD）**

`raw/solutions/methods/` 是規則 1 的例外，發現公式／係數／單位錯誤時可直接修正來源：

```
1. 驗算：邊界代入、量綱檢查、與 verified 題目解答交叉比對
   （只憑印象或單一參考書就改 = 不合格）
2. 改 raw/solutions/methods/[id]/[id].md
3. cp 覆蓋 wiki/methods/[id].md（不可只改 wiki，compile-all 會蓋回）
4. 全庫 grep 同一個錯誤係數，其他頁面一併修正
5. wiki/log.md 追加紀錄：改了什麼、為什麼、怎麼驗證的
```

> **單位是最常見的錯誤來源**。同一條規範式在不同單位制下係數完全不同，
> 抄書時很容易把 A 制的係數配上 B 制的單位標註。
> **撰寫方法論頁時，係數一律附上單位制標註，並盡量同時給出無因次形式。**

---

## REFRESH-DASHBOARD

**觸發語句：** `更新儀表板資料`（Cowork 直接執行）

**用途：** `index.html`（資料夾根目錄的離線儀表板）讀取 `dashboard-data.js` 顯示題庫。當 `question_index.json` 變動（新增題目、改標籤）後，需重新生成快照。

**執行步驟：**
```
1. 讀取 raw/json/question_index.json 全部條目
2. 轉換為精簡陣列格式寫入 dashboard-data.js：
   [moduleId, primaryTopicId縮寫(去SA-前綴), secondaryTopicIds縮寫, viz檔名前綴陣列, tags, pdf補充筆記檔名陣列]
   - viz 前綴：掃描 raw/solutions/SA-XXXX-N/ 下 *-viz.html，
     取檔名中 moduleId 與 -viz.html 之間的字段（如 sfd-bmd、influence-line）
   - pdf 補充筆記：掃描 raw/solutions/SA-XXXX-N/ 下所有 *.pdf，取原始檔名（含副檔名）存入陣列；
     無 PDF 的題目寫入空陣列 []
3. 讀取 `raw/json/syllabus_taxonomy.json`，提取出 `subject.id === "SA"` 的分類樹，並自動轉換成 `window.SA_TOPICS` 與 `window.SA_UNITS` 寫入 `dashboard-data.js` 中。
4. 在 wiki/log.md 追加紀錄
注意：index.html 本身不需改動；僅當需求變更時才修改 UI。
```

**補充說明：補充筆記 PDF**
- 使用者可將任意 `.pdf` 檔案放入 `raw/solutions/SA-YYYY-N/` 資料夾，命名無強制規範
- PDF 檔名清單由 REFRESH-DASHBOARD 指令掃描並寫入 dashboard-data.js（q.pdf 欄位），不再於前端即時掃描資料夾
- index.html 題庫瀏覽頁會依 dashboard-data.js 資料，對有 PDF 的題目卡片直接顯示「📎 補充筆記 PDF」按鈕；無 PDF 者不顯示
- 使用者新增或移除 PDF 後，需對 Cowork 說「更新儀表板資料」才會反映在按鈕上

---

## FREQUENCY

**觸發語句：** `frequency`（Cowork 直接執行）

**用途：** 統計各 topicId（命題考點）在歷年考題中的出現次數，協助識別高頻考點、準備備考重點。

**輸出格式：**
```
讀取 question_index.json 所有條目，統計 primaryTopicId 與 secondaryTopicIds：

【高頻考點 Top 10】
SA-U2-3 靜不定結構之傾角變位法：X 題（主：X 題，副：X 題）
SA-U2-5 彎矩分配法：X 題
...

【各單元命題比例】
SA-U1（靜定結構分析）：XX%
SA-U2（靜不定結構分析）：XX%
SA-U3（建築結構系統）：XX%

【近5年趨勢】：[逐年考點列表]
```

---

## ANALYZE

**觸發語句：** `analyze YYYY`（例：`analyze 2018`）

**用途：** 深度分析某一年考卷的題目，輸出考點覆蓋、難度評估、與歷年的異同。

**輸出格式：**
```
【SA-YYYY 考卷分析】

題號 | 主考點           | 副考點    | 難度 | 解析狀態
-----|-----------------|----------|------|--------
1   | SA-U2-5 彎矩分配法 | SA-U2-3 | ★★★  | ✅ verified
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
5. 考慮各題的搭配慣例（通常各單元各出題）
6. 輸出預測報告與建議複習清單
```

---

## STUDY

**觸發語句：**
- `study SA-U2`（單元層級，Cowork 直接執行）
- `study SA-U1-2`（子項層級 → 單元總覽 `study/unit-SA-U1-2.html`，Cowork 直接執行）

**用途：** 彙整某單元／子項所有考題、重點公式、常見陷阱，產生帶圖表的互動 HTML 複習導覽頁面，存入 `study/` 目錄。

**輸出格式：帶圖表的自含 HTML 檔案**（非純 Markdown，需使用 KaTeX 渲染公式）

### 單元層級（study SA-UN）頁面結構（六區塊）：
```
① 總覽（KPI 卡片 + 子項頻率橫條圖）
  - 4 個 KPI 卡：總題數、佔全科比例、排名、近6年出題率
  - 子項卡片（點擊可過濾題目清單）
  - Canvas 橫向頻率條圖

② 年度熱力圖
  - 熱力格（每格=1年，深色=多題）
  - Canvas 年度堆疊長條圖（各子項不同顏色）

③ 考題清單（互動篩選）
  - 篩選按鈕（全部 + 各子項）
  - 每題顯示：題號/年度、題型摘要、關鍵 tags（前5個）、解析/互動圖/驗證狀態 icon
  - 【重要】點擊題號或標題時，必須以 `<a href="../index.html#md=raw/solutions/SA-XXXX-N/SA-XXXX-N.md&t=SA-XXXX-N" target="_blank">` 格式連結至 markdown 渲染器，確保公式能透過 KaTeX 呈現，且相對路徑的附圖（png）與補充檔（pdf）皆可正常載入。

④ 核心公式速查（KaTeX 渲染）
  - 每個子項一張公式卡，含主要計算公式與注意事項

⑤ 高頻陷阱 Top 8
  - 標色區分子項、附說明

⑥ 備考優先序
  - 表格：優先順序、掌握目標、備考要點
  - 整合備考策略說明框
```

**單元層級命名：** `study/study-SA-UN.html`（例：`study/study-SA-U2.html`）；資料來源 `raw/json/question_index.json`。

### 子項層級（study SA-UN-n）→ 單元總覽 `study/unit-SA-UN-n.html`

> 2026-10-29 起，子項層級只產一頁「單元總覽」，取代舊的 `study-SA-UN-n.html`（命題分析）與
> `formula-given-SA-UN-n.html`（主要公式給／背分界）兩頁；舊檔名保留為轉址頁。
> 原理與圖解仍在 `lecture-SA-UN-n.html`（觀念講義），兩者並列。

**頁面結構（四節）：**
```
頂端　定位列：全科排名、主＋副題數、有出題考年、近 6 考年（全由索引算出）＋連到全科熱圖
一、這單元考什麼：考點群卡片（點了篩第三節）、前後段考點漂移＋年度堆疊圖、題型走向、
　　命題風險排序（每列附「這類題的門票」公式標籤）
二、公式給／背：判定方法、三級圖例、公式卡（回想模式；卡底列「考了卻沒給」的題號）、
　　逐年證據表（可展開）、背誦策略
三、考題總表：主＋副逐題一列——題型、考點群、題解用到的公式標籤（紅／橘＝要背、
　　綠框＝當年有印、綠底＝給數值）、解析頁／影片／互動圖連結；可依考點群、主副、公式篩選
四、只剩三天
```

**資料流（單一事實來源）：**
```
study/data/unit-SA-UN-n.json        ← 唯一需要維護的資料：考點群、逐題用到哪幾條公式（Q[].f）、
                                       公式卡（F[]，含 ok＝考卷印出的年份）、逐年備註、文字段落
raw/json/question_index.json        ← 題數、主副考點、排名、viz、verified 一律由此計算
解題過程影片/<題號>/video/*.mp4       ← 有影片就加 🎬
        ↓  python scripts/build_unit_page.py SA-UN-n   （或 --all；--check 只檢查不寫檔）
study/unit-SA-UN-n.html             ← 產出；請勿手改
```
- 卡片上的「考了卻沒給」題號、逐年表的 ✗、第三節的公式標籤，**全部由 `Q[].f` 推出**，三處不會再對不上。
- 「用到」的判定標準：**該題題解實際寫出或套用了這條式子**才算（「也可用」不算）。
- 腳本會檢查：資料檔題目集合＝索引中本子項的主＋副考點題；公式索引不越界；給數值類必須在逐年表最後一欄。
  索引改分類（主／副考點異動）後，先跑 `--check`，依錯誤訊息補刪 `Q[]` 再產生。
- PDF（`unit-SA-UN-n.pdf`）用瀏覽器列印或 Playwright `page.pdf()` 產生；列印時逐年證據表會自動展開。

---

## FIND

**觸發語句：** `find [關鍵字]`（例：`find 彎矩分配`、`find 影響線`）

**用途：** 快速搜尋 `raw/solutions/` 下所有 .md 檔案及 `question_index.json`，找出含有特定關鍵字的題目。

**輸出格式：**
```
搜尋「彎矩分配」，找到 X 筆結果：

SA-XXXX-N：[題型摘要]（出現位置：標題/tags/解析內容）
...
```

---

## RELATED

**觸發語句：** `related SA-XXXX-N`（例：`related SA-2018-2`）

**用途：** 根據 primaryTopicId、secondaryTopicIds、tags 的重疊程度，找出與指定題目最相關的其他題目，方便集中練習同類題型。

**輸出格式：**
```
【與 SA-XXXX-N 相關的題目】（依相似度排序）

★★★ SA-YYYY-N：[共同考點] [共同標籤X個]
★★☆ SA-YYYY-N：...
★☆☆ SA-YYYY-N：...
```

---

## UNVERIFIED

**觸發語句：** `unverified`（Cowork 直接執行）

**用途：** STATUS 指令的快捷版，只列出「已有解析但尚未驗算」的題目，方便追蹤待辦清單。

**輸出格式：**
```
【待驗算題目清單】（hasSolution=true 且 verificationStatus=unverified）

SA-2018-1：三跨連續梁傾角變位法
SA-2018-2：桁架影響線分析
...

共 X 題待驗算。驗算完成後說：「將 SA-XXXX-N 的 verificationStatus 改為 verified」
```

---

## QUERY

**觸發語句：** 直接提問（自由格式）

**範例：**
- 「哪些題目考到彎矩分配法？」
- 「SA-U2 靜不定結構共出了幾題？」
- 「2015 到 2020 年有哪些題目考傾角變位法？」

查詢結果可存入 `wiki/queries/` 供日後參考（告訴 Cowork「請存檔」即可）。

---

## CHANGELOG

| 日期 | 變更 | 原因 |
|------|------|------|
| 2026-07-02 | 從 exam-wiki-RC 克隆改寫，全面替換為 SA 科目 | 建立結構學獨立知識庫 |
| 2026-10-29 | STUDY 子項層級改為「單元總覽」`unit-SA-UN-n.html`（`scripts/build_unit_page.py` ＋ `study/data/unit-SA-UN-n.json`），取代命題分析與給／背分界兩頁 | 兩頁逐年列同一批題目、出題概況又與全科熱圖重複；逐題標公式用途後才發現舊給／背頁的年份證據有多處錯誤 |
