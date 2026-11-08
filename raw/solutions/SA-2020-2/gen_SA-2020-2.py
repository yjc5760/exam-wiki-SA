#!/usr/bin/env python3
"""SA-2020-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2020-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2020-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-2"

# ── 判讀清單 #1–#6 ──
N_ = {"a": (0, 4), "b": (4, 4), "c": (8, 4), "d": (12, 4), "e": (0, 0), "f": (4, 0), "g": (8, 0), "h": (12, 0),
      "P1": (6, 4), "P2": (6, 0)}                                             # #3、#4
SPEC = dict(
    nodes=N_, members=[{"ij": (x, y)} for x, y in (("a", "b"), ("b", "c"), ("c", "d"), ("e", "f"), ("f", "g"),
                                                    ("g", "h"), ("b", "f"), ("c", "g"))],
    supports=[("a", "fixed"), ("d", "fixed"), ("e", "fixed"), ("h", "fixed")],   # #1
    loads=[("P1", (0, -1.5), "12 kN", (0, -14)), ("P2", (0, -1.5), "12 kN", (0, -14))],   # #6
    labels={"a": (16, -16), "b": (-12, -16), "c": (12, -16), "d": (-16, -16), "e": (16, 16), "f": (-12, 16), "g": (12, 16), "h": (-16, 16)},
    dims=[((0, 0), (4, 0), "4 m", 48), ((4, 0), (6, 0), "2 m", 48), ((6, 0), (8, 0), "2 m", 48),
          ((8, 0), (12, 0), "4 m", 48), ((12, 0), (12, 4), "4 m", 62)],
    extra_pts=[(-0.9, 6.0), (13.4, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 420,
                          note="a、d、e、h 固定端；b、c、f、g 剛接；bc = 4 m（中間刻度只標載重位置）；EI = 20000 kN-m^{2}")

FIGURES = [(fig1_problem, "把中間刻度當成柱位而讀成 bc = 2 m")]

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解，與 SA-2020-2.md §4 Step 5–6 對照（assert）──
#    EIθ_b = 8（順時針）、EIΔ = 48（向下）、M_ab = −14、M_ba = −10、M_bc = −2、M_bf = +12 kN-m（EI = 20000）
SOL = dict(nodes={k: v for k, v in N_.items()}, supports=[("a", "fixed"), ("d", "fixed"), ("e", "fixed"), ("h", "fixed")])

def _solve():
    from frame2d import Frame
    f = Frame(); EI = 20000.0
    for n, p in N_.items(): f.node(n, *p)
    for n in "adeh": f.support(n, 1, 1, 1)
    for nm, i, j in (("ab", "a", "b"), ("bP", "b", "P1"), ("Pc", "P1", "c"), ("cd", "c", "d"),
                     ("ef", "e", "f"), ("fP", "f", "P2"), ("Pg", "P2", "g"), ("gh", "g", "h"),
                     ("bf", "b", "f"), ("cg", "c", "g")):
        f.member(nm, i, j, EI)                                       # 不計軸向變形
    f.load("P1", fy=-12); f.load("P2", fy=-12)
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    assert abs(-f.d["b"][1] - 48/EI) < 1e-9 and abs(-f.d["b"][2] - 8/EI) < 1e-9
    assert all(abs(x - y) < 1e-6 for x, y in zip(cw("ab") + (cw("bP")[0], cw("bf")[0]), (-14, -10, -2, 12)))
    assert abs(f.d["f"][1] - f.d["b"][1]) < 1e-12                    # 上下對稱：bf 柱兩端同沉、軸力 0
    return f

def fig2_solution():
    from beamfig import frame_figure
    f = _solve()
    L = [("ab", 0.0, 4, -14), ("ab", 1.0, -26, 6), ("bP", 0.0, 24, 16), ("bP", 1.0, 0, 20),
         ("bf", 0.0, -22, 18), ("bf", 1.0, -22, -12), ("ef", 0.0, 4, 18), ("ef", 1.0, -10, 22), ("fP", 1.0, 0, 20)]
    return frame_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2020-2 變形形狀與彎矩圖（單位 kN-m）",
        "b、c、f、g 一起下沉 2.40 mm；柱 bf、cg 平移不轉弦",
        "左右對稱、上下兩層相同", L, fmt="{:.0f}", W=560, H=470,
        dlabels=[("b", "vb = 2.40 mm ↓", 0, -62)],
        notes=("θb = 0.0004 rad（順時針）", "ab 兩端 14、10；柱 bf 兩端 12；bc 中點 10"))

FIGURES.append((fig2_solution, "以為無側移就沒有垂直位移（漏了 b 點下沉）；ab 兩端彎矩同號被畫成反曲"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
