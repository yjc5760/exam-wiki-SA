#!/usr/bin/env python3
"""SA-2012-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2012-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2012-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2012-1"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"a": (0, 0), "b": (4, 0), "c": (8, 0), "d": (12, 0), "e": (16, 0)},   # #5
    members=[dict(ij=("a", "c"), thick=True), dict(ij=("c", "e"))],           # #6
    supports=[("a", "fixed"), ("d", "roller")],                               # #1 #3
    hinges=["c"],                                                             # #2
    loads=[("b", (0, -2.4), "40 kN", (0, -14)), ("e", (0, -2.4), "40 kN", (0, -14))],   # #7
    labels={"a": (-8, 22), "b": (0, 20), "c": (0, 22), "d": (0, -18), "e": (14, 18)},
    mlabels=[((6, -1.3), "2EI", None, "middle"), ((14, -1.3), "EI", None, "middle")],
    dims=[((0, 0), (4, 0), "4 m", 95), ((4, 0), (8, 0), "4 m", 95), ((8, 0), (12, 0), "4 m", 95), ((12, 0), (16, 0), "4 m", 95)],
    extra_pts=[(-0.6, 0), (16.4, 0), (0, -3.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 360,
                          note="a 固接；c 內鉸；d 滾支承；e 自由端；a–c 段 2EI、c–e 段 EI", margins=(80, 80, 60, 80))

FIGURES = [(fig1_problem, "c 讀成剛接、d 位置或剛度分段讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
