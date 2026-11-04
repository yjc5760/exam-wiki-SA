#!/usr/bin/env python3
"""SA-2007-2：題目附圖重繪（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2007-2-problem.md §4 判讀清單（註解中的 #n）。
用法：python3 gen_SA-2007-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2007-2"

# ── 判讀清單 #1–#6 ──
SPEC = dict(
    nodes={"A": (0, 0), "G": (0, 2), "C": (0, 4), "D": (6, 4), "E": (12, 4), "B": (6, 0)},
    members=[dict(name="AG", ij=("A", "G"), EI=1), dict(name="GC", ij=("G", "C"), EI=1),   # #4 柱 AC
             dict(name="CD", ij=("C", "D"), EI=2, thick=True), dict(name="DE", ij=("D", "E"), EI=2, thick=True),  # #3
             dict(name="BD", ij=("B", "D"), EI=1)],
    supports=[("A", "fixed"), ("B", "fixed"), ("E", "pin")],                                 # #1 #2
    udl=[("C", "E", 0.9, "2 kN/m")],                                                         # #5
    loads=[("G", (1.7, 0), "8 kN", (0, -16))],                                               # #6
    labels={"A": (-16, 14), "B": (16, 14), "C": (-16, -14), "D": (14, 16), "E": (6, -18)},
    mlabels=[((-0.45, 3.0), "I", None, "end"), ((6.45, 2.0), "I", None, "start"),
             ((3, 3.5), "2I", None, "middle"), ((9, 3.5), "2I", None, "middle")],
    dims=[((0, 0), (6, 0), "6 m", 48), ((6, 0), (12, 0), "6 m", 48),
          ((0, 0), (0, 2), "2 m", -150), ((0, 2), (0, 4), "2 m", -150)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 520,
                          note="A、B 固接；E 鉸支承；2 kN/m 作用於 C–E 全長；8 kN 作用於 AC 中點")

FIGURES = [(fig1_problem, "均布載重範圍、8 kN 作用點、E 支承誤讀")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
