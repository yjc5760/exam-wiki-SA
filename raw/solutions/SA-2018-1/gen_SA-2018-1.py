#!/usr/bin/env python3
"""SA-2018-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2018-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2018-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2018-1"

# ── 判讀清單 #1–#6 ──（考卷沒有尺寸：層高取 1、跨度與牆寬照圖面比例，僅示意）
NS = 8; X = dict(f1=0.0, f2=1.95, l1=2.55, w0=2.65, w1=4.10, r1=4.20, f3=4.80, f4=6.80)   # 圖面量取比例

def fig1_problem():
    W, H = 640, 640
    cv = Canvas(W, H, sx=62, ox=150, oy=70, bg="#FFFFFF")
    top = NS
    cv.polygon([(X["w0"], 0), (X["w1"], 0), (X["w1"], top), (X["w0"], top)], "rgba(63,74,90,0.18)", C["member"], 2.6)   # #3 剪力牆
    for x in (X["f1"], X["f2"], X["f3"], X["f4"]):                                                                     # #2 柱
        cv.line((x, 0), (x, top), C["member"], 4.0, cap="butt")
    for k in range(1, NS + 1):
        cv.line((X["f1"], k), (X["f2"], k), C["member"], 4.0, cap="butt")                                              # 梁
        cv.line((X["f3"], k), (X["f4"], k), C["member"], 4.0, cap="butt")
        for (a, b) in ((X["f2"], X["w0"]), (X["w1"], X["f3"])):                                                         # #4 連桿
            cv.line((a, k), (b, k), C["member"], 2.4)
            cv.dot((a + 0.14 if a == X["f2"] else a + 0.04, k), 4.2, fill="#FFFFFF", stroke=C["member"], w=1.8)
            cv.dot((b - 0.04 if b == X["w0"] else b - 0.14, k), 4.2, fill="#FFFFFF", stroke=C["member"], w=1.8)
        cv.arrow((X["f1"] - 1.3, k), (X["f1"], k), C["load"], 3.0, 11)                                                  # #5
        cv.math((X["f1"] - 1.3, k), "F", 17, C["load"], "end", dx=-6, dy=8, weight="700")
    cv.line((X["f1"] - 0.6, 0), (X["f4"] + 0.6, 0), C["member"], 2.6)                                                  # #6 地面
    for i in range(16):
        x = X["f1"] - 0.5 + i * 0.5; cv.line((x, 0), (x - 0.18, -0.25), C["member"], 1.6)
    cv.text(((X["w0"] + X["w1"]) / 2, top + 0.45), "剪力牆", 14, C["muted"])
    cv.text(((X["f2"] + X["w0"]) / 2, top + 0.45), "連桿", 14, C["muted"])
    cv.text_px(W / 2, H - 18, "8 層；兩側單跨構架以兩端鉸接連桿連到中央剪力牆；牆的樓層勁度為構架 5 倍（尺寸為示意）", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-problem.svg")

FIGURES = [(fig1_problem, "把連桿當成剛接（可傳彎矩）、外力只作用在剪力牆")]

# ── 解題圖（階段 E，2026-11-08）：示意數值模型（題目要求的是形狀），assert 對照 SA-2018-1.md §4（一）示意數值 ──
#    牆：8 層懸臂撓曲梁柔度矩陣；構架：剪力型樓層彈簧 k；連桿軸向剛性 ⇒ 同層同位移；「5 倍」取 12EI/h³ = 5k
def _solve(EI=5/12, k=1.0):
    import numpy as np
    z = np.arange(1, NS + 1, dtype=float)
    fw = np.array([[min(a, b) ** 2 * (3 * max(a, b) - min(a, b)) / (6 * EI) for b in z] for a in z]); Kw = np.linalg.inv(fw)
    Kf = np.zeros((NS, NS))
    for s_ in range(NS):
        Kf[s_, s_] += k
        if s_: Kf[s_ - 1, s_ - 1] += k; Kf[s_, s_ - 1] -= k; Kf[s_ - 1, s_] -= k
    u = np.linalg.solve(Kw + Kf, np.ones(NS)); return Kf @ u, Kw @ u

def fig2_distribution():
    from structdraw import compose
    ff, fw = _solve()
    exp_f = [-2.44, 0.41, 0.90, 0.98, 0.99, 0.95, 0.71, 1.35]; exp_w = [3.44, 0.59, 0.10, 0.02, 0.01, 0.05, 0.29, -0.35]
    assert all(abs(a - b) < 0.006 for a, b in zip(ff, exp_f)) and all(abs(a - b) < 0.006 for a, b in zip(fw, exp_w))
    assert all(abs(a + b - 1) < 1e-9 for a, b in zip(ff, fw))
    W, H = 480, 620; sc = 50
    panels = []
    for name, vals, sub in (("構架受的樓層力", ff, "下部反向（向左）、頂層大於 F"), ("剪力牆受的樓層力", fw, "下部大於 F、頂層反向（向左）")):
        cv = Canvas(W, H, sx=sc, ox=0.42 * W, oy=70)
        cv.panel(name, sub)
        cv.line((0, 0), (0, NS), C["member"], 4.0, cap="butt"); cv.line((-1.0, 0), (1.0, 0), C["member"], 2.4)
        for k_, v in enumerate(vals, start=1):
            cv.arrow((0, k_), (1.0, k_), C["ghost"], 2.0, 8, dash="5 4")                       # 虛線：外力 F（量尺）
            if abs(v) > 0.02:
                cv.arrow((0, k_), (v * 1.0, k_), C["load"] if v > 0 else C["compr"], 3.2, 10)
            cv.text_px(cv.X(max(v, 1.0)) + 10, cv.Y(k_) + 5, f"{v:+.2f}F".replace("-", "−"), 12.5,
                       C["load"] if v > 0 else C["compr"], anchor="start", weight="700")
            cv.text_px(12, cv.Y(k_) + 5, f"{k_} 樓", 11.5, C["muted"], anchor="start")
        panels.append(cv)
    path = f"{OUT}/{TAG}-fig-2-distribution.svg"
    compose(panels, title=f"圖 2　{TAG} 牆–構架互制的樓層水平力分布（示意數值，12EI/h³ = 5k）", path=path,
            note="灰虛線＝外力 F（量尺）；紅＝與外力同向、藍＝反向；同一層構架＋牆 = F。字面 1:5 讀法則為構架 F/6、牆 5F/6 均勻分布")
    return path

FIGURES.append((fig2_distribution, "照字面 1:5 畫成均勻分布、看不出互制；反向力畫錯層（構架反向只在下部 1–2 層，頂層構架大於 F）"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
