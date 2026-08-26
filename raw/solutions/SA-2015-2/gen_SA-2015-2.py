#!/usr/bin/env python3
"""
SA-2015-2 F 點剪力影響線（Müller–Breslau ＋ 共軛梁法）— 解題圖解產生腳本

用法：
    python3 gen_SA-2015-2.py [輸出目錄]

三條鐵則的落實：
  1. 影響線曲線與每個縱距都由下方 IL 分段多項式取樣，沒有一個座標是描摹的
  2. 分段多項式由 y'' = M/EI 逐段積分＋邊界條件在 _solve() 內解出；
     改 XA…XE 任一座標重跑，M(x)、共軛梁載重與影響線會一起變
  3. 另以「釋放 R_A」的獨立路徑重算一次，兩者逐點 assert（見 _crosscheck）
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-2"

# ══════════════════════════════════════════════════════════
# 幾何（考卷圖二：AF = FB = 15、BC = CD = 10、DE = 30）
# ══════════════════════════════════════════════════════════
XA, XF, XB, XC, XD, XE = 0.0, 15.0, 30.0, 40.0, 50.0, 80.0
SPAN = XE - XA
STA = [("A", XA), ("F", XF), ("B", XB), ("C", XC), ("D", XD), ("E", XE)]
SUPPORTS = {XA: "pin", XB: "roller", XD: "roller", XE: "roller"}

# 靜不定度：反力 A(2) + B,D,E 各 1 = 5；平衡 3 式 ＋ 內鉸 C 1 式 ⇒ 1 度
N_R, N_EQ, N_HINGE = 5, 3, 1
assert N_R - N_EQ - N_HINGE == 1

# ── 釋放 F 點剪力（施加單位剪力對）後的靜定基本結構 ────────
# 反力由靜力平衡解得（推導見 .md §4 Step 1）
RA0, RB0, RD0, RE0 = 1.0, -4.0, 4.0, -1.0
assert abs(RA0 + RB0 + RD0 + RE0) < 1e-12                      # 單位剪力對自身平衡


def M0(x):
    """基本結構的彎矩（下凹為正）。由左側自由體：Σ R_i·(x − x_i)。"""
    return (RA0 * x + (RB0 * (x - XB) if x > XB else 0.0)
            + (RD0 * (x - XD) if x > XD else 0.0))


assert abs(M0(XC)) < 1e-12                     # 內鉸 C 處彎矩必須為零 ← 檢查反力對不對
assert abs(M0(XE)) < 1e-12                     # 端點彎矩為零


# ══════════════════════════════════════════════════════════
# y'' = M/EI 逐段積分（EI = 1）
#   斷點：F（剪力釋放：y 跳、θ 連續）、C（內鉸：θ 跳、y 連續）
#   邊界：A、B、D、E 四個支承 y = 0
# ══════════════════════════════════════════════════════════
KNOT = [XA, XF, XB, XC, XD, XE]


def _solve():
    import numpy as np
    # 以四階多項式表示每段（M 為一次式 ⇒ y 為三次式），區段：[0,15] [15,40] [40,80]
    # 每段內部 M 有轉折，改以「數值積分 + 常數」處理：用 3 段各自的 (θ0, y0)
    segs = [(XA, XF), (XF, XC), (XC, XE)]
    n = 4000

    def integrate(a, b, th0, y0):
        h = (b - a) / n
        xs = [a + i * h for i in range(n + 1)]
        th = [th0]; y = [y0]
        for i in range(n):
            xm = xs[i] + h / 2
            th.append(th[-1] + M0(xm) * h)
            y.append(y[-1] + (th[-2] + th[-1]) / 2 * h)
        return xs, th, y

    def run(p):
        """p = [θ_A, θ_F+ 的增量恆為 0（θ 連續）, Δy_F, θ_C+ ]  → 只需 3 個自由參數
        取 u = [θ_A, Δy_F, Δθ_C]，y_A = 0 已知。"""
        thA, dyF, dthC = p
        x1, t1, y1 = integrate(XA, XF, thA, 0.0)
        x2, t2, y2 = integrate(XF, XC, t1[-1], y1[-1] + dyF)     # θ 連續、y 跳 dyF
        x3, t3, y3 = integrate(XC, XE, t2[-1] + dthC, y2[-1])    # y 連續、θ 跳 dthC
        def at(xq):
            for xs, ys in ((x1, y1), (x2, y2), (x3, y3)):
                if xs[0] <= xq <= xs[-1]:
                    i = min(int((xq - xs[0]) / (xs[1] - xs[0]) + 0.5), len(xs) - 1)
                    return ys[i]
            raise ValueError
        return (x1, y1, x2, y2, x3, y3), [at(XB), at(XD), at(XE)]

    A = np.zeros((3, 3)); b0 = np.array(run([0, 0, 0])[1])
    for j in range(3):
        p = [0, 0, 0]; p[j] = 1.0
        A[:, j] = np.array(run(p)[1]) - b0
    u = np.linalg.solve(A, -b0)
    curves, resid = run(list(u))
    assert max(abs(r) for r in resid) < 1e-6, resid
    return curves, u


_CURVES, _U = _solve()
_X1, _Y1, _X2, _Y2, _X3, _Y3 = _CURVES
THETA_A, DYF = _U[0], _U[1]
Y_Fm = _Y1[-1]
Y_Fp = _Y2[0]
DELTA = Y_Fp - Y_Fm                            # 影響線正規化用的相對位移
Y_C = _Y2[-1]


def _round(v, q=1e-6):
    return round(v / q) * q


# 對照手算的精確值（.md §4 引用的就是這組）
assert abs(THETA_A - (-950.0)) < 1.0, THETA_A
assert abs(DELTA - 24000.0) < 3.0, DELTA
assert abs(Y_C - (-4000.0)) < 3.0, Y_C
assert abs(Y_Fm - (-13687.5)) < 3.0, Y_Fm
assert abs(Y_Fp - 10312.5) < 3.0, Y_Fp


# ══════════════════════════════════════════════════════════
# 影響線：精確分段多項式（由 sympy 解出後固化；下方 _crosscheck 逐點驗）
# ══════════════════════════════════════════════════════════
def IL(x, right=False):
    if x < XF or (x == XF and not right):
        return x * (x ** 2 - 5700) / 144000
    if x <= XB:
        return (x - 30) * (x ** 2 + 30 * x - 4800) / 144000
    if x <= XC:
        return -(x - 30) * (x ** 2 - 90 * x + 2800) / 48000
    if x <= XD:
        return -(x - 50) * (x ** 2 - 70 * x + 400) / 48000
    return (x - 110) * (x - 80) * (x - 50) / 144000


def _crosscheck():
    """數值積分得到的 y(x)/Δ 必須等於上面的解析分段式。"""
    worst = 0.0
    for xs, ys in ((_X1, _Y1), (_X2, _Y2), (_X3, _Y3)):
        for i in range(0, len(xs), 137):
            xq = xs[i]
            ref = IL(xq, right=(xs is _X2 and i == 0))
            worst = max(worst, abs(ys[i] / DELTA - ref))
    assert worst < 2e-4, worst
    # 剪力影響線在斷面處的跳躍必須恰為 1
    assert abs(IL(XF, True) - IL(XF, False) - 1.0) < 1e-12
    # 支承處縱距必為 0（載重直接落在支承上，V_F 不受影響 ⇒ 由結構決定）
    for xq in (XA, XB, XD, XE):
        assert abs(IL(xq)) < 1e-12, xq
    return worst


_W = _crosscheck()

KEY = [("A", XA, IL(XA)), ("F−", XF, IL(XF, False)), ("F+", XF, IL(XF, True)),
       ("B", XB, IL(XB)), ("C", XC, IL(XC)), ("D", XD, IL(XD)), ("E", XE, IL(XE))]
# DE 跨內的極大值（數值搜尋，非目測）
_g = [XD + (XE - XD) * i / 6000 for i in range(6001)]
X_PEAK = max(_g, key=IL)
V_PEAK = IL(X_PEAK)


def _fs(v):
    q = Fr(v).limit_denominator(400)
    if abs(float(q) - v) > 1e-9:
        return f"{v:+.4f}"
    return "0" if q == 0 else (f"{q.numerator:+d}" if q.denominator == 1
                               else f"{q.numerator:+d}/{q.denominator}")


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 1080
PADL, PADR = 72, 72
SX = (W - PADL - PADR) / SPAN
Y_BEAM = 150


def beam_canvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BEAM, bg=bg)


def draw_beam(cv, mw=7.0, color=None, supports=True, hinge=True, cut=None):
    color = color or C["member"]
    cv.line((XA, 0), (XE, 0), color, mw, cap="butt")
    if supports:
        for x, k in SUPPORTS.items():
            cv.support((x, 0), k, size=16)
    if hinge:
        cv.dot((XC, 0), 7.4, fill="#FFFFFF", stroke=color, w=3.0)
    if cut is not None:
        px = cv.X(cut)
        cv.parts.append(f'<line x1="{px:.2f}" y1="{cv.Y(0) - 24:.2f}" x2="{px:.2f}" '
                        f'y2="{cv.Y(0) + 24:.2f}" stroke="{C["accent"]}" '
                        f'stroke-width="2.6" stroke-dasharray="5 4"/>')


def stations(cv, dy=34, size=16):
    for nm, x in STA:
        cv.text_px(cv.X(x), cv.Y(0) + dy, nm, size,
                   C["accent"] if nm == "F" else C["text"], weight="700")


# ══════════════════════════════════════════════════════════
def fig1_beam():
    """題目重繪。攔：把 C 當支承、把 F 當支承、或把 DE 跨長記錯（30 m，是 BC 的三倍）。"""
    H = 348
    cv = beam_canvas(H, bg="#FFFFFF")
    cv.panel("題目重繪（考卷圖二）",
             "A 鉸支承　B、D、E 滾支承　C 內部鉸　F 為所求剪力斷面（AB 跨中點）　EI 為定值")
    draw_beam(cv, cut=XF)
    stations(cv, 54, 17)
    cv.text_px(cv.X(XC), cv.Y(0) - 26, "內部鉸", 12.5, C["muted"])
    cv.text_px(cv.X(XF), cv.Y(0) - 26, "所求剪力斷面", 12.5, C["accent"], weight="700")
    for a, b, lab in ((XA, XF, "15 m"), (XF, XB, "15 m"), (XB, XC, "10 m"),
                      (XC, XD, "10 m"), (XD, XE, "30 m")):
        cv.dim((a, 0), (b, 0), lab, off=92, label_off=15)
    cv.text_px(W / 2, H - 52,
               f"反力 {N_R} 個（A 為 2）　平衡方程 {N_EQ} 式 ＋ 內鉸 C 的 M = 0 共 {N_HINGE} 式"
               f"　⇒　靜不定度 = {N_R - N_EQ - N_HINGE}", 13.5, C["muted"])
    cv.text_px(W / 2, H - 26,
               "1 度靜不定 ＋ 解除 F 點剪力（1 個釋放）⇒ 基本結構恰為靜定，這正是本題可用共軛梁法的前提",
               13.5, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-beam.svg")


def fig2_released():
    """基本結構與其彎矩圖。攔：反力算錯（用 M(C) = 0 可以當場自我檢查）。"""
    H1, H2 = 312, 300
    MY = lambda px: -px / SX                 # 「梁下方 px 像素」換成模型座標

    cv1 = beam_canvas(H1)
    cv1.panel("基本結構：解除 F 點剪力，施加單位剪力對",
              "F 左側向下 1、右側向上 1（力偶自身平衡）　"
              "剪力釋放 ⇒ F 兩側可相對上下錯動，但仍傳遞彎矩、斜率保持連續")
    draw_beam(cv1, cut=XF)
    for nm, x in STA:                        # 站名改放梁的上方，讓出下方給反力
        cv1.text_px(cv1.X(x), cv1.Y(0) - 30, nm, 16,
                    C["accent"] if nm == "F" else C["text"], weight="700")
    cv1.arrow((XF - 3.2, MY(-72)), (XF - 3.2, MY(-14)), C["load"], 3.4, 12)
    cv1.arrow((XF + 3.2, MY(72)), (XF + 3.2, MY(14)), C["load"], 3.4, 12)
    cv1.text_px(cv1.X(XF - 3.2) - 10, cv1.Y(MY(-46)), "1", 15, C["load"], "end", weight="700")
    cv1.text_px(cv1.X(XF + 3.2) + 10, cv1.Y(MY(46)), "1", 15, C["load"], "start", weight="700")
    for x, v in ((XA, RA0), (XB, RB0), (XD, RD0), (XE, RE0)):
        a, b = (MY(88), MY(44)) if v > 0 else (MY(44), MY(88))
        cv1.arrow((x, a), (x, b), C["deform"], 3.2, 11)
        cv1.text_px(cv1.X(x), cv1.Y(MY(106)), f"{v:+.0f}", 15, C["deform"], weight="700")
    cv1.text_px(W / 2, H1 - 22,
                "反力自我檢查：C 是內部鉸 ⇒ M(C) 必須為 0　⇒　1·40 − 4·(40−30) = 0 ✓",
                13.5, C["muted"])

    cv2 = Canvas(W, H2, sx=SX, ox=PADL, oy=H2 - 168)
    cv2.panel("基本結構的彎矩圖 M(x)（下凹為正）",
              "M = x（0–30）；M = 120 − 3x（30–50）；M = x − 80（50–80）"
              "　│　這條 M(x) 就是共軛梁的載重")
    kk = 66.0 / 30.0 / SX                    # 30 個單位彎矩 = 66 px
    xs = [XA + SPAN * i / 400 for i in range(401)]
    pts = [(x, M0(x) * kk) for x in xs]
    cv2.polygon([(XA, 0.0)] + pts + [(XE, 0.0)], C["fill_m"], C["bmd"], 2.4)
    cv2.line((XA, 0), (XE, 0), C["muted"], 1.6)
    for x in (XB, XD):
        v = M0(x)
        cv2.dot((x, v * kk), 4.0, fill=C["bmd"])
        cv2.text_px(cv2.X(x), cv2.Y(v * kk) + (-14 if v >= 0 else 17),
                    f"{v:+.0f}", 13.5, C["bmd"], weight="700")
    cv2.dot((XC, 0), 6.6, fill="#FFFFFF", stroke=C["accent"], w=2.8)
    cv2.text_px(cv2.X(XC), cv2.Y(0) - 20, "M = 0（內部鉸）", 12.5, C["accent"], weight="700")
    for nm, x in STA:
        cv2.text_px(cv2.X(x), H2 - 16, nm, 12.5, "#9AA4B2", weight="700")
    return compose([cv1, cv2], cols=1, path=f"{OUT}/{TAG}-fig-2-released.svg")


def fig3_conjugate():
    """共軛梁。攔：邊界轉換記反（滾支承↔內部鉸、內部鉸↔內部支承），
    以及漏掉 F 處那個代表 y 跳躍的集中力矩。"""
    H = 372
    cv = beam_canvas(H)
    cv.panel("共軛梁：邊界對調，載重換成 M/EI",
             "真實梁的 θ ↔ 共軛梁的 V*　　真實梁的 y ↔ 共軛梁的 M*")
    cv.line((XA, 0), (XE, 0), C["member"], 7.0, cap="butt")
    cv.pin_support((XA, 0), size=16)
    cv.pin_support((XE, 0), size=16)
    for x in (XB, XD):                      # 原滾支承 → 共軛內部鉸
        cv.dot((x, 0), 7.4, fill="#FFFFFF", stroke=C["member"], w=3.0)
    cv.roller_support((XC, 0), size=16)     # 原內部鉸 → 共軛內部支承
    cv.moment_arrow((XF, -32 / SX * -1), r=20, ccw=True, color=C["load"], w=2.8)
    cv.text_px(cv.X(XF) + 34, cv.Y(0) - 32, "M_{0}：代表 y 在 F 的跳躍", 13,
               C["load"], "start", weight="700")
    for nm, x in STA:                       # 站名放上方，讓出下方給支承與說明
        cv.text_px(cv.X(x), cv.Y(0) - 66, nm, 16,
                   C["accent"] if nm == "F" else C["text"], weight="700")
    for x, lab in ((XA, "端鉸 → 端鉸"), (XB, "滾支承 → 內部鉸"),
                   (XC, "內部鉸 → 內部支承"), (XD, "滾支承 → 內部鉸"),
                   (XE, "端滾 → 端鉸")):
        cv.text_px(cv.X(x), cv.Y(0) + 56, lab, 11.5, C["muted"])
    cv.text_px(W / 2, H - 100,
               "未知數 4 個：R*_{A}、R*_{C}、R*_{E}、M_{0}　"
               "／　方程 4 條：ΣF_{y}*、ΣM*、M*(B) = 0、M*(D) = 0",
               13.5, C["text"], weight="700")
    cv.text_px(W / 2, H - 72,
               f"解得　EI·R*_{{A}} = EI·θ_{{A}} = {THETA_A:,.0f}　，　"
               f"EI·M_{{0}} = EI·Δ_{{F}} = {DELTA:,.0f}", 14, C["bmd"], weight="700")
    cv.text_px(W / 2, H - 44,
               f"EI·M*(F−) = EI·y(F−) = {Y_Fm:,.1f}　，　"
               f"EI·M*(F+) = {Y_Fp:,.1f}　，　EI·M*(C) = {Y_C:,.0f}",
               14, C["bmd"], weight="700")
    cv.text_px(W / 2, H - 16,
               "M*(F−) = R*_{A}·15 ＋（0–15 段 M/EI 載重對 F 的力矩）"
               "= (−950)(15) + 562.5 = −13 687.5　← 這個負號是本題最易掉的分",
               13, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-3-conjugate.svg")


def fig4_influence_line():
    """V_F 影響線全曲線。攔：把靜不定結構的影響線畫成直線、把 F 兩側的正負號畫反。"""
    H = 340
    cv = Canvas(W, H, sx=SX, ox=PADL, oy=H - 176)
    cv.panel("IL of V_{F}（縱距無因次；V_F 以「斷面左側向上」為正）",
             "靜不定結構的影響線是曲線（不是折線）：AB、BC、CD、DE 各為三次曲線，"
             "折點只在 F（單位跳躍）與內部鉸 C（斜率轉折）")
    kk = 112.0 / SX          # 1.0 縱距 = 112 px
    for nm, x in STA:
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="64" x2="{p:.2f}" y2="{H - 32}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
    for a, b, right in ((XA, XF, False), (XF, XE, True)):
        xs = [a + (b - a) * i / 600 for i in range(601)]
        pts = [(x, IL(x, right and x == XF) * kk) for x in xs]
        cv.polygon([(a, 0.0)] + pts + [(b, 0.0)], C["fill_s"], C["sfd"], 2.6)
    cv.line((XA, 0), (XE, 0), C["muted"], 1.6)
    cv.line((XF, IL(XF, False) * kk), (XF, IL(XF, True) * kk), C["accent"], 2.6, dash="5 4")
    for nm, x, v in KEY:
        cv.dot((x, v * kk), 4.2, fill=C["sfd"])
        if abs(v) > 1e-9:
            dx = -16 if nm == "F−" else (16 if nm == "F+" else 0)
            cv.text_px(cv.X(x) + dx, cv.Y(v * kk) + (-14 if v > 0 else 17),
                       _fs(v), 13.5, C["sfd"], weight="700", anchor="middle")
    cv.dot((X_PEAK, V_PEAK * kk), 4.2, fill=C["sfd"])
    cv.text_px(cv.X(X_PEAK), cv.Y(V_PEAK * kk) - 14,
               f"{V_PEAK:+.4f} @ x≈{X_PEAK:.1f}", 12.5, C["sfd"], weight="700")
    cv.text_px(cv.X(XF) + 22, (cv.Y(IL(XF, False) * kk) + cv.Y(IL(XF, True) * kk)) / 2,
               "跳躍 = 1", 13, C["accent"], "start", weight="700")
    for nm, x in STA:
        cv.text_px(cv.X(x), H - 16, nm, 13, "#9AA4B2", weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-4-influence-line.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_beam, fig2_released, fig3_conjugate, fig4_influence_line):
        f(); print("寫出", f.__name__)
    print(f"\n數值積分 vs 解析分段式，最大差 = {_W:.2e}")
    print(f"EI·θ_A = {THETA_A:,.2f}   EI·Δ_F = {DELTA:,.2f}   EI·y(C) = {Y_C:,.2f}")
    print("\n關鍵縱距")
    for nm, x, v in KEY:
        print(f"  {nm:3s} @ {x:5.1f}   {_fs(v):>10s}  = {v:+.6f}")
    print(f"  DE 極大 @ {X_PEAK:.3f}   {V_PEAK:+.6f}")
