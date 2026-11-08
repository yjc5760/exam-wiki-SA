#!/usr/bin/env python3
"""SA-2004-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2004-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2004-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-4"

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

# ── 判讀清單 #1–#8（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"A": (0, 0), "C": (1, 0), "B": (3, 0)},                           # #1 #5
    members=[dict(ij=("A", "C")), dict(ij=("C", "B"), thick=True)],          # #6 CB 為 3EI（畫粗）
    supports=[("A", "fixed"), ("B", "roller")],                               # #2 #3
    springs=[("C", 0.55, "k")],                                               # #4
    udl=[("A", "B", 0.32, "w")],                                              # #7
    labels={"A": (-30, -4), "B": (22, -16), "C": (16, 16)},
    mlabels=[((0.5, -0.14), "EI", None, "middle"), ((2.0, -0.16), "3EI", None, "middle")],   # #6
    dims=[((0, 0), (1, 0), "L", 112), ((1, 0), (3, 0), "2L", 112)],          # #5
    extra_pts=[(-0.25, 0.5), (3.2, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 400,
                          note="A 固定、B 滾支承；C 為連續節點，下接軸力彈簧 k = 12EI/L^{3}；w 作用於 A–B 全長",
                          margins=(80, 80, 60, 70))

FIGURES = [(fig1_problem, "C 讀成內鉸、CB 段 3EI 漏讀、w 只算到 C")]

# ── 解題圖（階段 E，2026-11-08）：以勁度法重解（w = L = EI = 1），assert 對照 SA-2004-4.md §4 Step 5–6 ──
#    v_C = −263/3192 wL⁴/EI、θ_C = −545/6384 wL³/EI；M_AC = +433/1064（逆時針）、M_CA = +37/532、M_CB = −37/532 wL²；彈簧力 263/266 wL（壓）
def _solve():
    from frame2d import Frame
    f = Frame()
    for n, p in {"A": (0, 0), "C": (1, 0), "B": (3, 0), "s": (1, -1)}.items(): f.node(n, *p)
    f.support("A", 1, 1, 1); f.support("B", 0, 1, 0); f.support("s", 1, 1, 1)
    f.member("AC", "A", "C", 1.0, w=1.0); f.member("CB", "C", "B", 3.0, w=1.0)
    f.member("Cs", "C", "s", 1e-9, rel=(1, 1), EA=12.0)            # 彈簧 k = 12EI/L³（長 1 的二力桿）
    f.solve()
    from frameviz import member_moment
    M = lambda nm, xi: member_moment(f, next(m for m in f.M if m["name"] == nm), xi)
    assert abs(f.d["C"][1] + 263/3192) < 1e-9 and abs(f.d["C"][2] + 545/6384) < 1e-9
    assert abs(M("AC", 0) + 433/1064) < 1e-9 and abs(M("AC", 1) - 37/532) < 1e-9 and abs(M("CB", 0) - 37/532) < 1e-9
    assert abs(M("CB", 1)) < 1e-9 and abs(12 * f.d["C"][1] + 263/266) < 1e-9
    return f, M

def fig2_solution():
    from beamfig import beam_strip
    f, M = _solve()
    xs = [k / 2000 for k in range(2001)]
    xm = max(xs, key=lambda x: M("CB", x)); Mmax = M("CB", xm)           # CB 段正彎矩極大（剪力零點）
    def extra(a, b):
        b.text_px(b.X(1 + 2 * xm), b.Y(0) + 104, f"CB 段極大 +{Mmax:.4f}（距 C {2*xm:.3f}L）", 12.5, C["bmd"], weight="700")
        b.text_px(b.X(1), b.Y(0) - 40, "C 不是鉸：M_C = +37/532 ≈ +0.0695", 12.5, C["accent"], weight="700")
    return beam_strip(f, ["AC", "CB"], f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2004-4 變形形狀與梁彎矩圖", W=900, H1=245, H2=320, prec=4,
        supports=[("A", "fixed"), ("B", "roller")], springs=["C"],
        dlabels=[("C", "v_C = 263/3192 wL^4/EI ≈ 0.0824（向下）", 44)],
        mlabels=[("AC", 0.0, "R", True), ("AC", 1.0, "L", False)],
        sub_def="C 下沉壓縮彈簧：彈簧力 263/266 wL ≈ 0.989 wL（壓力）",
        sub_bmd="A −433/1064 ≈ −0.4070（上緣受拉）→ C +37/532 → B 0",
        note="彈簧把 C 托住但仍下沉，C 處彎矩為正（下緣受拉）；把 C 當成剛性支承會得到負彎矩", unit_m="wL^2", extra=extra)

FIGURES.append((fig2_solution, "C 當成內鉸或剛性支承；彈簧力方向（壓／拉）判反；A 端受拉側畫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
