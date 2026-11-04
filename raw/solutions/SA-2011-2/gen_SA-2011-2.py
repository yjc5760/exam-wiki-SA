#!/usr/bin/env python3
"""SA-2011-2：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2011-2-problem.md §4 判讀清單（註解中的 #n）。
彎矩由勁度法重算，並 assert 與解析一致（M_AB = -436/15、M_CB = 16.40 kN-m）。
用法：python3 gen_SA-2011-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2011-2"

# ── 判讀清單 #1–#8（EI = 10000 kN·m²） ──
SPEC = dict(
    nodes={"A": (0, 3), "B": (3, 3), "C": (6, 3), "G": (7.5, 3), "D": (9, 3), "E": (6, 0)},
    members=[dict(name="AB", ij=("A", "B"), EI=2e4, thick=True), dict(name="BC", ij=("B", "C"), EI=1e4),
             dict(name="CG", ij=("C", "G"), EI=1e4), dict(name="GD", ij=("G", "D"), EI=1e4),
             dict(name="EC", ij=("E", "C"), EI=1e4)],
    supports=[("A", "fixed"), ("D", "pin"), ("E", "pin")],                               # #1 #2 #3
    loads=[("B", (0, -1.1), "30 kN", (0, -14)), ("G", (0, -1.1), "16 kN", (0, -14))],      # #8
    fe_loads=[("B", 0, -30, 0), ("G", 0, -16, 0)],
    labels={"A": (-22, -20), "B": (12, 16), "C": (-12, -16), "D": (4, -22), "E": (16, 6)},
    mlabels=[((1.5, 2.7), "2EI", None, "middle"), ((4.5, 2.7), "EI", None, "middle"),
             ((8.0, 2.7), "EI", None, "middle"), ((5.7, 1.5), "EI", None, "end")],
    dims=[((0, -0.5), (3, -0.5), "3 m", 26), ((3, -0.5), (6, -0.5), "3 m", 26), ((6, -0.5), (9, -0.5), "3 m", 26),
          ((6, 2.3), (7.5, 2.3), "1.5 m", 18), ((9.6, 0), (9.6, 3), "3 m", 30)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 780, 520,
                          note="A 固接；D、E 鉸支承；B 為斷面變化點（剛接）")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(M["AB"][0] + 436/15) < 1e-3 and abs(M["BC"][1] - 16.40) < 1e-3
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 300, 0.028,
        "SA-2011-2　無側移剛架（D、E 鉸支）", "C 節點轉角很小；柱 CE 單曲率",
        "單位 kN·m", munit="", fmt="{:.2f}", W=600, H=440,
        notes=("", "C 節點：16.40 − 12.70 − 3.70 = 0 ✓"))

FIGURES = [(fig1_problem, "AB 慣性矩（2EI）、16 kN 作用點、D／E 支承誤讀"),
           (fig2_solution, "C 節點彎矩不平衡、或 AB 段畫成單一斜率")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
