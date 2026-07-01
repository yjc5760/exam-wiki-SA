# 結構工程技師考試知識庫 — 鋼筋混凝土設計與預力（RC）

> 科目代碼：RC｜資料夾：`exam-wiki-RC`｜其他科目另建獨立資料庫

## 專案說明

本資料庫專門收錄「專門職業及技術人員高等考試結構工程技師」**第三科：鋼筋混凝土設計與預力**的考古題解析知識庫。

- **科目代碼：** RC（Reinforced Concrete Design and Prestress）
- **題目編號格式：** RC-YYYY-N（如 RC-2015-1）
- **其他科目：** 各自建立獨立資料庫（exam-wiki-SS、exam-wiki-SM 等）

**核心工作流程：**
```
在 Cowork 開啟 exam-wiki-RC/ 資料夾（Project）
    ↓
說：「解析 XXXX 年考卷」
Cowork 讀取 CLAUDE.md + 考卷 PDF + question_index.json
  → 建立所有尚無解析的題目資料夾（已有解析者跳過）
  → 提醒你將各題附圖截圖存入對應資料夾
  → 等待你通知「截圖完成，請開始解題」
    ↓
【你做】依提醒截圖存檔，完成後告知 Cowork
    ↓
【重要】Cowork 一次只解一題，解完存檔後再繼續下一題
    ↓
你加入補充截圖（chart/eqn/hand）
請 Cowork 更新 question_index.json（tags、verified）
    ↓
說：「ingest RC-XXXX-N」→ Cowork 直接執行，wiki 自動更新
```

---

## 兩個環境分工

| 環境 | 負責什麼 |
|------|---------|
| **你（使用者）** | PDF 題目附圖截圖（fig-N.png）、chart/eqn/hand 補充截圖、人工驗算後通知 Cowork 更新 verificationStatus |
| **Cowork** | 解題（SOLVE，**一次一題**）、存檔（.md + viz.html）、更新 question_index.json、**所有 wiki 操作指令**（ingest / compile-all / lint / status / reindex / add-concept / add-method / refresh-dashboard / frequency / analyze / predict / study / find / related / unverified / query，共 16 個，詳見 CLAUDE-CODE.md）、直接維護 wiki/diagnosis/ · wiki/failure-modes/ · wiki/materials/ · wiki/code-ref/ · wiki/queries/ · study/（study 指令輸出） |

---

## 單向資料流

```
raw/solutions/RC-XXXX-N/RC-XXXX-N.md  ──→  wiki/problems/      （Cowork: ingest）
raw/json/concepts.json                 ──→  wiki/concepts/      （Cowork: compile-all）
raw/solutions/methods/                 ──→  wiki/methods/       （Cowork: compile-all）
Cowork 查詢結果                        ──→  wiki/queries/       （Cowork 直接存入）
Cowork study 指令輸出                  ──→  study/              （Cowork 直接存入）
Cowork 跨層知識工具                    ──→  wiki/diagnosis/     （Cowork 直接存入）
                                       ──→  wiki/failure-modes/ （Cowork 直接存入）
                                       ──→  wiki/materials/     （Cowork 直接存入）
                                       ──→  wiki/code-ref/      （Cowork 直接存入）

解題內容唯一來源：raw/solutions/ 下的 .md 檔案
索引資訊唯一來源：raw/json/question_index.json
wiki/queries/、study/（study 輸出）及四個跨層知識目錄：由 Cowork 直接寫入，不走 ingest 流程
```

---

## 資料夾結構

```
exam-wiki-RC/
├── README.md                        ← 冷啟動快速導覽
├── CLAUDE.md                        ← 本檔（身份層：分工、資料流、重要規則）
├── CLAUDE-SOLVE.md                  ← Cowork 解題 Skill
├── CLAUDE-CODE.md                   ← Claude Code 操作指令（Runbook）
├── CLAUDE-SPEC.md                   ← 規格驗證層（格式、命名、完成標準）
│
├── study/                           ← 讀書筆記、講義、study 指令 HTML 輸出（study-RC-UN.html / study-RC-UN-n.html）
│
├── raw/                             ← 所有原始資料（唯讀，絕對不可修改）
│   ├── exams/                       ← 原始考卷 PDF（命名：RC-YYYY_鋼筋混凝土設計與預力.pdf）
│   ├── json/
│   │   ├── concepts.json            ← 概念定義（供 compile-all）
│   │   └── question_index.json      ← ⭐ 題目總索引（唯一需要人工維護的 JSON）
│   └── solutions/                   ← AI 解析 + 補充截圖（每題一個資料夾）
│       ├── RC-YYYY-N/
│       │   ├── RC-YYYY-N.md
│       │   ├── RC-YYYY-N-fig-1.png
│       │   ├── RC-YYYY-N-[內容碼]-viz.html
│       │   └── *.pdf                    ← 補充筆記（選用，命名無限制）
│       └── methods/                 ← 解題方法論
│
└── wiki/                            ← 知識庫輸出
    ├── index.md                     ← 主導航（七層架構）
    ├── by-year.md                   ← 依考年分類
    ├── log.md                       ← 操作紀錄（append only）
    ├── concepts/                    ← 概念頁         ← Cowork (compile-all)
    ├── methods/                     ← 方法論頁       ← Cowork (compile-all)
    ├── traps/                       ← 陷阱頁         ← Cowork (compile-all)（補充目錄，非七層架構核心）
    ├── problems/                    ← 題目頁         ← Cowork (ingest)
    ├── philosophy/                  ← 設計哲學頁     ← Cowork (compile-all)
    ├── queries/                     ← 查詢結果頁     ← Cowork (直接存入)
    ├── diagnosis/                   ← 題型診斷層     ← Cowork (直接存入)
    ├── failure-modes/               ← 失敗模式層     ← Cowork (直接存入)
    ├── materials/                   ← 材料行為層     ← Cowork (直接存入)
    └── code-ref/                    ← 規範條文對應層 ← Cowork (直接存入)
```

---

## 知識分類骨架（七層）

Wiki 導航依七層知識架構組織（前三層由 Cowork 透過 compile-all/ingest 生成，後四層由 Cowork 直接維護）：

| 層 | 目錄 | 維護者 | 內容 |
|----|------|:------:|------|
| Layer 1 | `concepts/` + `problems/` | Cowork (ingest/compile) | 核心構件設計（梁/柱/板/基礎/預力） |
| Layer 2 | `philosophy/` | Cowork (compile-all) | 設計哲學與實務（強度折減/韌性/耐震） |
| Layer 3 | `methods/` | Cowork (compile-all) | 解題方法論（P-M互制/等效側力法/損失計算） |
| Layer 4 | `diagnosis/` | Cowork (直接存入) | 題型診斷決策樹 |
| Layer 5 | `failure-modes/` | Cowork (直接存入) | 失敗模式（彎曲/剪力/壓碎/撓度/裂縫） |
| Layer 6 | `materials/` | Cowork (直接存入) | 材料行為（混凝土應力應變/鋼筋降伏/潛變收縮） |
| Layer 7 | `code-ref/` | Cowork (直接存入) | 規範條文對應（ACI 318/CNS 1480/耐震規範） |

> **補充目錄 `wiki/traps/`：** 不屬於七層架構，由 compile-all 從題目解析萃取陷阱頁面，與 concepts/ 並列為輔助導航。

---

## 命題大綱分類（依官方命題大綱，93年3月公告）

> topicId 格式：`RC-UN-n`，U = 單元號，n = 子項號。
> `primaryTopicId` 填最主要考點；跨子項時用 `secondaryTopicIds` 列出。

### 第一單元（RC-U1）

| topicId | 命題大綱子項 |
|---------|------------|
| RC-U1-1 | RC 梁彎矩強度分析與設計 |
| RC-U1-2 | RC 柱強度分析與設計 |
| RC-U1-3 | 細長柱 |
| RC-U1-4 | 柱設計圖之應用 |

### 第二單元（RC-U2）

| topicId | 命題大綱子項 |
|---------|------------|
| RC-U2-1 | RC 剪力強度分析與設計 |
| RC-U2-2 | RC 扭力強度設計 |
| RC-U2-3 | 鋼筋錨定長度與斷點計算 |

### 第三單元（RC-U3）

| topicId | 命題大綱子項 |
|---------|------------|
| RC-U3-1 | 梁工作性要求（含撓度、裂縫） |
| RC-U3-2 | 樓版與基腳設計 |
| RC-U3-3 | 韌性要求與耐震設計 |

### 第四單元（RC-U4）

| topicId | 命題大綱子項 |
|---------|------------|
| RC-U4-1 | 預力梁斷面應力分析 |
| RC-U4-2 | 預力量與偏心量設計 |
| RC-U4-3 | 預力損失 |
| RC-U4-4 | 預力梁剪力分析與設計 |

---

## 重要規則

1. **`raw/` 目錄下所有檔案絕對不可修改**（`question_index.json` 除外）
2. **`verifiedSolution` 是最終答案，不可質疑或重新計算**
3. **`wiki/log.md` 只可 append，不可刪除已有紀錄**
4. **wiki/ 大多數目錄是 compile 輸出，不可手動修改**；例外：diagnosis/ · failure-modes/ · materials/ · code-ref/ · queries/ 由 Cowork 直接維護
5. **ingest 前必須確認 verificationStatus = "verified"**
6. 概念連結使用 `[[concept_id]]`（Obsidian 相容）
7. 每次 ingest 同時更新 index.md 和 by-year.md
8. **格式與命名規範見 CLAUDE-SPEC.md；操作指令（ingest/compile/lint/status）見 CLAUDE-CODE.md，全部由 Cowork 執行**

---

## CHANGELOG

| 日期 | 變更 | 原因 |
|------|------|------|
| 2026-05-29 | 從 exam-wiki-SS 克隆，全面改寫為 RC 科目 | 建立鋼筋混凝土設計與預力獨立知識庫 |
| 2026-06-04 | 從三層架構（User/Cowork/Claude Code）改為兩層（User/Cowork） | 知識庫全程在 Cowork 運行，無獨立 Claude Code 終端機環境 |
| 2026-06-04 | Cowork 指令由 4 個擴充至 15 個（新增備考分析類、查詢快捷類、題庫維護類） | 增強備考分析與知識查詢功能 |
| 2026-06-08 | 修正 concepts.json classification 格式（RC-N → RC-UN-n）；修正 CLAUDE-SPEC.md §6 殘留 SS 類別代碼；更新 檔案架構索引表.md 快照數字；澄清 wiki/traps/ 補充目錄定位 | 知識庫 review 後修正 |
| 2026-06-11 | 新增 index.html + dashboard-data.js（離線儀表板：題庫篩選/統計/進度追蹤/指令速查）；指令由 15 個擴充至 16 個（新增 refresh-dashboard）；補完 lint SKIP 項掃描（hasViz/hasHandwritten/圖說均一致） | 建立使用者視覺化入口，提升知識庫易用性 |
| 2026-06-26 | study 指令輸出目錄從 wiki/queries/ 改為 study/；新增子項層級（study RC-UN-n）深度複習格式（七區塊：命題分析/截面圖解/解題流程/公式/考題清單/陷阱/互動計算） | 講義與複習頁集中在 study/ 管理，wiki/queries/ 保留純查詢結果 |
| 2026-06-30 | 修正 study 指令產生的考題連結路徑，改為直接連結至 `raw/solutions/` 下的原始 md 檔 | 解決透過 index.html#md 渲染器預覽時，相對路徑附圖與 PDF 補充資料無法載入的 bug |
| 2026-06-30 | index.html 題庫瀏覽新增「📎 補充筆記 PDF」按鈕與「📎 掃描補充 PDF」工具列按鈕；使用者可將任意 .pdf 放入 `raw/solutions/RC-YYYY-N/`，dashboard 透過 File System Access API 即時掃描顯示（不修改 dashboard-data.js）；更新 CLAUDE-CODE.md、CLAUDE-SPEC.md、CLAUDE.md 補充規範 | 支援每題補充筆記 PDF 快速存取 |
| 2026-07-01 | index.html「考點統計」頁籤改為呈現 frequency 指令輸出格式（高頻考點 Top10、各單元命題比例、近5年趨勢動態計算），移除原設計法分布與高頻標籤 Top20 兩張卡片 | 對齊 CLAUDE-CODE.md FREQUENCY 指令規格，避免統計呈現重複 |
| 2026-07-01 | dashboard-data.js 每題新增 pdf 補充筆記檔名陣列欄位（由 REFRESH-DASHBOARD 掃描 raw/solutions/RC-YYYY-N/ 下 *.pdf 寫入）；index.html 移除「📎 掃描補充 PDF」工具列按鈕與前端即時掃描機制（injectPdfButtons/pdfCache/listDir），改為依 dashboard-data.js 靜態資料直接顯示「📎 補充筆記 PDF」按鈕；同步更新 CLAUDE-CODE.md、CLAUDE-SPEC.md | 使用者自行放入補充 PDF 後無需手動點擊掃描按鈕，題卡即可自動顯示 PDF 連結 |

