#!/usr/bin/env python3
"""SA-2018-4：上部梁 A–E 上，中點 C 向下位移之影響線 — 解題圖解（struct-diagram，2026-11-07）

用法：python3 gen_SA-2018-4_il.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。

數值來源：SA-2018-4.md §1.5–§4（馬克士威互惠＋傾角變位法；2026-11-07 盲解比對「一致」）
  互惠：IL_vC(x) ＝ C 點施加向下單位力時梁 A–E 的撓度曲線 v(x)（向下為正）
  對稱 ⇒ B、D 無垂直位移；BF、DG 提供轉動勁度 4EI/5 = 640
  θ_B = 1/1024；M_BA = 15/32、M_BD = −35/32 kN·m
  AB：v = x(x² − 25)/51200；BD：簡支梁跨中集中載重 ＋ 兩端彎矩 −35/32
鐵則：曲線、極值、極值位置都由下方函數算出；自我檢核含節點 B 平衡、B 點兩側轉角連續、
      C 點值 = 55/6144、AB 跨極值 = −5√3/9216（§3.1）。
"""
import sys, os, math
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2018-4"

# ── 幾何與勁度（題目正本判讀清單 #1、#6）──
EI = Fr(800)
LA = Fr(5)                  # AB、DE
LM = Fr(10)                 # BD（C 在中點）
LBR = Fr(5)                 # 斜撐 BF、DG 長 √(3²+4²)
XA, XB, XC, XD, XE = 0, 5, 10, 15, 20
STA = [("A", XA, "（滾）"), ("B", XB, "（接斜撐 BF）"), ("C", XC, "（所求點）"),
       ("D", XD, "（接斜撐 DG）"), ("E", XE, "（滾）")]

# ── §2 傾角變位法（對稱，θ_D = −θ_B）──
K_BA = 3 * EI / LA          # 480
K_BF = 4 * EI / LBR         # 640
K_BD = 2 * EI / LM          # 2EI/L(2θ_B + θ_D) = EI/5·θ_B = 160·θ_B
FEM = 1 * LM / 8            # 1.25
THETA_B = FEM / (K_BA + K_BF + K_BD)
M_BA = K_BA * THETA_B       # 15/32（AB 段 B 端負彎矩之大小）
M_BF = K_BF * THETA_B
M_BD = K_BD * THETA_B - FEM # −35/32
assert THETA_B == Fr(1, 1024) and M_BA == Fr(15, 32) and M_BD == Fr(-35, 32)
assert M_BA + M_BF + M_BD == 0                     # 節點 B 平衡


# ── §3 撓度曲線（向下為正，單位 m/kN）──
def v_end(x):               # AB 跨，x 自 A 起算；B 端彎矩 M = −15/32（正彎矩下緣受拉、向下撓為正）
    # 簡支梁一端彎矩 M：v = M·x(L² − x²)/(6EIL) ⇒ = x(x² − 25)/51200（§3.1 最終式）
    # 註：§3.1 中間式寫 x(x²−L²)M_B/(6EIL) 再代 M_B = −15/32，符號與最終式差一個負號；最終式正確
    return (-M_BA) * x * (LA ** 2 - x * x) / (6 * EI * LA)


def v_mid(s):               # BD 跨，s 自 B 起算
    s2 = s if s <= LM / 2 else LM - s
    point = s2 * (3 * LM ** 2 - 4 * s2 ** 2) / (48 * EI)
    moment = M_BD * s * (LM - s) / (2 * EI)
    return point + moment


def v(x):
    x = Fr(x)
    if x <= XB:
        return v_end(x)
    if x <= XD:
        return v_mid(x - XB)
    return v_end(XE - x)


def _selftest():
    assert v(XA) == v(XB) == v(XD) == v(XE) == 0
    VC = v(XC)
    assert VC == Fr(55, 6144)                           # §3.2
    for x in (Fr(1), Fr(2), Fr(3)):
        assert v(x) == x * (x * x - 25) / 51200          # §3.1 最終式
    h = Fr(1, 10 ** 6)                                   # B 點兩側斜率一致（= θ_B）
    sl = (v(XB) - v(XB - h)) / h
    sr = (v(XB + h) - v(XB)) / h
    assert abs(float(sl) - float(THETA_B)) < 1e-8 and abs(float(sr) - float(THETA_B)) < 1e-8
    for i in range(201):                                 # 對稱
        x = Fr(XE) * Fr(i, 200)
        assert v(x) == v(XE - x)


_selftest()

V_MAX = v(XC)
X_MIN = 5 / math.sqrt(3)                                 # v'(x) = 0 ⇒ 3x² = 25
V_MIN = -5 * math.sqrt(3) / 9216
assert abs(float(v_end(Fr(X_MIN).limit_denominator(10 ** 9))) - V_MIN) < 1e-12
assert max(float(v(Fr(XB) * Fr(i, 5000))) for i in range(5001)) <= 1e-15       # AB 跨全為負或 0
_grid = [Fr(XE) * Fr(i, 20000) for i in range(20001)]
assert abs(min(float(v(x)) for x in _grid) - V_MIN) < 1e-9                       # 全域最小值
assert max(float(v(x)) for x in _grid) == float(V_MAX)                           # 全域最大值在 C


# ══════════════════ 版面 ══════════════════
W, PADL, PADR = 1040, 90, 90
SX = (W - PADL - PADR) / XE
PH = 380


def fig2_influence_line():
    """攔：(1) 把 AB、DE 段畫成 0——B、D 雖無垂直位移，但梁跨越 B、D 連續且 B、D 會轉動，
    載重在外跨會把 C 抬起（負值）；(2) 漏掉斜撐的轉動勁度，把 BD 當成兩端簡支（C 值會算成 5/192）；
    (3) 把 B、D 當成會沉陷的點——斜撐不計軸向變形且對稱，B、D 縱距必為 0。"""
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=150)
    cv.panel("IL of v_{C}（C 點向下位移，向下為正）",
             "互惠定理：等於 C 點施加向下單位力時梁 A–E 的撓度曲線　│　縱距向上畫為正；單位 m/kN（EI = 800 kN·m²）")
    for nm, x, sup in STA:
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH - 34}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
        cv.text_px(p, PH - 18, nm + sup, 12.5, "#9AA4B2", weight="700")
    k = 13000.0 / SX                      # 1 m/kN → 13000 px
    xs = [XE * i / 1600 for i in range(1601)]
    pts = [(x, float(v(Fr(x).limit_denominator(10 ** 6))) * k) for x in xs]
    cv.polygon([(0.0, 0.0)] + pts + [(float(XE), 0.0)], C["fill_c"])
    cv.poly(pts, C["deform"], 2.4)
    cv.line((0, 0), (XE, 0), C["muted"], 1.6)
    col = C["deform"]
    cv.dot((XC, float(V_MAX) * k), 4.2, fill=col)
    cv.text_px(cv.X(XC), cv.Y(float(V_MAX) * k) - 30, f"+55/6144 ≈ +{float(V_MAX):.5f}", 13.5, col, weight="700")
    cv.text_px(cv.X(XC), cv.Y(float(V_MAX) * k) - 13, "全域最大（x = 10 m）", 12, C["muted"])
    for xm in (X_MIN, XE - X_MIN):
        cv.dot((xm, V_MIN * k), 4.0, fill=col)
        cv.text_px(cv.X(xm), cv.Y(V_MIN * k) + 22, f"−5√3/9216 ≈ {V_MIN:.6f}", 13, col, weight="700")
        cv.text_px(cv.X(xm), cv.Y(V_MIN * k) + 40, f"局部最小（x = {xm:.3f} m）", 12, C["muted"])
    for x in (XB, XD):
        cv.dot((x, 0.0), 4.0, fill=C["accent"])
        cv.text_px(cv.X(x), cv.Y(0) - 14, "0", 12.5, C["accent"], weight="700")
    cv.text_px(cv.X(XB) + 10, cv.Y(0) + 62, f"θ_{{B}} = 1/1024 rad（兩側切線連續）", 12, C["accent"], anchor="start")
    return compose([cv], note="外跨為負：C 受壓下沉時 B、D 轉動，把外跨梁往上翹；"
                              "B、D 由斜撐支住（不計軸向變形且對稱）而不沉陷，縱距為 0",
                   path=f"{OUT}/{TAG}-fig-2-influence-line.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_influence_line()
    print("寫出", f"{TAG}-fig-2-influence-line.svg")
    print(f"θ_B = {THETA_B}  M_BA = {M_BA}  M_BD = {M_BD}")
    print(f"v_C 最大 = {V_MAX} = {float(V_MAX):.6f} m/kN @ x = 10")
    print(f"局部最小 = {V_MIN:.6f} m/kN @ x = {X_MIN:.3f}、{XE - X_MIN:.3f}")
    for x in range(0, 21, 1):
        print(f"  x = {x:2d}   v = {float(v(x)):+.6f}")
