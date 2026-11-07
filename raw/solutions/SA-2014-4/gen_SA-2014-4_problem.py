#!/usr/bin/env python3
"""SA-2014-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2014-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2014-4_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2014-4"

# ── 補畫 probfig 沒有的元素（儲存前注入；只影響本腳本） ──
_save = structdraw.Canvas.save
def _hooked(extra):
    def save(self, path):
        extra(self); structdraw.Canvas.save = _save
        return _save(self, path)
    return save

# ── 判讀清單 #1–#6 ──
N_ = {"A": (0, 12), "B": (6, 12), "C": (12, 12), "D": (12, 0)}                 # #5
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D"), "thick": True}],   # #1：CD 為 2EI
    supports=[("A", "fixed"), ("D", "roller")],                               # #2、#3
    loads=[("B", (0, -2.4), "20 kN", (0, -14))],                              # #6：載重依題文
    labels={"A": (-18, 0), "B": (0, 20), "C": (16, -14), "D": (20, 0)},
    mlabels=[((3, 12.9), "EI", None, "middle"), ((12.9, 6), "2EI", None, "start")],
    dims=[((0, 12), (6, 12), "6 m", -96), ((6, 12), (12, 12), "6 m", -96), ((12, 0), (12, 12), "12 m", 82)],
    extra_pts=[(-1.4, 16.4), (15.0, -1.6)])

def _dot(cv):                                                                  # #4：B 為實心標示點（不是鉸）
    x, y = cv.P(N_["B"]); cv.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.6" fill="{C["member"]}"/>')

def fig1_problem():
    structdraw.Canvas.save = _hooked(_dot)
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 560,
                          note="A 固定端；D 滾支承（垂直反力）；AC 為 EI、CD 為 2EI；20 kN 依題文（考卷附圖未畫箭頭）")

FIGURES = [(fig1_problem, "B 讀成內鉸、D 讀成鉸支承、AC／CD 剛度對調")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
