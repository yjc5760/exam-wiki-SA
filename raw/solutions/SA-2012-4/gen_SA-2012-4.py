#!/usr/bin/env python3
"""SA-2012-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2012-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2012-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2012-4"

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

# ── 判讀清單 #1–#7（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"a": (0, 0), "b": (0, 1), "c": (0.5, 1), "d": (1, 1)},             # #1
    members=[dict(ij=("a", "b")), dict(ij=("b", "c")), dict(ij=("c", "d"), thick=True)],   # #2 cd 為 EI = ∞（粗線）
    supports=[("a", "fixed"), ("d", "pin")],                                  # #4 #5
    couples=[((0, 1.17), False, "R_{1}, r_{1}", (-34, -28)), ((1, 1.2), False, "R_{2}, r_{2}", (36, -28))],   # #6 皆順時針（畫在節點上方，照考卷）
    labels={"a": (-24, -16), "b": (-20, 10), "c": (0, 18), "d": (22, 6)},
    mlabels=[((-0.08, 0.5), "EI", None, "end"), ((0.25, 1.09), "EI", None, "middle"),
             ((0.75, 1.09), "EI = ∞", None, "middle")],                      # #2
    dims=[((0, 0), (0, 1), "L", -80), ((0, 0), (0.5, 0), "L/2", 50), ((0.5, 0), (1, 0), "L/2", 50)],
    extra_pts=[(-0.35, 1.35), (1.25, -0.15)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 500,
                          note="a 固接、d 鉸支承；ab、bc 為 EI，cd 為剛性桿（EI = ∞）；r_{1}、r_{2} 皆順時針")

FIGURES = [(fig1_problem, "d 讀成滾支承、cd 剛桿長度或自由度轉向讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
