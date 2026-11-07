#!/usr/bin/env python3
"""SA-2014-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2014-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2014-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2014-3"

# ── 判讀清單 #1–#10 ──（以 L = 1 為單位）
R3 = math.sqrt(3) / 2
N_ = {"A": (0, 1), "B": (0, 0), "C": (0, -1), "D": (R3, 0), "E": (2 * R3, -0.5)}   # #5–#7
SPEC = dict(
    nodes=N_, members=[{"ij": ("B", "A")}, {"ij": ("B", "C")}, {"ij": ("B", "D")}, {"ij": ("D", "E")}],
    supports=[("A", "fixed"), ("C", "fixed"), ("E", "fixed")],                # #1–#3：E 支承面垂直 DE
    loads=[("B", (0.34, 0), "P = 66 kN", (-6, -16))],                       # #10
    labels={"A": (-18, 14), "B": (-14, 16), "C": (-18, -14), "D": (4, -16), "E": (12, 14)},
    mlabels=[((0.06, 0.5), "2I", None, "start"), ((0.06, -0.5), "2I", None, "start"), ((1.42, -0.12), "I", None, "middle")],
    ptexts=[((R3 / 2 + 0.12, 0.1), "√3 I", 14, None, "middle"),
            ((R3 / 2, -1.27), "√3 L/2", 13.5, None, "middle"), ((1.5 * R3, -1.27), "√3 L/2", 13.5, None, "middle")],
    dims=[((0, -1), (0, 0), "L", -104), ((0, 0), (0, 1), "L", -104),
          ((0, -1), (R3, -1), "", 32), ((R3, -1), (2 * R3, -1), "", 32), ((2 * R3, -0.5), (2 * R3, 0), "L/2", 46)],
    extra_pts=[(-0.95, 1.15), (2.05, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 560,
                          note="L = 8 m；A、C、E 皆固接；B、D 剛接；E 比 D 低 L/2，DE 實長 L")

FIGURES = [(fig1_problem, "DE 讀成水平、E 支承方向讀錯、各桿慣性矩對調")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
