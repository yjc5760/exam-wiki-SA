#!/usr/bin/env python3
"""
SA-2006-4 剪力屋（剛性梁 ＋ 剛性矮牆）的短柱效應 — 解題圖解產生腳本

用法：
    python3 gen_SA-2006-4.py [輸出目錄]

三條鐵則的落實：
  1. 彎矩、剪力、比值全部由 12EIΔ/L³、6EIΔ/L² 算出；再與剛架有限元
     （剛性梁取極大 EI）逐項 assert
  2. 改 H_LONG / H_SHORT / N_LONG / N_SHORT / P 重跑，兩張圖與所有比值會一起變
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
TAG = "SA-2006-4"

# ══════════════════════════════════════════════════════════
# 幾何與載重（由考卷附圖判讀）
# ══════════════════════════════════════════════════════════
BAY, N_BAY = 5.0, 4
SPAN = BAY * N_BAY                 # 20 m
H_ROOF = 3.0                       # 剛性梁的高度
H_WALL = 1.0                       # 剛性矮牆高
H_LONG = H_ROOF                    # 長柱 AF、BG
H_SHORT = H_ROOF - H_WALL          # 短柱 CJ、DK、EL
X_WALL = 10.0                      # 矮牆左緣
P = 100.0
COLS = [(0.0, H_LONG, "AF"), (5.0, H_LONG, "BG"),
        (10.0, H_SHORT, "CJ"), (15.0, H_SHORT, "DK"), (20.0, H_SHORT, "EL")]
N_LONG = sum(1 for _, h, _ in COLS if abs(h - H_LONG) < 1e-9)
N_SHORT = len(COLS) - N_LONG

# ══════════════════════════════════════════════════════════
# 閉合式：兩端無轉角的柱，M = 6EIΔ/L²、V = 12EIΔ/L³
# ══════════════════════════════════════════════════════════
def m_of(L):  return 6.0 / L ** 2          # ×(EIΔ)
def v_of(L):  return 12.0 / L ** 3         # ×(EIΔ)


SUM_V = sum(v_of(h) for _, h, _ in COLS)
EID = P / SUM_V                            # EIΔ
M_LONG = m_of(H_LONG) * EID
M_SHORT = m_of(H_SHORT) * EID
V_LONG = v_of(H_LONG) * EID
V_SHORT = v_of(H_SHORT) * EID
R_M = Fr(m_of(H_LONG) / m_of(H_SHORT)).limit_denominator(200)      # 長/短 = 4/9
R_V = Fr(v_of(H_LONG) / v_of(H_SHORT)).limit_denominator(200)      # 長/短 = 8/27
assert R_M == Fr(int(H_SHORT), int(H_LONG)) ** 2
assert R_V == Fr(int(H_SHORT), int(H_LONG)) ** 3

# ── 有限元交叉驗證（剛性梁以極大 EI 模擬）─────────────────
def _fe():
    top = [(x, H_ROOF) for x in (0.0, 5.0, 10.0, 15.0, 20.0)]
    bot = [(0.0, 0.0), (5.0, 0.0), (10.0, H_WALL), (15.0, H_WALL), (20.0, H_WALL)]
    nodes = top + bot
    elems = [(i, i + 1, 1e8) for i in range(4)] + \
            [(5 + i, i, 1.0) for i in range(5)]
    fixed = {(5 + i, d) for i in range(5) for d in (0, 1, 2)}
    u, R, M = solve(nodes, elems, fixed, {(0, 0): P}, EI=1.0, EA=1e10)
    return u, R, M


_u, _R, _M = _fe()
FE_D = _u[0]                                # 屋頂側移
assert abs(FE_D - EID) < 1e-4 * EID, (FE_D, EID)
for i, (_, h, nm) in enumerate(COLS):
    mb = abs(_M[(5 + i, i)][0])             # 柱底彎矩
    mt = abs(_M[(5 + i, i)][1])             # 柱頂彎矩
    assert abs(mb - mt) < 1e-4 * mb, nm     # 兩端無轉角 ⇒ 兩端彎矩等值
    assert abs(mb - m_of(h) * EID) < 1e-3 * mb, (nm, mb, m_of(h) * EID)
assert abs(sum(abs(_R[(5 + i, 0)]) for i in range(5)) - P) < 1e-4

# 長柱 vs 短柱的側向勁度（相對值）
K_LONG, K_SHORT = v_of(H_LONG), v_of(H_SHORT)


def _fs(q):
    return f"{q.numerator}/{q.denominator}" if q.denominator != 1 else str(q.numerator)


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 1120
PADL, PADR = 170, 90
SX = (W - PADL - PADR) / SPAN
Y_BASE = 150


def fcanvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=Y_BASE, bg=bg)


def draw_structure(cv, w=7.0, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    cv.line((0.0, H_ROOF), (SPAN, H_ROOF), col, 11.0, cap="butt")      # 剛性梁
    for x, h, _ in COLS:
        cv.line((x, H_ROOF - h), (x, H_ROOF), col, w, cap="butt")
    cv.polygon([(X_WALL, 0.0), (SPAN, 0.0), (SPAN, H_WALL), (X_WALL, H_WALL)],
               "rgba(138,148,166,0.35)" if not ghost else "rgba(195,202,213,0.3)",
               col, 2.4)
    cv.line((-1.0, 0.0), (SPAN + 1.0, 0.0), col, 2.6)


def labels(cv):
    for x, h, nm in COLS:
        cv.text_px(cv.X(x), cv.Y(H_ROOF) - 20, nm[0], 17, C["text"],
                   weight="700", italic=True)
        cv.text_px(cv.X(x), cv.Y(H_ROOF - h) + 26, nm[1], 16, C["text"],
                   weight="700", italic=True)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔：把長柱高度看成 2 m（矮牆之上才是 2 m，長柱是 2+1 = 3 m）。"""
    H = 520
    cv = fcanvas(H, bg="#FFFFFF")
    cv.panel("題目重繪（剪力屋模型）",
             f"AE 為剛性梁（I = ∞）　HJLM 為剛性矮牆（I = ∞）　各柱 EI 相同　"
             f"A 點受水平 {P:g} kN")
    draw_structure(cv)
    labels(cv)
    cv.arrow((-1.9, H_ROOF), (-0.10, H_ROOF), C["load"], 3.6, 13)
    cv.text_px(cv.X(-2.0), cv.Y(H_ROOF), f"{P:g} kN", 16, C["load"], "end",
               weight="700")
    cv.text_px(cv.X(SPAN / 2 - 5), cv.Y(H_ROOF) + 22, "剛性梁 I = ∞", 13.5,
               C["accent"], weight="700")
    cv.text_px(cv.X((X_WALL + SPAN) / 2), cv.Y(H_WALL / 2), "剛性矮牆 I = ∞",
               13.5, C["accent"], weight="700")
    cv.dim((SPAN, 0.0), (SPAN, H_WALL), f"{H_WALL:g} m", off=54, label_off=14)
    cv.dim((SPAN, H_WALL), (SPAN, H_ROOF), f"{H_SHORT:g} m", off=54, label_off=14)
    cv.dim((0.0, 0.0), (0.0, H_ROOF), f"{H_LONG:g} m", off=-54, label_off=-14)
    cv.dim((0.0, 0.0), (SPAN, 0.0), f"{N_BAY} @ {BAY:g} m = {SPAN:g} m",
           off=86, label_off=15)
    cv.text_px(W / 2, H - 52,
               f"剛性梁 ⇒ 柱頂無轉角、且同一個側移 Δ；矮牆頂 J、K、L 視同固定端"
               f" ⇒ 每根柱都是「兩端無轉角＋相對側移 Δ」", 13.5, C["text"],
               weight="700")
    cv.text_px(W / 2, H - 24,
               f"長柱 {H_LONG:g} m（{N_LONG} 根）＝ 矮牆 {H_WALL:g} m ＋ "
               f"{H_SHORT:g} m；短柱只有 {H_SHORT:g} m（{N_SHORT} 根）",
               13.5, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_short_column():
    """短柱效應。攔：以為剪力按柱數平均分配（實際上與 1/L³ 成正比，
    短柱吸走的剪力是長柱的 27/8 倍）。"""
    H1, H2 = 470, 300
    cv1 = fcanvas(H1)
    cv1.panel("兩端無轉角的柱：彎矩圖與側移",
              f"M = 6EIΔ/L²（兩端等值）　V = 12EIΔ/L³　"
              f"⇒ 柱越短，同一個 Δ 逼出的內力越大")
    draw_structure(cv1, w=4.5, ghost=True)
    amp = 0.55 / FE_D
    cv1.line((FE_D * amp, H_ROOF), (SPAN + FE_D * amp, H_ROOF), C["deform"], 6.0,
             cap="butt")
    for x, h, _ in COLS:                     # 雙曲率：反曲點在柱中央
        pts = []
        for i in range(31):
            t = i / 30
            pts.append((x + FE_D * amp * (3 * t ** 2 - 2 * t ** 3), H_ROOF - h + h * t))
        cv1.poly(pts, C["deform"], 4.2)
    k = 0.030
    for x, h, nm in COLS:
        m = m_of(h) * EID
        cv1.polygon([(x, H_ROOF - h), (x - m * k, H_ROOF - h),
                     (x + m * k, H_ROOF), (x, H_ROOF)],
                    C["fill_m"], C["bmd"], 2.0)
        cv1.text_px(cv1.X(x) - 8, cv1.Y(H_ROOF - h) + 22, f"{m:.1f}", 13,
                    C["bmd"], "end", weight="700")
    labels(cv1)
    cv1.text_px(W / 2, H1 - 24,
                f"柱底彎矩：長柱 {M_LONG:.2f}　短柱 {M_SHORT:.2f} kN·m"
                f"　（EIΔ = {EID:.3f} kN·m²）", 14, C["bmd"], weight="700")

    cv2 = Canvas(W, H2, sx=1.0, ox=0.0, oy=0.0)
    cv2.panel("比值：只跟柱長有關，與外力大小無關",
              "同一個 Δ 之下，M ∝ 1/L²、V ∝ 1/L³")
    rows = [
        (f"柱底彎矩比　M_{{AF}} : M_{{EL}}", f"({H_SHORT:g}/{H_LONG:g})² = {_fs(R_M)}",
         f"{M_LONG:.2f} : {M_SHORT:.2f}", C["bmd"]),
        (f"柱底剪力比　V_{{AF}} : V_{{EL}}", f"({H_SHORT:g}/{H_LONG:g})³ = {_fs(R_V)}",
         f"{V_LONG:.2f} : {V_SHORT:.2f}", C["sfd"]),
    ]
    y = 118
    for lab, formula, num, colr in rows:
        cv2.text_px(150, y, lab, 16, C["text"], "start", weight="700")
        cv2.text_px(560, y, formula, 18, colr, "middle", weight="700")
        cv2.text_px(980, y, num, 15, C["muted"], "end")
        y += 56
    cv2.text_px(W / 2, H2 - 78,
                f"層剪力分配：{N_LONG} 根長柱共 {N_LONG * V_LONG:.1f} kN"
                f"（{N_LONG * V_LONG / P * 100:.1f}%），"
                f"{N_SHORT} 根短柱共 {N_SHORT * V_SHORT:.1f} kN"
                f"（{N_SHORT * V_SHORT / P * 100:.1f}%）", 14.5, C["accent"],
                weight="700")
    cv2.text_px(W / 2, H2 - 48,
                f"單根短柱吸走 {V_SHORT:.2f} kN，是單根長柱 {V_LONG:.2f} kN 的 "
                f"{V_SHORT / V_LONG:.3g} 倍 —— 這就是短柱效應", 14,
                C["load"], weight="700")
    cv2.text_px(W / 2, H2 - 20,
                "非結構的剛性矮牆把柱的自由長度縮短，剪力破壞常由此而來，為耐震設計大忌",
                13, C["muted"])
    return compose([cv1, cv2], cols=1, path=f"{OUT}/{TAG}-fig-2-short-column.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_short_column):
        f(); print("寫出", f.__name__)
    print(f"\nEIΔ = {EID:.6f} kN·m²   （= 1800/97 = {1800 / 97:.6f}）")
    print(f"長柱（{H_LONG:g} m）：M = {M_LONG:.4f} kN·m   V = {V_LONG:.4f} kN")
    print(f"短柱（{H_SHORT:g} m）：M = {M_SHORT:.4f} kN·m   V = {V_SHORT:.4f} kN")
    print(f"彎矩比 = {_fs(R_M)}   剪力比 = {_fs(R_V)}")
    print(f"層剪力檢核：{N_LONG}×{V_LONG:.4f} + {N_SHORT}×{V_SHORT:.4f} = "
          f"{N_LONG * V_LONG + N_SHORT * V_SHORT:.4f} kN")
    print(f"有限元側移 = {FE_D:.6f}（EIΔ）")
