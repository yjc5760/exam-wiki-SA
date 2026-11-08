#!/usr/bin/env python3
"""SA-2019-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2019-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2019-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-2"

# ── 判讀清單 #1–#5 ──（單位 m）
N_ = {k: (4 * i, 0) for i, k in enumerate("ABCDE")}; N_.update({k: (4 * i, 6) for i, k in enumerate("FGHIJ")})   # #2
MEM = [(a, b) for a, b in zip("ABCD", "BCDE")] + [(a, b) for a, b in zip("FGHI", "GHIJ")] + list(zip("ABCDE", "FGHIJ"))  # #3
SPEC = dict(
    nodes=N_, members=[{"ij": m} for m in MEM],
    supports=[("A", "pin", 0), ("E", "roller", 0)],                                                         # #1
    loads=[(k, (0, -2.4), "100 kN", (0, 16), True) for k in "BCD"],                                         # #4
    labels={"A": (-16, -14), "B": (14, 14), "C": (14, 14), "D": (14, 14), "E": (16, -14),
            "F": (-14, -14), "G": (0, -16), "H": (0, -16), "I": (0, -16), "J": (14, -14)},
    dims=[((0, 6), (4, 6), "4 m", -40), ((4, 6), (8, 6), "4 m", -40), ((8, 6), (12, 6), "4 m", -40), ((12, 6), (16, 6), "4 m", -40),
          ((0, 0), (0, 6), "6 m", -52)],
    extra_pts=[(-2.2, 8.0), (17.5, -3.4)])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 720, 500,
                              note="全部節點剛接；A 鉸支承、E 滾支承；近似分析假設各構件反曲點在中點",
                              margins=(60, 50, 60, 100))

FIGURES = [(fig1_problem, "把載重放在上弦、支承讀反")]

# ── 解題圖（階段 E，2026-11-08）：近似法模型＝每根桿中點放鉸（題給假設），以勁度法解（對稱載重不激發多出的機構），assert 對照 SA-2019-2.md §4 ──
#    弦桿軸力：下弦 +50、+116.67（拉），上弦 −50、−116.67（壓）；腹桿 AF、EJ −75、BG、CH、DI +50；端彎矩：弦 150／50、腹桿 150／200／0 kN-m
def _solve():
    from frame2d import Frame
    f = Frame(); mid = {}
    for n, p in N_.items(): f.node(n, *p)
    for i, j in MEM:
        (x0, y0), (x1, y1) = N_[i], N_[j]; m = i + j + "m"; f.node(m, (x0 + x1) / 2, (y0 + y1) / 2); mid[i + j] = m
        f.member(i + j + "1", i, m, 1.0, rel=(0, 1)); f.member(i + j + "2", m, j, 1.0, rel=(1, 0))
    f.support("A", 1, 1, 0); f.support("E", 0, 1, 0)
    for k in "BCD": f.load(k, fy=-100)
    f.solve()
    Nax = {i + j: -f.end[i + j + "1"][0] for i, j in MEM}           # 拉為正
    Mi = {i + j: abs(f.end[i + j + "1"][2]) for i, j in MEM}
    exp_N = {"AB": 50, "BC": 350/3, "CD": 350/3, "DE": 50, "FG": -50, "GH": -350/3, "HI": -350/3, "IJ": -50,
             "AF": -75, "BG": 50, "CH": 50, "DI": 50, "EJ": -75}
    exp_M = {"AB": 150, "BC": 50, "CD": 50, "DE": 150, "FG": 150, "GH": 50, "HI": 50, "IJ": 150,
             "AF": 150, "BG": 200, "CH": 0, "DI": 200, "EJ": 150}
    for k in exp_N: assert abs(Nax[k] - exp_N[k]) < 1e-3 and abs(Mi[k] - exp_M[k]) < 1e-3, (k, Nax[k], Mi[k])
    return f, Nax

def fig2_forces():
    from structdraw import Canvas, compose
    from frameviz import draw_bmd
    f, Nax = _solve()
    W, H = 620, 520; sx = 30; ox = 70; oy = 120
    a = Canvas(W, H, sx=sx, ox=ox, oy=oy); a.panel("軸力圖（kN，拉＋）", "上弦全壓、下弦全拉；中間兩格 ±116.67")
    peak = max(abs(v) for v in Nax.values())
    for i, j in MEM:
        v = Nax[i + j]; col = C["muted"] if abs(v) < 1e-9 else (C["tension"] if v > 0 else C["compr"])
        a.line(N_[i], N_[j], col, 3 + 6 * abs(v) / peak, cap="butt")
        (x0, y0), (x1, y1) = N_[i], N_[j]; vert = abs(x1 - x0) < 1e-9
        dx, dy = (16 + 0, 4) if vert else (0, -12 if y0 > 3 else 22)
        a.math_px(a.X((x0 + x1) / 2) + dx, a.Y((y0 + y1) / 2) + dy, f"{v:+.2f}".replace("-", "−").replace(".00", ""), 13, col,
                  anchor="start" if vert else "middle", weight="700")
    for k in "BCD":
        a.arrow(N_[k], (N_[k][0], -1.6), C["load"], 2.6, 9)
    a.support(N_["A"], "pin", 0, 13); a.support(N_["E"], "roller", 0, 13)
    for n, p in N_.items(): a.text_px(a.X(p[0]) - 12, a.Y(p[1]) - 10 if p[1] > 3 else a.Y(p[1]) + 30, n, 13, C["text"], weight="700")
    b = Canvas(W, H, sx=sx, ox=ox, oy=oy); b.panel("彎矩圖（kN-m，畫在受拉側）", "每根桿反對稱、中點為 0；CH 彎矩為 0")
    ms = [m for m in f.M]
    draw_bmd(b, f, 0.0042, marks=False)
    for i, j in MEM: b.line(N_[i], N_[j], "#4A5568", 3.0, cap="butt")
    for i, j in MEM:
        m1 = f.end[i + j + "1"]; v = abs(m1[2])
        if v < 1e-3: continue
        (x0, y0), (x1, y1) = N_[i], N_[j]; vert = abs(x1 - x0) < 1e-9
        dx, dy = (0.55, 0.0) if vert else (0.0, 0.0)
        px, py = (x0 + (x1 - x0) * 0.16, y0 + (y1 - y0) * 0.16)
        b.math_px(b.X(px) + (22 if vert else 0), b.Y(py) + (0 if vert else (-26 if y0 > 3 else 34)), f"{v:.0f}", 12.5, C["bmd"], weight="700")
    b.support(N_["A"], "pin", 0, 13); b.support(N_["E"], "roller", 0, 13)
    path = f"{OUT}/{TAG}-fig-2-forces.svg"
    compose([a, b], title=f"圖 2　{TAG} 近似分析（反曲點在各桿中點）：軸力圖與彎矩圖", path=path,
            note="反力 A、E 各 150 kN↑；各格剪力由上下弦平分（第 1、4 格各 75、第 2、3 格各 25 kN）")
    return path

FIGURES.append((fig2_forces, "上下弦軸力拉壓對調；以為腹桿 CH 有彎矩或 AF、EJ 受拉；弦桿剪力沒有上下平分"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
