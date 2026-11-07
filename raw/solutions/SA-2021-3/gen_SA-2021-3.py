#!/usr/bin/env python3
"""SA-2021-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-3"

# ── 判讀清單 ──
N_ = {"a": (0, 0), "b": (3, 0), "c": (6, 0), "d": (9, 0), "e": (12, 0), "f": (3, 4), "g": (6, 4), "h": (9, 4)}  # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("f", "g"), ("g", "h"), ("a", "f"), ("h", "e"),
           ("f", "b"), ("g", "c"), ("h", "d"), ("b", "g"), ("g", "d")],             # #2、#3
    joints=list(N_),
    supports=[("a", "pin"), ("e", "pin")],                                          # #4
    labels={"a": (-18, -10), "b": (0, 20), "c": (0, 20), "d": (0, 20), "e": (18, -10), "f": (0, -18), "g": (0, -18), "h": (0, -18)},
    dims=[((0, 0), (3, 0), "3 m", 62), ((3, 0), (6, 0), "3 m", 62), ((6, 0), (9, 0), "3 m", 62),
          ((9, 0), (12, 0), "3 m", 62), ((12, 0), (12, 4), "4 m", 50)],
    extra_pts=[(-1, 4.5), (13.5, -1)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 460,
                          note="a、e 皆鉸支承；單位載重沿底弦 a–e 移動；各桿 EA 相同")

FIGURES = [(fig1_problem, "e 讀成滾支承、斜桿 bg／gd 方向讀反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
