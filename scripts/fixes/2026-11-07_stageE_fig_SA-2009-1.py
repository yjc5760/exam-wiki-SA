"""SA-2009-1 階段 E（勘誤 FIX-SA-2009-1 落實後）：插入桁架力流圖函式、插圖與圖說。可重複執行。
共用碼（_Fmt、_truss、_truss_check）取自 2026-11-07_stageE_figs_SA-U2-2_B1.py 的 TRUSS_COMMON，原樣複用。"""
import os, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1] / "raw/solutions"
src = (HERE / "2026-11-07_stageE_figs_SA-U2-2_B1.py").read_text(encoding="utf-8")
common = re.search(r"TRUSS_COMMON = '''(.*?)'''", src, re.S).group(1)
SNIP = common + '''
# ── 解題圖（階段 E，2026-11-07，勘誤後）：取自 SA-2009-1.md §4 Step 3、5（N = u·X_1，X_1 = 24000/661）──
X9 = 24000/661
U9 = {("a", "b"): 5/8, ("a", "e"): -1/2, ("e", "d"): -1, ("c", "d"): 0, ("e", "c"): 5/8, ("b", "e"): -3/8, ("b", "c"): 1/2}
F9 = {k: (u*X9 if u else 0.0) for k, u in U9.items()}
R9 = {"a": (0, -3/8*X9), "c": (X9, 3/8*X9), "d": (-X9, 0)}

def fig2_truss():
    _truss_check(N_, F9, R9)
    _truss(N_, [(i, j, v) for (i, j), v in F9.items()],
           supports=[("a", "roller", 0), ("c", "pin", 90), ("d", "roller", 90)], loads=[], fmt=FMT,
           title=f"圖 2　{TAG} 桿力（kN，拉＋）—— 只由 a 點下沉 0.1 m 引起",
           note="斜桿為 e–c。反力：a_y 13.62↓、c_x 36.31→、c_y 13.62↑、d_x 36.31←；cd 為零桿",
           path=f"{OUT}/{TAG}-fig-2-truss.svg", W=720, H=520)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "斜桿畫成 b–d（本題舊版解析）；以為支承沉陷不產生桿力"))
'''
p = ROOT / "SA-2009-1" / "gen_SA-2009-1.py"; t = p.read_text(encoding="utf-8")
if "階段 E" not in t:
    key = '\nif __name__ == "__main__":'; assert t.count(key) == 1
    if not re.search(r"^import [^\n]*\bmath\b", t, re.M): t = t.replace("import sys, os", "import sys, os, math", 1)
    p.write_text(t.replace(key, SNIP + key), encoding="utf-8"); print("gen inserted")
m = ROOT / "SA-2009-1" / "SA-2009-1.md"; t = m.read_text(encoding="utf-8")
fig = "figs/SA-2009-1-fig-2-truss.svg"
if fig not in t:
    lines = t.split("\n"); idx = [i for i, l in enumerate(lines) if "N_{cd} = 0" in l and "N_{ab}" in l]; assert len(idx) == 1
    lines[idx[0]] += ("\n\n![SA-2009-1 桿力圖：斜桿為 e–c；ab、ec +22.69、bc +18.15 受拉，ae −18.15、be −13.62、ed −36.31 受壓，cd 零桿；"
                      "反力 a_y 13.62 向下、c_x 36.31 向右、c_y 13.62 向上、d_x 36.31 向左](" + fig + ")\n\n"
                      "*圖 2　桿力（$N = u\\,X_1$；全節點平衡含反力殘差為 0 才繪製）。靜不定桁架受支承沉陷會產生桿力；斜桿是 e–c 而不是 b–d——"
                      "換成 b–d 反力不變但桿力全變，這張圖攔的就是這個看圖錯。*")
    t = "\n".join(lines).rstrip("\n") + "\n*修正日期：2026-11-07（非勘誤）圖解補繪：圖 2（gen_SA-2009-1.py，可重跑）*\n"
    m.write_text(t, encoding="utf-8"); print("md inserted")
