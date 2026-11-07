#!/usr/bin/env python3
"""SA-2021-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-2"

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 3), "b": (3, 3), "e": (9, 3), "f": (12, 3), "c": (3, 0), "d": (9, 0)}   # #5
SPEC = dict(
    nodes=N_, members=[{"ij": (x, y)} for x, y in (("a", "b"), ("b", "e"), ("e", "f"), ("b", "c"), ("e", "d"), ("c", "d"))],
    supports=[("a", "roller"), ("f", "roller"), ("d", "roller"), ("c", "pin")],   # #1–#3
    loads=[("f", (1.6, 0), "24 kN", (24, -14), True)],                        # #7
    labels={"a": (0, -18), "b": (0, -18), "e": (0, -18), "f": (-4, -18), "c": (-16, -10), "d": (16, -10)},
    dims=[((0, 0), (3, 0), "3 m", 56), ((3, 0), (9, 0), "6 m", 56), ((9, 0), (12, 0), "3 m", 56), ((0, 0), (0, 3), "3 m", -48)],
    extra_pts=[(-0.9, 4.0), (14.4, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 660, 400,
                          note="a、d、f 滾支承；c 鉸支承；框 b–e–d–c 各角剛接；EI = 20000 kN-m^{2}；不計軸向變形")

FIGURES = [(fig1_problem, "c、d 支承型式對調、把 c、d 當成桿件之間的鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
