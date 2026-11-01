# archive/wiki — 已封存（2026-11-01）

這個資料夾是 2026-11-01 從 `wiki/` 搬來的舊內容，**不再維護、不再同步勘誤**，只留作參考。

| 目錄 | 原用途 |
|---|---|
| problems/ | 題解摘要頁（與 raw/solutions 正本重複） |
| concepts/、methods/、traps/、code-ref/ | 觀念、方法論、陷阱、公式來源整理 |
| diagnosis/、philosophy/、failure-modes/、materials/ | 題型診斷、分析哲學、常見錯誤、材料特性 |
| index.md、by-year.md | 舊主導航、依年份瀏覽 |

**為什麼封存**
- 內容是早期由 AI 從正本編譯的摘要，**未逐頁核對**。
- 與 `raw/solutions/`（正本）、`study/`（講義、單元總覽、題目瀏覽頁）重複，每次勘誤都要多同步一份。
- 同類風險：SS 科 2026-11-01 掃描同類觀念頁與方法頁 84 頁，發現 45 項確定錯誤；SA 這批頁面未做同樣掃描，應視為可能含錯。

**現在請用**
- 題解：`study/problems-view/`（由正本 `raw/solutions/` 以 `scripts/md2view.py` 產生）。封存前有 13 題（SA-2002-3、2003-1、2006-2、2006-3、2008-1、2017-4、2018-1、2019-2、2019-3、2020-4、2021-4、2023-2、2023-4）只有 wiki 題目頁、沒有 problems-view，已於封存當天補齊。
- 觀念與公式：`study/lecture-SA-*.html`、`study/unit-SA-*.html`
- 方法論正本：`raw/solutions/methods/`（仍維護）
- 稽核紀錄與變更紀錄：`wiki/queries/`（含 `log.md`）

**注意**：搬移後目錄多了一層，頁內的相對連結與圖片路徑（`../../raw/...`）可能失效；題號連結請改用 study/problems-view。
