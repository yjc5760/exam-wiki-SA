# 健檢與狀態報告（2026-07-09，修正版）

> 知識庫優化作業後重新執行 LINT + STATUS 的結果快照。
>
> ⚠️ **重要更正：** 本報告最初版本執行時，lint.py 的 ROOT_DIR 寫死為 Windows 路徑，在 Cowork 的 Linux 環境下該路徑不存在，導致腳本靜默對空目錄操作，回報「全部通過、僅 5 項 failure-modes 警告」為假陽性。已修正 lint.py 改用相對路徑後重新執行，以下為真實結果。

## LINT（16 項檢查）

✅ 無 Errors。

⚠️ 警告 8 項（均為同一類：verified 題目內容提及彎矩圖/剪力圖，但缺少對應的 sfd-bmd-viz.html 互動圖）：
- SA-2002-1、SA-2002-4、SA-2003-1、SA-2004-1、SA-2005-3、SA-2006-3、SA-2015-2、SA-2015-3

> 這 8 題目前只有靜態解析文字與題目附圖，尚無互動式彎矩圖/剪力圖。建議後續逐題建立 `SA-YYYY-N-sfd-bmd-viz.html`（規格見 CLAUDE-SPEC.md §6）。

## STATUS

驗證進度：96 / 96（100% verified）

- ✅ verified：96 題
- ⚠️ needs-review：0 題
- ❌ unverified：0 題

solutions/ 已有解析但未驗證：0 題
已 verified 但尚無 solutions/ 資料夾：0 題

## 本次優化前後對照

| 項目 | 優化前 | 優化後 |
|------|--------|--------|
| wiki/queries/ 內 RC 科目污染檔案 | 6 個（5 md + 1 pdf） | 0 |
| 根目錄過期損毀健檢報告 | lint_output.txt（RC 內容，編碼損毀） | 已刪除 |
| primaryTopicId 使用虛構代碼（SA-U4/U5）或空白 | 22 題 | 0 |
| secondaryTopicIds 含無效代碼 | 6 題 | 0 |
| year/rocYear 欄位錯誤（民國年誤植為西元年） | SA-2013-1~4（4題） | 0 |
| questionNumber 欄位缺失（schema 不一致） | 8 題 | 0 |
| wiki/index.md 主索引未收錄的已驗證題目 | 22 題（約 23%） | 0 |
| wiki/by-year.md 錯誤年份標題「102 年」 | 有 | 已修正為「2013 年」 |
| lint.py / update_dashboard.py 路徑寫死導致假陽性 | 是 | 已改相對路徑 |
| wiki/methods/、wiki/philosophy/ 空目錄 | 0 個檔案 | 各 5、3 個頁面 |
| SFD/BMD 互動圖缺口（真實掃描結果） | 未知（先前假陽性掩蓋） | 8 題待補（已列出待辦） |

## 尚未處理的已知缺口

- **8 題缺 SFD/BMD 互動圖**（見上表）：需逐題依驗證解析重建彎矩圖/剪力圖數據，工作量較大，建議另行安排。
- **wiki/traps/、wiki/code-ref/ 仍為空**：traps/ 需從 91 篇題目解析中的「陷阱分析」段落萃取歸納（非簡單複製，需去重與分類）；code-ref/ 需要使用者提供實際採用的教材版本/章節，才能填入正確的公式來源對照，目前未動作以避免虛構來源。
