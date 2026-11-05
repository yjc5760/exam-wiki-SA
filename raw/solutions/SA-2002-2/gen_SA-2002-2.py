#!/usr/bin/env python3
"""SA-2002-2：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2002-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2002-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2002-2"

# ── 判讀清單 #1–#13 ──
N_ = {"A": (0, 0), "B": (32, 0), "D": (0, 12), "F": (8, 12), "C": (16, 12), "H": (24, 12), "I": (32, 12),
      "E": (8, 6), "G": (24, 6)}                                              # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("D", "A"), ("I", "B"), ("D", "F"), ("F", "C"), ("C", "H"), ("H", "I"), ("D", "E"), ("F", "E"),
           ("E", "C"), ("A", "E"), ("C", "G"), ("H", "G"), ("G", "I"), ("G", "B")],   # #2
    dashed=[("A", "B")],                                                      # #3 虛線非桿件
    joints=list(N_),
    supports=[("A", "pin"), ("B", "pin")],                                    # #5 兩端皆鉸
    loads=[(k, (0, -4.5), "20T", (0, -14)) for k in ("D", "F", "C", "H", "I")]
          + [("D", (5.5, 0), "16T", (-30, 0))],                               # #12
    labels={"A": (-18, 0), "B": (18, 0), "D": (-18, 10), "F": (14, 14), "C": (0, 18), "H": (14, 14), "I": (16, 10),
            "E": (0, 18), "G": (0, 18)},
    mlabels=[((4, 12.9), "a", "#1565C0", "middle"), ((4.7, 9.9), "b", "#1565C0", "middle"),
             ((3.4, 3.3), "c", "#1565C0", "middle"), ((20, 12.9), "d", "#1565C0", "middle"),
             ((20.9, 9.6), "e", "#1565C0", "middle")],                         # #8–#11
    dims=[((0, 0), (8, 0), "8 m", 62), ((8, 0), (16, 0), "8 m", 62), ((16, 0), (24, 0), "8 m", 62),
          ((24, 0), (32, 0), "8 m", 62), ((32, 0), (32, 6), "6 m", 60), ((32, 6), (32, 12), "6 m", 60)],
    ptexts=[((13.6, 8.4), "斜率 3:4", 13, None, "start")],                        # #4
    extra_pts=[(-6, 12), (35, 0)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 520,
                          note="A、B 皆鉸支承；A–B 虛線照考卷，不是桿件（14 桿＋4 反力＝2×9 節點）")

FIGURES = [(fig1_problem, "B 讀成滾支承、A–B 虛線讀成繫索")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
