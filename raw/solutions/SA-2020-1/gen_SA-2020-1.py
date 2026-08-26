#!/usr/bin/env python3
"""
SA-2020-1 折線剛架（水平桿＋斜桿）傾角變位法 — 解題圖解產生腳本

用法：
    python3 gen_SA-2020-1.py [輸出目錄]

⚠ 幾何來源：對考卷附圖 SA-2020-1-fig-1.png 逐像素掃描確認：
     尺寸刻度落在 x = 0 / 4.00 / 5.99 / 7.99  ⇒  4 m ｜ 2 m ｜ 2 m
     水平桿橫跨 x = 0 → 4.10                  ⇒  ab 是水平桿，長 4 m
     載重箭頭（實心三角）中心 x ≈ 6.0          ⇒  68 kN 在 bc 的中點
     c 處為單一圓圈貼在垂直剖面線牆上          ⇒  滾支承（可轉動），非滑軌

三條鐵則的落實：
  1. 圖上每個彎矩、位移、角度都由下方常數區算出，常數區的值又由
     內建剛架有限元（figs/_lib/frame_fe.py）解出並 assert
  2. 改 XB / YC / P / XLOAD 重跑，四張圖與所有數字會一起變
  3. 每張圖攔一種特定誤讀，見各 fig 的 docstring
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose
from frame_fe import solve

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-1"

# ══════════════════════════════════════════════════════════
# 幾何與載重（全部由附圖判讀）
# ══════════════════════════════════════════════════════════
A = (0.0, 0.0)                    # 固定端（貼左側垂直牆）
B = (4.0, 0.0)                    # 折點（剛節點）
CC = (8.0, -3.0)                  # 滾支承（貼右側垂直牆，只束制水平）
XLOAD = 6.0                       # 68 kN 的水平位置 → bc 的中點
P = 68.0
L_AB = 4.0
L_BC = (( CC[0] - B[0]) ** 2 + (CC[1] - B[1]) ** 2) ** 0.5      # = 5.0
assert abs(L_BC - 5.0) < 1e-12
MID = ((B[0] + CC[0]) / 2, (B[1] + CC[1]) / 2)
assert abs(MID[0] - XLOAD) < 1e-12, "68 kN 必須落在 bc 中點"

# bc 桿的方向與法向
EX = ((CC[0] - B[0]) / L_BC, (CC[1] - B[1]) / L_BC)              # (4/5, -3/5)
EY = (-EX[1], EX[0])                                             # (3/5, 4/5)
P_PERP = abs(-P * EY[1])                                         # 68 × 4/5 = 54.4
P_AXIAL = abs(-P * EX[1])                                        # 68 × 3/5 = 40.8
FEM = P_PERP * L_BC / 8                                          # = 34.0

# 靜不定度：反力 a(3) + c(1) = 4；平衡 3 式 ⇒ 1 度
N_R, N_EQ = 4, 3
assert N_R - N_EQ == 1

# ══════════════════════════════════════════════════════════
# 有限元求解（EA 極大 ⇒ 不考慮軸向變形）
# ══════════════════════════════════════════════════════════
_nodes = [A, B, MID, CC]
_u, _R, _M = solve(_nodes, [(0, 1), (1, 2), (2, 3)],
                   {(0, 0), (0, 1), (0, 2), (3, 0)}, {(2, 1): -P}, EI=1.0)

M_AB, M_BA = _M[(0, 1)]           # 順時針為正
M_BC = _M[(1, 2)][0]
M_MID = -_M[(1, 2)][1]            # bc 中點的實際彎矩（下凹為正）
M_CB = _M[(2, 3)][1]
DELTA = -_u[3 * 1 + 1]            # b、c 的向下位移 × EI
THETA_B = -_u[3 * 1 + 2]          # 順時針為正 × EI
THETA_C = -_u[3 * 3 + 2]
C_X = _R[(3, 0)]                  # c 點水平反力
A_X, A_Y, M_A = _R[(0, 0)], _R[(0, 1)], _R[(0, 2)]

# ── 與手算精確值對照（.md §4 引用的就是這組）──────────────
assert abs(M_AB - (-191)) < 1e-2, M_AB
assert abs(M_BA - (-81)) < 1e-2, M_BA
assert abs(M_CB) < 1e-6, M_CB                       # 滾支承不提供彎矩
assert abs(M_BA + M_BC) < 1e-6                      # 節點 b 平衡
assert abs(C_X - 217 / 3) < 1e-3, C_X
assert abs(A_Y - P) < 1e-2 and abs(A_X + C_X) < 1e-2
assert abs(THETA_B - 220) < 1e-2 and abs(THETA_C + 152.5) < 1e-2
assert abs(DELTA - 2408 / 3) < 1e-1, DELTA
# 側移方程：M_ab + M_ba = −P·L_AB（由虛功，δψ_ab = δΔ/L_AB）
assert abs((M_AB + M_BA) + P * L_AB) < 1e-2

# 彎矩圖縱距（下凹為正）：起點 = +M_nf，終點 = −M_fn
BM_A, BM_B = M_AB, -M_BA
BM_MID, BM_C = M_MID, -M_CB
X_ZERO = L_AB * BM_A / (BM_A - BM_B)                # ab 桿的反曲點，由內插算出
assert 0 < X_ZERO < L_AB


def _f(v, nd=1):
    q = Fr(v).limit_denominator(64)
    return str(q) if abs(float(q) - v) < 1e-9 else f"{v:.{nd}f}"


# ══════════════════════════════════════════════════════════
# 版面：結構佔 x∈[0,8]、y∈[-3,0]，四張圖共用同一組像素定位
# ══════════════════════════════════════════════════════════
W = 1080
PADL, PADR = 110, 110
SX = (W - PADL - PADR) / (CC[0] - A[0])          # px / m
Y_TOP = 150                                       # y = 0 的像素位置


def frame_canvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_TOP, bg=bg)


def draw_frame(cv, w=7.0, color=None, ghost=False):
    col = color or (C["ghost"] if ghost else C["member"])
    cv.line(A, B, col, w, cap="butt")
    cv.line(B, CC, col, w, cap="butt")


def supports(cv, size=20, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    cv.fixed_support(A, ang=-90, size=size, color=col)          # 牆在左側
    cv.roller_support(CC, ang=90, size=int(size * 0.85), color=col)   # 牆在右側


def labels(cv, ghost=False):
    col = C["ghost"] if ghost else C["text"]
    cv.text_px(cv.X(A[0]) + 20, cv.Y(A[1]) - 20, "a", 19, col, "start",
               weight="700", italic=True)
    cv.text_px(cv.X(B[0]) - 12, cv.Y(B[1]) + 30, "b", 19, col, "end",
               weight="700", italic=True)
    cv.text_px(cv.X(CC[0]) - 22, cv.Y(CC[1]) - 8, "c", 19, col, "end",
               weight="700", italic=True)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔本題最致命的三個誤讀：ab／bc 哪根是斜桿、68 kN 在
    節點還是桿件中間、c 是可轉動的滾支承還是不可轉動的滑軌。"""
    H = 660
    cv = frame_canvas(H, bg="#FFFFFF")
    cv.panel("題目重繪（依考卷附圖逐像素判讀）",
             "a 固定端　b 剛節點　c 滾支承（貼垂直牆，只束制水平、可自由轉動）"
             "　ab、bc 的 EI 相同，不考慮軸向變形")
    draw_frame(cv)
    supports(cv)
    labels(cv)
    cv.arrow((XLOAD, 0.30), (XLOAD, MID[1] + 0.14), C["load"], 3.6, 13)
    cv.text_px(cv.X(XLOAD), cv.Y(0.30) - 18, f"{P:g} kN", 17, C["load"], weight="700")
    cv.dot(MID, 6.0, fill=C["load"])
    cv.text_px(cv.X(XLOAD) + 20, cv.Y(MID[1]) + 6,
               "作用在 bc 中點（不是節點 b）", 13.5, C["load"], "start", weight="700")
    cv.text_px(cv.X(2.0), cv.Y(0) - 26, "ab：水平桿，長 4 m", 14, C["bmd"], weight="700")
    cv.text_px(cv.X(5.2), cv.Y(-1.55) + 30, "bc：斜桿 4-3-5，長 5 m", 14,
               C["bmd"], "middle", weight="700")
    cv.text_px(cv.X(CC[0]) - 30, cv.Y(CC[1]) + 44,
               "c 為單一滾輪 ⇒ 可自由轉動，M_{c} = 0", 13, C["accent"], "end", weight="700")
    for a, b, lab in ((0.0, 4.0, "4 m"), (4.0, XLOAD, "2 m"), (XLOAD, CC[0], "2 m")):
        cv.dim((a, CC[1]), (b, CC[1]), lab, off=96, label_off=16)
    cv.dim((CC[0], CC[1]), (CC[0], 0.0), "3 m", off=52, label_off=13)
    cv.text_px(W / 2, H - 52,
               f"反力 {N_R} 個（a 為 3、c 為 1）− 平衡 {N_EQ} 式 ⇒ "
               f"{N_R - N_EQ} 度靜不定", 13.5, C["muted"])
    cv.text_px(W / 2, H - 24,
               "若把 ab／bc 對調、或把 68 kN 放在節點 b、或把 c 當成不可轉動的滑軌，"
               "整份答案都會作廢", 13.5, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_kinematics():
    """運動學。攔：以為斜桿 bc 有弦旋轉。實際上有弦旋轉的是水平桿 ab。"""
    H = 660
    amp = 0.9 / DELTA
    cv = frame_canvas(H)
    cv.panel("運動學：不考慮軸向變形 ⇒ 只剩一個側移自由度",
             "ab 水平且軸向剛性 ⇒ u_{b} = 0　│　c 靠垂直牆 ⇒ u_{c} = 0　│　"
             "bc 軸向剛性且兩端 u = 0 ⇒ v_{c} = v_{b} = Δ")
    draw_frame(cv, w=4.0, ghost=True)
    supports(cv, ghost=True)
    d = DELTA * amp
    Bd, Cd = (B[0], B[1] - d), (CC[0], CC[1] - d)
    cv.line(A, Bd, C["deform"], 5.4, cap="butt")
    cv.line(Bd, Cd, C["deform"], 5.4, cap="butt")
    cv.dot(Bd, 5.6, fill=C["deform"]); cv.dot(Cd, 5.6, fill=C["deform"])
    for p, pd in ((B, Bd), (CC, Cd)):
        cv.arrow((p[0], p[1] - 0.05), (pd[0], pd[1] + 0.05), C["accent"], 2.8, 10)
        cv.text_px(cv.X(p[0]) + 13, (cv.Y(p[1]) + cv.Y(pd[1])) / 2, "Δ", 16,
                   C["accent"], "start", weight="700")
    labels(cv, ghost=True)
    cv.text_px(cv.X(1.9), cv.Y(-d) + 34, "弦轉了　⇒　ψ_{ab} = Δ/4", 14,
               C["deform"], weight="700")
    cv.text_px(cv.X(6.3), cv.Y(-2.6 - d) + 34,
               "兩端同時下移 Δ　⇒　純平移　⇒　ψ_{bc} = 0", 14,
               C["deform"], weight="700")
    cv.text_px(W / 2, H - 52,
               "未知數只有 θ_{b}、θ_{c}、Δ 三個；c 可自由轉動，另有 M_{cb} = 0 一式",
               13.5, C["text"], weight="700")
    cv.text_px(W / 2, H - 24,
               "最常見的錯：把「有弦旋轉的那一根」認成斜桿 bc —— 恰好相反",
               13.5, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-kinematics.svg")


def fig3_load_decomp():
    """68 kN 在斜桿上的分解。攔：直接拿 68 kN 去算固端彎矩（斜桿要先取法向分量）。"""
    H = 640
    cv = frame_canvas(H)
    cv.panel("斜桿上的載重必須先分解：只有法向分量進固端彎矩",
             "bc 的方向餘弦 (4/5, −3/5)　⇒　法向分量 68 × 4/5　軸向分量 68 × 3/5")
    draw_frame(cv, w=4.5, ghost=True)
    supports(cv, ghost=True)
    labels(cv, ghost=True)
    sc = 0.016
    cv.arrow((XLOAD, MID[1] + P * sc), (XLOAD, MID[1] + 0.09), C["load"], 3.6, 13)
    cv.text_px(cv.X(XLOAD) - 14, cv.Y(MID[1] + P * sc * 0.6), f"{P:g} kN", 15,
               C["load"], "end", weight="700")
    # 兩個分量都由作用點往外畫：法向 −EY（左下）、軸向 +EX（右下，指向 c）
    hn = (MID[0] - EY[0] * P_PERP * sc, MID[1] - EY[1] * P_PERP * sc)
    cv.arrow(MID, hn, C["bmd"], 3.4, 12)
    cv.text_px(cv.X(hn[0]) - 12, cv.Y(hn[1]) + 14, f"法向 {P_PERP:g} kN", 14,
               C["bmd"], "end", weight="700")
    ha = (MID[0] + EX[0] * P_AXIAL * sc, MID[1] + EX[1] * P_AXIAL * sc)
    cv.arrow(MID, ha, C["member2"], 3.0, 11)
    cv.text_px(cv.X(ha[0]) + 12, cv.Y(ha[1]) + 16, f"軸向 {P_AXIAL:g} kN（不生彎矩）",
               13, C["member2"], "start", weight="700")
    cv.dot(MID, 5.4, fill=C["load"])
    cv.text_px(W / 2, H - 78,
               f"固端彎矩：法向 {P_PERP:g} kN 落在 5 m 桿的中點　⇒　"
               f"M_{{F}} = ±PL/8 = ±{FEM:g} kN·m", 14.5, C["bmd"], weight="700")
    cv.text_px(W / 2, H - 50,
               f"若直接拿 {P:g} kN 去算，會得到 ±{P * L_BC / 8:g}，"
               f"高估 {(P / P_PERP - 1) * 100:.0f}%", 13.5, C["load"], weight="700")
    cv.text_px(W / 2, H - 22,
               "軸向分量在「不考慮軸向變形」的假設下由桿件直接傳遞，不影響彎矩",
               12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-load-decomp.svg")


def fig4_bmd():
    """彎矩圖（畫在受拉側）＋反曲點。攔：把 ab 桿當成全段同號、
    或漏掉 bc 中點因法向載重而多出來的三角形。"""
    H = 626
    cv = frame_canvas(H)
    cv.panel("彎矩圖（畫在受拉側；下凹為正 ⇒ 畫在桿件下方）",
             f"ab：{BM_A:+.0f} 線性到 {BM_B:+.0f}，反曲點距 a {X_ZERO:.3f} m"
             f"　│　bc：端點 {BM_B:+.0f} → 0，中點再疊加 P_{{法向}}L/4 = {P_PERP * L_BC / 4:g}")
    draw_frame(cv, w=5.0)
    supports(cv, size=17)
    labels(cv)
    k = -0.0030                      # 負號 ⇒ 畫在受拉側（下凹為正時往下畫）
    cv.polygon([(A[0], 0.0), (A[0], BM_A * k), (B[0], BM_B * k), (B[0], 0.0)],
               C["fill_m"], C["bmd"], 2.4)
    seg, n = [], 60
    for i in range(n + 1):
        t = i / n
        x = B[0] + (CC[0] - B[0]) * t
        y = B[1] + (CC[1] - B[1]) * t
        bm = BM_B * (1 - t) + BM_C * t + P_PERP * L_BC / 4 * (1 - abs(2 * t - 1))
        seg.append((x + EY[0] * bm * k, y + EY[1] * bm * k))
    cv.polygon([B] + seg + [CC], C["fill_m"], C["bmd"], 2.4)
    cv.line(A, B, C["muted"], 1.4)
    for p, v, dx, dy in ((A, BM_A, 8, -14), (B, BM_B, -14, 24),
                         (MID, BM_MID, -18, 26), (CC, BM_C, -16, -18)):
        if p in (A, B):
            px, py = p[0], v * k
        else:
            px, py = p[0] + EY[0] * v * k, p[1] + EY[1] * v * k
        cv.dot((px, py), 4.4, fill=C["bmd"])
        if abs(v) > 1e-9:
            cv.text_px(cv.X(px) + dx, cv.Y(py) + dy, f"{v:+.1f}", 15,
                       C["bmd"], weight="700")
    cv.dot((X_ZERO, 0.0), 5.6, fill="#FFFFFF", stroke=C["accent"], w=2.8)
    cv.text_px(cv.X(X_ZERO), cv.Y(0) + 34, f"反曲點 x = {X_ZERO:.3f} m", 13,
               C["accent"], weight="700")
    cv.text_px(W / 2, H - 78,
               f"M_{{ab}} = {M_AB:+.0f}　M_{{ba}} = {M_BA:+.0f}　"
               f"M_{{bc}} = {M_BC:+.0f}　M_{{cb}} = 0　（順時針為正，kN·m）",
               14.5, C["bmd"], weight="700")
    cv.text_px(W / 2, H - 50,
               f"c 點反力為水平的 {C_X:.2f} kN（= 217/3）；c 是滾支承，垂直分量為 0，"
               f"{P:g} kN 全由固定端 a 承擔", 13.5, C["accent"], weight="700")
    cv.text_px(W / 2, H - 22,
               "ab 桿兩端同號會漏掉反曲點；bc 中點若只畫端點連線，會漏掉法向載重的三角形",
               12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-4-bmd.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_kinematics, fig3_load_decomp, fig4_bmd):
        f(); print("寫出", f.__name__)
    print(f"\nM_ab = {M_AB:+.4f}   M_ba = {M_BA:+.4f}   M_bc = {M_BC:+.4f}   M_cb = {M_CB:+.4f}")
    print(f"bc 中點彎矩 = {M_MID:+.4f}    ab 反曲點 x = {X_ZERO:.4f} m")
    print(f"EIθ_b = {THETA_B:+.4f}   EIθ_c = {THETA_C:+.4f}   EIΔ = {DELTA:.4f}")
    print(f"c 點反力（水平）= {C_X:.4f} = {Fr(C_X).limit_denominator(1000)}")
    print(f"a 點：A_x = {A_X:+.4f}  A_y = {A_Y:+.4f}  M_a(逆時針) = {M_A:+.4f}")
    print(f"法向分量 = {P_PERP:g} kN   軸向分量 = {P_AXIAL:g} kN   FEM = ±{FEM:g}")
