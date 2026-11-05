#!/usr/bin/env python3
"""SA-2019-4 解題圖解（struct-diagram；2026-11-05 階段 E）
  圖 2  元素端點條件與等效節點載重（兩格）：
        ① 五個元素的端點條件與它們貢獻給 [K] 的係數——C 鉸、E 滾的轉角沒有編號，② 與 ⑤ 用修正勁度
        ② 桿件載重換成 d₁–d₄ 上的等效節點載重——w 在 DE、Q 的柱下端為鉸
  攔：C 讀成固定端、w 放到 BD、一端鉸的桿套用兩端固定的固端力、轉角正向與考卷相反。
所有係數由本腳本以元素公式組裝，再與解析 §4 Step 2–3／§5 的 [K]、{P} assert。
用法：python3 gen_SA-2019-4_fem.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
from fractions import Fraction as Fr
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-4"

# ── 題目正本 §4：A(0,0) 固定、C(L,0) 鉸、E(2L,L) 滾；B 為零長度旋轉彈簧 10EI/L；各桿 L、EI ──
KR = Fr(10)                                   # 旋轉彈簧 k_r·L/EI
# 元素對 (d1, θ) 的係數，單位 EI/L^3、EI/L^2、EI/L（d1 向右、θ 逆時針為正）
FIXED = dict(kdd=Fr(12), kdt=Fr(6), ktt=Fr(4))        # 兩端固定柱（遠端固定）
PROP = dict(kdd=Fr(3), kdt=Fr(3), ktt=Fr(3))          # 遠端鉸的柱（修正勁度，凝縮遠端轉角）
BEAM = dict(near=Fr(4), far=Fr(2))                    # 梁 BD 兩端轉角
BEAM_PIN = Fr(3)                                      # 梁 DE，E 鉸 → 3EI/L

# ── 組裝 [K]（以 EI/L^3 為單位，L 次方另記：K_dd、K_dθ·L、K_θθ·L^2）──
K = {(1, 1): FIXED["kdd"] + PROP["kdd"],
     (1, 2): FIXED["kdt"], (1, 3): Fr(0), (1, 4): PROP["kdt"],
     (2, 2): FIXED["ktt"] + KR, (2, 3): -KR, (2, 4): Fr(0),
     (3, 3): KR + BEAM["near"], (3, 4): BEAM["far"],
     (4, 4): PROP["ktt"] + BEAM["near"] + BEAM_PIN}
DOC_K = {(1, 1): 15, (1, 2): 6, (1, 3): 0, (1, 4): 3, (2, 2): 14, (2, 3): -10, (2, 4): 0,
         (3, 3): 14, (3, 4): 2, (4, 4): 10}                      # 解析 §5
assert K == {k: Fr(v) for k, v in DOC_K.items()}, K

# ── 等效節點載重（固端力反號）：中點集中力、均佈 ──
FF_V, FF_M = Fr(1, 2), Fr(1, 8)          # 兩端固定，中點集中力：V = P/2、M = PL/8
PR_V, PR_M = Fr(11, 16), Fr(3, 16)       # 遠端鉸、中點集中力：固定端 V = 11Q/16、M = 3QL/16
PR_W = Fr(1, 8)                          # 遠端鉸、均佈：固定端 M = wL²/8
P_vec = {"d1": {"P": FF_V, "Q": PR_V, "R": Fr(1)},
         "d2": {"PL": FF_M}, "d3": {}, "d4": {"QL": PR_M, "wL2": -PR_W}}
assert P_vec == {"d1": {"P": Fr(1, 2), "Q": Fr(11, 16), "R": 1}, "d2": {"PL": Fr(1, 8)},
                 "d3": {}, "d4": {"QL": Fr(3, 16), "wL2": Fr(-1, 8)}}   # 解析 §5 {P}


def fr(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


A, B, D, Cn, E = (0, 0), (0, 1), (1, 1), (1, 0), (2, 1)
PW, PH = 700, 600


def base_canvas(title, sub):
    xr, yr = (-0.75, 2.55), (-0.32, 1.42)
    Lm, Tm, Bm = 40, 120, 70
    sx = min((PW - 2 * Lm) / (xr[1] - xr[0]), (PH - Tm - Bm) / (yr[1] - yr[0]))
    extra = (PH - Tm - Bm - (yr[1] - yr[0]) * sx) / 2
    cv = Canvas(PW, PH, sx=sx, ox=Lm - xr[0] * sx + 10, oy=Bm + extra - yr[0] * sx)
    cv.panel(title, sub)
    return cv


def frame(cv, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    for p, q in ((A, B), (B, D), (Cn, D), (D, E)):
        cv.line(p, q, col, 5, cap="butt")
    cv.support(A, "fixed"); cv.support(Cn, "pin"); cv.support(E, "roller")
    for p, t, dx, dy in ((A, "A", -18, 6), (B, "B", -16, 24), (D, "D", 16, 24),
                         (Cn, "C", 20, 4), (E, "E", 18, -16)):
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, t, 15, C["text"], weight="700")
    cv.circle((0.07, 1), 0.045, "#FFFFFF", C["accent"], 2.4)     # 旋轉彈簧（零長度，畫在 B 右側）


def panel1():
    cv = base_canvas("① 元素端點條件與 [K] 係數", "側移向右、三個轉角逆時針為正（同考卷右圖）；係數單位 EI/L³、EI/L²、EI/L")
    frame(cv)
    # 自由度
    cv.arrow((2.0, 1.0), (2.32, 1.0), C["deform"], 2.4, 9)
    cv.math_px(cv.X(2.36), cv.Y(1.0) - 12, "d_{1}", 15, C["deform"], "start", weight="700")
    cv.moment_arrow(B, r=24, ccw=True, color=C["deform"], w=2.2, span=200, start=110)
    cv.math_px(cv.X(0) - 34, cv.Y(1) - 26, "d_{2}", 14, C["deform"], weight="700")
    cv.moment_arrow((0.07, 1), r=20, ccw=True, color=C["deform"], w=2.0, span=160, start=-20)
    cv.math_px(cv.X(0.07) + 26, cv.Y(1) - 28, "d_{3}", 14, C["deform"], weight="700")
    cv.moment_arrow(D, r=24, ccw=True, color=C["deform"], w=2.2, span=200, start=10)
    cv.math_px(cv.X(1) + 30, cv.Y(1) - 28, "d_{4}", 14, C["deform"], weight="700")
    # 元素說明
    lab = [((-0.1, 0.55), "end", f"① AB 兩端固定", f"{FIXED['kdd']}, {FIXED['kdt']}L, {FIXED['ktt']}L^{{2}}"),
           ((1.1, 0.55), "start", "② CD：C 鉸 → 修正", f"{PROP['kdd']}, {PROP['kdt']}L, {PROP['ktt']}L^{{2}}"),
           ((0.5, 1.12), "middle", "④ BD", f"{BEAM['near']}, {BEAM['far']}"),
           ((1.62, 1.24), "middle", "⑤ DE：E 滾 → 修正", f"{BEAM_PIN}EI/L")]
    for (x, y), anc, t1, t2 in lab:
        cv.text_px(cv.X(x), cv.Y(y) - 10, t1, 13.5, C["text"], anc, weight="700")
        cv.math_px(cv.X(x), cv.Y(y) + 12, t2, 13.5, C["bmd"], anc, weight="700")
    cv.text_px(cv.X(0.12), cv.Y(1) + 26, f"③ 彈簧 {KR}EI/L", 13, C["accent"], "start", weight="700")
    for p in (Cn, E):
        cv.circle(p, 0.11, "none", C["accent"], 2.2, dash="5 4")
    cv.text_px(cv.X(1.55), cv.Y(0.25), "C、E 的轉角題目沒編號", 12.5, C["accent"], weight="700")
    cv.text_px(cv.X(1.55), cv.Y(0.25) + 20, "→ ② ⑤ 用一端鉸的修正勁度", 12.5, C["accent"], weight="700")
    cv.math_px(PW / 2, PH - 50, f"K_{{11}} = 12 + 3 = {K[(1,1)]},   K_{{44}} = 3 + 4 + 3 = {K[(4,4)]},   K_{{14}} = +{K[(1,4)]}", 14, C["bmd"], weight="700")
    cv.text_px(PW / 2, PH - 24, "C 讀成固定端，前兩項會錯成 24、11", 12.5, C["muted"])
    return cv


def panel2():
    cv = base_canvas("② 桿件載重 → 等效節點載重 {P}", "固端力反號；② 與 ⑤ 用一端鉸（遠端）的固端力")
    frame(cv, ghost=True)
    # 實際載重
    cv.arrow((-0.32, 0.5), (-0.02, 0.5), C["load"], 2.8, 10)
    cv.math_px(cv.X(-0.36), cv.Y(0.5), "P", 15, C["load"], "end", weight="700")
    cv.arrow((0.68, 0.5), (0.98, 0.5), C["load"], 2.8, 10)
    cv.math_px(cv.X(0.64), cv.Y(0.5), "Q", 15, C["load"], "end", weight="700")
    cv.udl(D, E, 0.16, n=8, color=C["load"], label=None)
    cv.math_px(cv.X(1.38), cv.Y(1.16) - 12, "w", 15, C["load"], weight="700")
    cv.text_px(cv.X(1.38) + 12, cv.Y(1.16) - 12, "（DE 全長）", 12.5, C["load"], "start", weight="700")
    cv.arrow((2.03, 1.0), (2.3, 1.0), C["load"], 2.8, 10)
    cv.math_px(cv.X(2.33), cv.Y(1.0) + 16, "R", 15, C["load"], "start", weight="700")
    # 等效節點載重
    d1 = f"P/2 + {P_vec['d1']['Q'].numerator}Q/{P_vec['d1']['Q'].denominator} + R"
    cv.arrow((0.15, 1.3), (0.75, 1.3), C["deform"], 3.0, 11)
    cv.math_px(cv.X(0.45), cv.Y(1.3) - 16, "d_{1}: " + d1, 14, C["deform"], weight="700")
    cv.moment_arrow(B, r=26, ccw=True, color=C["deform"], w=2.6, span=200, start=110)
    cv.math_px(cv.X(0) - 40, cv.Y(1) - 4, f"d_{{2}}: +PL/{FF_M.denominator}", 14, C["deform"], "end", weight="700")
    cv.math_px(cv.X(0.3), cv.Y(1) + 28, "d_{3}: 0", 14, C["deform"], weight="700")
    cv.text_px(cv.X(0.3), cv.Y(1) + 50, "（BD 無載重）", 12.5, C["muted"])
    cv.moment_arrow(D, r=26, ccw=True, color=C["deform"], w=2.6, span=150, start=200)
    cv.math_px(cv.X(1) + 8, cv.Y(1) + 44, f"d_{{4}}: +{PR_M.numerator}QL/{PR_M.denominator} - wL^{{2}}/{PR_W.denominator}", 14, C["deform"], "start", weight="700")
    cv.text_px(PW / 2, PH - 50, "② CD 中點 Q（C 鉸）：D 端 11Q/16、3QL/16；⑤ DE 均佈 w（E 滾）：D 端 wL²/8", 13, C["text"])
    cv.text_px(PW / 2, PH - 26, "w 放到 BD 會在梁端轉角多出 wL²/12；套兩端固定會寫成 Q/2、QL/8", 12.5, C["muted"])
    return cv


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    compose([panel1(), panel2()], cols=2, path=f"{OUT}/{TAG}-fig-2-elements-loads.svg")
    print("K =", {k: str(v) for k, v in K.items()})
    print("{P} =", P_vec)
