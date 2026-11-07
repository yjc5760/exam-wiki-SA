#!/usr/bin/env python3
"""SA-2006-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2006-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2006-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2006-1"

# ── 補畫 probfig 沒有的元素（儲存前注入；只影響本腳本） ──
_save = structdraw.Canvas.save
def _hooked(extra):
    def save(self, path):
        extra(self); structdraw.Canvas.save = _save
        return _save(self, path)
    return save

# ── 判讀清單 #1–#9 ──（桁架上弦 y = 0、深 10 m；梁示意畫在上弦上方 2.4 m）
YB = 2.4
N_ = {"A": (0, YB), "B": (10, YB), "C": (20, YB), "D": (30, YB), "E": (40, YB),            # #1：梁 A–E
      "P1": (15, YB), "P2": (25, YB),                                                      # #5：載重點
      "F": (0, 0), "T1": (10, 0), "T2": (20, 0), "T3": (30, 0), "G": (40, 0),              # #6：上弦（內部三點無字母）
      "H": (10, -10), "J": (20, -10), "K": (30, -10)}
SPEC = dict(
    nodes=N_, members=[],
    rigid=[("A", "E")],                                                                    # 梁
    truss=[("F", "T1"), ("T1", "T2"), ("T2", "T3"), ("T3", "G"), ("H", "J"), ("J", "K"),
           ("T1", "H"), ("T2", "J"), ("T3", "K"), ("F", "H"), ("H", "T2"), ("T2", "K"), ("K", "G")],   # #7
    joints=["F", "T1", "T2", "T3", "G", "H", "J", "K"],
    supports=[("F", "pin"), ("G", "pin")],                                                  # #9
    loads=[("P1", (0, -3.0), "10 kN", (36, 4)), ("P2", (0, -3.0), "10 kN", (36, 4))],      # #5
    labels={"A": (-14, -18), "B": (0, -18), "C": (0, -18), "D": (0, -18), "E": (14, -18),
            "F": (-20, 8), "G": (20, 8), "H": (0, 20), "J": (0, 20), "K": (0, 20)},
    dims=[((0, YB), (15, YB), "15 m", -96), ((15, YB), (25, YB), "10 m", -96), ((25, YB), (40, YB), "15 m", -96),
          ((0, -10), (40, -10), "4@10 m = 40 m", 52), ((0, -10), (0, 0), "10 m", -66)],
    ptexts=[((41.2, YB - 0.1), "自由端", 12.5, None, "start")],                            # #2
    extra_pts=[(-1.6, 7.2), (43.5, -12.6)])

def _extra(cv):
    r = YB / 2 * cv.sx - 3
    for x in (10, 30):                                                                     # #3：B、D 梁與上弦之間的滾支承
        cx, cy = cv.P((x, YB / 2))
        cv.parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#FFFFFF" stroke="{C["member"]}" stroke-width="2.4"/>')
    ra = 0.42 * cv.sx                                                                      # #1：A 滾支承擱在左橋台
    ax, ay = cv.P((0, YB)); cy = ay + 4 + ra; gy = cy + ra
    cv.parts.append(f'<circle cx="{ax:.2f}" cy="{cy:.2f}" r="{ra:.2f}" fill="#FFFFFF" stroke="{C["member"]}" stroke-width="2.2"/>')
    cv.parts.append(f'<line x1="{ax - 2.6 * cv.sx:.2f}" y1="{gy:.2f}" x2="{ax + 0.5 * cv.sx:.2f}" y2="{gy:.2f}" stroke="{C["member"]}" stroke-width="2.6"/>')
    cv._hatch(ax - 1.05 * cv.sx, gy, 1, 0, 0, 1, 1.5 * cv.sx, C["member"])

def fig1_problem():
    structdraw.Canvas.save = _hooked(_extra)
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 900, 520,
                          note="梁 A–E 擱在 A（橋台）與 B、D 滾支承上，E 端無支承；F、G 鉸支承；載重在 x = 15、25 m，不在節點")

FIGURES = [(fig1_problem, "E 端多加支承、載重放到節點 B／C／D、把梁當成桁架上弦")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
