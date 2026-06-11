# 解題方法論層（Layer 3）

> **用途：** 每頁說明一種跨題目使用的「解題工具」——原理、步驟、邊界條件表、出現題目。
> **格式說明：** 公式為主，步驟流程為輔，與 wiki/philosophy/ 互補（philosophy 答「為什麼」，methods 答「怎麼算」）。
> **命名規範：** 依 CLAUDE-SPEC，檔名採全小寫連字號（kebab-case），與 raw/solutions/methods/ 來源一一對應。

---

## 方法論索引

| 方法 ID | 方法名稱 | 適用題型 |
|--------|---------|---------|
| [whitney-stress-block-method](whitney-stress-block-method.md) | Whitney 等值矩形應力塊法 | RC-U1-1, RC-U1-2 |
| [pm-interaction-diagram](pm-interaction-diagram.md) | P-M 互制圖計算法 | RC-U1-2, RC-U1-4 |
| [moment-magnifier-method](moment-magnifier-method.md) | 長柱放大彎矩法（δns / δs） | RC-U1-3 |
| [t-beam-analysis](t-beam-analysis.md) | T 形梁彎矩強度分析法 | RC-U1-1 |
| [effective-inertia-deflection](effective-inertia-deflection.md) | 有效慣性矩撓度計算法 | RC-U3-1 |
| [seismic-capacity-method](seismic-capacity-method.md) | 耐震能力設計法 | RC-U3-3 |
| [prestress-loss-calculation](prestress-loss-calculation.md) | 預力損失計算流程 | RC-U4-3 |
| [friction-loss-method](friction-loss-method.md) | 摩擦損失計算法（後拉法） | RC-U4-3 |

---

> **整併紀錄（2026-06-11）：** 原雙命名體系（大寫頁＋kebab 頁）已整併為上列 8 個 kebab-case 頁，
> 各頁「出現題目」表均依 question_index.json 標籤重新核實。
> 廢棄轉址頁（MOMENT-MAGNIFIER / EFFECTIVE-INERTIA / PRESTRESS-LOSS-CALC）待檔案系統操作可用時刪除。
> 大寫檔名（如 PM-INTERACTION-DIAGRAM.md）在 Windows 下與 kebab-case 連結等效，檔名正規化同樣待後續處理。

---

> **提示：** 備考時先用 wiki/philosophy/ 理解「為什麼這樣設計」，再用 wiki/methods/ 熟練「手算步驟」，最後在 wiki/problems/ 套用到歷年考題。
