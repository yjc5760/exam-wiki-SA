#!/usr/bin/env python3
"""SA-2014-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2014-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2014-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2014-3"

# ── 判讀清單 #1–#10 ──（以 L = 1 為單位）
R3 = math.sqrt(3) / 2
N_ = {"A": (0, 1), "B": (0, 0), "C": (0, -1), "D": (R3, 0), "E": (2 * R3, -0.5)}   # #5–#7
SPEC = dict(
    nodes=N_, members=[{"ij": ("B", "A")}, {"ij": ("B", "C")}, {"ij": ("B", "D")}, {"ij": ("D", "E")}],
    supports=[("A", "fixed"), ("C", "fixed"), ("E", "fixed")],                # #1–#3：E 支承面垂直 DE
    loads=[("B", (0.34, 0), "P = 66 kN", (-6, -16))],                       # #10
    labels={"A": (-18, 14), "B": (-14, 16), "C": (-18, -14), "D": (4, -16), "E": (12, 14)},
    mlabels=[((0.06, 0.5), "2I", None, "start"), ((0.06, -0.5), "2I", None, "start"), ((1.42, -0.12), "I", None, "middle")],
    ptexts=[((R3 / 2 + 0.12, 0.1), "√3 I", 14, None, "middle"),
            ((R3 / 2, -1.27), "√3 L/2", 13.5, None, "middle"), ((1.5 * R3, -1.27), "√3 L/2", 13.5, None, "middle")],
    dims=[((0, -1), (0, 0), "L", -104), ((0, 0), (0, 1), "L", -104),
          ((0, -1), (R3, -1), "", 32), ((R3, -1), (2 * R3, -1), "", 32), ((2 * R3, -0.5), (2 * R3, 0), "L/2", 46)],
    extra_pts=[(-0.95, 1.15), (2.05, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 560,
                          note="L = 8 m；A、C、E 皆固接；B、D 剛接；E 比 D 低 L/2，DE 實長 L")

FIGURES = [(fig1_problem, "DE 讀成水平、E 支承方向讀錯、各桿慣性矩對調")]

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解（L = 8 m、P = 66 kN、I 比 2：2：√3：1），與 SA-2014-3.md §4 Step 5 對照 ──
#    M_AB = +3168/115、M_BA = +1848/115、M_BC = −7128/115、M_CB = −5808/115、M_BD = +5280/115、
#    M_DB = +5544/115、M_DE = −5544/115、M_ED = −5016/115（順時針為正）；D 點位移 ⟂ DE：上移 √3Δ
def _solve():
    from frame2d import Frame
    f = Frame(); Lm = 8.0; r3 = math.sqrt(3)
    for n, (x, y) in N_.items(): f.node(n, x * Lm, y * Lm)
    for n in "ACE": f.support(n, 1, 1, 1)
    f.member("AB", "A", "B", 2.0); f.member("BC", "B", "C", 2.0); f.member("BD", "B", "D", r3); f.member("DE", "D", "E", 1.0)
    f.load("B", fx=66.0)
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    ref = (3168, 1848, -7128, -5808, 5280, 5544, -5544, -5016)
    assert all(abs(x - y/115) < 1e-3 for x, y in zip(cw("AB") + cw("BC") + cw("BD") + cw("DE"), ref))   # EA = 1e8·EI 近似不計軸向，差 < 0.001 kN-m
    assert abs(f.d["D"][1] / f.d["B"][0] - r3) < 1e-6                 # D 上移 √3Δ
    return f

def fig2_solution():
    from beamfig import frame_figure
    f = _solve()
    sol = dict(nodes={n: f.N[n] for n in "ABCDE"}, supports=[("A", "fixed"), ("C", "fixed"), ("E", "fixed")])
    L = [("AB", 0.0, 34, 22), ("AB", 1.0, -30, -14), ("BC", 0.0, 30, 16), ("BC", 1.0, -30, 0),
         ("BD", 0.0, 46, 26), ("BD", 1.0, 0, 20), ("DE", 1.0, 18, 18)]
    return frame_figure(f, sol, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2014-3 變形形狀與彎矩圖（單位 kN-m）",
        "B 右移 Δ；D 沿垂直 DE 方向移動，上移 √3Δ",
        "下柱 C 端逆時針、上柱 A 端順時針", L, fmt="{:.2f}", W=560, H=520,
        notes=("", "D 點 BD、DE 兩端彎矩相等 48.21"))

FIGURES.append((fig2_solution, "D 點位移方向畫錯（只水平移動、或向下）；八個桿端彎矩正負整組相反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
