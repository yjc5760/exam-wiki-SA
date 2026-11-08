#!/usr/bin/env python3
"""SA-2012-4：題目附圖重繪（struct-diagram 規範；2026-11-05，SA-U2-4 題目正本批 1）
幾何、支承、載重逐項對應題目正本 SA-2012-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2012-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
from structdraw import Canvas, C
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2012-4"

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

# ── 判讀清單 #1–#7（L 取 1 個模型單位）──
SPEC = dict(
    nodes={"a": (0, 0), "b": (0, 1), "c": (0.5, 1), "d": (1, 1)},             # #1
    members=[dict(ij=("a", "b")), dict(ij=("b", "c")), dict(ij=("c", "d"), thick=True)],   # #2 cd 為 EI = ∞（粗線）
    supports=[("a", "fixed"), ("d", "pin")],                                  # #4 #5
    couples=[((0, 1.17), False, "R_{1}, r_{1}", (-34, -28)), ((1, 1.2), False, "R_{2}, r_{2}", (36, -28))],   # #6 皆順時針（畫在節點上方，照考卷）
    labels={"a": (-24, -16), "b": (-20, 10), "c": (0, 18), "d": (22, 6)},
    mlabels=[((-0.08, 0.5), "EI", None, "end"), ((0.25, 1.09), "EI", None, "middle"),
             ((0.75, 1.09), "EI = ∞", None, "middle")],                      # #2
    dims=[((0, 0), (0, 1), "L", -80), ((0, 0), (0.5, 0), "L/2", 50), ((0.5, 0), (1, 0), "L/2", 50)],
    extra_pts=[(-0.35, 1.35), (1.25, -0.15)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 500,
                          note="a 固接、d 鉸支承；ab、bc 為 EI，cd 為剛性桿（EI = ∞）；r_{1}、r_{2} 皆順時針")

FIGURES = [(fig1_problem, "d 讀成滾支承、cd 剛桿長度或自由度轉向讀錯")]

# ── 解題圖（階段 E，2026-11-08）：單位狀態（EI = L = 1；cd 以 EI = 1e9 模擬 ∞），assert 對照 SA-2012-4.md §4 Step 4：[K] = 4EI/L [[3, 4], [4, 14]]（順時針為正）──
def _model(mb=0.0, md=0.0):
    from frame2d import Frame
    f = Frame()
    for n, p in SPEC["nodes"].items(): f.node(n, *p)
    f.support("a", 1, 1, 1); f.support("d", 1, 1, 0)
    f.member("ab", "a", "b", 1.0); f.member("bc", "b", "c", 1.0); f.member("cd", "c", "d", 1e9)
    f.load("b", mz=mb); f.load("d", mz=md)                     # frame2d 力矩逆時針為正
    return f.solve()

def _K():
    import numpy as np
    Fm = np.zeros((2, 2))
    for k, (mb, md) in enumerate([(-1.0, 0.0), (0.0, -1.0)]):   # 順時針單位力矩
        f = _model(mb, md); Fm[:, k] = [-f.d["b"][2], -f.d["d"][2]]
    K = np.linalg.inv(Fm)
    assert np.allclose(K, 4 * np.array([[3, 4], [4, 14]]), atol=1e-4), K
    return K

def _unit(col, path, title, sub_def, sub_bmd, labels, dl):
    import beamfig
    from beamfig import frame_figure
    _inf = beamfig.inflections
    def _inf_nz(f_, m, n=400):                                  # 彎矩全為 0 的桿件（數值雜訊）不標反曲點
        return [] if max(abs(beamfig.member_moment(f_, m, k / 40)) for k in range(41)) < 1e-3 else _inf(f_, m, n)
    beamfig.inflections = _inf_nz
    K = _K(); f = _model(-K[0, col], -K[1, col])                 # 施加 [K] 第 col 行 ⇒ r = 單位向量
    r = (-f.d["b"][2], -f.d["d"][2]); assert abs(r[col] - 1) < 1e-6 and abs(r[1 - col]) < 1e-6
    sp = dict(nodes=SPEC["nodes"], supports=[("a", "fixed"), ("d", "pin")])
    try:
        return frame_figure(f, sp, path, title, sub_def, sub_bmd, labels, W=560, H=470, dfrac=0.16, dlabels=dl,
                            fmt="{:.0f}", notes=("", "數值單位 EI/L；cd 為剛桿（EI = ∞）"))
    finally:
        beamfig.inflections = _inf

def fig2_unit_r1():
    return _unit(0, f"{OUT}/{TAG}-fig-2-unit-r1.svg", f"圖 2　{TAG} 單位狀態 r1 = 1（r2 = 0）：[K] 第一行",
                 "b 順時針轉 1，cd 剛桿不動", "K11 = 4 + 8 = 12，K21 = 4 + 12 = 16（EI/L）",
                 [("ab", 1.0, -22, 4), ("ab", 0.0, 18, -6), ("bc", 0.0, 16, 24), ("bc", 1.0, 0, 22), ("cd", 1.0, -8, -14)],
                 [("b", "r1 = 1（順）", -64, -18)])

def fig3_unit_r2():
    return _unit(1, f"{OUT}/{TAG}-fig-3-unit-r2.svg", f"圖 3　{TAG} 單位狀態 r2 = 1（r1 = 0）：[K] 第二行",
                 "d 順時針轉 1：剛桿 cd 帶 c 上移 L/2、轉 1", "K12 = 16，K22 = 20 + 36 = 56（EI/L）",
                 [("bc", 0.0, -20, 24), ("bc", 1.0, 0, 22), ("cd", 1.0, -8, -14)],
                 [("c", "c 上移 L/2", 0, -22), ("d", "r2 = 1（順）", 30, -26)])

FIGURES += [(fig2_unit_r1, "以為 r1 狀態下 d 端不需力矩（漏掉 bc 剪力經剛桿力臂 L/2 的貢獻 12）"),
            (fig3_unit_r2, "剛桿轉動時漏掉 c 點平移 L/2 造成的弦轉角（K22 會少 36）")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
