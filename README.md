# exam-wiki-SA — 結構學考古題知識庫

**科目：** 專門職業及技術人員高等考試結構工程技師 — 第一科：結構學
**收錄範圍：** 2002–2025 年（民國 91–114 年）
**題目編號：** SA-YYYY-N（如 SA-2018-1 = 2018年第1題）

---

## 這個資料庫是什麼

每道考古題都有一份 **深度解析**（LaTeX 公式、逐步計算、陷阱說明），解析由 AI 完成，人工驗算確認後才進 wiki。

**兩個工作角色：**

| 你要做什麼 | 怎麼做 |
|-----------|--------|
| 解一道新題 | 對 **Cowork** 說「解析 XXXX 年考卷」 |
| 把解析寫進 wiki | 對 **Cowork** 說「ingest SA-XXXX-N」 |
| 查詢知識 / 跨題分析 | 對 **Cowork** 直接提問 |
| 維護橫向知識工具 | 對 **Cowork** 說（diagnosis / failure-modes / materials / code-ref） |

> 所有操作都在 Cowork 對話中完成，無需終端機或其他工具。完整指令清單見 **CLAUDE-CODE.md**。

---

## 快速導航

| 我想找... | 去哪找 |
|----------|-------|
| **視覺化瀏覽整個知識庫** | **雙擊 `index.html`**（題庫搜尋篩選、考點統計、進度追蹤、指令速查） |
| 特定題目的解析 | `raw/solutions/SA-YYYY-N/SA-YYYY-N.md` |
| 子項單元總覽（考什麼＋公式給／背＋逐題要背哪幾條） | `study/unit-SA-UN-n.html`（說 `study SA-UN-n` 生成）；觀念講義 `study/lecture-SA-UN-n.html` |
| 題目瀏覽頁（KaTeX 排版） | `study/problems-view/SA-YYYY-N.html` |
| 方法論（彎矩分配、傾角變位、矩陣法等） | `raw/solutions/methods/` |
| 查詢、稽核報告 | `wiki/queries/` |
| 變更紀錄 | `wiki/queries/log.md` |
| 舊 wiki 各層（2026-11-01 封存，唯讀參考） | `archive/wiki/` |

---

## 檔案地圖

```
exam-wiki-SA/
├── README.md          ← 你在這裡（冷啟動導覽）
├── CLAUDE.md          ← 身份層：分工、資料流、重要規則
├── CLAUDE-SOLVE.md    ← Cowork 解題 Skill（流程層）
├── CLAUDE-CODE.md     ← 所有 Cowork 指令 Runbook（16個指令）
├── CLAUDE-SPEC.md     ← 所有格式/命名規範（規格層）
├── index.html         ← 離線儀表板（題庫篩選/統計/進度追蹤/指令速查）
├── dashboard-data.js  ← 儀表板快照（更新儀表板資料 指令重新生成）
│
├── study/             ← 讀書講義（study 指令輸出的 HTML 複習頁）
│
├── raw/               ← 原始資料（唯讀）
│   ├── exams/         ← 考卷 PDF（SA-YYYY_結構學.pdf）
│   ├── json/          ← question_index.json、concepts.json
│   └── solutions/     ← 每題一個資料夾，含 .md + 截圖
│
├── wiki/
│   └── queries/       ← 查詢、稽核報告、log.md（變更紀錄）
│
└── archive/wiki/      ← 2026-11-01 封存的舊 wiki 各層（唯讀參考，不再維護）
```

---

## 如何開始解一道新題

```
1. 在 Cowork 開啟此資料夾（Project）
2. 說：「解析 2025 年考卷」
3. 依提醒截圖題目附圖，存入對應資料夾
4. 告知 Cowork「截圖完成，請開始解題」
5. Cowork 輸出 SA-2025-1.md（一次一題）
6. 人工驗算無誤後，說：「將 SA-2025-1 的 verificationStatus 改為 verified」
7. 說：「ingest SA-2025-1」→ Cowork 直接寫入 wiki
```

---

## 關鍵規則（避免常見錯誤）

- 年份用**西元**（SA-2018-1，不是 SA-107-1）
- PNG 截圖必須加序號（`fig-1.png`，不可寫 `fig.png`）
- 不產生互動圖 `*-viz.html`（2026-11-01 廢止）；圖解一律用 `figs/*.svg` 向量圖
- 公式必須用 LaTeX（`$M_{AB}$`，不可寫純文字）
- ingest 前確認 `verificationStatus = "verified"`

> 完整規則見 **CLAUDE-SPEC.md**
