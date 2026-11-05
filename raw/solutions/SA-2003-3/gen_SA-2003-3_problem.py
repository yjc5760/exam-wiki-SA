#!/usr/bin/env python3
"""SA-2003-3：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2003-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2003-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2003-3"

# ── 判讀清單 #1–#8 ──
N_ = {"L0": (0, 0), "L1": (8, 0), "L2": (16, 0), "L3": (24, 0), "L4": (32, 0),
      "M1": (4, 4), "M2": (12, 4), "M3": (20, 4), "M4": (28, 4), "U1": (8, 8), "U2": (16, 8), "U3": (24, 8)}   # #1
T_ = [("L0", "M1"), ("M1", "U1"), ("U1", "M2"), ("M2", "L2"), ("M1", "M2"), ("M1", "L1"), ("L1", "M2"),
      ("L2", "M3"), ("M3", "U3"), ("U3", "M4"), ("M4", "L4"), ("M3", "M4"), ("M3", "L3"), ("L3", "M4"),
      ("U1", "U2"), ("U2", "U3"), ("U2", "L2"), ("L0", "L1"), ("L1", "L2"), ("L2", "L3"), ("L3", "L4")]          # #2
SPEC = dict(
    nodes=N_, members=[], truss=T_, joints=list(N_),
    supports=[("L0", "pin"), ("L4", "roller")],                               # #6
    loads=[("L1", (0, -3.2), "2t", (0, 16), True), ("L2", (0, -3.2), "2t", (0, 16), True)],   # #7 向下
    mlabels=[((8, 4.7), "a", "#1565C0", "middle"), ((10.6, 6.6), "b", "#1565C0", "start")],  # #4 #5
    dims=[((0, 0), (32, 0), "4×8 m = 32 m", 95), ((32, 0), (32, 4), "4 m", 60), ((32, 4), (32, 8), "4 m", 60)],
    extra_pts=[(0, -5), (34, 8)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 470,
                          note="左端鉸支承、右端滾支承；a＝左側水平腹桿 (4,4)–(12,4)，b＝(8,8)–(12,4) 斜桿")

FIGURES = [(fig1_problem, "a、b 桿位置認錯、右端支承讀成鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
