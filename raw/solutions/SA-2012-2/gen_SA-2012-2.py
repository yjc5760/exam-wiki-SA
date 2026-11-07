#!/usr/bin/env python3
"""SA-2012-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2012-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2012-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2012-2"

# ── 判讀清單 #1–#6 ──
N_ = {"a": (0, 0), "b": (4, 0), "c": (8, 0), "d": (4, 4)}                      # #5
SPEC = dict(
    nodes=N_, members=[],
    truss=[("a", "d"), ("d", "c"), ("d", "b"), ("a", "b"), ("b", "c")],       # #1
    joints=list(N_),
    supports=[("a", "pin"), ("c", "roller")],                                 # #2、#3
    springs=[("b", 1.5, "K_{s}")],                                            # #4
    loads=[("d", (0, -1.4), "40 kN", (0, -14)), ("d", (1.5, 0), "20 kN", (-4, -16))],   # #6
    labels={"a": (-16, -14), "b": (-14, -16), "c": (16, -14), "d": (16, -10)},
    dims=[((0, 0), (4, 0), "4 m", 92), ((4, 0), (8, 0), "4 m", 92), ((8, 0), (8, 4), "4 m", 64)],
    extra_pts=[(-0.6, 5.6), (9.0, -2.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 520,
                          note="a 鉸支承；c 滾支承；b 點垂直彈簧 K_{s} = 2,500 kN/m；各桿 EA = 10,000 kN")

FIGURES = [(fig1_problem, "漏畫 b 點彈簧（當成靜定）、c 讀成鉸支承、20 kN 方向讀反")]

# ── 解題圖（階段 E，2026-11-07）：桿力取自 SA-2012-2.md §4 步驟 5（kN，拉＋）──
from recipes import truss_forces
R2 = math.sqrt(2)
S = (280*R2 - 20)/17                             # 彈簧力（向上）
F2 = {("a", "d"): (280 - 180*R2)/17, ("d", "c"): (280 - 520*R2)/17, ("d", "b"): (20 - 280*R2)/17,
      ("a", "b"): (520 - 140*R2)/17, ("b", "c"): (520 - 140*R2)/17}

def _check2():
    """自由節點 b、d 平衡殘差須為 0（b 受彈簧力 S 向上；d 受 20 kN→、40 kN↓）。"""
    R = {n: [0.0, 0.0] for n in N_}
    for (i, j), f in F2.items():
        (xi, yi), (xj, yj) = N_[i], N_[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    R["b"][1] += S; R["d"][0] += 20; R["d"][1] -= 40
    assert max(abs(v) for n in ("b", "d") for v in R[n]) < 1e-9

def _labels(cv, forces, spec, unit_fmt="{:+.2f}"):
    """spec: {(i, j): (t, dx_px, dy_px, anchor)}；t 為自 i 起的桿長比例。"""
    for (i, j), (tt, dx, dy, anc) in spec.items():
        f = forces[(i, j)]; p0, p1 = N_[i], N_[j]
        x, y = p0[0] + (p1[0]-p0[0])*tt, p0[1] + (p1[1]-p0[1])*tt
        col = C["tension"] if f > 0 else C["compr"]
        cv.math_px(cv.X(x) + dx, cv.Y(y) + dy, unit_fmt.format(f).replace("-", "\u2212"), 14, col, anc, weight="700")

def fig2_truss():
    _check2()
    cv = truss_forces(N_, [(i, j, f) for (i, j), f in F2.items()],
                        supports=[("a", "pin", 0), ("c", "roller", 0)],
                        loads=[("d", (0, -1.3), "40 kN"), ("d", (1.4, 0), "20 kN"), ("b", (0, 1.3), "")],
                        fmt="", title=f"圖 2　{TAG} 桿力（kN，拉＋）與彈簧力",
                        note="b 點向上箭頭＝彈簧對桁架的力 S = (280√2 − 20)/17（彈簧受壓、b 下沉 8.85 mm）",
                        path=None, W=720, H=600)
    _labels(cv, F2, {("a", "d"): (0.5, -12, -8, "end"), ("d", "c"): (0.5, 12, -8, "start"),
                     ("d", "b"): (0.55, 12, 0, "start"), ("a", "b"): (0.5, 0, -16, "middle"),
                     ("b", "c"): (0.5, 0, -16, "middle")})
    cv.math_px(cv.X(4) + 12, cv.Y(-0.75), f"S = {S:.2f} kN", 15, C["load"], "start", weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")

FIGURES.append((fig2_truss, "漏計彈簧（把 b 當固定或自由）、db 豎桿當零桿"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
