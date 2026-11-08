#!/usr/bin/env python3
"""SA-2019-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2019-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2019-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-3"

# ── 判讀清單 #1–#5 ──（以 L = 1 為單位）
N_ = {"A": (0, 0), "B": (1, 0), "C": (2, 0), "D": (3, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "pin"), ("B", "roller"), ("C", "roller"), ("D", "roller")],   # #1、#2
    udl=[("A", "D", 0.2, "w")],                                               # #4
    labels={"A": (-14, -14), "B": (-14, -14), "C": (-14, -14), "D": (14, -14)},
    mlabels=[((0.5, -0.1), "EI, L", None, "middle"), ((1.5, -0.1), "EI, L", None, "middle"), ((2.5, -0.1), "EI, L", None, "middle")],
    dims=[((0, 0), (1, 0), "L", 74), ((1, 0), (2, 0), "L", 74), ((2, 0), (3, 0), "L", 74)],
    extra_pts=[(-0.1, 0.4), (3.1, -0.42)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 330,
                          note="A 鉸支承；B、C、D 滾支承；B、C 同量向下沉陷 Δ（未知，為所求）")

FIGURES = [(fig1_problem, "A 讀成滾支承、只讓一個支承沉陷")]

# ── 解題圖（階段 E，2026-11-08）：以 L = w = EI = 1 的勁度法重解（沉陷以極硬彈簧＋等值節點力施加）──
#    SA-2019-3.md §4：M_BA = −6EIΔ/(5L²) + wL²/10、R_A = 0.4wL + 6EIΔ/(5L³)；所求 Δ = wL⁴/(12EI)
def _solve(delta):
    from frame2d import Frame
    f = Frame(); kpen = 1e8
    for n, p in {**N_, "B0": (1, -1), "C0": (2, -1)}.items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("D", 0, 1, 0); f.support("B0", 1, 1, 1); f.support("C0", 1, 1, 1)
    for nm, i, j in (("AB", "A", "B"), ("BC", "B", "C"), ("CD", "C", "D")): f.member(nm, i, j, 1.0, w=1.0)
    for nd in "BC":                                         # 沉陷 Δ：彈簧 kpen ＋ 節點力 kpen·Δ（向下）
        f.member(nd + "s", nd, nd + "0", 1e-9, rel=(1, 1), EA=kpen); f.load(nd, fy=-kpen * delta)
    f.solve()
    cw = -f.end["AB"][5]                                      # M_BA（順時針為正）
    assert abs(cw - (-6/5 * delta + 1/10)) < 1e-6 and abs(f.R["A"][1] - (0.4 + 6/5 * delta)) < 1e-6
    return f

def fig2_settle():
    from beamfig import beam_strip
    from frameviz import member_moment
    D = 1/12                                                  # 所求沉陷 wL⁴/(12EI)
    f, f0 = _solve(D), _solve(0.0)
    assert abs(member_moment(f, f.M[0], 1.0)) < 1e-6          # Δ = wL⁴/12EI 時 M_B = 0
    def extra(_a, b):
        sx = b.sx; mmax = max(abs(member_moment(f, m, k/80)) for m in f.M[:3] for k in range(81))
        msc = 90 / sx / mmax
        for m in f0.M[:3]:
            (x0, y0), (x1, _) = f0.N[m["i"]], f0.N[m["j"]]
            b.poly([(x0 + (x1 - x0)*k/80, y0 - member_moment(f0, m, k/80) * msc) for k in range(81)], C["muted"], 2, dash="6 5")
        b.text_px(b.X(1), b.Y(0) - 0.1 * msc * sx - 16, "虛線：無沉陷時 MB = MC = −0.1 wL^2", 12.5, C["muted"])
        b.text_px(b.X(0) + 6, b.Y(0) - 30, f"RA = {f.R['A'][1]:.1f} wL（無沉陷 {f0.R['A'][1]:.1f} wL）", 12.5, C["text"], anchor="start", weight="700")
    return beam_strip(f, ["AB", "BC", "CD"], f"{OUT}/{TAG}-fig-2-settlement.svg",
        "圖 2　SA-2019-3 沉陷 Δ = wL⁴/(12EI) 時的變形與彎矩", W=900, H1=230, H2=360, yc=0.40, mpx=90,
        supports=[("A", "pin"), ("B", "roller"), ("C", "roller"), ("D", "roller")],
        dlabels=[("B", "下沉 Δ", 52), ("C", "下沉 Δ", 52)], prec=3,
        mlabels=[("AB", 0.5, "C", False), ("BC", 0.5, "C", False), ("CD", 0.5, "C", False)],
        sub_def="B、C 同量下沉，中跨整段平移（弦轉角 0），兩邊跨弦轉角 ±Δ/L",
        sub_bmd="實線：Δ = wL^4/(12EI)，B、C 彎矩恰為 0，三跨各如簡支梁（跨中 0.125 wL^2）",
        note="沉陷把 B、C 的負彎矩卸掉：RA 由 0.4wL 增為 0.5wL，正好增加 0.1wL", unit_m="wL^2", extra=extra)

FIGURES.append((fig2_settle, "沉陷方向或弦轉角正負寫反（RA 變小）；以為沉陷不改變彎矩分布"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
