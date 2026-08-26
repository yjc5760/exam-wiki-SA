#!/usr/bin/env python3
"""
SA-2017-3 有側移門型剛架（兩端鉸支承）傾角變位法 — 解題圖解產生腳本

用法：
    python3 gen_SA-2017-3.py [輸出目錄]

三條鐵則的落實：
  1. 圖上每個彎矩、轉角、側移都由下方的分數精確解算出；該精確解再與
     內建剛架有限元（figs/_lib/frame_fe.py）逐項 assert
  2. 改 H_COL / L_BM / W_UDL / P_H 重跑，四張圖與所有數字會一起變
  3. 每張圖攔一種特定錯誤，見各 fig 的 docstring
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
TAG = "SA-2017-3"

# ══════════════════════════════════════════════════════════
# 幾何與載重（由考卷附圖判讀）
# ══════════════════════════════════════════════════════════
H_COL, L_BM = 4.0, 6.0
A_, B_, CC_, D_ = (0.0, 0.0), (0.0, H_COL), (L_BM, H_COL), (L_BM, 0.0)
W_UDL = 45.0                       # 梁 BC 的均布載重（向下）
P_H = 60.0                         # 兩個水平集中力，皆向左
Y_P = H_COL / 2                    # 桿件集中力在右柱的高度（距 D 2 m）
E_PT = (L_BM, Y_P)

# 固端彎矩（順時針為正）
FEM_BC = -W_UDL * L_BM ** 2 / 12          # = -135
FEM_CB = +W_UDL * L_BM ** 2 / 12          # = +135
# 右柱 D→C（向上）：向左的載重在該桿的局部座標是「向上」⇒ 標準式要變號
FEM_DC = +P_H * H_COL / 8                 # = +30   ← 舊版寫成 -30，是本題全部錯誤的源頭
FEM_CD = -P_H * H_COL / 8                 # = -30
FEM_CD_MOD = FEM_CD - FEM_DC / 2          # = -45   （D 為鉸的修正固端彎矩）

# ══════════════════════════════════════════════════════════
# 分數精確解（傾角變位法，順時針為正，ψ 以向右側移為正）
#   未知：t = EIθ_B, s = EIθ_C, p = EIψ
# ══════════════════════════════════════════════════════════
def _gauss(A, b):
    A = [row[:] + [b[i]] for i, row in enumerate(A)]
    n = len(A)
    for i in range(n):
        piv = next(r for r in range(i, n) if A[r][i] != 0)
        A[i], A[piv] = A[piv], A[i]
        A[i] = [x / A[i][i] for x in A[i]]
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i]
                A[r] = [x - f * y for x, y in zip(A[r], A[i])]
    return [A[i][n] for i in range(n)]


kC = Fr(3, 1) / Fr(H_COL).limit_denominator()      # 3EI/L 的係數 3/4
kB = Fr(2, 1) / Fr(L_BM).limit_denominator()       # 2EI/L 的係數 1/3
_A = [[kC + 2 * kB, kB, -kC],                      # 節點 B
      [kB, kC + 2 * kB, -kC],                      # 節點 C
      [Fr(1), Fr(1), Fr(-2)]]                      # 層剪力（除以 3EI/4 後）
# 層剪力式（推導見 .md §4.4）：
#   H_A = M_BA / H          （左柱無桿件載重）
#   H_D = [P_H·(H − y_P) + M_CD] / H     （右柱含桿件載重的力矩修正）
#   H_A + H_D = 2·P_H
#   ⇒ M_BA + M_CD = 2·P_H·H − P_H·(H − y_P) = SHEAR_RHS
SHEAR_RHS = Fr(int(2 * P_H * H_COL)) - Fr(int(P_H * (H_COL - Y_P)))     # = 360
_b = [Fr(-int(FEM_BC)),
      Fr(-int(FEM_CB)) - Fr(int(FEM_CD_MOD)),
      (SHEAR_RHS - Fr(int(FEM_CD_MOD))) / Fr(3, 4)]
T, S, PSI = _gauss(_A, _b)

M_BA = Fr(3, 4) * (T - PSI)
M_BC = kB * (2 * T + S) + Fr(int(FEM_BC))
M_CB = kB * (2 * S + T) + Fr(int(FEM_CB))
M_CD = Fr(3, 4) * (S - PSI) + Fr(int(FEM_CD_MOD))
TH_A = (3 * PSI - T) / 2
TH_D = (Fr(-int(2 * FEM_DC)) - S + 3 * PSI) / 2

# ══════════════════════════════════════════════════════════
# 有限元交叉驗證
# ══════════════════════════════════════════════════════════
def _fe(N=24):
    l = L_BM / N
    nodes = [A_, B_] + [(L_BM * k / N, H_COL) for k in range(1, N + 1)] + [E_PT, D_]
    beam = [1] + list(range(2, 2 + N))
    iC, iE, iD = beam[-1], beam[-1] + 1, beam[-1] + 2
    elems = [(0, 1)] + [(beam[k], beam[k + 1]) for k in range(N)] + [(iC, iE), (iE, iD)]
    loads = {}
    for k in range(N):
        n1, n2 = beam[k], beam[k + 1]
        for n, sg in ((n1, -1), (n2, +1)):
            loads[(n, 1)] = loads.get((n, 1), 0) - W_UDL * l / 2
            loads[(n, 2)] = loads.get((n, 2), 0) + sg * W_UDL * l * l / 12
    loads[(iC, 0)] = -P_H
    loads[(iE, 0)] = -P_H
    u, R, M = solve(nodes, elems, {(0, 0), (0, 1), (iD, 0), (iD, 1)}, loads,
                    EI=1.0, EA=1e7)
    fem = W_UDL * l * l / 12
    return dict(psi=u[3 * 1] / H_COL, thB=-u[3 * 1 + 2], thC=-u[3 * iC + 2],
                thA=-u[3 * 0 + 2], thD=-u[3 * iD + 2],
                MBA=M[(0, 1)][1], MCD=M[(iC, iE)][0],
                MBC=M[(beam[0], beam[1])][0] - fem,
                MCB=M[(beam[N - 1], beam[N])][1] + fem,
                HA=R[(0, 0)], VA=R[(0, 1)], HD=R[(iD, 0)], VD=R[(iD, 1)])


_F = _fe()
for nm, exact, got in (("ψ", PSI, _F["psi"]), ("θ_B", T, _F["thB"]), ("θ_C", S, _F["thC"]),
                       ("θ_A", TH_A, _F["thA"]), ("θ_D", TH_D, _F["thD"]),
                       ("M_BA", M_BA, _F["MBA"]), ("M_CD", M_CD, _F["MCD"]),
                       ("M_BC", M_BC, _F["MBC"]), ("M_CB", M_CB, _F["MCB"])):
    assert abs(float(exact) - got) < 0.05, (nm, float(exact), got)
assert M_BA + M_BC == 0 and M_CB + M_CD == 0                 # 節點平衡
assert M_BA + M_CD == SHEAR_RHS                              # 層剪力式
H_A = float(M_BA) / H_COL
H_D = (P_H * (H_COL - Y_P) + float(M_CD)) / H_COL
assert abs(H_A + H_D - 2 * P_H) < 1e-9

# 梁的彎矩圖：兩端 + 拋物線
BM_B = float(M_BC)                       # 起點：+M_nf
BM_C = -float(M_CB)                      # 終點：−M_fn
BM_MIDSPAN = (BM_B + BM_C) / 2 + W_UDL * L_BM ** 2 / 8
X0 = [x for x in (0.001 * i * L_BM for i in range(1001))
      if (BM_B + (BM_C - BM_B) * x / L_BM + W_UDL * x * (L_BM - x) / 2) > 0]
X_ZERO1, X_ZERO2 = (X0[0], X0[-1]) if X0 else (0.0, 0.0)


def _s(v):
    q = Fr(v).limit_denominator(400) if not isinstance(v, Fr) else v
    return f"{q.numerator}/{q.denominator}" if q.denominator != 1 else str(q.numerator)


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 1060
PADL, PADR = 178, 302        # 右側留給水平載重的箭頭與標註
SX = (W - PADL - PADR) / L_BM
Y_BASE = 150                 # y = 0（柱底）距畫布底端的像素


def fcanvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=Y_BASE, bg=bg)


def draw_frame(cv, w=7.0, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    for p, q in ((A_, B_), (B_, CC_), (D_, CC_)):
        cv.line(p, q, col, w, cap="butt")
    cv.pin_support(A_, size=17, color=col)
    cv.pin_support(D_, size=17, color=col)


def node_labels(cv, ghost=False):
    col = C["ghost"] if ghost else C["text"]
    for p, nm, dx, dy in ((A_, "A", -22, 6), (B_, "B", -22, -10),
                          (CC_, "C", 22, -10), (D_, "D", 22, 6)):
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, nm, 19, col, weight="700",
                   italic=True)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔：把 C 點的 60 kN 當成桿件載重（它是節點載重，不進 FEM），
    以及把柱底當成固定端（圖上是鉸）。"""
    H = 726
    cv = fcanvas(H, bg="#FFFFFF")
    cv.panel("題目重繪",
             f"A、D 鉸支承　B、C 剛節點　柱高 {H_COL:g} m　梁跨 {L_BM:g} m　EI 為定值")
    draw_frame(cv)
    node_labels(cv)
    cv.udl((0.0, H_COL + 0.10), (L_BM, H_COL + 0.10), 0.50, n=13, color=C["load"], w=1.8)
    cv.text_px(cv.X(L_BM / 2), cv.Y(H_COL + 0.92), f"{W_UDL:g} kN/m", 16,
               C["load"], weight="700")
    for y, tag in ((H_COL, "節點載重"), (Y_P, "桿件載重")):
        cv.arrow((L_BM + 1.15, y), (L_BM + 0.06, y), C["load"], 3.4, 12)
        cv.text_px(cv.X(L_BM + 1.20), cv.Y(y) - 2, f"{P_H:g} kN", 15,
                   C["load"], "start", weight="700")
        cv.text_px(cv.X(L_BM + 1.20), cv.Y(y) + 20, tag, 12.5,
                   C["accent"] if tag == "節點載重" else C["bmd"], "start", weight="700")
    cv.dim((L_BM, H_COL), (L_BM, Y_P), "2 m", off=-52, label_off=-14)
    cv.dim((L_BM, Y_P), (L_BM, 0.0), "2 m", off=-52, label_off=-14)
    cv.dim((0, 0), (0, H_COL), f"{H_COL:g} m", off=-64, label_off=-14)
    cv.dim(A_, D_, f"{L_BM:g} m", off=66, label_off=14)
    cv.text_px(W / 2, H - 52,
               "C 點的 60 kN 直接作用在剛節點上 ⇒ 不進固端彎矩，"
               "只在層剪力方程中以外力出現", 13.5, C["accent"], weight="700")
    cv.text_px(W / 2, H - 24,
               "柱中的 60 kN 才是桿件載重 ⇒ 必須算固端彎矩（而且符號最容易錯，見圖 2）",
               13.5, C["bmd"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_fem_sign():
    """右柱固端彎矩的符號判定。攔的就是本題原解析唯一的錯：把 M_F^DC 寫成 −30。"""
    Wp, Hp = 520, 520
    sx = 62.0

    cv1 = Canvas(Wp, Hp, sx=sx, ox=Wp / 2, oy=110)
    cv1.panel("① 右柱：向左的桿件載重", "把柱單獨取出，兩端暫時視為固定")
    cv1.line((0, 0), (0, H_COL), C["member"], 7.0, cap="butt")
    cv1.fixed_support((0, 0), ang=0, size=20)
    cv1.fixed_support((0, H_COL), ang=180, size=20)
    cv1.arrow((1.55, Y_P), (0.07, Y_P), C["load"], 3.4, 12)
    cv1.text_px(cv1.X(1.62), cv1.Y(Y_P), f"{P_H:g} kN", 15, C["load"], "start",
                weight="700")
    cv1.text_px(cv1.X(0) - 16, cv1.Y(0) - 4, "D", 18, C["text"], "end",
                weight="700", italic=True)
    cv1.text_px(cv1.X(0) - 16, cv1.Y(H_COL) - 4, "C", 18, C["text"], "end",
                weight="700", italic=True)
    cv1.text_px(Wp / 2, Hp - 76, "局部座標：桿軸 D→C 朝上", 13.5, C["muted"])
    cv1.text_px(Wp / 2, Hp - 48,
                "把它順時針轉 90° 攤平 ⇒ 桿軸朝右", 13.5, C["text"], weight="700")
    cv1.text_px(Wp / 2, Hp - 20,
                "向左 (−1, 0) 轉 90° 之後變成 (0, +1) ＝ 向上", 14,
                C["accent"], weight="700")

    cv2 = Canvas(Wp, Hp, sx=sx, ox=110, oy=Hp / 2)
    cv2.panel("② 攤平後：載重朝上 ⇒ 標準式要變號",
              "標準 ±PL/8 是為「向下」寫的；本題朝上，兩端符號整組相反")
    cv2.line((0, 0), (H_COL, 0), C["member"], 7.0, cap="butt")
    cv2.fixed_support((0, 0), ang=-90, size=20)
    cv2.fixed_support((H_COL, 0), ang=90, size=20)
    cv2.arrow((Y_P, -1.55), (Y_P, -0.07), C["load"], 3.4, 12)
    cv2.text_px(cv2.X(Y_P), cv2.Y(-1.75), f"{P_H:g} kN（朝上）", 15, C["load"],
                weight="700")
    cv2.text_px(cv2.X(0) + 6, cv2.Y(0) + 30, "D", 18, C["text"], "start",
                weight="700", italic=True)
    cv2.text_px(cv2.X(H_COL) - 6, cv2.Y(0) + 30, "C", 18, C["text"], "end",
                weight="700", italic=True)
    cv2.text_px(Wp / 2, Hp - 104,
                f"M_{{F}}^{{DC}} = +PL/8 = {FEM_DC:+.0f} kN·m", 16, C["bmd"],
                weight="700")
    cv2.text_px(Wp / 2, Hp - 76,
                f"M_{{F}}^{{CD}} = −PL/8 = {FEM_CD:+.0f} kN·m", 16, C["bmd"],
                weight="700")
    cv2.text_px(Wp / 2, Hp - 44,
                f"D 為鉸 ⇒ 修正：M_{{F}}^{{CD,mod}} = {FEM_CD:+.0f} − "
                f"({FEM_DC:+.0f})/2 = {FEM_CD_MOD:+.0f}", 14.5, C["accent"],
                weight="700")
    cv2.text_px(Wp / 2, Hp - 16,
                f"寫成 {-FEM_DC:+.0f} / {-FEM_CD:+.0f} 的話，修正值會變成 "
                f"{-FEM_CD_MOD:+.0f}，之後每個答案都跟著錯", 13,
                C["load"], weight="700")
    return compose([cv1, cv2], cols=2, path=f"{OUT}/{TAG}-fig-2-fem-sign.svg")


def fig3_shear_eq():
    """層剪力方程的兩個自由體。攔：對含桿件載重的右柱直接套 (M_top+M_bot)/L。"""
    Wp, Hp = 500, 540
    sx = 60.0

    def col(title, sub, has_load, Mtop, Hbot, note):
        cv = Canvas(Wp, Hp, sx=sx, ox=Wp / 2, oy=130)
        cv.panel(title, sub)
        cv.line((0, 0), (0, H_COL), C["member"], 7.0, cap="butt")
        cv.dot((0, 0), 6.5, fill="#FFFFFF", stroke=C["member"], w=3.0)
        cv.moment_arrow((0, H_COL), r=24, ccw=False, color=C["bmd"], w=2.8)
        cv.text_px(cv.X(0) + 40, cv.Y(H_COL) - 6, Mtop, 15, C["bmd"], "start",
                   weight="700")
        if has_load:
            cv.arrow((1.5, Y_P), (0.07, Y_P), C["load"], 3.2, 11)
            cv.text_px(cv.X(1.56), cv.Y(Y_P), f"{P_H:g} kN", 14, C["load"], "start",
                       weight="700")
        cv.arrow((-1.35, 0), (-0.10, 0), C["deform"], 3.2, 11)
        cv.text_px(cv.X(-1.42), cv.Y(0), Hbot, 15, C["deform"], "end", weight="700")
        cv.text_px(cv.X(0) - 14, cv.Y(0) + 26, "鉸 ⇒ M = 0", 12.5, C["muted"], "end")
        cv.text_px(Wp / 2, Hp - 44, note, 14, C["text"], weight="700")
        return cv

    c1 = col("左柱 AB（無桿件載重）", "ΣM_{B} = 0（對柱頂取矩）",
             False, "M_{BA}", "H_{A}",
             f"H_{{A}} = M_{{BA}} / {H_COL:g} = {H_A:.3f} kN")
    c2 = col("右柱 DC（有桿件載重）", "ΣM_{C} = 0，必須把 60 kN 的力矩算進去",
             True, "M_{CD}", "H_{D}",
             f"H_{{D}} = ({P_H * (H_COL - Y_P):g} + M_{{CD}}) / {H_COL:g}"
             f" = {H_D:.3f} kN")
    return compose([c1, c2], cols=2,
                   note=f"層剪力：H_{{A}} + H_{{D}} = 總水平外力 {2 * P_H:g} kN　⇒　"
                        f"M_{{BA}} + M_{{CD}} = {float(M_BA + M_CD):.0f}　"
                        f"（右柱若漏掉 60 kN 的力矩，這條式子就整條錯）",
                   path=f"{OUT}/{TAG}-fig-3-shear-eq.svg")


def fig4_bmd():
    """彎矩圖（畫在受拉側）。攔：把左右柱的端彎矩畫成一樣大
    （右柱因為有反向的桿件載重，端彎矩只有左柱的約 28%）。"""
    H = 790
    cv = fcanvas(H)
    cv.panel("彎矩圖（畫在受拉側）",
             f"M_{{BA}} = {float(M_BA):+.2f}　M_{{CD}} = {float(M_CD):+.2f}"
             f"　M_{{AB}} = M_{{DC}} = 0（鉸支承）　單位 kN·m")
    draw_frame(cv, w=5.0)
    node_labels(cv)
    k = 0.0040                       # 模型單位 / (kN·m)；沿 ŷ 偏移 −M_bend·k ⇒ 畫在受拉側
    # 左柱 A→B：M_bend 由 0（鉸）線性到 −M_BA；ŷ = 左 ⇒ 畫在柱的外（左）側
    cv.polygon([A_, (float(M_BA) * k * -1 * -1 * 0 + 0.0, 0.0),
                (-float(M_BA) * k, H_COL), B_], C["fill_m"], C["bmd"], 2.2)
    # 右柱 D→C：M_bend(y) = H_D·y − P_H·max(y−y_P, 0)，在 y = y_P 有折點；ŷ = 右 ⇒ 畫在內（左）側
    colpts = [(L_BM, 0.0)]
    for i in range(41):
        y = H_COL * i / 40
        bm = H_D * y - P_H * max(y - Y_P, 0.0)
        colpts.append((L_BM - bm * k, y))
    cv.polygon(colpts + [CC_], C["fill_m"], C["bmd"], 2.2)
    BM_KINK = H_D * Y_P
    cv.dot((L_BM - BM_KINK * k, Y_P), 4.2, fill=C["bmd"])
    cv.text_px(cv.X(L_BM - BM_KINK * k) - 12, cv.Y(Y_P) + 6,
               f"{BM_KINK:.1f}", 13.5, C["bmd"], "end", weight="700")
    # 梁 B→C：兩端 + 拋物線；ŷ = 上 ⇒ 正（下凹）畫在下方
    seg = []
    for i in range(81):
        x = L_BM * i / 80
        bm = BM_B + (BM_C - BM_B) * x / L_BM + W_UDL * x * (L_BM - x) / 2
        seg.append((x, H_COL - bm * k))
    cv.polygon([B_] + seg + [CC_], C["fill_m"], C["bmd"], 2.2)
    cv.text_px(cv.X(-float(M_BA) * k) - 10, cv.Y(H_COL) - 26,
               f"{abs(BM_B):.1f}", 14.5, C["bmd"], "end", weight="700")
    cv.text_px(cv.X(L_BM) + 14, cv.Y(H_COL) + 26,
               f"{abs(BM_C):.1f}", 14.5, C["bmd"], "start", weight="700")
    cv.dot((L_BM / 2, H_COL - BM_MIDSPAN * k), 4.4, fill=C["bmd"])
    cv.text_px(cv.X(L_BM / 2), cv.Y(H_COL - BM_MIDSPAN * k) + 24,
               f"跨中 {BM_MIDSPAN:+.1f}", 14, C["bmd"], weight="700")
    cv.dot((X_ZERO1, H_COL), 5.2, fill="#FFFFFF", stroke=C["accent"], w=2.6)
    cv.text_px(cv.X(X_ZERO1), cv.Y(H_COL) - 24, f"反曲點 {X_ZERO1:.2f} m", 12.5,
               C["accent"], weight="700")
    cv.text_px(W / 2, H - 78,
               f"θ_{{A}} = {float(TH_A):.2f}/EI　θ_{{D}} = {float(TH_D):.2f}/EI"
               f"　（皆為順時針）　ψ = {float(PSI):.0f}/EI（負 ⇒ 向左側移）",
               14, C["deform"], weight="700")
    cv.text_px(W / 2, H - 50,
               f"梁端彎矩 {abs(BM_B):.1f}（B）與 {abs(BM_C):.1f}（C）差了 "
               f"{abs(BM_B) / abs(BM_C):.1f} 倍 —— 右柱被反向的桿件載重「卸掉」了一部分",
               13.5, C["muted"])
    cv.text_px(W / 2, H - 22,
               f"層剪力檢核：M_{{BA}} + M_{{CD}} = {float(M_BA + M_CD):.0f} = "
               f"2 × {P_H:g} × {H_COL:g} − {P_H:g} × {H_COL - Y_P:g}",
               13, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-4-bmd.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_fem_sign, fig3_shear_eq, fig4_bmd):
        f(); print("寫出", f.__name__)
    print("\n=== 精確解（分數）===")
    for nm, v in (("EIψ", PSI), ("EIθ_B", T), ("EIθ_C", S), ("EIθ_A", TH_A),
                  ("EIθ_D", TH_D), ("M_BA", M_BA), ("M_BC", M_BC),
                  ("M_CB", M_CB), ("M_CD", M_CD)):
        print(f"  {nm:7s} = {_s(v):>10s} = {float(v):+10.4f}")
    print(f"  H_A = {H_A:.4f}   H_D = {H_D:.4f}   和 = {H_A + H_D:.4f}")
    print(f"  梁跨中彎矩 = {BM_MIDSPAN:+.3f}   反曲點 x = "
          f"{X_ZERO1:.3f} / {X_ZERO2:.3f} m")
    print(f"  FEM：BC {FEM_BC:+.0f} / {FEM_CB:+.0f}　DC {FEM_DC:+.0f} / "
          f"{FEM_CD:+.0f}　修正 {FEM_CD_MOD:+.0f}")
