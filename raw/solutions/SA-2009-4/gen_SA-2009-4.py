#!/usr/bin/env python3
"""SA-2009-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2009-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2009-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2009-4"

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

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 0), "d": (-4, 0), "b": (4, 3), "c": (0, 3)}                    # #1 #3（ac = 3 m，c 與 b 同高；使用者確認）
SPEC = dict(
    nodes=N_, members=[],
    truss=[("a", "d"), ("a", "b"), ("a", "c")],                               # #2
    joints=["a"],
    supports=[("d", "pin", -90), ("b", "pin", 90), ("c", "pin", 180)],        # #4 d 左牆、b 右牆、c 天花板
    loads=[("a", (0, -1.3), "100 kN", (40, 0), True)],                        # #6
    labels={"a": (-14, 16), "d": (-6, 20), "b": (-16, -14), "c": (-18, 10)},
    dims=[((-4, 0), (0, 0), "4 m", 78), ((0, 0), (4, 0), "4 m", 78), ((4, 0), (4, 3), "3 m", 66)],
    extra_pts=[(-5.0, 3.8), (5.2, -1.6)])

def _dofs(cv):                                                                # #5 位移編號
    for nd, nx, ny in (("a", "1", "2"), ("b", "3", "4"), ("c", "5", "6"), ("d", "7", "8")):
        p = N_[nd]
        dof(cv, p, (1, 0), nx, 0.75, (10, 0)); dof(cv, p, (0, 1), ny, 0.75, (12, -4) if nd == "a" else (0, -10))
    cv.axes((-4.6, 2.4), 0.8, 0.8)
    cv.text_px(cv.X(-2.2), cv.Y(1.9), "ac = 3 m（c 與 b 同高；考卷未標）", 12.5, C["muted"], "middle")

def fig1_problem():
    return _post(lambda: problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 500,
                 note="b、c、d 皆為鉸支承（b、d 接垂直牆，c 接天花板）；藍色箭頭為考卷的結點位移編號"), _dofs)

FIGURES = [(fig1_problem, "支承方向讀錯、位移編號對錯節點、ac 長度亂取")]

# ── 解題圖（階段 E，2026-11-08）：直接勁度法重解，assert 對照 SA-2009-4.md §4（d₁ = 1/15 m →、d₂ = −21/80 m ↓；T_ad 16.67、T_ac 87.5、T_ab 20.83 kN 皆拉）──
def fig2_truss():
    from trussfig import solve, figure
    disp, N = solve(N_, [("a", "d"), ("a", "c"), ("a", "b")], 1000.0, ["a"], loads={"a": (0, -100)})
    assert abs(disp["a"][0] - 1/15) < 1e-12 and abs(disp["a"][1] + 21/80) < 1e-12
    assert abs(N[("a", "d")] - 50/3) < 1e-9 and abs(N[("a", "c")] - 87.5) < 1e-9 and abs(N[("a", "b")] - 125/6) < 1e-9
    return figure(N_, N, [("d", "pin", -90), ("b", "pin", 90), ("c", "pin", 180)], [],
                  disp, f"{OUT}/{TAG}-fig-2-truss.svg", f"圖 2　{TAG} 桿力（kN，拉＋）與 a 點位移",
                  note="a 點 d1 = 1/15 m（向右）、d2 = 21/80 m（向下）；三桿皆受拉", dlabel="(+0.0667, −0.2625) m",
                  dlabel_off=(92, 0), dpx=60, H=600, loads_out=[("a", (-0.0, -1.1), "100 kN", (-40, 0))],
                  lab_pos={("a", "d"): (0.5, -1)})

FIGURES.append((fig2_truss, "ad 桿以為受壓（a 向右移、ad 被拉長）；a 點水平位移漏算或方向畫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
