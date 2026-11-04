#!/usr/bin/env python3
"""SA-2010-2：題目附圖重繪（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2010-2-problem.md §4 判讀清單（註解中的 #n）。
用法：python3 gen_SA-2010-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2010-2"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (10, 0), "B": (10, 5), "C": (10, 10), "D": (0, 10)},
    members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BC", ij=("B", "C"), EI=1),
             dict(name="DC", ij=("D", "C"), EI=2, thick=True)],
    supports=[("A", "fixed"), ("D", "roller")],                       # #1 #2
    labels={"A": (18, 10), "B": (16, 0), "C": (16, -14), "D": (-16, -16)},
    mlabels=[((9.3, 2.5), "EI", None, "end"), ((5, 9.3), "2EI", None, "middle")],
    dims=[((0, 10), (10, 10), "10 m", -46), ((10, 0), (10, 5), "5 m", 52), ((10, 5), (10, 10), "5 m", 52)],
    extra_pts=[(0, 0)])

def fig1_problem():
    import sys
    sp = dict(SPEC); cvpre = None
    p = problem_figure(sp, f"{OUT}/{TAG}-fig-1-problem.svg", 520, 540,
                       note="A 固接；D 滾支承；B 為 AC 中點（實心點，非鉸）；EI = 1000 kN·m²")
    return p

FIGURES = [(fig1_problem, "B 讀成鉸、D 讀成鉸支（多一個水平束制）")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
