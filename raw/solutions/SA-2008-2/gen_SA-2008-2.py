#!/usr/bin/env python3
"""SA-2008-2：題目附圖重繪＋載重／剪力圖／彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2008-2-problem.md §4 判讀清單（註解中的 #n）。
剪力、彎矩由勁度法重算，並 assert 與解析一致（M_AC = -453/55、M_DC = 21/22 kN-m）。
用法：python3 gen_SA-2008-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2008-2"

import sys as _s
from recipes import beam_vm
# ── 判讀清單 #1–#4 ──
X = dict(A=0, B=3, C=6, D=12, E=18, F=24, G=27, H=30)        # #2
SPEC = dict(
    nodes={k: (v, 0) for k, v in X.items()},
    members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BC", ij=("B", "C"), EI=1),
             dict(name="CD", ij=("C", "D"), EI=1, w=1.2), dict(name="DE", ij=("D", "E"), EI=1),
             dict(name="EF", ij=("E", "F"), EI=1, w=1.2), dict(name="FG", ij=("F", "G"), EI=1),
             dict(name="GH", ij=("G", "H"), EI=1)],
    supports=[("A", "fixed"), ("H", "fixed"), ("C", "roller"), ("D", "roller"), ("E", "roller"), ("F", "roller")],  # #1
    extra_restraints={"B": (1, 0, 0)},
    udl=[("C", "D", 1.4, "1.2 kN/m"), ("E", "F", 1.4, "1.2 kN/m")],                  # #4
    loads=[("B", (0, -2.6), "10 kN", (0, -14)), ("G", (0, -2.6), "10 kN", (0, -14))],  # #3
    fe_loads=[("B", 0, -10, 0), ("G", 0, -10, 0)],
    labels={k: (0, 50) for k in X},
    dims=[((X[a], 0), (X[b], 0), f"{X[b]-X[a]} m", 86) for a, b in zip("ABCDEFG", "BCDEFGH")])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 900, 420,
                          note="A、H 固接；C、D、E、F 滾支承；EI 常數", margins=(70, 70, 70, 150))

def fig2_vm():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(M["AB"][0] + 453/55) < 1e-3 and abs(M["CD"][1] - 21/22) < 1e-3
    from frameviz import member_moment
    xs, V, Mv = [], [], []
    for m in f.M:
        x0 = SPEC["nodes"][m["i"]][0]; x1 = SPEC["nodes"][m["j"]][0]; Vi = f.end[m["name"]][1]
        for k in range(21):
            xi = k / 20; x = x0 + (x1 - x0) * xi
            xs.append(x); V.append(Vi - m["w"] * (x - x0)); Mv.append(member_moment(f, m, xi))
    path = f"{OUT}/{TAG}-fig-2-vm.svg"
    beam_vm(30, xs, V, Mv, supports=[(0, "fixed"), (6, "roller"), (12, "roller"), (18, "roller"), (24, "roller"), (30, "fixed")],
            point_loads=[(3, "10 kN"), (27, "10 kN")], udls=[(6, 12, "1.2 kN/m"), (18, 24, "1.2 kN/m")],
            title="SA-2008-2　對稱連續梁：剪力圖反對稱、彎矩圖對稱",
            note="DE 跨剪力為 0、彎矩為常數 −0.955 kN·m；支承 C、F 負彎矩 6.03，固端 A、H 8.24，B、G 正彎矩 7.87（kN·m）",
            path=path, v_unit=" kN", m_unit=" kN·m",
            key_V=[(0.6, "5.37", -14), (5.4, "−4.63", 16), (6.6, "4.45", -14), (11.4, "−2.75", 16)], key_M=[(0.4, "−8.24", 16), (3, "7.87", -14), (6, "−6.03", 16), (15, "−0.955", 16)])
    return path

FIGURES = [(fig1_problem, "均布載重範圍、跨距與支承誤讀"),
           (fig2_vm, "DE 跨剪力不為零、彎矩圖不對稱 → 前面必有錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
