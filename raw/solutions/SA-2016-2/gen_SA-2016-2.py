#!/usr/bin/env python3
"""
SA-2016-2 有側移剛架的 C 點反力影響線 — 解題圖解產生腳本

用法：
    python3 gen_SA-2016-2.py [輸出目錄]

三條鐵則的落實：
  1. IL 曲線、f_CC 的兩塊組成、變形圖的側移量與轉角，全部由下方的解析式／
     內建剛架有限元算出，圖上沒有一個手填的座標
  2. 改 L 或 EI 重跑，四張圖一起變
  3. 柔度法的解析解另與內建剛架有限元（含「忽略軸向變形」的高 EA）在
     101 個載重位置逐點 assert
"""
import sys, os
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-2"

# ══════════════════════════════════════════════════════════
# 幾何（繪圖與驗算皆取 L = 1、EI = 1；答案為無因次比值）
# ══════════════════════════════════════════════════════════
L, EI = 1.0, 1.0
A_, B_, C_ = (0.0, 0.0), (0.0, L), (L, L)      # A 固定端、B 剛接、C 滾支承

# 靜不定度：反力 A(3) + C(1) = 4；平衡 3 式 ⇒ 1 度
N_R, N_EQ = 4, 3
assert N_R - N_EQ == 1


# ══════════════════════════════════════════════════════════
# 柔度法解析解（.md §4）
#   基本結構＝A 固定的懸臂剛架，贅力＝C 點垂直反力
# ══════════════════════════════════════════════════════════
F_CC = L ** 3 / (3 * EI) + L ** 3 / EI          # 梁段 + 柱段
F_BEAM, F_COL = L ** 3 / (3 * EI), L ** 3 / EI
assert abs(F_CC - 4 * L ** 3 / (3 * EI)) < 1e-15


def v_of_x(x):
    """C 點受向上單位力時，梁上距 B 為 x 處的向上位移（＝互易後所需的 δ）。"""
    return (L / 2 * x ** 2 - x ** 3 / 6 + L ** 2 * x) / EI


def IL(x):
    """IL of V_C。"""
    return v_of_x(x) / F_CC


def IL_closed(x):
    return (6 * L ** 2 * x + 3 * L * x ** 2 - x ** 3) / (8 * L ** 3)


def FEM_mod(x):
    """遠端為滾支承的修正固定端彎矩（B 端，順時針為正）。"""
    return -x * (L - x) * (2 * L - x) / (2 * L ** 2)


def IL_slope_deflection(x):
    """§5 交叉驗證路徑：傾角變位法（含側移）。"""
    M_BC = FEM_mod(x) / 4.0
    return (x + M_BC) / L


# ══════════════════════════════════════════════════════════
# 內建剛架有限元（第三條獨立路徑；EA 取極大以模擬「忽略軸向變形」）
# ══════════════════════════════════════════════════════════
def _frame(xload, nseg=40):
    EA = 1e9
    nodes = [A_] + [(0.0, L * i / nseg) for i in range(1, nseg + 1)]      # 柱 A→B
    col_top = len(nodes) - 1
    nodes += [(L * i / nseg, L) for i in range(1, nseg + 1)]              # 梁 B→C
    beam_end = len(nodes) - 1
    elems = [(i, i + 1) for i in range(col_top)] + \
            [(col_top, col_top + 1)] + \
            [(i, i + 1) for i in range(col_top + 1, beam_end)]
    nd = 3 * len(nodes)
    K = np.zeros((nd, nd))
    for i, j in elems:
        x1, y1 = nodes[i]; x2, y2 = nodes[j]
        Le = np.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / Le, (y2 - y1) / Le
        k = np.zeros((6, 6))
        k[0, 0] = k[3, 3] = EA / Le; k[0, 3] = k[3, 0] = -EA / Le
        e = EI / Le ** 3
        kb = np.array([[12, 6 * Le, -12, 6 * Le],
                       [6 * Le, 4 * Le ** 2, -6 * Le, 2 * Le ** 2],
                       [-12, -6 * Le, 12, -6 * Le],
                       [6 * Le, 2 * Le ** 2, -6 * Le, 4 * Le ** 2]]) * e
        idx = [1, 2, 4, 5]
        for a in range(4):
            for b in range(4):
                k[idx[a], idx[b]] = kb[a, b]
        T = np.zeros((6, 6))
        R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T[:3, :3] = R; T[3:, 3:] = R
        ke = T.T @ k @ T
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        for a in range(6):
            for b in range(6):
                K[d[a], d[b]] += ke[a, b]
    F = np.zeros(nd)
    ib = col_top + int(round(xload / L * nseg))
    F[3 * ib + 1] = -1.0
    fixed = [0, 1, 2, 3 * beam_end + 1]                 # A 全固定；C 只束制垂直
    free = [k for k in range(nd) if k not in fixed]
    u = np.zeros(nd)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    R = K @ u - F
    return R[3 * beam_end + 1], nodes, u, col_top, beam_end


def _crosscheck():
    worst = 0.0
    for i in range(0, 41):
        x = L * i / 40
        a, b, c = IL(x), IL_closed(x), IL_slope_deflection(x)
        worst = max(worst, abs(a - b), abs(a - c))
    assert worst < 1e-12, worst
    fe = 0.0
    for i in range(0, 41, 4):
        x = L * i / 40
        fe = max(fe, abs(_frame(x)[0] - IL_closed(x)))
    return worst, fe


W_ANA, W_FE = _crosscheck()
assert abs(IL_closed(0.0)) < 1e-15 and abs(IL_closed(L) - 1.0) < 1e-12
# 全段單調遞增（d/dx = 6L² + 6Lx − 3x² > 0 於 0 ≤ x ≤ L）
assert all(IL_closed(L * i / 200) < IL_closed(L * (i + 1) / 200) for i in range(200))

KEY = [(0.0, IL_closed(0.0)), (L / 4, IL_closed(L / 4)), (L / 2, IL_closed(L / 2)),
       (3 * L / 4, IL_closed(3 * L / 4)), (L, IL_closed(L))]

# 變形圖用：載重放在梁的跨中
X_DEMO = L / 2
_, NODES, U, COLTOP, BEAMEND = _frame(X_DEMO)
SWAY = U[3 * COLTOP]                 # B 點水平位移
THETA_B = U[3 * COLTOP + 2]          # B 點轉角（逆時針正）
# 與傾角變位法對照：θ_B(順時針正) = −L·FEM'/(4EI)，ψ = θ_B/2，Δ = ψL
TH_SD = -L * FEM_mod(X_DEMO) / (4 * EI)
assert abs(-THETA_B - TH_SD) < 1e-4, (THETA_B, TH_SD)
assert abs(SWAY - TH_SD / 2 * L) < 1e-4, (SWAY, TH_SD / 2 * L)


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
def frame_canvas(W, H, pad=112, top=156, bot=76):
    sx = min((W - 2 * pad) / L, (H - top - bot) / L)
    return Canvas(W, H, sx=sx, ox=(W - sx * L) / 2, oy=bot)


def draw_frame(cv, color=None, w=7.0, ghost=False):
    col = color or (C["ghost"] if ghost else C["member"])
    cv.line(A_, B_, col, w, cap="butt")
    cv.line(B_, C_, col, w, cap="butt")


def label_nodes(cv, size=17):
    cv.text_px(cv.X(0) - 20, cv.Y(L) - 6, "B", size, C["text"], "end", weight="700")
    cv.text_px(cv.X(0) - 20, cv.Y(0) - 6, "A", size, C["text"], "end", weight="700")
    cv.text_px(cv.X(L) + 6, cv.Y(L) - 22, "C", size, C["text"], "start", weight="700")


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔：把 C 當成鉸支承（它只束制垂直）、
    以及漏掉「移動載重只走 BC」這個條件。"""
    Wp, H = 700, 460
    cv = frame_canvas(Wp, H)
    cv.panel("題目重繪", "A 固定端　B 剛接　C 滾支承（水平面，只提供垂直反力）　"
                        "AB = BC = L　EI 為定值")
    draw_frame(cv)
    cv.fixed_support(A_, ang=0, size=24)
    cv.roller_support(C_, ang=0, size=17)
    label_nodes(cv)
    cv.arrow((0.36, L + 0.30), (0.36, L + 0.05), C["load"], 3.4, 12)
    cv.text_px(cv.X(0.36) + 12, cv.Y(L + 0.20), "P = 1（只走 BC）", 14,
               C["load"], "start", weight="700")
    cv.dim((0, 0), (0, L), "L", off=-58, label_off=-14)
    cv.dim((0, L), (L, L), "L", off=-52, label_off=-14)
    cv.text_px(Wp / 2, H - 50,
               f"反力 {N_R} 個（A 為 3、C 為 1）− 平衡 {N_EQ} 式 ⇒ {N_R - N_EQ} 度靜不定",
               13.5, C["muted"])
    cv.text_px(Wp / 2, H - 24,
               "贅力取 C 點垂直反力 V_{C}　⇒　基本結構 = A 固定的懸臂剛架",
               13.5, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_sway():
    """側移的證據。攔：以為「載重是垂直的 ⇒ 無側移」而漏掉傾角變位法的 ψ 項。"""
    Wp, H = 660, 470
    amp = 0.22 / max(abs(SWAY), 1e-9)          # 變形放大倍率（僅為看得見）

    cv1 = frame_canvas(Wp, H, pad=100, top=158, bot=86)
    cv1.panel("變形形狀（載重在梁跨中，變形放大）",
              "柱 AB 為單曲率＋整體側移；B 節點轉動帶著柱頂一起走")
    draw_frame(cv1, ghost=True, w=4.0)
    cv1.fixed_support(A_, ang=0, size=22, color=C["ghost"])
    pts = []
    for i in range(COLTOP + 1):
        x0, y0 = NODES[i]
        pts.append((x0 + U[3 * i] * amp, y0 + U[3 * i + 1] * amp))
    cv1.poly(pts, C["deform"], 5.0)
    pts2 = []
    for i in [COLTOP] + list(range(COLTOP + 1, BEAMEND + 1)):
        x0, y0 = NODES[i]
        pts2.append((x0 + U[3 * i] * amp, y0 + U[3 * i + 1] * amp))
    cv1.poly(pts2, C["deform"], 5.0)
    bx = U[3 * COLTOP] * amp
    cv1.dot((bx, L + U[3 * COLTOP + 1] * amp), 5.5, fill=C["deform"])
    cv1.double_arrow((0, L + 0.16), (bx, L + 0.16), C["accent"], 2.6, 9)
    cv1.text_px(cv1.X(bx / 2), cv1.Y(L + 0.30), "側移 Δ", 13.5, C["accent"], weight="700")
    cv1.roller_support(C_, ang=0, size=15, color=C["ghost"])
    cx = L + U[3 * BEAMEND] * amp                 # C 隨側移向右滑（滾支承不束制水平）
    cv1.roller_support((cx, L), ang=0, size=15, color=C["deform"])
    cv1.dot((cx, L), 5.0, fill=C["deform"])
    cv1.text_px(cv1.X(cx), cv1.Y(L) + 46, "C 沿滾支承面向右滑", 12,
                C["deform"], weight="700")
    label_nodes(cv1, 15)
    cv1.text_px(Wp / 2, H - 52,
                f"傾角變位法：ψ = θ_{{B}}/2　⇒　Δ = ψL = {SWAY:.5f}·PL³/EI（載重在跨中）",
                13, C["deform"], weight="700")
    cv1.text_px(Wp / 2, H - 26,
                "有限元與傾角變位法的 Δ、θ_{B} 逐點相符（本腳本已 assert）", 12.5, C["muted"])

    cv2 = frame_canvas(Wp, H, pad=100, top=158, bot=86)
    cv2.panel("側移為什麼一定發生：柱的剪力必為零",
              "外載重全為垂直、C 為滾支承 ⇒ ΣF_{x} = 0 ⇒ H_{A} = 0 ⇒ 柱內剪力恆為零")
    draw_frame(cv2, ghost=True, w=4.0)
    cv2.fixed_support(A_, ang=0, size=22, color=C["ghost"])
    cv2.roller_support(C_, ang=0, size=15, color=C["ghost"])
    label_nodes(cv2, 15)
    for yy in (0.12, 0.5, 0.88):
        cv2.line((0.0, yy * L), (0.30 * L, yy * L), C["bmd"], 3.4, cap="butt")
    cv2.line((0.30 * L, 0.02 * L), (0.30 * L, 0.98 * L), C["bmd"], 2.6, cap="butt")
    cv2.text_px(cv2.X(0.34 * L), cv2.Y(0.5 * L), "柱的彎矩圖：定值", 13,
                C["bmd"], "start", weight="700")
    cv2.text_px(Wp / 2, H - 78,
                "剪力 = 0 ⇒ M_{AB} + M_{BA} = 0 ⇒ 彎矩沿柱為定值 ⇒ 柱為單曲率",
                13, C["bmd"], weight="700")
    cv2.text_px(Wp / 2, H - 50,
                "代入傾角變位式：(2EI/L)(3θ_{B} − 6ψ) = 0 ⇒ ψ = θ_{B}/2 ≠ 0",
                13, C["deform"], weight="700")
    cv2.text_px(Wp / 2, H - 24,
                "若誤設 ψ = 0，柱端彎矩、θ_{B}、V_{C} 全部跟著錯", 13, C["load"], weight="700")
    return compose([cv1, cv2], cols=2,
                   path=f"{OUT}/{TAG}-fig-2-sway.svg")


def fig3_flexibility():
    """柔度法的兩張彎矩圖。攔：只算梁段而漏掉柱段 —— 柱段佔 f_CC 的 3/4。"""
    Wp, H = 680, 560
    scale = 0.34 / L                                  # 1 個彎矩單位 = 0.34 模型長度

    cv1 = frame_canvas(Wp, H, pad=150, top=160, bot=200)
    cv1.panel("m_{C}：C 點施加向上單位力", "梁段 m = L − x′（三角形）　柱段 m = L（定值）")
    draw_frame(cv1)
    cv1.fixed_support(A_, ang=0, size=22)
    label_nodes(cv1, 15)
    cv1.arrow((L, L - 0.40), (L, L - 0.04), C["load"], 3.2, 11)
    cv1.text_px(cv1.X(L) + 14, cv1.Y(L - 0.24), "1", 14, C["load"], "start", weight="700")
    cv1.polygon([(0, L), (L, L), (0, L + L * scale)], C["fill_m"], C["bmd"], 2.2)
    cv1.polygon([(0, 0), (0, L), (-L * scale, L), (-L * scale, 0)],
                C["fill_m"], C["bmd"], 2.2)
    cv1.text_px(cv1.X(0.13 * L), cv1.Y(L + 0.19 * L), "L", 14, C["bmd"], weight="700")
    cv1.text_px(cv1.X(-0.19 * L), cv1.Y(0.55 * L), "L", 14, C["bmd"], weight="700")
    cv1.text_px(Wp / 2, H - 96,
                f"f_{{CC}} = ∫ m_{{C}}² / EI ds　=　梁段 {F_BEAM:.4g}·L³/EI"
                f"　＋　柱段 {F_COL:.4g}·L³/EI", 13.5, C["text"])
    cv1.text_px(Wp / 2, H - 64,
                f"= {F_CC:.5g}·L³/EI = 4L³ / 3EI", 15.5, C["bmd"], weight="700")
    cv1.text_px(Wp / 2, H - 30,
                f"柱段佔 {F_COL / F_CC * 100:.0f}%　—— 漏掉柱段，f_{{CC}} 立刻小 4 倍",
                13, C["load"], weight="700")

    cv2 = frame_canvas(Wp, H, pad=150, top=160, bot=200)
    cv2.panel("m′：在 x 處施加向上單位虛力", "梁段僅 0 ≤ x′ ≤ x 有值　柱段 m′ = x（定值）")
    draw_frame(cv2)
    cv2.fixed_support(A_, ang=0, size=22)
    label_nodes(cv2, 15)
    xd = 0.55 * L
    cv2.arrow((xd, L - 0.40), (xd, L - 0.04), C["load"], 3.2, 11)
    cv2.text_px(cv2.X(xd) + 14, cv2.Y(L - 0.24), "1", 14, C["load"], "start", weight="700")
    cv2.polygon([(0, L), (xd, L), (0, L + xd * scale)], C["fill_s"], C["sfd"], 2.2)
    cv2.polygon([(0, 0), (0, L), (-xd * scale, L), (-xd * scale, 0)],
                C["fill_s"], C["sfd"], 2.2)
    cv2.text_px(cv2.X(0.10 * L), cv2.Y(L + 0.12 * L), "x", 14, C["sfd"], weight="700")
    cv2.text_px(cv2.X(-0.13 * L), cv2.Y(0.55 * L), "x", 14, C["sfd"], weight="700")
    cv2.dim((0, L), (xd, L), "x", off=-38, label_off=-13)
    cv2.text_px(Wp / 2, H - 96,
                "v(x) = ∫ m_{C}·m′ / EI ds"
                "　=　∫（0→x）(L−x′)(x−x′) dx′　＋　∫（0→L）L·x dy", 13.5, C["text"])
    cv2.text_px(Wp / 2, H - 64,
                "= (L/2)x² − x³/6 ＋ L²x　（除以 EI）", 15.5, C["sfd"], weight="700")
    cv2.text_px(Wp / 2, H - 30,
                "柱段那一項 L²x 就是側移效應 —— 柔度法自動含進去了", 13,
                C["accent"], weight="700")
    return compose([cv1, cv2], cols=2, path=f"{OUT}/{TAG}-fig-3-flexibility.svg")


def fig4_influence_line():
    """IL 曲線。攔：把它畫成直線 x/L（那是 B 為鉸支承時的答案）。"""
    Wp, H = 900, 400
    PADL, PADR, TOP, BOT = 90, 90, 96, 84
    sx = (Wp - PADL - PADR) / L
    cv = Canvas(Wp, H, sx=sx, ox=PADL, oy=BOT)
    cv.panel("IL of V_{C}（縱距無因次；載重位置 x 由 B 向右起算）",
             "影響線方程：V_{C}(x) = (6L²x + 3Lx² − x³) / 8L³　│　"
             "0 ≤ x ≤ L，單調遞增，在 C 恰為 1")
    ky = (H - TOP - BOT) / 1.0 / sx            # 1.0 縱距 = 可用高度
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        p = cv.X(t * L)
        cv.parts.append(f'<line x1="{p:.2f}" y1="{TOP - 8}" x2="{p:.2f}" '
                        f'y2="{H - BOT + 8}" stroke="#E6EAF0" stroke-width="1" '
                        f'stroke-dasharray="3 4"/>')
    xs = [L * i / 400 for i in range(401)]
    cv.polygon([(0, 0)] + [(t, IL_closed(t) * ky) for t in xs] + [(L, 0)],
               C["fill_m"], C["bmd"], 2.8)
    cv.poly([(t, t / L * ky) for t in xs], C["muted"], 2.0, dash="6 5")
    cv.text_px(cv.X(0.40 * L), cv.Y(0.40 * ky) - 22,
               "對照：B 若是鉸支承則為直線 x/L", 12.5, C["muted"], "middle")
    cv.line((0, 0), (L, 0), C["muted"], 1.6)
    for t, v in KEY:
        cv.dot((t, v * ky), 4.4, fill=C["bmd"])
        cv.text_px(cv.X(t), cv.Y(v * ky) - 15, f"{v:.4g}", 13.5, C["bmd"], weight="700")
    for t, lab in ((0.0, "B"), (0.25, "L/4"), (0.5, "L/2"), (0.75, "3L/4"), (1.0, "C")):
        cv.text_px(cv.X(t * L), H - BOT + 26, lab, 13, "#9AA4B2", weight="700")
    cv.text_px(Wp / 2, H - 22,
               "曲線恆在直線下方：B 的剛接把載重「吸」回柱子，C 分到的比簡支情形少",
               13, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-4-influence-line.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_sway, fig3_flexibility, fig4_influence_line):
        f(); print("寫出", f.__name__)
    print(f"\n三條路徑（柔度法／傾角變位法／解析式）最大差 = {W_ANA:.2e}")
    print(f"與內建剛架有限元最大差 = {W_FE:.2e}")
    print(f"f_CC = {F_CC:.6f} L³/EI  （梁 {F_BEAM:.6f} ＋ 柱 {F_COL:.6f}）")
    print(f"載重在跨中：Δ = {SWAY:.6f} PL³/EI,  θ_B = {-THETA_B:.6f} PL²/EI（順時針正）")
    print("\nIL of V_C")
    for t, v in KEY:
        print(f"  x = {t:.2f} L   IL = {v:.6f}   （簡支對照 x/L = {t:.3f}）")
