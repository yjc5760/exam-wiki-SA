#!/usr/bin/env python3
"""SA-2024-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2024-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2024-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2024-3"

# ── 判讀清單 #1–#6 ──（L = 1、L_b = 2 為示意；題目只給 L_b/L > 1）
N_ = {"A": (0, 0), "B": (0, 1), "C": (2, 1), "D": (2, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "fixed"), ("D", "fixed")],                                # #1
    hinges=["C"],                                                             # #3：C 內鉸（使用者確認）
    loads=[("B", (0.42, 0), "P", (-10, -16))],                               # #6
    labels={"A": (-20, -14), "B": (-12, -16), "C": (14, -16), "D": (20, -14)},
    mlabels=[((1, 1.1), "EI, L_{b}", None, "middle"), ((-0.08, 0.5), "EI, L", None, "end"), ((2.08, 0.5), "EI, L", None, "start")],
    extra_pts=[(-0.6, 1.4), (2.5, -0.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 400,
                          note="A、D 固定；B 剛接；C 為梁與右柱之間的內鉸；L_{b}/L > 1（圖中比例為示意）")

FIGURES = [(fig1_problem, "漏讀 C 點內鉸（當成對稱門型剛架）")]

# ── 解題圖（階段 E，2026-11-08）：以 L = P = EI = 1、L_b = 3/2 L 的勁度法重解，與 SA-2024-3.md §4 Step 6 對照 ──
#    M_AB = −4PL/9、M_BA = −2PL/9、M_BC = +2PL/9、M_DC = −PL/3、M_CB = M_CD = 0（順時針為正）
from fractions import Fraction
KB = Fraction(3, 2)                                                  # 本題答案 L_b/L

class _Frac:
    """彎矩標註寫成 PL 的分數（如 4PL/9），數值仍由勁度法解出、再化成最簡分數。"""
    def format(self, v):
        q = Fraction(v).limit_denominator(36)
        n = "" if q.numerator == 1 else str(q.numerator)
        return f"{n}PL/{q.denominator}" if q.denominator != 1 else f"{n}PL"

def _solve():
    from frame2d import Frame
    f = Frame()
    for n, p in {"A": (0, 0), "B": (0, 1), "C": (float(KB), 1), "D": (float(KB), 0)}.items(): f.node(n, *p)
    f.support("A", 1, 1, 1); f.support("D", 1, 1, 1)
    f.member("AB", "A", "B", 1.0); f.member("BC", "B", "C", 1.0, rel=(0, 1)); f.member("DC", "D", "C", 1.0, rel=(0, 1))   # C 內鉸
    f.load("B", fx=1.0)
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    assert all(abs(x - y) < 1e-6 for x, y in zip(cw("AB") + cw("BC") + cw("DC"), (-4/9, -2/9, 2/9, 0, -1/3, 0)))  # 容差 1e-6
    assert abs(abs(cw("AB")[0]) / abs(cw("BC")[0]) - 2) < 1e-6        # 柱最大：梁最大 = 2：1
    return f

def fig2_solution():
    from beamfig import frame_figure
    f = _solve()
    sol = dict(nodes={n: f.N[n] for n in "ABCD"}, supports=[("A", "fixed"), ("D", "fixed")], hinges=["C"])
    L = [("AB", 0.0, -34, 4), ("AB", 1.0, -34, 4), ("BC", 0.0, 10, 22), ("DC", 0.0, -40, -22)]
    return frame_figure(f, sol, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2024-3 變形形狀與彎矩圖（Lb/L = 3/2）",
        "B 向右側移；C 內鉸處梁與柱各自轉動",
        "柱最大 4PL/9（A）＝ 2 × 梁最大 2PL/9（B）", L, fmt=_Frac(), W=520, H=470,
        notes=("", "C 鉸 M = 0；右柱 D 端 PL/3"))

FIGURES.append((fig2_solution, "把 C 當剛接角點（兩柱彎矩相同、L_b/L 得 3）；拿右柱 PL/3 當柱最大"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
