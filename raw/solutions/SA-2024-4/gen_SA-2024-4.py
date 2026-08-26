#!/usr/bin/env python3
"""
SA-2024-4 對稱剛度、反對稱側力的門型剛架 — 解題圖解產生腳本

用法：
    python3 gen_SA-2024-4.py [輸出目錄]

三條鐵則的落實：
  1. 位移、轉角、彎矩全部由內建剛架有限元解出，並與 PL、PL³/EI 的閉合式 assert
  2. 改 LB / RATIO 重跑，兩張圖與所有數字會一起變
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
TAG = "SA-2024-4"

# ══════════════════════════════════════════════════════════
# 幾何（L = 1、EI = 1、P = 1 ⇒ 結果即為 PL、PL³/EI 的係數）
# ══════════════════════════════════════════════════════════
LB, EI, P = 1.0, 1.0, 1.0          # 梁長 L、梁剛度 EI、側力 P
HC = 2 * LB                        # 柱高 2L
EIC = 2 * EI                       # 柱剛度 2EI
A_, B_, CC_, D_ = (0.0, 0.0), (0.0, HC), (LB, HC), (LB, 0.0)
K_COL = EIC / HC                   # = EI/L
K_BM = EI / LB                     # = EI/L
assert abs(K_COL - K_BM) < 1e-12, "本題三根桿的相對勁度刻意設計成相等"

_u, _R, _M = solve([A_, B_, CC_, D_], [(0, 1, EIC), (1, 2, EI), (3, 2, EIC)],
                   {(0, 0), (0, 1), (0, 2), (3, 0), (3, 1), (3, 2)},
                   {(1, 0): P}, EI=EI)
DELTA_B = _u[3 * 1]                                    # B 的水平位移
TH_B = -_u[3 * 1 + 2]                                  # 順時針為正
TH_C = -_u[3 * 2 + 2]
M_AB, M_BA = _M[(0, 1)]
M_BC, M_CB = _M[(1, 2)]
M_DC, M_CD = _M[(3, 2)]

# ── 與閉合式對照 ────────────────────────────────────────
assert abs(DELTA_B - 5 / 21) < 1e-8, DELTA_B                    # 5PL³/21EI
assert abs(abs(M_CD) - 3 / 7) < 1e-8 and abs(abs(M_DC) - 4 / 7) < 1e-8
assert abs(abs(M_BA) - 3 / 7) < 1e-8 and abs(abs(M_AB) - 4 / 7) < 1e-8
assert abs(abs(M_CB) - 3 / 7) < 1e-8
assert abs(TH_B - TH_C) < 1e-9, "反對稱 ⇒ θ_B = θ_C"
assert abs(TH_B - 1 / 14) < 1e-9, TH_B      # +PL²/14EI（順時針正）；.md 舊版用逆時針正故記為 −1/14
assert abs(M_BA + M_BC) < 1e-9 and abs(M_CB + M_CD) < 1e-9       # 節點平衡
assert abs(_R[(0, 0)] + _R[(3, 0)] + P) < 1e-9                   # ΣFx
assert abs(_R[(0, 0)] - _R[(3, 0)]) < 1e-9, "反對稱 ⇒ 兩柱平分層剪力"
PSI = -DELTA_B / HC                     # 逆時針為正的弦轉角（.md 的約定）


def _fr(v):
    q = Fr(v).limit_denominator(200)
    return f"{q.numerator}/{q.denominator}" if q.denominator != 1 else str(q.numerator)


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 620
PADL, PADR = 210, 190
SX = (W - PADL - PADR) / LB
Y_BASE = 130
Wp2 = W                       # 子圖寬（compose 用）


def fcanvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=Y_BASE, bg=bg)


def draw_frame(cv, w=7.0, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    for p, q in ((A_, B_), (B_, CC_), (D_, CC_)):
        cv.line(p, q, col, w, cap="butt")
    cv.fixed_support(A_, size=20, color=col)
    cv.fixed_support(D_, size=20, color=col)


def node_labels(cv, ghost=False):
    col = C["ghost"] if ghost else C["text"]
    for p, nm, dx, dy in ((A_, "A", -22, 4), (B_, "B", -22, -12),
                          (CC_, "C", 22, -12), (D_, "D", 22, 4)):
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, nm, 19, col, weight="700",
                   italic=True)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔：看到「柱 2EI、梁 EI」就以為是不對稱結構 ——
    換算成相對勁度 K = EI/L 之後三根桿完全相等。"""
    H = 790
    cv = fcanvas(H, bg="#FFFFFF")
    cv.panel("題目重繪（考卷圖四）",
             "A、D 固定端　柱 AB、CD 長 2L、剛度 2EI　梁 BC 長 L、剛度 EI　"
             "節點 B 受向右的集中力 P")
    draw_frame(cv)
    node_labels(cv)
    cv.arrow((-0.72, HC), (-0.05, HC), C["load"], 3.6, 13)
    cv.text_px(cv.X(-0.80), cv.Y(HC), "P", 18, C["load"], "end", weight="700",
               italic=True)
    cv.text_px(cv.X(LB / 2), cv.Y(HC) - 26, "EI，長 L", 14, C["bmd"], weight="700")
    cv.text_px(cv.X(0) - 16, cv.Y(HC / 2), "2EI，長 2L", 14, C["bmd"], "end",
               weight="700")
    cv.text_px(cv.X(LB) + 16, cv.Y(HC / 2), "2EI，長 2L", 14, C["bmd"], "start",
               weight="700")
    cv.text_px(W / 2, H - 78,
               f"相對勁度 K = EI/L：柱 2EI/(2L) = EI/L，梁 EI/L ⇒ "
               f"三根桿的 K 完全相等", 13.5, C["accent"], weight="700")
    cv.text_px(W / 2, H - 50,
               "剛度對稱 ＋ 反對稱側力 ⇒ 可直接斷定 θ_{B} = θ_{C}，未知數少一個",
               13.5, C["text"], weight="700")
    cv.text_px(W / 2, H - 22,
               "沒先換算成 K 就會誤判為不對稱結構，算式冗長且易錯", 13,
               C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_antisym_bmd():
    """反對稱變形與彎矩圖（分兩格）。攔：以為柱頂與柱底的彎矩一樣大
    （反對稱下 |M_底| = 4/7 PL 是 |M_頂| = 3/7 PL 的 4/3 倍）。"""
    Hp = 760
    amp = 0.45 / DELTA_B

    cv1 = fcanvas(Hp)
    cv1.panel("① 反對稱變形",
              f"Δ_{{B}} = {_fr(DELTA_B)} PL³/EI（向右）　"
              f"θ_{{B}} = θ_{{C}} = {_fr(TH_B)} PL²/EI（順時針）")
    draw_frame(cv1, w=4.0, ghost=True)
    node_labels(cv1, ghost=True)
    for x0, th_top in ((0.0, TH_B), (LB, TH_C)):
        pts = []
        for i in range(41):
            t = i / 40
            h01 = -2 * t ** 3 + 3 * t ** 2
            h11 = t ** 3 - t ** 2
            d = h01 * DELTA_B + h11 * HC * (-th_top)      # 底端 u = 0、θ = 0
            pts.append((x0 + d * amp, HC * t))
        cv1.poly(pts, C["deform"], 5.0)
    cv1.line((DELTA_B * amp, HC), (LB + DELTA_B * amp, HC), C["deform"], 5.0)
    cv1.double_arrow((0, HC + 0.20), (DELTA_B * amp, HC + 0.20), C["accent"], 2.6, 9)
    cv1.text_px(cv1.X(DELTA_B * amp / 2), cv1.Y(HC + 0.38), "Δ_{B}", 15,
                C["accent"], weight="700")
    cv1.text_px(Wp2 / 2, Hp - 50,
                "兩柱皆為雙曲率、變形模式完全相同（不是鏡像）—— 這就是反對稱",
                13.5, C["deform"], weight="700")
    cv1.text_px(Wp2 / 2, Hp - 22,
                f"兩柱平分層剪力：H_{{A}} = H_{{D}} = P/2", 13.5, C["muted"])

    cv2 = fcanvas(Hp)
    cv2.panel("② 彎矩圖（畫在受拉側）",
              f"柱底 {_fr(abs(M_DC))} PL　柱頂 {_fr(abs(M_CD))} PL　"
              f"梁在跨中反曲（反對稱的必然結果）")
    draw_frame(cv2, w=5.0)
    node_labels(cv2)
    k = 0.42
    for x0, mtop, mbot, sgn in ((0.0, M_BA, M_AB, -1), (LB, M_CD, M_DC, +1)):
        cv2.polygon([(x0, 0.0), (x0 + sgn * abs(mbot) * k, 0.0),
                     (x0 - sgn * abs(mtop) * k, HC), (x0, HC)],
                    C["fill_m"], C["bmd"], 2.2)
        cv2.text_px(cv2.X(x0 + sgn * abs(mbot) * k) + sgn * 10, cv2.Y(0.0) - 8,
                    f"{_fr(abs(mbot))} PL", 14, C["bmd"],
                    "start" if sgn > 0 else "end", weight="700")
        cv2.text_px(cv2.X(x0 - sgn * abs(mtop) * k) - sgn * 10, cv2.Y(HC) + 22,
                    f"{_fr(abs(mtop))} PL", 14, C["bmd"],
                    "end" if sgn > 0 else "start", weight="700")
    cv2.polygon([B_, (0.0, HC + abs(M_BC) * k * 0.6),
                 (LB, HC - abs(M_CB) * k * 0.6), CC_], C["fill_m"], C["bmd"], 2.2)
    cv2.dot((LB / 2, HC), 5.2, fill="#FFFFFF", stroke=C["accent"], w=2.6)
    cv2.text_px(cv2.X(LB / 2), cv2.Y(HC) - 40, "梁的反曲點", 12.5,
                C["accent"], weight="700")
    cv2.text_px(Wp2 / 2, Hp - 50,
                f"C 點：M_{{CD}} = {_fr(abs(M_CD))} PL　D 點：M_{{DC}} = "
                f"{_fr(abs(M_DC))} PL", 15, C["bmd"], weight="700")
    cv2.text_px(Wp2 / 2, Hp - 22,
                f"柱底是柱頂的 {abs(M_DC) / abs(M_CD):.3g} 倍 —— 兩者不相等，"
                f"因為柱頂還要跟梁分攤節點彎矩", 13, C["load"], weight="700")
    return compose([cv1, cv2], cols=2, path=f"{OUT}/{TAG}-fig-2-antisym-bmd.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_antisym_bmd):
        f(); print("寫出", f.__name__)
    print(f"\nΔ_B = {DELTA_B:.6f} PL³/EI = {_fr(DELTA_B)}")
    print(f"θ_B = θ_C = {TH_B:.6f} PL²/EI = {_fr(TH_B)}（順時針為正）")
    print(f"ψ（逆時針為正）= {PSI:.6f} = {_fr(PSI)} PL²/EI")
    for nm, v in (("M_AB", M_AB), ("M_BA", M_BA), ("M_BC", M_BC),
                  ("M_CB", M_CB), ("M_CD", M_CD), ("M_DC", M_DC)):
        print(f"  {nm} = {v:+.6f} PL = {_fr(v)} PL")
    print(f"  H_A = {_R[(0, 0)]:+.4f}   H_D = {_R[(3, 0)]:+.4f}")
