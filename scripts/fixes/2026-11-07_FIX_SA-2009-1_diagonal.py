"""FIX-SA-2009-1：§4 Step 3–4 斜桿 bd → ec（題目正本判讀 #7；考卷第 1 頁第一題附圖，PyMuPDF 450 dpi）。
反力與 boxed 不變；補最終桿力；§1 常見誤讀、§5 補說明。可重複執行。"""
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "raw/solutions/SA-2009-1/SA-2009-1.md"
t = p.read_text(encoding="utf-8")
if "FIX-SA-2009-1" in t:
    print("already"); raise SystemExit
a = t.index("接下來，使用節點法求出各桿件內力 $u_i$：")
b = t.index("$$ \\sum u_i^2 L_i")
NEW = r"""接下來，使用節點法求出各桿件內力 $u_i$（右側面板斜桿為 **e–c**，見題目正本判讀 #7）：
*   **節點 a**：
    *   $\sum F_y = 0 \implies u_{ab} \times \frac{3}{5} - \frac{3}{8} = 0 \implies u_{ab} = \frac{5}{8}$ (張力)
    *   $\sum F_x = 0 \implies u_{ae} + u_{ab} \times \frac{4}{5} = 0 \implies u_{ae} = -\frac{1}{2}$ (壓力)
*   **節點 d**（只接 ed、cd 兩桿，受向左單位力）：
    *   $\sum F_x = 0 \implies -u_{ed} - 1 = 0 \implies u_{ed} = -1$ (壓力)
    *   $\sum F_y = 0 \implies u_{cd} = 0$
*   **節點 e**：
    *   $\sum F_x = 0 \implies -u_{ae} + u_{ed} + u_{ec} \times \frac{4}{5} = 0 \implies \frac{1}{2} - 1 + 0.8\,u_{ec} = 0 \implies u_{ec} = \frac{5}{8}$ (張力)
    *   $\sum F_y = 0 \implies u_{be} + u_{ec} \times \frac{3}{5} = 0 \implies u_{be} = -\frac{3}{8}$ (壓力)
*   **節點 b**：
    *   $\sum F_x = 0 \implies u_{bc} - u_{ab} \times \frac{4}{5} = 0 \implies u_{bc} = \frac{1}{2}$ (張力)
    *   $\sum F_y = 0 \implies -u_{be} - u_{ab} \times \frac{3}{5} = \frac{3}{8} - \frac{3}{8} = 0$ ✓（檢核）
*   **節點 c**（檢核）：$\sum F_x = -u_{bc} - u_{ec} \times \frac{4}{5} + R_{cx}^{(u)} = -\frac{1}{2} - \frac{1}{2} + 1 = 0$ ✓；$\sum F_y = -u_{ec} \times \frac{3}{5} - u_{cd} + R_{cy}^{(u)} = -\frac{3}{8} - 0 + \frac{3}{8} = 0$ ✓

各桿件長度 $L_i$ 與內力 $u_i$ 整理：
$L_{ab} = 5\text{ m}, L_{ae} = 4\text{ m}, L_{be} = 3\text{ m}, L_{bc} = 4\text{ m}, L_{ec} = 5\text{ m}, L_{cd} = 3\text{ m}, L_{ed} = 4\text{ m}$

**Step 4: 柔度係數 $f_{11}$ 與相容方程式求解**
$$ f_{11} = \sum \frac{u_i^2 L_i}{AE} $$
*   ab: $(5/8)^2 \times 5 = 125/64$
*   ae: $(-1/2)^2 \times 4 = 64/64$
*   be: $(-3/8)^2 \times 3 = 27/64$
*   bc: $(1/2)^2 \times 4 = 64/64$
*   ec: $(5/8)^2 \times 5 = 125/64$
*   cd: $0$
*   ed: $(-1)^2 \times 4 = 256/64$

"""
t = t[:a] + NEW + t[b:]
old_sum = r"$$ \sum u_i^2 L_i = \frac{125 + 64 + 0 + 256 + 125 + 27 + 64}{64} = \frac{661}{64}\text{ m} $$"
assert old_sum in t
t = t.replace(old_sum, r"$$ \sum u_i^2 L_i = \frac{125 + 64 + 27 + 64 + 125 + 0 + 256}{64} = \frac{661}{64}\text{ m} $$")
# 最終桿力（Step 5 之後、§5 之前）
key = "\n## 5. 關鍵爭議點"
add = r"""
4.  **各桿最終內力**（題目未問，供核對；0-系統桿力為 0，故 $N_i = u_i X_1$，$X_1 = \frac{24000}{661}$ kN）：
    $N_{ab} = N_{ec} = \frac{15000}{661} = +22.69$ kN（拉）、$N_{bc} = \frac{12000}{661} = +18.15$ kN（拉）、$N_{ae} = -18.15$ kN（壓）、$N_{be} = -\frac{9000}{661} = -13.62$ kN（壓）、$N_{ed} = -36.31$ kN（壓）、$N_{cd} = 0$。
"""
t = t.replace(key, add + key, 1)
# §1 常見誤讀
row_key = "| 作用 | 只有 a 向下沉陷 0.1 m，無外加載重 | 另加載重 |"
assert row_key in t
t = t.replace(row_key, row_key + "\n| 右側面板斜桿 | e–c（e 在下弦中點、c 在右上鉸支承） | b–d（本題舊版解析；兩對角線等長，反力碰巧相同，但桿力全錯） |")
# §5 說明
s5 = "- **剛架 vs 桁架的支承沉陷**："
assert s5 in t
t = t.replace(s5, "- **斜桿取錯為何反力不變**：右側面板 b–c–d–e 為 4 m × 3 m 矩形，兩條對角線都是 5 m。單位力系統中，斜桿只負責把節點 e 與 b、c、d 間的剪力傳過面板；改用 b–d 斜桿時各桿 $u_i$ 的絕對值會在 be／cd、bc／ed 之間互換，$\\sum u_i^2 L_i$ 仍為 661/64，贅力與反力因此完全相同——但桿力不同（例：$N_{cd}$ 由 0 變 13.62 kN）。只問反力的題目，答案對不代表模型對。\n" + s5)
t = t.rstrip("\n") + "\n*修正日期：2026-11-07（FIX-SA-2009-1 解析勘誤：§4 Step 3–4 右側面板斜桿由 bd 改為 ec（題目正本判讀 #7；考卷第 1 頁第一題附圖 450 dpi），u 值與 f₁₁ 逐桿表重列，Σu²L 仍為 661/64，X₁、四個反力與 boxed 不變；補最終桿力；§1 常見誤讀、§5 補說明。驗證：recalc_SA-2009-1.py 柔度法＋直接勁度法兩路徑，MISMATCHES: 0）*\n"
p.write_text(t, encoding="utf-8"); print("ok")
