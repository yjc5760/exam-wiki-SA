#!/usr/bin/env python3
"""SA-2015-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2015-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2015-4_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-4"

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
G = 0.07                                                                      # B 與 BD 桿端之間留彈簧符號的間隙（示意）
N_ = {"A": (-1, 0), "B": (0, 0), "C": (0, -1), "B2": (G, 0), "D": (1, 0), "F": (0.5, 0)}   # #1；F 為 P 作用點
SPEC = dict(
    nodes=N_,
    members=[dict(ij=("A", "B")), dict(ij=("B", "C")), dict(ij=("B2", "D"))],  # #2 AB、BC 剛接；BD 經彈簧接 B
    supports=[("A", "fixed"), ("C", "fixed"), ("D", "fixed")],                # #3
    udl=[("A", "B", 0.26, "w")],                                              # #5 A 到 B 全長
    loads=[("F", (0, -0.34), "P", (0, -14))],                                 # #6 BD 中點
    labels={"A": (-30, -4), "B": (-16, 16), "C": (18, 10), "D": (28, -4)},
    dims=[((-1, -1), (0, -1), "L", 48), ((0, -1), (0.5, -1), "L/2", 48), ((0.5, -1), (1, -1), "L/2", 48),
          ((1, 0), (1, -1), "L", -70)],
    extra_pts=[(-1.2, 0.45), (1.25, -1.25)])

def _springs(cv):                                                             # #4 抗扭彈簧＋水平線性彈簧
    x0, y0 = cv.P(N_["B"]); x1, _ = cv.P(N_["B2"])
    # 水平線性彈簧：B 與 BD 桿端之間的鋸齒線（在桿軸上方）
    n = 5; pts = [(x0, y0 - 9)]
    for i in range(n):
        pts.append((x0 + (x1 - x0) * (i + 0.5) / n, y0 - 9 + (-5 if i % 2 == 0 else 5)))
    pts.append((x1, y0 - 9))
    cv.parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>'
                    % (" ".join("%.2f,%.2f" % q for q in pts), C["accent"]))
    for x in (x0, x1):
        cv.parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="2"/>' % (x, y0, x, y0 - 9, C["accent"]))
    # 抗扭彈簧：B 與 BD 桿端之間的螺旋（在桿軸下方）
    cx, cy = (x0 + x1) / 2, y0 + 10; r = (x1 - x0) / 2 + 3
    cv.parts.append('<path d="M %.2f %.2f A %.2f %.2f 0 1 0 %.2f %.2f A %.2f %.2f 0 1 0 %.2f %.2f" fill="none" stroke="%s" stroke-width="2"/>'
                    % (x0, y0, r, r, x1, y0, r * 0.6, r * 0.6, cx, cy, C["accent"]))
    cv.text_px(x1 + 40, y0 - 40, "線性彈簧 k_{s}（水平力）", 13, C["accent"], "start")
    cv.parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="1.2"/>' % (x1 + 38, y0 - 36, (x0 + x1) / 2 + 4, y0 - 12, C["accent"]))
    cv.text_px(x1 + 40, y0 + 46, "抗扭彈簧 k_{θ}（彎矩）", 13, C["accent"], "start")
    cv.parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="1.2"/>' % (x1 + 38, y0 + 42, cx + 6, cy + 8, C["accent"]))

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 500,
                 note="A、C、D 固定；B 與 BD 只以抗扭彈簧與水平線性彈簧連結，無垂直力傳遞；各桿長 L"), _springs)

FIGURES = [(fig1_problem, "B–BD 接合讀成剛接或鉸接、P 作用點讀錯、w 範圍讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
