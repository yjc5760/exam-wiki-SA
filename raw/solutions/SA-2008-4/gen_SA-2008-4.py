#!/usr/bin/env python3
"""SA-2008-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2008-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2008-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2008-4"

def _post(fn, post):
    """在 problem_figure 存檔前補畫（自由度箭頭、彈簧符號等），不改共用程式庫。"""
    orig = Canvas.save
    def save(self, path):
        post(self); return orig(self, path)
    Canvas.save = save
    try: return fn()
    finally: Canvas.save = orig

def dof(cv, p, d, lab, L=0.55, lo=(0, 0)):
    """自由度箭頭（藍色）：p 為節點，d 為方向，lab 為編號。"""
    q = (p[0] + d[0]*L, p[1] + d[1]*L)
    cv.arrow(p, q, C["deform"], 2.2, 9)
    cv.math(q, lab, 14, C["deform"], "middle", dx=lo[0], dy=lo[1], weight="700")

# ── 判讀清單 #1–#5 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 4), "C": (6, 4)},                           # #1
    members=[dict(ij=("A", "B")), dict(ij=("B", "C"))],                      # #2
    supports=[("A", "fixed"), ("C", "pin")],                                  # #3 #4
    udl=[("B", "C", 0.9, "1 kN/m")],                                          # #5
    labels={"A": (-22, 6), "B": (-20, -10), "C": (24, -12)},
    dims=[((0, 0), (0, 4), "4 m", -70), ((0, 0), (6, 0), "6 m", 52)],
    extra_pts=[(-1.2, 4), (6.5, -0.5)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 500,
                          note="A 固定端、B 剛接、C 鉸支承；1 kN/m 作用於 BC 全長；各桿 EI 相同")

FIGURES = [(fig1_problem, "C 讀成滾支承、均布載重範圍讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
