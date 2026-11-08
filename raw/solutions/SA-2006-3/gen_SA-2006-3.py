#!/usr/bin/env python3
"""SA-2006-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2006-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2006-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2006-3"

# ── 判讀清單 #1–#6 ──（單位 m）
N_ = {"A": (0, 0), "B": (6, 0), "C": (14, 0), "D": (18, 0), "E": (26, 0), "F": (32, 0)}   # #2
SPEC = dict(
    nodes=N_,
    members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}, {"ij": ("D", "E")}, {"ij": ("E", "F")}],
    supports=[("A", "pin", 0)] + [(k, "roller", 0) for k in "BCDEF"],                    # #1
    udl=[("B", "C", 1.6, "1.2 kN/m"), ("D", "E", 1.6, "1.2 kN/m")],                     # #5
    labels={k: (0, 50) for k in "ABCDEF"},
    dims=[((0, 0), (6, 0), "6 m", 84), ((6, 0), (14, 0), "8 m", 84), ((14, 0), (18, 0), "4 m", 84),
          ((18, 0), (26, 0), "8 m", 84), ((26, 0), (32, 0), "6 m", 84)],
    extra_pts=[(-1.5, 3.2), (33.5, -1)])

def _post(cv, N):                                                                                 # #3 #4
    cv.moment_arrow(N["A"], r=24, ccw=False, span=190, start=185, color=C["load"])   # A 順時針：自左下繞上方到右
    cv.moment_arrow(N["F"], r=24, ccw=True, span=190, start=-5, color=C["load"])     # F 逆時針：自右下繞上方到左
    cv.math(N["A"], "5 kN-m", 15, C["load"], "middle", dy=-46, weight="700")
    cv.math(N["F"], "5 kN-m", 15, C["load"], "middle", dy=-46, weight="700")

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 860, 360, post=_post,
                              note="A 鉸支承、B～F 滾支承；A 端順時針、F 端逆時針（鏡射對稱）；E、I 常數",
                              margins=(50, 50, 60, 110))

FIGURES = [(fig1_problem, "兩端外加彎矩方向讀反、均佈放錯跨")]

# ── 解題圖（階段 E，2026-11-08）：勁度法重解（EI = 1），assert 對照 SA-2006-3.md §4–§5 ──
#    M_A = M_F = +5（下緣受拉）、M_B = M_E = −163/30、M_C = M_D = −59/15 kN-m；BC、DE 跨最大 +4.93 kN-m（距 B 約 4.16 m）
def _solve():
    from frame2d import Frame
    f = Frame()
    for n, p in N_.items(): f.node(n, *p)
    f.support("A", 1, 1, 0)
    for n in "BCDEF": f.support(n, 0, 1, 0)
    for (i, j), w in zip(zip("ABCDE", "BCDEF"), (0, 1.2, 0, 1.2, 0)): f.member(i + j, i, j, 1.0, w=w)
    f.load("A", mz=-5.0); f.load("F", mz=+5.0)                  # A 順時針、F 逆時針（frame2d 逆時針為正）
    f.solve()
    from frameviz import member_moment
    M = lambda nm, xi: member_moment(f, next(m for m in f.M if m["name"] == nm), xi)
    assert abs(M("AB", 0) - 5) < 1e-9 and abs(M("EF", 1) - 5) < 1e-9
    assert abs(M("AB", 1) + 163/30) < 1e-9 and abs(M("CD", 0) + 59/15) < 1e-9 and abs(M("CD", 1) + 59/15) < 1e-9
    xm = max((k / 4000 for k in range(4001)), key=lambda x: M("BC", x))
    assert abs(M("BC", xm) - 4.93) < 0.005 and abs(8 * xm - 4.16) < 0.01
    return f, M, xm

def fig2_bmd():
    from beamfig import beam_strip
    f, M, xm = _solve()
    def extra(a, b):
        b.text_px(b.X(6 + 8 * xm), b.Y(0) + 104, f"+{M('BC', xm):.2f}（距 B {8*xm:.2f} m）", 13, C["bmd"], weight="700")
        b.text_px(b.X(26 - 8 * xm), b.Y(0) + 104, f"+{M('BC', xm):.2f}（距 E {8*xm:.2f} m）", 13, C["bmd"], weight="700")
        b.text_px(b.X(16), b.Y(0) + 40, "CD 跨無載重：全長 −3.93（上緣受拉）", 12.5, C["accent"], weight="700")
    return beam_strip(f, ["AB", "BC", "CD", "DE", "EF"], f"{OUT}/{TAG}-fig-2-bmd.svg",
        "圖 2　SA-2006-3 變形形狀與彎矩圖", W=980, H1=240, H2=330, prec=2,
        supports=[("A", "pin")] + [(n, "roller") for n in "BCDEF"],
        mlabels=[("AB", 0.0, "R", True), ("AB", 1.0, "C", False), ("CD", 0.0, "C", False), ("EF", 0.0, "C", False), ("EF", 1.0, "L", True)],
        sub_def="A、F 外加彎矩使端部下緣受拉；BC、DE 跨下垂、CD 跨上拱；對 CD 跨中點對稱",
        sub_bmd="A +5 → B −5.43 → C −3.93 ＝ D → E −5.43 → F +5（對稱）",
        note="A、F 是鉸／滾支承但有外加彎矩：梁端彎矩 = 外加彎矩 5 kN-m（下緣受拉），不是 0", extra=extra)

FIGURES.append((fig2_bmd, "A、F 端彎矩當成 0（鉸支承）；外加彎矩方向讀反使端部受拉側畫反；CD 跨畫成正彎矩"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
