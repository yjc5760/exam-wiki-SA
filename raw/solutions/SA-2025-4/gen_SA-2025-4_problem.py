#!/usr/bin/env python3
"""SA-2025-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2025-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2025-4_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-4"

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
from structdraw import compose

# ── 判讀清單 #1–#7（考卷座標：d 為原點，x 由 d 指向 a、y 由 d 指向 c、z 向上；L 取 1）──
P3 = {"d": (0, 0, 0), "a": (1, 0, 0), "b": (1, 1, 0), "c": (0, 1, 0)}         # #1
CS, SN = math.cos(math.radians(30)), math.sin(math.radians(30))
def iso(p):                                                                   # 考卷視角：x 向左下、y 向右下、z 向上
    x, y, z = p; return ((y - x) * CS, -(x + y) * SN + z)

def fig1_problem():
    W, H = 640, 540
    pts = [iso(p) for p in P3.values()] + [iso((0, 0, 0.5)), iso((1.45, 0, 0)), iso((0, 1.45, 0)), iso((1, 1, 0.45))]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    sx = min((W - 160) / (max(xs) - min(xs)), (H - 200) / (max(ys) - min(ys)))
    cv = Canvas(W, H, sx=sx, ox=80 - min(xs) * sx + ((W - 160) - (max(xs) - min(xs)) * sx) / 2,
                oy=110 - min(ys) * sx, bg="#FFFFFF")
    I = {k: iso(v) for k, v in P3.items()}
    cv.line(I["d"], I["a"], C["muted"], 1.2)                                  # #2 a–d 細線不是桿件
    for o, e in (("d", (0, 0, 0.5)), ("d", (1.45, 0, 0)), ("d", (0, 1.45, 0))):   # 座標軸
        cv.arrow(I["d"], iso(e), C["muted"], 1.6, 9)
    cv.math(iso((0, 0, 0.5)), "z", 15, C["muted"], dy=-12)
    cv.math(iso((1.45, 0, 0)), "x", 15, C["muted"], dx=-10, dy=10)
    cv.math(iso((0, 1.45, 0)), "y", 15, C["muted"], dx=10, dy=10)
    for i, j in (("a", "b"), ("b", "c"), ("c", "d")):                         # #2 三根桿件
        cv.line(I[i], I[j], C["member"], 6.0, cap="round")
    for nd, other in (("a", "b"), ("d", "c")):                                # #4 a、d 固定端：剖線垂直於桿軸
        u = (I[other][0] - I[nd][0], I[other][1] - I[nd][1])
        cv.fixed_support(I[nd], math.degrees(math.atan2(-u[0], u[1])) + 180, 14)
    for k in range(9):                                                        # #6 ω 沿 −z，bc 全長
        t = k / 8; p = (1 - t, 1, 0)
        cv.arrow(iso((p[0], p[1], 0.4)), iso(p), C["load"], 2.0, 8)
    cv.line(iso((1, 1, 0.4)), iso((0, 1, 0.4)), C["load"], 2.0)
    cv.math(iso((1, 1, 0.4)), "ω", 18, C["load"], dx=-16, dy=-6, weight="700")
    for nd, d in (("a", (-16, 14)), ("b", (-18, 14)), ("c", (16, 14)), ("d", (-16, -10))):
        cv.text(I[nd], nd, 17, C["text"], weight="700", dx=d[0], dy=d[1])
    for i, j, d in (("a", "b", (-14, 14)), ("b", "c", (14, 14)), ("c", "d", (14, -12))):
        m = ((I[i][0] + I[j][0]) / 2, (I[i][1] + I[j][1]) / 2); cv.math(m, "L", 15, C["dim"], dx=d[0], dy=d[1])
    cv.text_px(W / 2, H - 40, "ab、cd 平行 y 軸，bc 平行 x 軸；a、d 固定端，b、c 垂直剛接；實心圓桿 E、G、I", 12.5, C["muted"])
    cv.text_px(W / 2, H - 18, "a–d 之間的細線照考卷，不是桿件", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-problem.svg")

FIGURES = [(fig1_problem, "桿件與座標軸對應讀反（ab 誤為沿 x）、a–d 細線讀成桿件")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
