#!/usr/bin/env python3
"""SA-2005-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2005-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2005-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2005-4"

# ── 判讀清單 #1–#6 ──
N_ = {"A": (0, 0), "B": (6, 0), "C": (0, 8), "D": (6, 8)}                      # #1、#5
SPEC = dict(
    nodes=N_, members=[],
    truss=[("A", "C"), ("B", "D"), ("C", "D"), ("A", "D"), ("C", "B")],       # #2：沒有 A–B 下弦
    joints=list(N_),
    supports=[("A", "pin"), ("B", "pin")],                                    # #4
    loads=[("D", (1.8, 0), "24 N", (30, 0), True)],                           # #6
    labels={"A": (-18, 4), "B": (18, 4), "C": (-16, -12), "D": (6, -18)},
    dims=[((0, 0), (6, 0), "6 m", 62), ((0, 0), (0, 8), "8 m", -52)],
    extra_pts=[(-1.2, 8.6), (9.2, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 540,
                          note="A、B 皆鉸支承；A–B 之間沒有桿件；兩斜桿交叉處不相連（5 桿）")

FIGURES = [(fig1_problem, "多畫 A–B 下弦（變靜定）、斜桿交叉處當成節點")]

# ── 解題圖（階段 E，2026-11-07）：桿力取自 SA-2005-4.md §4 最終表（N，拉＋）──
from recipes import truss_forces
F4 = {("A", "C"): 224/15, ("B", "D"): -256/15, ("C", "D"): 56/5, ("A", "D"): 64/3, ("B", "C"): -56/3}
AREA = 10.0                                      # cm²

def _check4():
    """自由節點 C、D 平衡殘差須為 0（D 受 24 N 向右）。"""
    R = {n: [0.0, 0.0] for n in N_}
    for (i, j), f in F4.items():
        (xi, yi), (xj, yj) = N_[i], N_[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    R["D"][0] += 24
    assert max(abs(v) for n in ("C", "D") for v in R[n]) < 1e-9

def _labels(cv, forces, spec, unit_fmt="{:+.2f}"):
    """spec: {(i, j): (t, dx_px, dy_px, anchor)}；t 為自 i 起的桿長比例。"""
    for (i, j), (tt, dx, dy, anc) in spec.items():
        f = forces[(i, j)]; p0, p1 = N_[i], N_[j]
        x, y = p0[0] + (p1[0]-p0[0])*tt, p0[1] + (p1[1]-p0[1])*tt
        col = C["tension"] if f > 0 else C["compr"]
        cv.math_px(cv.X(x) + dx, cv.Y(y) + dy, unit_fmt.format(f).replace("-", "\u2212"), 14, col, anc, weight="700")

def fig2_truss():
    _check4()
    cv = truss_forces(N_, [(i, j, f) for (i, j), f in F4.items()], supports=[("A", "pin", 0), ("B", "pin", 0)],
                      loads=[], fmt="", title=f"圖 2　{TAG} 桿力（N，拉＋）與應力",
                      note="應力 ＝ 內力 ÷ 10 cm²：AC +1.49、BD −1.71、CD +1.12、AD +2.13、BC −1.87 N/cm²",
                      path=None, W=680, H=640)
    _labels(cv, F4, {("A", "C"): (0.5, -14, 0, "end"), ("B", "D"): (0.5, 14, 0, "start"),
                     ("C", "D"): (0.5, 0, -16, "middle"), ("A", "D"): (0.22, 16, 6, "start"),
                     ("B", "C"): (0.22, -16, 6, "end")})
    D = N_["D"]; cv.arrow(D, (D[0] + 1.5, D[1]), C["load"], 3.4, 12)
    cv.math_px(cv.X(D[0] + 1.5) + 8, cv.Y(D[1]) - 16, "24 N", 16, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")

FIGURES.append((fig2_truss, "兩斜桿交叉處當成節點、CD 當零桿、只求內力不換成應力"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
