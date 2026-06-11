# Wiki 操作紀錄

> append-only，請勿刪除已有紀錄

---

## 2026-05-29

- **[INIT]** 從 exam-wiki-SS 克隆，全面改寫為 RC 科目（鋼筋混凝土設計與預力）
  - 改寫 CLAUDE.md（身份層）、CLAUDE-SOLVE.md（解題規範）、CLAUDE-SPEC.md（命名規格）
  - 改寫 CLAUDE-CODE.md（Runbook）、README.md（導覽）
  - 重建 wiki/index.md（RC 七層架構）、wiki/by-year.md（2002–2025 空白表格）
  - 重建 raw/json/question_index.json（空白索引）、concepts.json（RC 核心概念）
  - 科目代碼：RC｜題目編號格式：RC-YYYY-N

## 2026-06-07

- **[INGEST-BATCH]** 批次 ingest 94 題（所有 verificationStatus=verified 且 hasSolution=true）
  - 生成 wiki/problems/ 共 94 個頁面
  - 重建 wiki/index.md（依 RC-UN-n 分類，含題目連結表格）
  - 重建 wiki/by-year.md（2002–2025 年，含題號連結）
  - 涵蓋年份：2002–2025

## 2026-06-07

- **[COMPILE-ALL]** 完整重新編譯 wiki 知識庫
  - 生成 wiki/concepts/：10 個概念頁面
  - 生成 wiki/methods/：4 個解題方法論頁面
  - 確認 wiki/queries/ 存在
  - 建立 wiki/philosophy/index.md
  - wiki/problems/（94題）已於本日批次 ingest 完成
  - 未覆蓋：diagnosis/ · failure-modes/ · materials/ · code-ref/（Cowork 直接維護）

## 2026-06-07

- **[LINT-FIX]** 修復全部 7 項 lint 問題：
  - 概念頁補充：DUCTILE-FAILURE, LONG-COLUMN-MOMENT-MAGNIFIER, LONG-TERM-DEFLECTION, CREEP-SHRINKAGE, SPECIAL-MOMENT-FRAME-BEAM, SPECIAL-MOMENT-FRAME-COLUMN（6 頁）
  - 圖說補充：RC-2024-4-fig-1、RC-2025-3-fig-1（圖說缺漏）；RC-2023-4 加入 eqn-1.png 引用與 LaTeX 圖說
  - diagnosis/ 建立：beam-flexure, column-pm, shear-torsion, prestress, deflection-crack（5 頁）
  - failure-modes/ 建立：flexure, shear, crushing, deflection, cracking（5 頁）
  - materials/ 建立：concrete-stress-strain, steel-yielding, creep-shrinkage, prestress-strand（4 頁）
  - P-M 互動圖生成：10 個柱設計題（RC-2002-2 等），更新 hasViz=true

## 2026-06-07

- **[CLEANUP]** 清除 SS 鋼結構殘留：186 個檔案（problems/98 + concepts/58 + methods/19 + traps/11）
- **[CONCEPTS]** concepts.json 新增 7 個高頻概念（SHEAR-STRENGTH、TORSION-DESIGN、PUNCHING-SHEAR、SEISMIC-DESIGN、DEVELOPMENT-LENGTH、DEFLECTION-CONTROL、CRACK-WIDTH）
- **[FIX]** RC-2012-2 verificationStatus 改回 unverified（hasSolution=false，狀態矛盾修正）
- **[QUERY]** 建立 wiki/queries/題庫缺口報告（2017整年缺失、RC-2016-3、RC-2012-2）

## 2026-06-07

- **[REINDEX+INGEST]** 題庫補齊，新增 6 題（RC-2012-2、RC-2016-3、RC-2017-1~4）
  - question_index.json：共 100 題（verified+hasSolution：100 題）
  - wiki/problems/：新增 6 個頁面
  - wiki/by-year.md、wiki/index.md：重建完成
  - 題庫缺口報告更新：無缺口

## 2026-06-07

- **[CLEANUP-2]** 清除 SS 殘留 56 個（code-ref/22、philosophy/10、diagnosis/8、failure-modes/5、materials/5、queries/6）
- **[REBUILD]** 重建各目錄 RC 版 index.md（6 個目錄）
- **[ADD]** 補建 wiki/diagnosis/seismic.md

## 2026-06-08

- **[COMPILE-ALL]** 全面重建 wiki 知識庫（compile-all + ingest 完整驗證）
  - 確認 wiki/concepts/：17 個概念頁面（BALANCED-REINFORCEMENT-RATIO 至 CRACK-WIDTH 全部存在）
  - 確認 wiki/problems/：100 個題目頁面（2002–2025 全部 verified 題目）
  - 重建 wiki/index.md：採七層知識架構 + 四單元分類導航格式，含全部 100 題連結
  - 確認 wiki/by-year.md：2002–2025 完整年份表格（無需修改）
  - **[NEW]** 建立 wiki/traps/：13 個陷阱頁面 + index.md（T形梁、φ值、耐震Ve、預力fps、預力損失、扭力門檻、衝剪、細長柱、平衡鋼筋比、雙筋梁壓力筋、梁柱接頭、剪力臨界斷面、有效慣性矩）
  - **[LINT]** 執行 16 項健檢，結果：11項PASS、2項WARNING、3項SKIP（需bash）；完整報告：wiki/queries/lint-report-2026-06-08.md
  - **[FIX-1]** 同步 STIRRUP-DESIGN 至 concepts.json（第 18 個概念）
  - **[FIX-2]** 建立 wiki/code-ref/ 實體頁面（ACI-318.md、CNS-1480.md、seismic-code.md），更新 index.md；code-ref 從 stub 升格為完整規範速查層
  - 操作者：Cowork

## 2026-06-09

- **[COMPILE-ALL]** 全面重建 wiki 知識庫（全部修正），compile-all 第二次完整執行
  - 全部 100 題 wiki/problems/ 頁面確認（2002–2025 年，100 題均 verified）
  - **[CONCEPTS]** 24 個概念頁面全部以 §7.2 完整格式重新生成：
    - BALANCED-REINFORCEMENT-RATIO、WHITNEY-STRESS-BLOCK、BETA1-FACTOR
    - PM-INTERACTION-DIAGRAM、BALANCED-POINT、EFFECTIVE-MOMENT-OF-INERTIA
    - CRACKING-MOMENT、PRESTRESS-LOSS、EFFECTIVE-PRESTRESS、STRONG-COLUMN-WEAK-BEAM
    - SHEAR-STRENGTH、TORSION-DESIGN、PUNCHING-SHEAR、SEISMIC-DESIGN
    - DEVELOPMENT-LENGTH、DEFLECTION-CONTROL、CRACK-WIDTH、STIRRUP-DESIGN
    - DUCTILE-FAILURE、LONG-COLUMN-MOMENT-MAGNIFIER、LONG-TERM-DEFLECTION
    - CREEP-SHRINKAGE、SPECIAL-MOMENT-FRAME-BEAM、SPECIAL-MOMENT-FRAME-COLUMN
  - 格式特徵：每頁含完整 LaTeX 公式（$$...$$）、定義段落、前置概念、相關概念、常見陷阱、出現題目表格
  - **[INDEX]** 重建 wiki/index.md：七層知識架構表 + 24 概念快速導覽表（依四單元分類）+ 全 100 題連結
  - **[BY-YEAR]** 重建 wiki/by-year.md：2002–2025 年全 100 題，改為 [[RC-YYYY-N]] Obsidian 連結格式
  - 操作者：Cowork

## 2026-06-09

- **[METHODS]** 建立 wiki/methods/ 完整解題方法論目錄（Layer 3）
  - 新建 index.md：列出 8 個方法論頁面
  - 新建 WHITNEY-STRESS-BLOCK-METHOD.md（等值矩形應力塊，RC-U1-1/U1-2）
  - 升級 PM-INTERACTION-DIAGRAM.md（原 stub → 完整版含 LaTeX 公式與出現題目表）
  - 新建 MOMENT-MAGNIFIER.md（長柱放大彎矩法，RC-U1-3）
  - 新建 EFFECTIVE-INERTIA.md（有效慣性矩撓度計算法，RC-U3-1）
  - 新建 PRESTRESS-LOSS-CALC.md（預力損失計算流程，RC-U4-3）
  - 新建 T-BEAM-ANALYSIS.md（T 形梁彎矩強度分析法，RC-U1-1）
  - 新建 FRICTION-LOSS-METHOD.md（摩擦損失計算法，RC-U4-3）
  - 新建 SEISMIC-CAPACITY-METHOD.md（耐震能力設計法，RC-U3-3）
  - 知識庫健康狀態：wiki/ 七層架構全部完整，無缺漏
  - 操作者：Cowork

## 2026-06-10

- **[FREQUENCY]** 執行 frequency 指令，生成 wiki/queries/frequency-20260610.md
  - 統計全 100 題（2002–2025）各 topicId 出現頻次（primary + secondary）
  - 結果：RC-U1-1=22、RC-U4-1=21、RC-U1-2=19、RC-U3-3=16、RC-U2-1=16
  - 操作者：Cowork

- **[PREDICT]** 執行 predict 指令，生成 wiki/queries/predict-2026-20260610.md
  - 基於頻次統計＋近年趨勢＋補考點分析推測 2026 高機率考題
  - 優先補考點：RC-U3-1（8 年未考）、RC-U4-3（7 年未考）、RC-U1-3（10 年未考）
  - 操作者：Cowork

- **[RAW-METHODS]** 補建 raw/solutions/methods/ 來源檔案（4 個方法論 .md）
  - 新建 raw/solutions/methods/effective-inertia-deflection/effective-inertia-deflection.md
  - 新建 raw/solutions/methods/moment-magnifier-method/moment-magnifier-method.md
  - 新建 raw/solutions/methods/prestress-loss-calculation/prestress-loss-calculation.md
  - 新建 raw/solutions/methods/pm-interaction-diagram/pm-interaction-diagram.md
  - 修正 raw/→wiki/ 單向資料流缺口，4 個 wiki/methods/ 頁面現有對應原始檔
  - 操作者：Cowork

- **[TRAPS-BACKLINKS]** 建立 traps↔problems 雙向連結
  - 讀取全部 13 個 wiki/traps/ 陷阱頁，建立完整 trap→problem 對應表
  - 在 52 個 wiki/problems/ 頁末尾加入「## 相關陷阱」反向連結區塊
  - 涵蓋陷阱：T-BEAM-EFFECTIVE-WIDTH、BALANCED-RATIO-BOUNDARY、PHI-FACTOR-TRANSITION、COMPRESSION-STEEL-YIELDING、SHEAR-CRITICAL-SECTION、TORSION-THRESHOLD、DEFLECTION-EFFECTIVE-INERTIA、PUNCHING-SHEAR-CRITICAL、SEISMIC-BEAM-VE、JOINT-SHEAR-EFFECTIVE-AREA、LONG-COLUMN-SLENDERNESS、PRESTRESS-LOSS-SEQUENCE、PRESTRESS-FPS-FORMULA
  - wiki/traps/ 雙向連結完整度：13/13 陷阱頁均建立反向連結
  - 操作者：Cowork

## 2026-06-11

- **[HEALTH-CHECK]** 知識庫一致性健檢（補完 2026-06-08 lint 報告的 4 項 SKIP 掃描）
  - hasViz 比對：索引 14 題 hasViz=true ↔ raw/solutions/ 實際 16 個 *-viz.html（RC-2014-2、RC-2014-4 各 2 個），完全一致 ✅
  - hasHandwritten 比對：索引 0 題 ↔ 實際 0 個 *hand*.png，一致 ✅
  - 圖說掃描：59 個含 fig-*.png 的解析檔全部具備「圖說：」段落 ✅
  - lint 待補清單覆核：code-ref 實體頁 ✅、STIRRUP-DESIGN 已入 concepts.json ✅、raw methods 來源 ✅（均已於 06-08~06-10 解決）
  - 結論：資料層無待修項
  - 操作者：Cowork

- **[DASHBOARD]** 建立知識庫儀表板（新增使用者入口）
  - 新建 dashboard.html（離線單檔，雙擊即用）：題庫瀏覽（年份/單元/考點/設計法/標籤/關鍵字篩選）、考點統計圖、近5年走向、高頻標籤、讀書進度追蹤（localStorage）、七層架構導覽、16 指令速查
  - 新建 dashboard-data.js（question_index.json 快照，100 題）
  - 新增指令 REFRESH-DASHBOARD（觸發語句「更新儀表板資料」），登錄於 CLAUDE-CODE.md
  - 操作者：Cowork

- **[DASHBOARD-v2]** 儀表板新增站內解析閱讀器
  - 「完整解析」改於站內彈窗開啟：內建 Markdown 渲染器（標題/表格/清單/引用/程式碼區塊/圖片）＋ KaTeX 公式渲染（$...$ 與 $$...$$，CDN 載入、離線時顯示原始 LaTeX）
  - 因瀏覽器 file:// 安全限制，採 File System Access API：首次使用授權選擇 exam-wiki-RC 資料夾一次（儲存於 IndexedDB），即可讀取所有解析檔與附圖
  - 題目附圖以 Blob URL 載入；解析內 .md 相對連結可於閱讀器內跳轉
  - 移除題卡「wiki 題目頁」連結（依使用者要求）；知識庫導覽卡片也改走站內閱讀器
  - 操作者：Cowork

- **[DASHBOARD-v3]** 解析閱讀器新增「匯出 PDF」按鈕
  - 採瀏覽器原生列印管道（目的地選「另存為 PDF」）：向量文字、中文與 KaTeX 公式完整保留、離線可用
  - 列印樣式僅輸出解析內容＋標頭（題號、來源路徑、匯出日期）；表格/圖片/公式避免跨頁截斷
  - 匯出時自動以題號設定預設 PDF 檔名
  - 操作者：Cowork

- **[METHODS-CONSOLIDATION]** 整併 wiki/methods/ 雙命名體系（lint 後續優化）
  - 問題：methods/ 同時存在大寫頁（8 個，06-09 建立、index 引用、無 raw 來源）與 kebab 頁（3 個，06-10 raw 對應版），4 組內容重複；且多數大寫頁「出現題目」表與 question_index 不符（如 EFFECTIVE-INERTIA 原列 4 題中 3 題為剪力牆/預力/扭力題）
  - 整併為 8 個 kebab-case 方法頁（符合 CLAUDE-SPEC 命名規範）：whitney-stress-block-method、pm-interaction-diagram、moment-magnifier-method、t-beam-analysis、effective-inertia-deflection、seismic-capacity-method、prestress-loss-calculation、friction-loss-method
  - 所有「出現題目」表依 question_index.json 標籤重新核實重建
  - 補建 4 個 raw 來源：whitney-stress-block-method、t-beam-analysis、friction-loss-method、seismic-capacity-method；更新既有 4 個 raw 來源為完整版（與 wiki 頁同步）
  - 重寫 wiki/methods/index.md（8 法索引）
  - MOMENT-MAGNIFIER.md、EFFECTIVE-INERTIA.md、PRESTRESS-LOSS-CALC.md 改為廢棄轉址 stub
  - 操作者：Cowork

- **[ARCHIVE]** raw/json/ 暫存檔歸檔至 study/_archive/
  - pdf_text.txt、pdf_2016_blocks.txt、pdf_2016_text.txt 已複製到 study/_archive/（附 README 說明）
  - 操作者：Cowork

- **[PENDING-DELETE]** 待刪除清單（沙箱環境因磁碟空間不足無法啟動，刪除作業暫緩）
  - raw/json/pdf_text.txt、raw/json/pdf_2016_blocks.txt、raw/json/pdf_2016_text.txt（已歸檔至 study/_archive/）
  - wiki/methods/MOMENT-MAGNIFIER.md、EFFECTIVE-INERTIA.md、PRESTRESS-LOSS-CALC.md（廢棄轉址 stub）
  - raw/solutions/RC-2015-1 ~ RC-2015-4 等資料夾內的 .placeholder 空檔
  - 檔名大小寫正規化：PM-INTERACTION-DIAGRAM.md → pm-interaction-diagram.md 等 5 檔（Windows 大小寫不敏感，連結已可解析，僅顯示名稱待改）
  - 環境恢復後對 Cowork 說「清理待刪除檔案」即可執行
  - 操作者：Cowork
