#!/usr/bin/env python3
"""SA-2019-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2019-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2019-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-4"

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
from frameviz import fit, draw_problem
from structdraw import compose

# ── 判讀清單 #1–#9（L 取 1 個模型單位）──
G = 0.07                                                                      # B 處旋轉彈簧（零長度）示意間隙
N_ = {"A": (0, 0), "B": (0, 1), "B2": (G, 1), "C": (1, 0), "D": (1, 1), "E": (2, 1),
      "P": (0, 0.5), "Q": (1, 0.5)}                                           # #1；P、Q 為柱中點
BASE = dict(nodes=N_,
    members=[dict(ij=("A", "B")), dict(ij=("C", "D")), dict(ij=("B2", "D")), dict(ij=("D", "E"))],
    supports=[("A", "fixed"), ("C", "pin"), ("E", "roller")],                 # #2 #3 #4
    labels={"A": (-20, -14), "B": (-18, -8), "C": (-20, -14), "D": (-16, 16), "E": (-6, -18)})
EXT = [(-0.45, 1.5), (2.45, -0.25)]

def _spring(cv):                                                              # #5 旋轉彈簧 10EI/L
    x0, y0 = cv.P(N_["B"]); x1, _ = cv.P(N_["B2"]); cx = (x0 + x1) / 2; r = (x1 - x0) / 2 + 2
    cv.parts.append('<path d="M %.2f %.2f A %.2f %.2f 0 1 1 %.2f %.2f A %.2f %.2f 0 1 1 %.2f %.2f" fill="none" stroke="%s" stroke-width="2"/>'
                    % (x0, y0, r, r, x1, y0, r * 0.55, r * 0.55, cx, y0 - 3, C["accent"]))

def _canvas(sub):
    W, H = 560, 430
    sx, ox, oy = fit(list(N_.values()) + EXT, W, H, 70, 70, 95, 70)
    cv = Canvas(W, H, sx=sx, ox=ox, oy=oy); cv.panel(*sub); return cv

def fig1_problem():
    a = _canvas(("載重", "P、Q 作用於柱中點；w 作用於 DE 全長；R 作用於 E"))
    draw_problem(a, dict(BASE, udl=[("D", "E", 0.22, "w")],
        loads=[("P", (0.32, 0), "P", (-14, 0)), ("Q", (0.32, 0), "Q", (-14, 0)), ("E", (0.32, 0), "R", (14, 0), True)]))   # #7
    _spring(a); a.text_px(a.X(0.05), a.Y(1) - 34, "旋轉彈簧 10EI/L", 12.5, C["accent"], "start")
    b = _canvas(("自由度與元素編號", "d_{2}、d_{3}、d_{4} 皆逆時針為正"))
    draw_problem(b, BASE); _spring(b)
    b.arrow(N_["E"], (2.32, 1), C["deform"], 2.2, 9); b.math((2.32, 1), "d_{1}", 15, C["deform"], "start", dx=6, weight="700")   # #8
    for p, lab, lo, st, sp in ((N_["B"], "d_{2}", (-34, -18), 100, 160), (N_["B2"], "d_{3}", (30, -26), -80, 160),
                               (N_["D"], "d_{4}", (30, -30), -60, 200)):              # 逆時針；d2 畫在柱頂（左）、d3 畫在梁端（右）
        b.moment_arrow(p, r=19, ccw=True, color=C["deform"], w=2.2, span=sp, start=st)
        b.math(p, lab, 15, C["deform"], "middle", dx=lo[0], dy=lo[1], weight="700")
    for p, s in (((0.11, 0.5), "①"), ((1.11, 0.5), "②"), ((0.04, 1.27), "③"), ((0.5, 1.12), "④"), ((1.5, 1.12), "⑤")):   # #9
        b.text(p, s, 16, C["text"], weight="700")
    compose([a, b], title=None, path=f"{OUT}/{TAG}-fig-1-problem.svg",
            note="A 固定、C 鉸支承、E 滾支承；B 處柱頂與梁 BD 以零長度旋轉彈簧相接；各桿 E、I、L 相同")
    return f"{OUT}/{TAG}-fig-1-problem.svg"

FIGURES = [(fig1_problem, "C 讀成固定端、B 讀成剛接、轉角正向讀反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
