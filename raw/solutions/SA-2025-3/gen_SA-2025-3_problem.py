#!/usr/bin/env python3
"""SA-2025-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2025-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2025-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_libp"))   # 本題 figs/_lib 是解析自繪圖用的舊版，題目重繪另用 _libp
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-3"

# ── 補畫 probfig 沒有的元素（儲存前注入；只影響本腳本） ──
_save = structdraw.Canvas.save
def _hooked(extra):
    def save(self, path):
        extra(self); structdraw.Canvas.save = _save
        return _save(self, path)
    return save

# ── 判讀清單 #1–#5 ──（以 L = 3 為單位，三段各 L/3）
N_ = {"A": (0, 0), "S1": (1, 0), "S2": (2, 0), "B": (3, 0), "P": (1.5, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "S1")}, {"ij": ("S1", "S2"), "thick": True}, {"ij": ("S2", "B")}],   # #1
    supports=[],                                                              # #5：單桿自由體
    loads=[("P", (0, -0.7), "P", (0, -14))],                                  # #2
    labels={"A": (-4, 22), "B": (4, 22)},
    mlabels=[((0.5, 0.12), "EI", None, "middle"), ((1.78, 0.15), "2EI", None, "middle"), ((2.5, 0.12), "EI", None, "middle")],
    dims=[((0, 0), (1, 0), "L/3", 56), ((1, 0), (2, 0), "L/3", 56), ((2, 0), (3, 0), "L/3", 56)],
    extra_pts=[(-0.5, 0.9), (3.5, -0.6)])

def _moments(cv):                                                              # #3、#4：M_AB、M_BA 皆順時針，畫在桿端外側
    for p, st, lab, dx in (((-0.1, 0), 240, "M_{AB}", -46), ((3.1, 0), 120, "M_{BA}", 46)):
        cv.moment_arrow(p, r=24, ccw=False, color=C["load"], w=2.8, span=200, start=st)
        cv.math(p, lab, 16, C["load"], "middle", dx=dx, dy=-28, weight="700")

def fig1_problem():
    structdraw.Canvas.save = _hooked(_moments)
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 340,
                          note="三段各 L/3，剛度 EI、2EI、EI；P 在跨中；M_{AB}、M_{BA} 依附圖皆順時針；無支承")

FIGURES = [(fig1_problem, "端彎矩正向讀反、中段剛度與兩側對調")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
