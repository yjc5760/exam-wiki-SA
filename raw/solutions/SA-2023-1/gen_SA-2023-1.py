#!/usr/bin/env python3
"""SA-2023-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2023-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2023-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2023-1"

# ── 判讀清單 #1–#5 ──（單位 m）
N_ = {"A": (0, 0), "B": (2, 0), "C": (6, 0), "D": (10, 0), "E": (12, 0), "F": (6, 4)}             # #2 #3
SPEC = dict(
    nodes=N_,
    members=[{"ij": ("A", "E")}, {"ij": ("C", "F")}],                                              # #3 C 剛接
    supports=[("B", "roller", 0), ("D", "pin", 0)],                                                # #1
    loads=[("F", (1.8, 0), "P", (10, -16), True)],                                                 # #4
    labels={"A": (0, -18), "B": (0, -18), "C": (16, -16), "D": (0, -18), "E": (0, -18), "F": (-16, -8)},
    dims=[((0, 0), (2, 0), "2 m", 66), ((2, 0), (6, 0), "4 m", 66), ((6, 0), (10, 0), "4 m", 66), ((10, 0), (12, 0), "2 m", 66),
          ((4.4, 0), (4.4, 4), "4 m", 0)],
    extra_pts=[(-0.5, 4.8), (12.5, -1.4)])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 420,
                              note=["B 滾支承、D 鉸支承；CF 於 C 剛接；D 支承下陷 3 mm；EI＝20,000 kN-m²"],
                              margins=(60, 60, 50, 110))

FIGURES = [(fig1_problem, "B、D 支承型式對調、CF 位置不在 C")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
