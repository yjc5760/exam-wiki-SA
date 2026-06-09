# exam-wiki-RC — 鋼筋混凝土設計與預力考古題知識庫

**科目：** 專門職業及技術人員高等考試結構工程技師 — 第三科：鋼筋混凝土設計與預力
**收錄範圍：** 2002–2025 年（民國 91–114 年）
**題目編號：** RC-YYYY-N（如 RC-2018-1 = 2018年第1題）

---

## 這個資料庫是什麼

每道考古題都有一份 **深度解析**（LaTeX 公式、逐步計算、陷阱說明），解析由 AI 完成，人工驗算確認後才進 wiki。

**兩個工作角色：**

| 你要做什麼 | 怎麼做 |
|-----------|--------|
| 解一道新題 | 對 **Cowork** 說「解析 XXXX 年考卷」 |
| 把解析寫進 wiki | 對 **Cowork** 說「ingest RC-XXXX-N」 |
| 查詢知識 / 跨題分析 | 對 **Cowork** 直接提問 |
| 維護橫向知識工具 | 對 **Cowork** 說（diagnosis / failure-modes / materials / code-ref） |

> 所有操作都在 Cowork 對話中完成，無需終端機或其他工具。完整指令清單見 **CLAUDE-CODE.md**。

---

## 快速導航

| 我想找... | 去哪找 |
|----------|-------|
| 特定題目的解析 | `raw/solutions/RC-YYYY-N/RC-YYYY-N.md` |
| wiki 題目頁（含標籤/考點） | `wiki/problems/RC-YYYY-N.md` |
| 依年份瀏覽所有題目 | `wiki/by-year.md` |
| 概念說明（Whitney應力塊、P-M圖等） | `wiki/concepts/` |
| 解題策略（拿到考題怎麼判斷） | `wiki/diagnosis/` |
| 規範條文對應（ACI 318） | `wiki/code-ref/` |
| 操作紀錄 | `wiki/log.md` |

---

## 檔案地圖

```
exam-wiki-RC/
├── README.md          ← 你在這裡（冷啟動導覽）
├── CLAUDE.md          ← 身份層：分工、資料流、重要規則
├── CLAUDE-SOLVE.md    ← Cowork 解題 Skill（流程層）
├── CLAUDE-CODE.md     ← 所有 Cowork 指令 Runbook（15個指令）
├── CLAUDE-SPEC.md     ← 所有格式/命名規範（規格層）
│
├── raw/               ← 原始資料（唯讀）
│   ├── exams/         ← 考卷 PDF（RC-YYYY_鋼筋混凝土設計與預力.pdf）
│   ├── json/          ← question_index.json、concepts.json
│   └── solutions/     ← 每題一個資料夾，含 .md + 截圖
│
└── wiki/              ← 知識庫（七層架構）
    ├── problems/      ← 所有題目頁
    ├── concepts/      ← 概念頁
    ├── methods/       ← 解題方法論（Whitney、P-M互制、損失計算等）
    ├── diagnosis/     ← 題型診斷決策樹
    ├── failure-modes/ ← 失敗模式分類
    ├── materials/     ← 材料行為（混凝土/鋼筋）
    └── code-ref/      ← 規範條文對應（ACI 318/CNS 1480）
```

---

## 如何開始解一道新題

```
1. 在 Cowork 開啟此資料夾（Project）
2. 說：「解析 2025 年考卷」
3. 依提醒截圖題目附圖，存入對應資料夾
4. 告知 Cowork「截圖完成，請開始解題」
5. Cowork 輸出 RC-2025-1.md（一次一題）
6. 人工驗算無誤後，說：「將 RC-2025-1 的 verificationStatus 改為 verified」
7. 說：「ingest RC-2025-1」→ Cowork 直接寫入 wiki
```

---

## 關鍵規則（避免常見錯誤）

- 年份用**西元**（RC-2018-1，不是 RC-107-1）
- PNG 截圖必須加序號（`fig-1.png`，不可寫 `fig.png`）
- 互動圖後綴必須是 `-viz.html`（`pm-viz.html`，不是 `pm.html`）
- 公式必須用 LaTeX（`$f'_c$`，不可寫純文字）
- ingest 前確認 `verificationStatus = "verified"`

> 完整規則見 **CLAUDE-SPEC.md**
