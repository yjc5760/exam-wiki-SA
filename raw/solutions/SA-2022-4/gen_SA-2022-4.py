#!/usr/bin/env python3
"""SA-2022-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2022-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2022-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-4"

def _post(fn, post):
    """在 problem_figure 存檔前補畫（自由度箭頭、彈簧符號等），不改共用程式庫。"""
    orig = Canvas.save
    def save(self, path):
        post(self); return orig(self, path)
    Canvas.save = save
    try: return fn()
    finally: Canvas.save = orig

def dof(cv, p, d, lab, L=0.55, lo=(0, 0)):
    """自由度箭頭（藍色）：p 為節點，d 為方向，lab 為編號。"""
    q = (p[0] + d[0]*L, p[1] + d[1]*L)
    cv.arrow(p, q, C["deform"], 2.2, 9)
    cv.math(q, lab, 14, C["deform"], "middle", dx=lo[0], dy=lo[1], weight="700")

# ── 判讀清單 #1–#8 ──
X = {"a": 0, "e": 4, "m": 8, "n": 12}; H1, H2, H3 = 3.6, 7.2, 10.8            # #1 #2
N_ = {"a": (0, 0), "e": (4, 0), "m": (8, 0), "n": (12, 0),
      "b": (0, H1), "b2": (4, H1),
      "c": (0, H2), "c2": (4, H2), "c3": (8, H2), "c4": (12, H2),
      "d": (0, H3), "d2": (4, H3), "d3": (8, H3), "d4": (12, H3)}
cols = [("a", "b"), ("b", "c"), ("c", "d"), ("e", "b2"), ("b2", "c2"), ("c2", "d2"),
        ("m", "c3"), ("c3", "d3"), ("n", "c4"), ("c4", "d4")]                 # #4 m、n 柱直通第二層（長 7.2 m）
beams = [("b", "b2"), ("c", "c2"), ("c2", "c3"), ("c3", "c4"), ("d", "d2"), ("d2", "d3"), ("d3", "d4")]   # #3 #5
SPEC = dict(
    nodes=N_,
    members=[dict(ij=c) for c in cols],
    supports=[(k, "fixed") for k in ("a", "e", "m", "n")],                    # #6
    loads=[("b", (1.8, 0), "100 kN", (-34, -14)), ("c", (1.8, 0), "200 kN", (-34, -14)),
           ("d", (1.8, 0), "300 kN", (-34, -14))],                            # #8
    labels={"a": (14, -14), "e": (14, -14), "m": (16, -14), "n": (14, -14), "b": (12, -16), "c": (12, -16), "d": (12, -16)},
    dims=[((0, 0), (4, 0), "4 m", 52), ((4, 0), (8, 0), "4 m", 52), ((8, 0), (12, 0), "4 m", 52),
          ((12, 0), (12, H1), "3.6 m", 70), ((12, H1), (12, H2), "3.6 m", 70), ((12, H2), (12, H3), "3.6 m", 70)],
    extra_pts=[(-3.0, H3 + 0.6), (14.2, -1.0)])

def _beams(cv):                                                               # #7 梁 EI = ∞（粗線）
    for i, j in beams:
        cv.line(N_[i], N_[j], C["member"], 9.0, cap="butt")

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 600,
                 note="第一層梁只有 a–e 一跨，m、n 柱直通第二層；柱 EI = 97200 kN-m^{2}，梁 EI = ∞（粗線）"), _beams)

FIGURES = [(fig1_problem, "m、n 柱誤以為在第一層有梁（柱長 3.6 m）")]

# ── 解題圖（階段 E，2026-11-08）：平面剛架勁度法（柱 EI = 97200、梁 EI 取 1e7 倍模擬 ∞、EA = 1e11 不計軸向），assert 對照 SA-2022-4.md §4–§5 ──
#    Δ1 = Δb = 0.0098 m、Δ2 = Δc = 0.0176 m、Δ3 = 0.0206 m；a 柱底 245 kN ←、441 kN-m；m 柱底 55 kN ←、198 kN-m
def _solve():
    from frame2d import Frame
    f = Frame(); EI = 97200.0
    for n, p in N_.items(): f.node(n, *p)
    for k in ("a", "e", "m", "n"): f.support(k, 1, 1, 1)
    for i, j in cols: f.member(i + j, i, j, EI, EA=1e11)               # 不計軸向（EA 取大值；預設 1e8·EI 對剛梁會病態）
    for i, j in beams: f.member(i + j, i, j, EI * 1e7, EA=1e11)       # 梁 EI = ∞
    f.load("b", fx=100); f.load("c", fx=200); f.load("d", fx=300)
    f.solve()
    assert abs(f.d["b"][0] - 0.0098) < 1e-7 and abs(f.d["c"][0] - 0.0176) < 1e-7 and abs(f.d["d"][0] - 0.0206) < 1e-7
    assert abs(f.R["a"][0] + 245) < 1e-3 and abs(f.R["m"][0] + 55) < 1e-3
    assert abs(f.R["a"][2] - 441) < 1e-2 and abs(f.R["m"][2] - 198) < 1e-2        # 逆時針為正（容許量為 EI = ∞ 的數值近似）
    return f

def fig2_solution():
    from beamfig import frame_figure
    f = _solve()
    sp = dict(nodes=N_, supports=[(k, "fixed") for k in ("a", "e", "m", "n")])
    skip = tuple(i + j for i, j in beams)
    def extra(a, b):
        for i, j in beams:                                                     # 梁 EI = ∞：兩圖都畫粗線（不畫彎矩）
            b.line(N_[i], N_[j], "#4A5568", 7.0, cap="butt")
        b.text_px(b.X(0), b.Y(0) + 34, "a：245 kN ←、441 kN-m 逆時針", 12.5, C["load"], weight="700")
        b.text_px(b.X(9), b.Y(0) + 34, "m：55 kN ←、198 kN-m 逆時針", 12.5, C["load"], weight="700")
        from frameviz import deformed                                        # 變形圖補畫梁（剛梁只平移）：比例與 frame_figure 相同
        dmax = 0.0
        for m in f.M:
            if m["name"] in skip: continue
            p0, p1 = f.N[m["i"]], f.N[m["j"]]
            for k, q in enumerate(deformed(f, m, 1.0, 40)):
                b0 = (p0[0] + (p1[0] - p0[0]) * k / 40, p0[1] + (p1[1] - p0[1]) * k / 40)
                dmax = max(dmax, abs(q[0] - b0[0]), abs(q[1] - b0[1]))
        span = max(max(abs(p[0] - q[0]), abs(p[1] - q[1])) for p in f.N.values() for q in f.N.values())
        ds = 0.10 * span / dmax
        for i, j in beams:
            a.line((N_[i][0] + f.d[i][0] * ds, N_[i][1]), (N_[j][0] + f.d[j][0] * ds, N_[j][1]), C["deform"], 7.0, cap="butt")
    return frame_figure(f, sp, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", f"圖 2　{TAG} 側移形狀與柱彎矩圖",
                        "梁只平移不轉：各柱雙曲率、反曲點在柱中央", "柱彎矩（kN-m；梁 EI = ∞ 不標）",
                        [("ab", 0.0, -30, 0), ("mc3", 0.0, 44, 0)],
                        W=560, H=560, dfrac=0.10, mfrac=0.10, margins=(70, 70, 95, 110),
                        skip=skip, fmt="{:.0f}",
                        dlabels=[("b", "Δb = 9.8 mm", -64, 0), ("c", "Δc = 17.6 mm", -66, 0), ("d", "Δ3 = 20.6 mm", -66, 0)],
                        notes=("基底剪力 2×245 + 2×55 = 600 kN", ""), extra=extra)

FIGURES.append((fig2_solution, "m、n 挑高柱勁度沒用 k/8（以為 12EI/h^3）；柱底彎矩用 Vh 而非 Vh/2（a 柱）／Vh（m 柱，長 2h）弄混"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
