#!/usr/bin/env python3
"""SA-2021-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-1"

# ── 判讀清單 #1–#6 ──
N_ = {"a": (0, 0), "P": (2, 0), "b": (4, 0), "c": (8, 0), "d": (10, 0)}       # #5
SPEC = dict(
    nodes=N_, members=[{"ij": ("a", "b")}, {"ij": ("b", "c")}, {"ij": ("c", "d")}],
    supports=[("a", "roller"), ("d", "fixed")],                               # #1、#4
    hinges=["c"],                                                             # #3
    springs=[("b", 1.9, "k")],                                                # #2
    loads=[("P", (0, -1.6), "36 kN", (0, -14)), ("b", (0, -1.6), "36 kN", (0, -14))],   # #6
    labels={"a": (-4, -20), "b": (16, -14), "c": (0, -18), "d": (-14, -16)},
    dims=[((0, 0), (2, 0), "2 m", 104), ((2, 0), (4, 0), "2 m", 104), ((4, 0), (8, 0), "4 m", 104), ((8, 0), (10, 0), "2 m", 104)],
    extra_pts=[(-0.8, 2.4), (10.8, -3.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 420,
                          note="a 滾支承；b 點彈簧 k = 15000 kN/m；c 內鉸；d 固定端；EI = 10000 kN-m^{2}")

FIGURES = [(fig1_problem, "c 讀成支承、彈簧位置讀錯")]

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解，與 SA-2021-1.md §4 Step 6–7 對照（assert）──
#    Δ_b = 57/15000 m ↓、θ_b = −37/20000 rad（順時針為正 ⇒ 逆時針）、Δ_c = 1/2500 m ↑、M_b = −6、ab 中點 +33、M_d = +3 kN-m
def _solve():
    from frame2d import Frame
    f = Frame(); EI = 10000.0
    for n, p in {**N_, "s": (4, -1)}.items(): f.node(n, *p)
    f.support("a", 0, 1, 0); f.support("d", 1, 1, 1); f.support("s", 1, 1, 1)
    f.member("aP", "a", "P", EI); f.member("Pb", "P", "b", EI)
    f.member("bc", "b", "c", EI, rel=(0, 1)); f.member("cd", "c", "d", EI, rel=(1, 0))   # c 內鉸
    f.member("bs", "b", "s", 1e-6, rel=(1, 1), EA=15000.0)                                # 彈簧 k（長 1 m 二力桿）
    f.load("P", fy=-36); f.load("b", fy=-36)
    f.solve()
    from frameviz import member_moment
    M = lambda nm, xi: member_moment(f, next(m for m in f.M if m["name"] == nm), xi)
    assert abs(-f.d["b"][1] - 57/15000) < 1e-9 and abs(f.d["b"][2] - 37/20000) < 1e-9
    assert abs(f.d["c"][1] - 1/2500) < 1e-9
    assert abs(M("aP", 1.0) - 33) < 1e-6 and abs(M("Pb", 1.0) + 6) < 1e-6 and abs(M("cd", 1.0) - 3) < 1e-6
    return f

def fig2_solution():
    from beamfig import beam_strip
    f = _solve()
    xi_b = 72 / 19.5                                            # ab 段 M(x) = 72 − 19.5x = 0（§4 Step 7）
    def extra(a, b):
        b.text_px(b.X(xi_b) + 14, b.Y(0) + 40, f"反曲點 x = {xi_b:.3f} m（距 b {4 - xi_b:.3f} m）", 12.5, C["accent"], anchor="start", weight="700")
        b.text_px(b.X(8), b.Y(0) + 26, "c 鉸 M = 0", 12.5, C["muted"])
        a.text_px(a.X(4), a.Y(f.d["b"][1] * 0) - 46, "θb = 0.00185 rad（逆時針）", 13, C["deform"], weight="700")
    return beam_strip(f, ["aP", "Pb", "bc", "cd"], f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2021-1 變形形狀與梁彎矩圖", W=900, H1=245, H2=300,
        supports=[("a", "roller"), ("d", "fixed")], hinges=["c"], springs=["b"],
        dlabels=[("b", "Δb = 3.80 mm（向下）", 40), ("c", "Δc = 0.40 mm（向上）", -22)],
        mlabels=[("aP", 1.0, "C", True), ("Pb", 1.0, "C", True), ("cd", 1.0, "L", True)],
        sub_def="b 隨彈簧下沉、c 鉸被 bc 翹起（蹺蹺板）",
        sub_bmd="a 0 → ab 中點 +33 → b −6 → c 0 → d +3",
        note="b 點彈簧力 57 kN（不是 54 kN）：ab 右端與 bc 左端的端彎矩剪力同號相加", extra=extra)

FIGURES.append((fig2_solution, "b 點剪力合成寫成同號抵銷（Δb 3.6 mm、Mb −6.35）；c 鉸點被畫成下沉；cd 段彎矩正負畫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
