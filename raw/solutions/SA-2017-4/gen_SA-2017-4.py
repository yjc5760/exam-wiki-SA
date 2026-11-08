#!/usr/bin/env python3
"""SA-2017-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2017-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2017-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2017-4"

# ── 判讀清單 #1–#7 ──（考卷沒有尺寸；三個平面外框取 1 × 0.76，牆的位置依圖面比例量取）
W0, H0 = 1.0, 0.76          # 平面外框（考卷三圖外框比例約 370 × 282 px）
WALL, LINE = 7.5, 1.6

def _plan(cv, ox, walls, label):
    """ox：平面左下角 x（模型座標）；walls：[(x0,y0,x1,y1), ...]（以外框比例 0–1 表示）。"""
    rect = [(ox, 0), (ox + W0, 0), (ox + W0, H0), (ox, H0), (ox, 0)]
    cv.poly(rect, C["member"], LINE)
    for (a, b, c, d) in walls:
        cv.line((ox + a * W0, b * H0), (ox + c * W0, d * H0), C["member"], WALL, cap="square")
    cv.text((ox + W0 / 2, -0.12), label, 17, C["text"])

PLANS = [
    ("(a)", [(0, 0, 0, 1),                      # #1 左緣全長
             (0, 1, 0.31, 1), (0, 0, 0.31, 0),  # #2 上、下緣靠左約 1/3
             (0.31, 1, 0.31, 0.80), (0.31, 0, 0.31, 0.20)]),   # #3 向內短牆
    ("(b)", [(0.30, 0.5, 0.70, 0.5), (0.5, 0.27, 0.5, 0.73)]),  # #5 中央十字
    ("(c)", [(0, 0, 0.2, 0), (0, 0, 0, 0.23), (1, 0, 0.8, 0), (1, 0, 1, 0.23),     # #6 四角 L 形
             (0, 1, 0.2, 1), (0, 1, 0, 0.77), (1, 1, 0.8, 1), (1, 1, 1, 0.77),
             (0.34, 0.69, 0.66, 0.69), (0.34, 0.69, 0.34, 0.57), (0.66, 0.69, 0.66, 0.57),   # #7 中央核心上ㄇ
             (0.34, 0.31, 0.66, 0.31), (0.34, 0.31, 0.34, 0.43), (0.66, 0.31, 0.66, 0.43)]),  # 下ㄇ
]

def fig1_problem():
    W, H = 900, 330
    cv = Canvas(W, H, sx=205, ox=50, oy=95, bg="#FFFFFF")
    for k, (lab, walls) in enumerate(PLANS):
        _plan(cv, k * 1.45, walls, lab)
    cv.text_px(W / 2, 26, "粗線＝剪力牆，細線＝平面外框（考卷沒有尺寸，比例照圖面）", 13.5, C["muted"])
    cv.text_px(W / 2, H - 18, "(c) 除四角 L 形牆外，平面中央另有一個左右留開口的核心（上、下兩個ㄇ形）", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-problem.svg")

FIGURES = [(fig1_problem, "(a) 牆的方向讀反、(c) 漏讀中央核心")]

# ── 解題圖（階段 E，2026-11-08）：以圖面比例的牆位置（PLANS）計算剛心 CR、偏心 e 與樓層抗扭勁度 Kθ = Σk·d²
#    （剛性樓板；牆面內勁度取與牆長成正比的示意值，只比較相對大小）；assert 對照 SA-2017-4.md §4–§5 的定性結論：
#    (b) CR = CM、Kθ ≈ 0（兩片牆都通過剛心）；(c) Kθ 最大；(a) y 向偏心最大；排序 Kθ(c) > Kθ(a) > Kθ(b)
def _props(walls):
    xw, yw = [], []                                   # x 向牆（水平線）：(y, L)；y 向牆（垂直線）：(x, L)
    for a, b, c, d in walls:
        if abs(b - d) < 1e-9: xw.append((b * H0, abs(c - a) * W0))
        else: yw.append((a * W0, abs(d - b) * H0))
    ycr = sum(y * L for y, L in xw) / sum(L for _, L in xw); xcr = sum(x * L for x, L in yw) / sum(L for _, L in yw)
    Kt = sum(L * (y - ycr) ** 2 for y, L in xw) + sum(L * (x - xcr) ** 2 for x, L in yw)
    return xcr, ycr, Kt

def fig2_torsion():
    P = {lab: _props(w) for lab, w in PLANS}
    (xa, ya, Ka), (xb, yb, Kb), (xc, yc, Kc) = P["(a)"], P["(b)"], P["(c)"]
    assert abs(xb - W0 / 2) < 1e-9 and abs(yb - H0 / 2) < 1e-9 and Kb < 1e-12
    assert abs(xc - W0 / 2) < 1e-9 and abs(yc - H0 / 2) < 1e-9 and Kc > Ka > Kb
    assert abs(ya - H0 / 2) < 1e-9 and W0 / 2 - xa > 0.4 * W0
    W, H = 900, 400
    cv = Canvas(W, H, sx=205, ox=50, oy=130, bg="#FFFFFF")
    for k, (lab, walls) in enumerate(PLANS):
        ox = k * 1.45; _plan(cv, ox, walls, lab)
        xcr, ycr, Kt = P[lab]; cm = (ox + W0 / 2, H0 / 2); cr = (ox + xcr, ycr)
        cv.dot(cm, 7, fill="#FFFFFF", stroke=C["deform"], w=2.6)
        cv.polygon([(cr[0], cr[1] + 0.035), (cr[0] + 0.035, cr[1]), (cr[0], cr[1] - 0.035), (cr[0] - 0.035, cr[1])], C["load"], C["load"], 1)
        if abs(cr[0] - cm[0]) > 1e-6:
            cv.line(cr, cm, C["load"], 2.0, dash="5 4")
            cv.text_px(cv.X((cr[0] + cm[0]) / 2) + 14, cv.Y(cm[1]) + 26, f"e ≈ {cm[0] - cr[0]:.2f} 倍平面長", 12.5, C["load"], weight="700")
        cv.text_px(cv.X(ox + W0 / 2), cv.Y(-0.12) + 26, f"相對抗扭勁度 Σk·d² = {100 * Kt / Kc:.0f}", 13, C["accent"], weight="700")
    cv.text_px(W / 2, 28, f"圖 2　{TAG} 三種配置的剛心、偏心與抗扭勁度（示意比例，以 (c) = 100）", 16, C["text"], weight="700")
    cv.text_px(W / 2, 52, "◆ 剛心 CR　○ 質心 CM（平面中心）", 13, C["muted"])
    cv.text_px(W / 2, H - 16, "(b) 無偏心但兩片牆都通過剛心，Σk·d² = 0；(c) 牆在外圍、力臂最大；(a) 有上下牆力偶但 y 向偏心最大", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-torsion.svg")

FIGURES.append((fig2_torsion, "以為 (b) 對稱就抗扭好（十字牆當閉合核心筒）；(a) 的偏心方向判錯"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
