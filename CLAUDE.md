# 結構工程技師考試知識庫 — 結構學（SA）

> 科目代碼：SA｜資料夾：`exam-wiki-SA`｜其他科目另建獨立資料庫

## 專案說明

本資料庫專門收錄「專門職業及技術人員高等考試結構工程技師」**第一科：結構學**的考古題解析知識庫。

- **科目代碼：** SA（Structural Analysis）
- **題目編號格式：** SA-YYYY-N（如 SA-2015-1）
- **其他科目：** 各自建立獨立資料庫（exam-wiki-SS、exam-wiki-RC、exam-wiki-SM 等）

**核心工作流程：**
```
在 Cowork 開啟 exam-wiki-SA/ 資料夾（Project）
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
（ingest 已停用：2026-11-01 wiki 封存；驗算後只需更新 question_index.json 的 verificationStatus）
```

---

## 兩個環境分工

| 環境 | 負責什麼 |
|------|---------|
| **你（使用者）** | PDF 題目附圖截圖（fig-N.png）、chart/eqn/hand 補充截圖、人工驗算後通知 Cowork 更新 verificationStatus |
| **Cowork** | 解題（SOLVE，**一次一題**）、存檔（.md）、更新 question_index.json、操作指令（詳見 CLAUDE-CODE.md；ingest / compile-all / lint / reindex / add-concept 等會寫 wiki 的指令已於 2026-11-01 停用）、直接維護 wiki/queries/ · study/ |

---

## 單向資料流

```
raw/solutions/SA-XXXX-N/SA-XXXX-N.md  ──→  study/problems-view/ （scripts/md2view.py）
raw/json/question_index.json          ──→  dashboard-data.js、study/unit-*、study/frequency-*（腳本重建）
raw/solutions/ ＋ question_index      ──→  study/lecture-*（講義，Cowork 維護）
Cowork 查詢、稽核、盲解報告            ──→  wiki/queries/        （Cowork 直接存入）
變更紀錄                               ──→  wiki/queries/log.md  （append only）

題意唯一來源：raw/solutions/SA-YYYY-N/SA-YYYY-N-problem.md（題目正本：考卷原文、附圖、判讀清單；確認後凍結）
解題內容唯一來源：raw/solutions/ 下的 .md 檔案
索引資訊唯一來源：raw/json/question_index.json
方法論唯一來源：raw/solutions/methods/（可修正，須驗算＋記 log，見規則 1）
封存：archive/wiki/（2026-11-01 前的 wiki 各層，唯讀參考、不再維護，ingest／compile-all 已停用）
```

---

## 資料夾結構

```
exam-wiki-SA/
├── README.md                        ← 冷啟動快速導覽
├── CLAUDE.md                        ← 本檔（身份層：分工、資料流、重要規則）
├── CLAUDE-SOLVE.md                  ← Cowork 解題 Skill
├── CLAUDE-CODE.md                   ← Claude Code 操作指令（Runbook）
├── CLAUDE-SPEC.md                   ← 規格驗證層（格式、命名、完成標準）
│
├── study/                           ← 讀書筆記、講義、study 指令 HTML 輸出（study-SA-UN.html / unit-SA-UN-n.html 單元總覽）
│   └── data/                        ← 單元總覽資料檔 unit-SA-UN-n.json（scripts/build_unit_page.py 的輸入）
│
├── raw/                             ← 所有原始資料（預設唯讀，僅 ✏️ 三處可改）
│   ├── exams/                       ← 原始考卷 PDF（命名：SA-YYYY_結構學.pdf）
│   ├── json/
│   │   ├── concepts.json            ← 概念定義（供 compile-all）
│   │   └── question_index.json      ← ⭐✏️ 題目總索引（唯一需要人工維護的 JSON）
│   └── solutions/                   ← AI 解析 + 補充截圖（每題一個資料夾）
│       ├── SA-YYYY-N/               ← ✏️ 個別題目解析（可修正，見規則 1）
│       │   ├── SA-YYYY-N-problem.md   ← 題目正本（考卷原文＋判讀清單，確認後凍結）
│       │   ├── SA-YYYY-N.md
│       │   ├── SA-YYYY-N-fig-1.png    ← 考卷附圖證據圖（不修改）
│       │   └── figs/SA-YYYY-N-fig-N-problem.svg ← 依判讀清單重繪的題目附圖
│       └── methods/                 ← ✏️ 解題方法論（可修正公式／單位，見規則 1）
│
├── wiki/
│   └── queries/                     ← 查詢、稽核報告、audit ledger、log.md（變更紀錄，append only）
│
└── archive/wiki/                    ← 2026-11-01 封存的舊 wiki 各層（唯讀參考，不再維護）
```

---

## 知識分類骨架（七層）

> **已封存（2026-11-01）**：原七層 wiki（concepts、philosophy、methods、diagnosis、failure-modes、materials、code-ref、traps、problems）已移至 `archive/wiki/`，不再維護、不再 compile。內容為早期由 AI 從正本編譯、未逐頁核對（SS 科同類頁面掃描發現 45 項錯誤），請改用 `study/`（講義、單元總覽、題目瀏覽頁）與 `raw/solutions/`、`raw/solutions/methods/`。

---

## 命題大綱分類（依官方命題大綱）

> topicId 格式：`SA-UN-n`，U = 單元號，n = 子項號。
> `primaryTopicId` 填最主要考點；跨子項時用 `secondaryTopicIds` 列出。

### 第一單元（SA-U1）

| topicId | 命題大綱子項 |
|---------|------------|
| SA-U1-1 | 靜不定度與穩定性之判斷 |
| SA-U1-2 | 靜定結構之分析 |
| SA-U1-3 | 靜定及靜不定結構影響線 |

### 第二單元（SA-U2）

| topicId | 命題大綱子項 |
|---------|------------|
| SA-U2-1 | 靜不定結構最小功法 |
| SA-U2-2 | 靜不定結構諧合變位 |
| SA-U2-3 | 靜不定結構之傾角變位法 |
| SA-U2-4 | 靜不定結構之矩陣分析法 |
| SA-U2-5 | 彎矩分配法 |

### 第三單元（SA-U3）

| topicId | 命題大綱子項 |
|---------|------------|
| SA-U3-1 | 建築結構系統之使用 |
| SA-U3-2 | 建築結構系統分析 |

---

## 重要規則

1. **`raw/` 目錄下所有檔案一律不可修改**，僅以下三處例外：
   - `raw/json/question_index.json`（索引唯一人工維護處）
   - `raw/solutions/methods/`（方法論文件，可修正公式錯誤與單位標註）
   - `raw/solutions/SA-YYYY-N/`（個別題目解析，含 .md、附圖、產圖腳本）
     - 其中題目正本 `SA-YYYY-N-problem.md`：建立時判讀狀態為「待確認」，使用者確認後改「已確認」並凍結；凍結後要改須回考卷原圖判讀並記 log（題意勘誤）。考卷證據圖 `-fig-*.png` 不修改，重繪圖一律另存 `figs/SA-YYYY-N-fig-N-problem.*`

   > **為什麼 methods/ 是例外**：本規則要保護的是**證據**（考卷、驗證過的答案），
   > 這些一旦被改就失去可追溯性。但 `raw/solutions/methods/` 存的是**可維護的知識整理**，
   > （`wiki/methods/` 已於 2026-11-01 封存，raw 即唯一版本。）
   > 發現公式或係數錯誤時，必須改 raw 來源才算根治。
   >
   > **修改 methods/ 的兩個條件（缺一不可）**：
   > ① 修正前先做**數值驗算**（邊界代入、量綱檢查、與驗證解答交叉比對），不可憑印象改；
   > ② 在 `wiki/queries/log.md` 記錄**改了什麼、為什麼、怎麼驗證的**。

2. **`verifiedSolution` 是最終答案，不可質疑或重新計算**
3. **`wiki/queries/log.md`（原 `wiki/log.md`）只可 append，不可刪除已有紀錄**
4. **wiki/ 只保留 `queries/`，由 Cowork 直接維護**；其餘舊 wiki 已封存於 `archive/wiki/`（唯讀參考，不再修改、不再 compile）
5. ~~ingest 前必須確認 verificationStatus = "verified"~~（ingest 已停用，2026-11-01 wiki 封存；verificationStatus 仍須人工複核後才改 verified）
6. 題號連結使用 `[[SA-YYYY-N]]`（Obsidian 相容）
7. ~~每次 ingest 同時更新 index.md 和 by-year.md~~（已停用：index.md、by-year.md 已封存）
8. **格式與命名規範見 CLAUDE-SPEC.md；操作指令見 CLAUDE-CODE.md（會寫 wiki 的指令已停用），全部由 Cowork 執行**

---

## CHANGELOG

| 日期 | 變更 | 原因 |
|------|------|------|
| 2026-11-04 | **題目正本導入**：新增 `raw/solutions/SA-YYYY-N/SA-YYYY-N-problem.md`（題目與解析拆分，確認後凍結）與重繪附圖 `figs/*-problem.svg`；規則 1、資料流、資料夾結構補列；`md2view.py` 渲染「📄 題目正本」區塊；索引新增 `problemStatus`（draft／confirmed）；首批 SA-U2-3 12 題 | 題意先單獨驗證，讀錯題在動解答前就被抓到（比照 SS） |
| 2026-11-04 | **虛功式少負號同類勘誤**：SA-2014-3 八個桿端彎矩正負號全部更正（M_AB −27.55→+27.55 kN-m 等）；SA-2005-2 §5 虛功驗算更正（主解不變）；lecture-SA-U2-3 §4.2 附註改為已勘誤並重出 PDF | 講義 §4.2 已註記的錯誤；與 SA-2013-3 同為「外功＝內功」寫法，詳見 wiki/queries/log.md |
| 2026-11-04 | **盲解比對後勘誤三題**：SA-2013-3 側移虛功式符號錯，四個桿端彎矩與 BC 剪力圖、彎矩圖全改（M_AB −0.0699→+0.1051 wL² 等）；SA-2007-4 AC 桿改為雙曲率有反曲點、SA-2002-4 彎矩圖受拉側全部更正（兩題數值不變）；三題新增題目正本（待確認） | wiki/queries/盲解比對-SA-U2-3a-2026-11-04.md 發現；詳見 wiki/queries/log.md |
| 2026-11-01 | **儀表板與題解渲染整理（比照 SS）**：刪除 40 份 `*-viz.html` 與 `mkviz_influence_line.py`，清除 .md／problems-view 引用、`hasViz`、dashboard viz／pdf 欄；`md2view.py` 加數學式保護並重新產生 96 頁 problems-view（修復 232 個被 markdown 改壞的數學式、50 處 `\cdotp`）；`index.html` 完整解析改連 problems-view、刪指令速查分頁、修導覽死連結與資料夾授權 | 互動圖維護成本高且易與 .md 不同步；舊渲染器未保護數學式，頁面公式與正本不一致 |
| 2026-11-01 | **wiki 封存**：wiki/ 只保留 queries/，其餘各層與 index.md、by-year.md 移至 `archive/wiki/`；`wiki/log.md` 改為 `wiki/queries/log.md`；ingest／compile-all 等會寫 wiki 的指令停用；補齊 13 題 problems-view | 舊 wiki 未逐頁核對、與 raw／study 重複，維護成本高（比照 SS 科） |
| 2026-10-30 | **全科分類稽核＋索引分類更正（四）**：14 題改分類（2008-3、2012-2→U2-1；2019-3→U2-3；2009-4、2024-4→U2-4；2007-1、2008-1、2009-1、2009-2→U2-2；2007-3→U1-3；2010-1→U1-2；刪 2013-1、2007-2、2007-4 副分類），U1-1 主分類歸零；33 題解析標頭的失效代碼對齊索引；wiki 導航、code-ref、diagnosis、單元總覽、講義、熱圖、儀表板同步 | 逐題比對考卷原文：5 題考卷明文指定的方法與分類不符，U1-1 七題全是靜不定桁架／矩陣／影響線被舊代碼誤歸；另發現 SA-2024-4 題解答錯題（待重解），詳見 wiki/log.md 與 wiki/queries/audit-classification-SA-2026-10-30.md |
| 2026-10-29 | **索引分類更正（三）**：SA-2007-2、SA-2007-4 由 SA-U2-1 改歸 SA-U2-3（U2-3 主 24 題、U2-1 主 10 題）；同步 wiki、單元總覽、講義、熱圖；刪除舊 `formula-given-*.pdf` | 兩題題解皆為傾角變位法，2007-4 考卷明文指定；舊 PDF 已被單元總覽取代且證據有誤，詳見 wiki/log.md |
| 2026-10-29 | **單元總覽**：五個子項的命題分析（`study-SA-Un-m`）與給／背分界（`formula-given-SA-Un-m`）合併為 `study/unit-SA-Un-m.html`（＋PDF），由 `scripts/build_unit_page.py` 從 `study/data/unit-SA-Un-m.json` 產生；舊十頁改轉址；逐題核對題解後更正多處給／背年份證據；熱圖、problems-view、講義、診斷頁連結同步 | 兩頁逐年列同一批題目、出題概況與全科熱圖重複；逐題標出「這題要背哪幾條」才看得出舊證據的錯，詳見 wiki/log.md |
| 2026-10-29 | **索引分類更正（續）**：SA-2009-3 由 SA-U1-1 改歸 SA-U2-3、SA-2011-1 移除副分類 SA-U2-3；同步 wiki、頻率熱圖、U2-3 給背分界與命題分析頁；`lecture-SA-U1-3`／`U2-3` 觀念講義改版（題數、對照表、權重） | 2009-3 考卷明文指定傾角變位法；2011-1 是柔度法桁架題、與傾角變位法無關；講義仍寫 13／9 題舊數字，詳見 wiki/log.md |
| 2026-10-28 | **索引分類更正**：10 題舊代碼改歸（8 題 SA-U3-1→SA-U2-3、2 題 SA-U3-2→SA-U1-3）；同步解析標頭、wiki、頻率熱圖、U1-3／U2-3 給背分界與命題分析頁，新建 9 頁 problems-view；`formula-given-SA-*` 五頁升級 unit-formula-map v2；SA-2022-3 依考卷原文補 R_b、R_c 影響線 | 舊代碼使 U2-3 帳面少 8 題、U3 多 10 題，全科排名與「U3-2 近年升溫」結論都是假的；SA-2022-3 原解答的題目要求與考卷不符，詳見 wiki/log.md |
| 2026-10-23 | **規則 1 例外擴充**：`raw/solutions/SA-YYYY-N/`（個別題目解析）移出唯讀保護，可直接修正 | 題解附圖、圖說等錯誤需能在原處根治（例：SA-2003-3 向量重繪圖幾何畫錯） |
| 2026-10-08 | **優化** `study/frequency-SA.html`（前／後半期比較、升溫／冷凍標記、可點熱圖連題目頁與影片、可排序排名表）；**新增** `scripts/build_frequency.py`（產生器 v1.1，進庫） | 舊版只看 24 年總數，低估近年升溫的 U3-2、未標出已冷凍的 U2-5／U1-1；格子只能 hover、手機無法用，也連不到 problems-view 與解題影片 |
| 2026-08-20 | **新增** `study/frequency-SA.html`（全科出題頻率熱圖：10 子項 × 24 考年，可切換主考點／主＋副，含排名總表與單元權重） | `study-SA-Un-m.html` 一次只看一個子項，缺少「整科該從哪裡開始讀」的全貌；數字全由 `build_frequency.py` 從 `question_index.json` 算出，題庫更新後可無腦重跑 |
| 2026-07-02 | 從 exam-wiki-RC 克隆，全面改寫為 SA 科目 | 建立結構學獨立知識庫 |
| 2026-08-09 | **新增** `study/formula-given-SA-*.html` + `.pdf`（5 單元，主要公式給／背分界）；**重構** `study/study-SA-*.html` 五頁為命題情報頁（刪除與 lecture／formula-given 重複的五個區段、補上漏列的 18 題副考點、題號連結改指 `problems-view/`） | 24 份考卷判定結果為「零參考公式區」，需獨立成頁供背誦決策；舊 study 七區段頁與 lecture 大量重複且數字有誤，詳見 wiki/log.md |
| 2026-07-25 | **規則 1 例外擴充**：`raw/` 唯讀的例外從「`question_index.json`」擴充為「`question_index.json` + `raw/solutions/methods/`」，並訂出三項修改條件（驗算／同步 wiki／記 log） | `methods/` 是 `wiki/methods/` 的 compile 來源，只改 wiki 副本會被 `compile-all` 蓋回；公式勘誤需能根治。個別題目解析 `raw/solutions/SA-YYYY-N/` 仍受完整保護 |
