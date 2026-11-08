#!/usr/bin/env python3
"""SA-2023-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2023-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2023-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2023-4"

# ── 判讀清單 #1–#8 ──（單位 m）
L1, E_, H_ = 4.0, 0.6, 4.0; XR = 2 * L1 + E_                                                      # #1 #2
N_ = {}
for k in range(4):
    N_[f"L{k}"] = (0, H_ * k); N_[f"R{k}"] = (XR, H_ * k)
for k in range(1, 4):
    N_[f"a{k}"] = (L1, H_ * k); N_[f"b{k}"] = (L1 + E_, H_ * k)
MEM = [{"ij": ("L0", "L3")}, {"ij": ("R0", "R3")}] + [{"ij": (f"L{k}", f"R{k}")} for k in range(1, 4)]
BR = [(f"L{k-1}", f"a{k}") for k in range(1, 4)] + [(f"R{k-1}", f"b{k}") for k in range(1, 4)]       # #3
SPEC = dict(
    nodes=N_, members=MEM + [{"ij": b} for b in BR],
    loads=[(f"L{k}", (1.6, 0), f"{v} kN", (-34, -14)) for k, v in ((1, 300), (2, 450), (3, 600))]
         + [(f"R{k}", (1.6, 0), f"{v} kN", (36, -14), True) for k, v in ((1, 300), (2, 450), (3, 600))],   # #6
    dims=[((0, 0), (0, 4), "4 m", -150), ((0, 4), (0, 8), "4 m", -150), ((0, 8), (0, 12), "4 m", -150),
          ((0, 0), (L1, 0), "4 m", 50), ((L1, 0), (L1 + E_, 0), "0.6 m", 50), ((L1 + E_, 0), (XR, 0), "4 m", 50)],
    extra_pts=[(-4.8, 13.6), (XR + 3.4, -1.6)])

def _pre(cv, N):
    for k in range(1, 4):                                                                          # #5 剛性區域
        y0, y1 = H_ * (k - 1), H_ * k
        cv.polygon([(0, y0), (0, y1), (L1, y1)], "rgba(63,74,90,0.14)", "none")
        cv.polygon([(XR, y0), (XR, y1), (L1 + E_, y1)], "rgba(63,74,90,0.14)", "none")
    cv.line((-0.8, 0), (XR + 0.8, 0), C["member"], 2.6)                                            # #7 地面（柱底未畫支承）
    for i in range(12):
        x = -0.6 + i * (XR + 1.2) / 11; cv.line((x, 0), (x - 0.3, -0.4), C["member"], 1.5)

def _post(cv, N):
    for k in range(1, 4):                                                                          # #4 連梁
        a, b = N[f"a{k}"], N[f"b{k}"]
        cv.line(a, b, C["accent"], 6.0, cap="butt")
        cv.text(((a[0] + b[0]) / 2, a[1]), f"連梁{k}", 14, C["accent"], dy=-16, weight="700")
    cv.text((L1 / 3, H_ * 3 - 1.0), "剛性區域", 13, C["muted"]); cv.text((XR - L1 / 3, H_ * 3 - 1.0), "剛性區域", 13, C["muted"])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 720, 620, pre=_pre, post=_post,
                              note=["每層斜撐自該層下緣兩角連到上方梁中央，留 0.6 m 連梁；連梁剛度 EI；頂端側移 6 cm",
                                    "樓板兩端各標一次 300／450／600 kN（是每端或合計題文未明說，不影響層剪力比例）"],
                              margins=(70, 70, 50, 120))

FIGURES = [(fig1_problem, "連梁位置放錯樓層、剛性區域畫成下方三角形")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
