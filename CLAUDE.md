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
| 2026-11-08 | **剩餘單元批 1 收尾**：勘誤三題落實檢查（SA-2018-1 §3 互制方向殘留補清後落實）；6 題補解題圖（2006-3、2003-1 梁彎矩圖、2019-2 范倫迪爾軸力＋彎矩圖、2018-1 互制樓層力分布、2016-4 傳力路徑與 24 根零桿、2017-4 三配置剛心與 Σk·d²）；lecture-SA-U1-2 PDF 重產、儀表板 tags 同步；全科題目皆已完成盲解比對 | 階段 D–F，詳見 wiki/queries/落實檢查-SA-剩餘單元-批1-2026-11-08.md 與 wiki/queries/log.md（RECHECK／FIGURE／CLOSE-SA-REST-B1） |
| 2026-11-08 | **SA-U2-4 批 1 收尾**：11-05 勘誤三題（SA-2008-4、SA-2019-4、SA-2024-4）落實檢查全部落實（不同工作階段複核）；6 題補解題圖（2004-4 梁變形＋彎矩、2009-4／2010-4／2011-4 桁架桿力＋節點位移、2012-4 兩個單位狀態、2022-4 剪力棟架側移＋柱彎矩），14 題皆有解題圖；problems-view 重產、KaTeX 檢查 0 錯誤 | 階段 D–F，詳見 wiki/queries/落實檢查-SA-U2-4-批1-2026-11-08.md 與 wiki/queries/log.md（RECHECK／FIGURE／CLOSE-SA-U2-4-B1） |
| 2026-11-08 | **剩餘單元批 1 盲解比對勘誤三題（階段 C）**：SA-2016-4 零桿 3 根（BF、LP、NP）→ 24 根，只有 AE 受 100 kN 拉、彈簧力 0（舊解誤讀 I 點有載重、只用口訣）；SA-2017-4 (b) 十字形牆改為開口截面、兩片牆通過剛心、抗扭勁度近零（舊解當閉合核心筒），排序 (c) ≥ (b) > (a) 不變；SA-2018-1 依使用者判定採牆–構架互制，§5 補字面 1:5 讀法與限制，§4 構架反向樓層 1~5 → 約 1–2 樓；lecture-SA-U1-2 同步（PDF 延到階段 F） | 盲解比對，詳見 wiki/queries/盲解比對-SA-剩餘單元-批1-2026-11-08.md 與 wiki/queries/log.md（FIX-SA-2016-4、FIX-SA-2017-4、FIX-SA-2018-1） |
| 2026-11-08 | **SA-U2-3 批 2 收尾**：4 題勘誤落實檢查全部落實（SA-2021-2 標籤「連桿效應」、SA-2025-3 §1.5 現在式指稱兩處殘留補清）；8 題補解題圖（2021-1 梁 BMD、2021-2 框角剛接變形圖＋梁 abef BMD 標 b、e 跳躍與受拉側、2015-3 梁 BMD 標 CD 段 +1.69、2019-3 沉陷彎矩對照、2014-3、2020-2、2023-3、2024-3 變形＋彎矩），12 題皆有解題圖；lecture-SA-U2-3 陷阱表第 17 列「柱底鉸 ⇒ 最大彎矩必在柱頂」與 SA-2017-3 右柱不符，改寫；4 題標頭主分類名稱對齊大綱；unit／lecture-SA-U2-3 HTML 與 PDF 重建、儀表板 tags 同步 | 階段 D–F，詳見 wiki/queries/落實檢查-SA-U2-3-批2-2026-11-08.md 與 wiki/queries/log.md（FIX-RESIDUE、FIGURE、CLOSE-SA-U2-3-B2） |
| 2026-11-08 | **SA-U2-3 批 2 盲解比對與勘誤四題**：11 題中 7 題一致（2020-2、2024-3 非獨立）；SA-2021-2 依使用者判定框角 c、d 剛接重解（舊解當柱底鉸＋連桿），θ_b 9→5×10⁻⁴ rad、Δ_b 8.1→3.30 mm、梁端 ±18→±10 kN-m 且受拉側更正；SA-2021-1 b 點剪力修正符號錯，Δ_b 3.6→3.80 mm、M_b −6.35→−6 kN-m；SA-2017-3 θ_A、θ_D 方向改逆時針（數值不變）；SA-2025-3 固端彎矩同號推導殘留清除（最終公式不變）；lecture／unit-SA-U2-3 同步並重出 PDF | 盲解比對發現，詳見 wiki/queries/盲解比對-SA-U2-3-批2-2026-11-07.md 與 wiki/queries/log.md（FIX-SA-2021-2、FIX-SA-2021-1、FIX-SA-2017-3、FIX-SA-2025-3） |
| 2026-11-07 | **剩餘 13 題題目正本（U1-2 尾段 5、U2-5 2、U3-1 1、U3-2 5）與讀題勘誤三題**：全科題目正本至此全部建立並凍結、重繪附圖、解析 §1 改指題目正本；SA-2017-1 桿件依考卷為 AD 斜桿（舊解 AC＋BE），AB 22→16、BD 0→−9、DE −20→−27.5 kN、新增 AD +7.5、δ_C 536/EA→566.5/EA；SA-2021-4 EI 依考卷 9720／48600（舊解讀成一半），柱頂位移減半（C3 1.6／7.6 mm、C4 1.6／2.8 mm），剪力不變；SA-2017-4 (a) 牆方向、(c) 中央核心改寫；lecture／unit-SA-U1-2 同步並重出 PDF | 題目正本盲讀考卷發現，詳見 wiki/queries/題目正本-SA-剩餘單元-批1-2026-11-07.md 與 wiki/queries/log.md（FIX-SA-2017-1、FIX-SA-2021-4、FIX-SA-2017-4、PROBLEM-SPLIT-CONFIRM-SA-REST-B1） |
| 2026-11-07 | **SA-U2-2 批 1 收尾**：盲解比對 10 題，9 題一致、1 題分歧-觀念作圖（SA-2009-1 §4 斜桿 bd → ec，兩對角線等長故反力不變，勘誤補最終桿力；落實檢查通過）；SA-2014-2、SA-2016-1 為一致但非獨立（勘誤數值已見於本表）；9 題補解題圖（2006-2、2009-2、2014-2、2016-1 變形＋彎矩；2007-1、2008-1、2009-1、2011-1、2023-2 桁架力流）；SA-2014-2 副分類 SA-U2-1 刪除（考卷限用諧合變位法）；SA-2008-1、SA-2009-2 表述修正（非勘誤）；lecture／unit-SA-U2-1 PDF 重產並修 KaTeX 未渲染兩處（Macaulay 式裸「<」、單元總覽模板頁尾未渲染） | 階段 B–F 一次完成；只比 boxed 答案會漏掉「答案對、模型錯」的題目，桿力圖在階段 E 攔下 |
| 2026-11-07 | **SA-U2-2 批 1 題目正本（9 題）與讀題勘誤一題**：SA-2014-2 的 CD 為斜桿（C 在 A 正上方，長 7.5 m；舊解當成 D 正上方 4.5 m 垂直桿），\|M\|max 28.8 → 51.24 kN-m（仍在 A）、CD 桿力 51.2 → 68.71 kN、R_B 20 → 23.12 kN；9 題題目正本確認凍結、重繪附圖、解析 §1 改指題目正本 | 題目正本批 1 盲讀考卷發現，詳見 wiki/queries/題目正本-SA-U2-2-批1-2026-11-07.md 與 wiki/queries/log.md（FIX-SA-2014-2、PROBLEM-SPLIT-CONFIRM-SA-U2-2-B1） |
| 2026-11-07 | **SA-U2-1 批 1 收尾**：盲解比對 12 題全部一致（0 勘誤）；7 題補解題圖（2005-1、2005-4、2008-3、2012-2、2013-2、2018-3、2022-1）；SA-2016-3 副分類 SA-U2-2 → SA-U2-3（題給桿端彎矩採傾角變位法規約，§5 補 CD 柱傾角變位式另解）；SA-2017-2、2019-1、2006-1 補註方向／位移控制對照／A 點受拉（皆非勘誤，答案不變）；U2-3 講義與單元總覽、U2-1 單元總覽 HTML 與 PDF 重建 | 階段 B–F，詳見 wiki/queries/盲解比對-SA-U2-1-批1-2026-11-07.md 與 wiki/queries/log.md（AUDIT／NOTE／FIGURE／PIPELINE-SA-U2-1-B1） |
| 2026-11-07 | **SA-U2-1 批 1（12 題）與 SA-U2-3 批 2（12 題）題目正本確認凍結**：24 題重繪題目附圖、解析 §1 改指題目正本；SA-2020-1 c 靠牆滾支承、SA-2023-3 50 kN 向上依使用者確認定案（與解析相同，答案不變）；SA-2018-3 補 §1 | 題目正本關卡一，詳見 wiki/queries/題目正本-SA-U2-1-批1-2026-11-07.md 與 wiki/queries/log.md |
| 2026-11-07 | **SA-U1-3 批 1 收尾**：盲解比對 12 題全部一致；7 題補影響線圖解（gen_<id>_il.py）；SA-2015-2 副分類 SA-U2-1 → SA-U2-2；SA-2004-2 標頭名稱、SA-2007-3 A_x 框式與合力精確值 130.975 kN、SA-2018-4 §3.1 中間式符號（皆非勘誤，答案不變）；lecture-SA-U1-3 §5 刪除細長拉桿敘述、圖 5-2 N_km 改 R_b；單元總覽 U1-3／U2-1、講義 U1-3／U2-1 HTML 與 PDF 重建 | 階段 B–F，詳見 wiki/queries/log.md（AUDIT／FIGURE／PIPELINE-SA-U1-3-B1） |
| 2026-11-07 | **SA-U1-3 題目正本（全 12 題）**：12 份題目正本確認凍結、重繪附圖、解析 §1 改指題目正本（SA-2018-4 新增 §1）；SA-2007-3「最大可能之 A 點反力」改以垂直反力 A_y = 130.25 kN 為主答案、合力 130.97 kN 並列；SA-2022-3 刪除考卷沒有的「細長拉桿」假設與補充 N_km（所求五條影響線不變，等 EA 彈性桁架驗證），lecture-SA-U1-3 與單元總覽同步延到階段 F | 題目正本批 1 盲讀考卷發現，詳見 wiki/queries/題目正本-SA-U1-3-批1-2026-11-07.md 與 wiki/queries/log.md |
| 2026-11-05 | **SA-U2-4 批 1 盲解比對與勘誤三題**：14 題中 11 題一致（verified 5 題全一致）；SA-2019-4 C 鉸支當固定端、w 放錯梁、轉角正向反，[K] 四元素與 {P} 三項更正（K₁₁ 24 → 15 EI/L³、K₄₄ 11 → 10 EI/L 等）；SA-2008-4 BC 最大正彎矩 0.125 @ 2.5 m → 3.125 kN-m @ 3.5 m、柱端彎矩 0.75／1.5 → 1.5／3.0；SA-2024-4 整題重解為 P−Δ 側推（梁端 100 kN、柱底 125.71 kN 形成塑鉸，P_u = 125.71 kN）；U2-4 單元資料與 U2-3／U2-4 講義同步（HTML／PDF 重建延到階段 F） | 盲解比對發現，詳見 wiki/queries/盲解比對-SA-U2-4-批1-2026-11-05.md 與 wiki/queries/log.md |
| 2026-11-05 | **SA-U2-4 題目正本（全 14 題）**：14 份題目正本確認凍結、重繪附圖、解析 §1 改指題目正本；SA-2024-4 確認為答錯題（考卷要求 P−Δ 側推曲線至極限承載力，解析只做彈性階段），§1 加警示、待依題目正本重解；SA-2012-4 刪「題幹明示不考慮軸向變形」加字；SA-2025-4 §1 加本解與考卷座標對照（數值不動） | 題目正本批 1 盲讀考卷發現，詳見 wiki/queries/題目正本-SA-U2-4-批1-2026-11-05.md 與 wiki/queries/log.md |
| 2026-11-05 | **SA-U1-2 批 1 盲解比對與勘誤一題**：11 題中 10 題一致；SA-2010-1 節點 G 漏算 GH 桿致零桿誤判，AC 0 → −10√2、BF 30 → 10、DE −60 → −30 kN，解析 §1–§5 改寫，講義歷屆題表與單元資料同步；SA-2012-1 刪副分類 SA-U2-1（U2-1 單元總覽與講義同步）；SA-2002-1、2004-1、2010-1 補解題圖解；講義與單元總覽 PDF 重出 | 盲解比對發現，詳見 wiki/queries/盲解比對-SA-U1-2-批1-2026-11-05.md 與 wiki/queries/log.md |
| 2026-11-05 | **SA-U1-2 批 1 題目正本（12 題）與讀支承勘誤兩題**：SA-2016-1 的 E 為固定端（舊解當鉸支承），本題改為一度靜不定，M_B = M_D 50 → 25、M_E 0 → 50 kN·m，並改歸 SA-U2-2（使用者決定）；SA-2002-2 的 B 為鉸支承、A–B 虛線不是桿件（舊解當滾支承＋繫索），a–e 答案不變、解題路徑與反力改寫；12 題重繪附圖、§1 改指題目正本；講義 lecture-SA-U1-2（兩個手算範例、圖 1-2／3-3、陷阱表）與 U1-2 單元總覽、頻率熱圖、儀表板同步並重出 PDF | 題目正本批 1 盲讀考卷發現，詳見 wiki/queries/題目正本-SA-U1-2-批1-2026-11-05.md 與 wiki/queries/log.md |
| 2026-11-05 | **題目正本批 2 讀題錯誤勘誤兩題**：SA-2024-3 附圖 C 角為內鉸（舊解當成對稱門型剛架），L_b/L 3 → 3/2，講義手算範例 6 改寫並重出 PDF、單元總覽改歸有側移剛架；SA-2020-2 的 bc 為 4 m（舊解 2 m），v_b 2.145 → 2.40 mm、M_ab −13.36 → −14.00、M_ba −10.64 → −10.00 kN-m、θ_b 轉向更正為順時針 | SA-U2-3 批 2 盲讀考卷建立題目正本時發現，詳見 wiki/queries/題目正本-SA-U2-3-批2-2026-11-05.md 與 wiki/queries/log.md |
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
