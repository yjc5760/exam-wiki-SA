#!/usr/bin/env python3
"""SA-2017-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2017-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2017-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2017-1"

# ── 判讀清單 #1–#6 ──（單位 m）
N_ = {"A": (0, 0), "B": (0, 4), "C": (0, 8), "D": (3, 4), "E": (6, 0)}                  # #2
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "B"), ("B", "C"), ("B", "D"), ("A", "D"), ("C", "D"), ("D", "E")],      # #3 #4 #5：AD 斜桿，無 AC、BE
    joints=list(N_),
    supports=[("A", "pin", 0), ("E", "pin", 0)],                                          # #1
    loads=[("C", (1.6, 0), "12 kN", (-32, -14)), ("B", (1.6, 0), "9 kN", (-30, -14))],    # #6
    labels={"A": (16, 6), "B": (16, 14), "C": (16, -12), "D": (16, -10), "E": (18, 6)},
    dims=[((0, 0), (0, 4), "4 m", -112), ((0, 4), (0, 8), "4 m", -112),
          ((0, 0), (3, 0), "3 m", 62), ((3, 0), (6, 0), "3 m", 62)],
    extra_pts=[(-2.6, 8.4), (6.5, -1.0)])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 520, 560,
                              note=["6 根桿：AB、BC、BD、AD、CD、DE（C、D、E 共線）", "A、E 鉸支承；E、A 為定值"],
                              margins=(90, 60, 50, 120))

FIGURES = [(fig1_problem, "把 A–D 斜桿讀成 B–E、多補一根 A–C 全高桿")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
