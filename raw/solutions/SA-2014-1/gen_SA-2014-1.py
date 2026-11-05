#!/usr/bin/env python3
"""SA-2014-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2014-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2014-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2014-1"

# ── 判讀清單 #1–#8 ──
N_ = {"A": (0, 0), "B": (12, 0), "C": (24, 0), "D": (36, 0), "E": (48, 0), "F": (60, 0), "G": (72, 0),
      "H": (12, 12), "I": (24, 17), "J": (36, 22), "K": (48, 17), "L": (60, 12)}   # #1 #2
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "H"), ("H", "I"), ("I", "J"), ("J", "K"), ("K", "L"), ("L", "G"),
           ("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("F", "G"),
           ("B", "H"), ("C", "I"), ("D", "J"), ("E", "K"), ("F", "L"),
           ("H", "C"), ("I", "D"), ("K", "D"), ("L", "E")],                    # #4
    joints=list(N_),
    supports=[("A", "pin"), ("G", "roller")],                                 # #5
    labels={"A": (-16, -8), "B": (0, 18), "C": (0, 18), "D": (0, 18), "E": (0, 18), "F": (0, 18), "G": (16, -8),
            "H": (-14, -12), "I": (-12, -14), "J": (0, -18), "K": (12, -14), "L": (14, -12)},   # #3
    dims=[((0, 0), (72, 0), "6@12 m", 85), ((12, 0), (12, 12), "12 m", 0), ((24, 0), (24, 17), "17 m", 0)],
    ptexts=[],
    extra_pts=[(-3, 22), (75, -4)])

def _dims(cv):
    pass

def fig1_problem():
    sp = dict(SPEC, dims=[((0, 0), (72, 0), "6@12 m", 85), ((-3, 0), (-3, 12), "12 m", 0),
                          ((-9, 0), (-9, 17), "17 m", 0), ((-15, 0), (-15, 22), "22 m", 0)],
              dashed=[("A", "H"), ("A", "H")][:0],
              extra_pts=[(-18, 22), (75, -4)])
    return problem_figure(sp, f"{OUT}/{TAG}-fig-1-problem.svg", 900, 420,
                          note="A 鉸支承、G 滾支承；H、L 高 12 m，I、K 高 17 m，J 高 22 m；圖上未畫載重（P 依題文作用於下弦）",
                          margins=(70, 70, 60, 90))

FIGURES = [(fig1_problem, "上弦節點高度讀錯、斜桿方向（HC、ID、KD、LE）讀反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
