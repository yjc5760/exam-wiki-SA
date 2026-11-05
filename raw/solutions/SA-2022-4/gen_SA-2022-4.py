#!/usr/bin/env python3
"""SA-2022-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2022-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2022-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-4"

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

# ── 判讀清單 #1–#8 ──
X = {"a": 0, "e": 4, "m": 8, "n": 12}; H1, H2, H3 = 3.6, 7.2, 10.8            # #1 #2
N_ = {"a": (0, 0), "e": (4, 0), "m": (8, 0), "n": (12, 0),
      "b": (0, H1), "b2": (4, H1),
      "c": (0, H2), "c2": (4, H2), "c3": (8, H2), "c4": (12, H2),
      "d": (0, H3), "d2": (4, H3), "d3": (8, H3), "d4": (12, H3)}
cols = [("a", "b"), ("b", "c"), ("c", "d"), ("e", "b2"), ("b2", "c2"), ("c2", "d2"),
        ("m", "c3"), ("c3", "d3"), ("n", "c4"), ("c4", "d4")]                 # #4 m、n 柱直通第二層（長 7.2 m）
beams = [("b", "b2"), ("c", "c2"), ("c2", "c3"), ("c3", "c4"), ("d", "d2"), ("d2", "d3"), ("d3", "d4")]   # #3 #5
SPEC = dict(
    nodes=N_,
    members=[dict(ij=c) for c in cols],
    supports=[(k, "fixed") for k in ("a", "e", "m", "n")],                    # #6
    loads=[("b", (1.8, 0), "100 kN", (-34, -14)), ("c", (1.8, 0), "200 kN", (-34, -14)),
           ("d", (1.8, 0), "300 kN", (-34, -14))],                            # #8
    labels={"a": (14, -14), "e": (14, -14), "m": (16, -14), "n": (14, -14), "b": (12, -16), "c": (12, -16), "d": (12, -16)},
    dims=[((0, 0), (4, 0), "4 m", 52), ((4, 0), (8, 0), "4 m", 52), ((8, 0), (12, 0), "4 m", 52),
          ((12, 0), (12, H1), "3.6 m", 70), ((12, H1), (12, H2), "3.6 m", 70), ((12, H2), (12, H3), "3.6 m", 70)],
    extra_pts=[(-3.0, H3 + 0.6), (14.2, -1.0)])

def _beams(cv):                                                               # #7 梁 EI = ∞（粗線）
    for i, j in beams:
        cv.line(N_[i], N_[j], C["member"], 9.0, cap="butt")

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 600,
                 note="第一層梁只有 a–e 一跨，m、n 柱直通第二層；柱 EI = 97200 kN-m^{2}，梁 EI = ∞（粗線）"), _beams)

FIGURES = [(fig1_problem, "m、n 柱誤以為在第一層有梁（柱長 3.6 m）")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
