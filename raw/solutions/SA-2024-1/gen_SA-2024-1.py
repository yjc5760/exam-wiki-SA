#!/usr/bin/env python3
"""SA-2024-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2024-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2024-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2024-1"

# ── 判讀清單 #1–#6 ──（單位 m）
N_ = {"A": (0, 0), "B": (4, 0), "C": (8, 0), "D": (12, 0)}                                       # #6
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "roller", 0), ("D", "fixed")],                                                 # #1 #5
    hinges=["C"],                                                                                  # #4
    loads=[("B", (0, -2.2), "100 kN", (0, -14))],                                                  # #3
    labels={"A": (0, -48), "B": (-14, 16), "C": (0, -22), "D": (-16, -16)},
    dims=[((0, 0), (4, 0), "4 m", 66), ((4, 0), (8, 0), "4 m", 66), ((8, 0), (12, 0), "4 m", 66)],
    extra_pts=[(-2.6, 2.8), (12.6, -1.2)])

def _post(cv, N):                                                                                 # #2 逆時針
    cv.moment_arrow(N["A"], r=26, ccw=True, span=200, start=-15, color=C["load"])
    cv.math(N["A"], "200 kN-m", 15, C["load"], "end", dx=-36, dy=-20, weight="700")

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 340, post=_post,
                              note="A 滾支承並受 200 kN-m 逆時針；C 內鉸；D 固定端；EI 常數；容許位移 40 mm（上、下皆同）",
                              margins=(60, 60, 50, 100))

FIGURES = [(fig1_problem, "A 端彎矩方向讀反、漏讀 C 內鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
