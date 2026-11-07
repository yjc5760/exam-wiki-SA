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

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
