#!/usr/bin/env python3
"""SA-2021-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-4"

# ── 判讀清單 #1–#6 ──（平面圖，單位 m；原點在平面中心）
N_ = {"C1": (-3, -2), "C2": (3, -2), "C3": (-3, 2), "C4": (3, 2)}                                # #1
SPEC = dict(nodes=N_, members=[], extra_pts=[(-4.6, -3.6), (4.6, 3.6)])

def _post(cv, N):
    cv.polygon([N["C1"], N["C2"], N["C4"], N["C3"]], "rgba(63,74,90,0.10)", "none")              # 剛性樓板
    for a, b, lab, off in (("C3", "C1", "B1", (0.35, 0)), ("C1", "C2", "B2", (0, 0.35)),
                           ("C2", "C4", "B3", (-0.4, -0.7)), ("C4", "C3", "B4", (-1.0, -0.35))):     # 梁 I＝∞
        cv.line(N[a], N[b], C["member"], 4.2, cap="butt")
        mx, my = (N[a][0] + N[b][0]) / 2 + off[0], (N[a][1] + N[b][1]) / 2 + off[1]
        cv.math((mx, my), lab, 15, C["muted"])
    for k, (x, y) in N.items():                                                                   # #2 柱斷面大小
        s = 0.17 if k in ("C1", "C3") else 0.30
        cv.polygon([(x - s, y - s), (x + s, y - s), (x + s, y + s), (x - s, y + s)], C["member"], C["member"], 1)
        cv.math((x, y), k, 15, C["text"], "middle", dx=(-24 if x < 0 else 26), dy=(18 if y < 0 else -16), weight="700")
    for k, (x, y) in N.items():                                                                   # #6 27 kN 沿 +y
        if y < 0: cv.arrow((x, y - 1.25), (x, y - 0.32), C["load"], 3.0, 11); lp = (x, y - 1.25); dy = 14
        else: cv.arrow((x, y + 0.32), (x, y + 1.25), C["load"], 3.0, 11); lp = (x, y + 1.25); dy = -12
        cv.math(lp, "27 kN", 14, C["load"], "middle", dx=(-30 if x < 0 else 30), dy=dy, weight="700")
    cv.axes((0, 0), 4.0, 2.9, ("x", "y"))
    cv.dim((-3, -2), (3, -2), "6 m", off=86)
    cv.dim((-3, -2), (-3, 2), "4 m", off=-92)

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 560, post=_post,
                              note=["C1、C3：EI_d＝9720 kN-m²；C2、C4：EI_e＝48600 kN-m²（兩方向相同；大方塊為 C2、C4）",
                                    "柱高 3.6 m、柱底固定、梁 I＝∞、樓板平面內剛性；不計柱扭轉勁度"],
                              margins=(70, 70, 50, 110))

FIGURES = [(fig1_problem, "EI 讀成一半（m² 的 2 當係數）、大小柱位置對調")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
