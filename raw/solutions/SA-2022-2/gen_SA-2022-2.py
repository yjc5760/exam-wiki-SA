#!/usr/bin/env python3
"""
SA-2022-2 階梯型有側移剛架 — 解題圖解產生腳本

用法：
    python3 gen_SA-2022-2.py [輸出目錄]

三條鐵則的落實：
  1. 所有彎矩、位移都由內建剛架有限元（figs/_lib/frame_fe.py）解出並 assert
     與手算值相符；圖上沒有手填的數字
  2. 改 L / P / EI 重跑，三張圖與所有數字會一起變
  3. 每張圖攔一種特定錯誤，見各 fig 的 docstring
"""
import sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose
from frame_fe import solve

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-2"

# ══════════════════════════════════════════════════════════
# 幾何與載重
# ══════════════════════════════════════════════════════════
L = 4.0
EI = 40000.0
P = 30.0
A_, B_, CC_ = (0.0, 0.0), (0.0, L / 2), (0.0, L)
D_, F_, E_ = (L, L), (L, 1.5 * L), (L, 2 * L)
K = EI / L                                    # 相對勁度 = 10000

# ── 有限元求解（EA 極大 ⇒ 不考慮軸向變形）─────────────────
_nodes = [A_, B_, CC_, (L / 2, L), D_, F_, E_]
iA, iB, iC, iG, iD, iF, iE = range(7)
_elems = [(iA, iB), (iB, iC), (iC, iG), (iG, iD), (iD, iF), (iF, iE)]
_u, _R, _M = solve(_nodes, _elems, {(iA, 0), (iA, 1), (iE, 0), (iE, 1)},
                   {(iB, 0): P, (iF, 0): P}, EI=EI)

D_C = _u[3 * iC] * 1000                       # mm
D_B = _u[3 * iB] * 1000
V_MID = _u[3 * iG + 1] * 1000                 # 梁中點相對弦的撓度（mm）
M_CD = _M[(iC, iG)][0]
M_DC = _M[(iG, iD)][1]
M_CA = _M[(iB, iC)][1]
M_DE = _M[(iD, iF)][0]
TH_C = -_u[3 * iC + 2] * K                    # K·θ_c（順時針為正）
TH_D = -_u[3 * iD + 2] * K

# ── 與手算對照 ─────────────────────────────────────────
assert abs(D_C - 23.0) < 1e-3, D_C
assert abs(D_B - 14.0) < 1e-3, D_B
assert abs(M_CD - 60.0) < 1e-3 and abs(M_DC + 60.0) < 1e-3
assert abs(M_CA + M_CD) < 1e-6 and abs(M_DC + M_DE) < 1e-6
assert abs(TH_C - 30.0) < 1e-3 and abs(TH_D + 30.0) < 1e-3
assert abs(_u[3 * iC] * K - 230.0) < 1e-2                          # KΔ = 230
assert V_MID < -1e-3, "梁中點必須相對弦「下」撓 ⇒ sagging ⇒ 下側受拉"

D_B_RIGID = D_C / 2                           # 弦的剛體位移
D_B_ELASTIC = D_B - D_B_RIGID                 # 桿件本身的彈性彎曲
assert abs(D_B_RIGID - 11.5) < 1e-3 and abs(D_B_ELASTIC - 2.5) < 1e-3

# 梁 cd 的彎矩：M_bend（下凹為正）＝ 起點 +M_cd、終點 −M_dc
BM_BEAM = M_CD
assert abs(BM_BEAM - (-M_DC)) < 1e-6, "定值彎矩 ⇒ 剪力為零"

# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 880
PADL, PADR = 260, 300
SX = (W - PADL - PADR) / L      # 80 px/m
Y_BASE = 132


def fcanvas(H, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=Y_BASE, bg=bg)


def draw_frame(cv, w=7.0, ghost=False):
    col = C["ghost"] if ghost else C["member"]
    for p, q in ((A_, CC_), (CC_, D_), (D_, E_)):
        cv.line(p, q, col, w, cap="butt")
    cv.pin_support(A_, size=16, color=col)
    cv.pin_support(E_, ang=180, size=16, color=col)


def node_labels(cv, ghost=False):
    col = C["ghost"] if ghost else C["text"]
    for p, nm, dx, dy in ((A_, "a", 20, 20), (B_, "b", 18, 8), (CC_, "c", -18, -12),
                          (D_, "d", 18, 22), (E_, "e", -18, 16)):
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, nm, 18, col,
                   weight="700", italic=True)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪。攔：把 e 當成柱底（它在柱頂）、以及漏看兩個 30 kN 都在桿件中點。"""
    H = 960
    cv = fcanvas(H, bg="#FFFFFF")
    cv.panel("題目重繪（考卷圖 2）",
             f"a、e 皆為鉸支承（a 在下方、e 在上方）　c、d 為剛節點　"
             f"各桿長 {L:g} m　EI = {EI:,.0f} kN·m²")
    draw_frame(cv)
    node_labels(cv)
    for p in (B_, F_):
        cv.arrow((p[0] - 1.30, p[1]), (p[0] - 0.07, p[1]), C["load"], 3.4, 12)
        cv.text_px(cv.X(p[0] - 1.36), cv.Y(p[1]), f"{P:g} kN", 15,
                   C["load"], "end", weight="700")
    for k in range(4):                       # 右側單一尺寸鏈，與考卷附圖一致
        cv.dim((L, L / 2 * k), (L, L / 2 * (k + 1)), f"{L / 2:g} m",
               off=96, label_off=15)
    cv.dim(CC_, D_, f"{L:g} m", off=52, label_off=14)
    cv.text_px(W / 2, H - 52,
               "不考慮軸向變形 ⇒ c、d 有相同的水平側移 Δ 且無垂直位移；"
               "未知數為 θ_{c}、θ_{d}、Δ 三個", 13.5, C["text"], weight="700")
    cv.text_px(W / 2, H - 24,
               "a 在柱底、e 在柱頂 ⇒ 兩根柱的弦轉角符號相反（ψ_{ac} = +Δ/4，"
               "ψ_{de} = −Δ/4）", 13.5, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_bmd():
    """cd 梁的彎矩圖。攔的就是本題原解析唯一的錯：把定值 60 kN·m 說成
    「梁上方受拉」而畫在上側 —— 實際是 sagging、下側受拉。"""
    H = 900
    amp = 9.0                                  # 變形放大倍率
    cv = fcanvas(H)
    cv.panel("cd 梁的彎矩圖：定值 60 kN·m，畫在下側（下側受拉）",
             f"M_{{cd}} = {M_CD:+.0f}　M_{{dc}} = {M_DC:+.0f}　⇒　兩端大小相等方向相反"
             f"　⇒　剪力為零、全梁彎矩為定值")
    draw_frame(cv, w=4.5, ghost=True)
    # 變形形狀（有限元節點位移，放大）
    pts = [(x + _u[3 * i] * amp, y + _u[3 * i + 1] * amp)
           for i, (x, y) in enumerate(_nodes)]
    cv.poly([pts[iA], pts[iB], pts[iC]], C["deform"], 4.4)
    cv.poly([pts[iC], pts[iG], pts[iD]], C["deform"], 4.4)
    cv.poly([pts[iD], pts[iF], pts[iE]], C["deform"], 4.4)
    # 梁的彎矩圖：定值，畫在下側
    k = 0.0075
    cv.polygon([CC_, (CC_[0], CC_[1] - BM_BEAM * k),
                (D_[0], D_[1] - BM_BEAM * k), D_], C["fill_m"], C["bmd"], 2.6)
    cv.text_px(cv.X(L / 2), cv.Y(L - BM_BEAM * k) + 24,
               f"{BM_BEAM:+.0f} kN·m（定值，下側受拉）", 15, C["bmd"], weight="700")
    cv.dot((L / 2, L + V_MID / 1000 * amp), 5.0, fill=C["deform"])
    cv.text_px(cv.X(L / 2), cv.Y(L) - 34,
               f"梁中點相對弦下撓 {abs(V_MID):.0f} mm ⇒ 下凹 ⇒ sagging", 13,
               C["deform"], weight="700")
    node_labels(cv, ghost=True)
    cv.text_px(W / 2, H - 78,
               f"K·θ_{{c}} = {TH_C:+.0f}　K·θ_{{d}} = {TH_D:+.0f}　K·Δ = "
               f"{D_C / 1000 * K:.0f}　（K = EI/L = {K:,.0f}）", 14, C["text"],
               weight="700")
    cv.text_px(W / 2, H - 50,
               f"Δ_{{c}} = Δ_{{d}} = {D_C:.0f} mm（向右）", 14.5, C["accent"],
               weight="700")
    cv.text_px(W / 2, H - 22,
               "把彎矩圖畫在梁的上側是最常見的錯：兩端彎矩雖為「一順一逆」，"
               "梁中點卻是往下撓的", 13, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-bmd.svg")


def fig3_delta_b():
    """b 點位移的疊加分解。攔：直接把 b 點位移當成頂端的一半。"""
    Wp, Hp = 470, 600
    sxx = 96.0

    def col(title, sub, kind):
        cv = Canvas(Wp, Hp, sx=sxx, ox=Wp / 2 - 40, oy=110)
        cv.panel(title, sub)
        cv.line((0, 0), (0, L), C["ghost"], 4.0, cap="butt")
        cv.pin_support((0, 0), size=15, color=C["ghost"])
        amp = 26.0
        n = 40
        pts = []
        for i in range(n + 1):
            y = L * i / n
            if kind == "rigid":
                d = D_C / 1000 * (y / L)
            elif kind == "elastic":
                d = (_u_col(y) - D_C / 1000 * (y / L))
            else:
                d = _u_col(y)
            pts.append((d * amp, y))
        cv.poly(pts, C["deform"] if kind != "elastic" else C["bmd"], 5.0)
        yb = L / 2
        db = {"rigid": D_B_RIGID, "elastic": D_B_ELASTIC, "total": D_B}[kind]
        cv.dot((db / 1000 * amp, yb), 5.4,
               fill=C["deform"] if kind != "elastic" else C["bmd"])
        cv.text_px(cv.X(db / 1000 * amp) + 14, cv.Y(yb),
                   f"{db:.1f} mm", 15,
                   C["deform"] if kind != "elastic" else C["bmd"], "start",
                   weight="700")
        cv.text_px(cv.X(0) - 14, cv.Y(yb), "b", 17, C["ghost"], "end",
                   weight="700", italic=True)
        return cv

    c1 = col("① 弦的剛體位移", f"c 點右移 {D_C:.0f} mm，b 在中點 ⇒ 線性內插", "rigid")
    c2 = col("② 桿件相對弦的彈性彎曲", "30 kN 直接作用在 b 上，柱自己也會彎", "elastic")
    c3 = col("③ 疊加＝真實位移", "傾角變位法只給節點位移，中間點要自己補", "total")
    return compose([c1, c2, c3], cols=3,
                   note=f"Δ_{{b}} = {D_B_RIGID:.1f} + {D_B_ELASTIC:.1f} = "
                        f"{D_B:.1f} mm（向右）　—— 只取一半（{D_B_RIGID:.1f} mm）"
                        f"會少了 {D_B_ELASTIC / D_B * 100:.0f}%",
                   path=f"{OUT}/{TAG}-fig-3-delta-b.svg")


def _u_col(y):
    """下柱 a–c 在高度 y 的水平位移（由三個有限元節點做三次 Hermite 內插）。"""
    import bisect
    ys = [0.0, L / 2, L]
    us = [_u[3 * iA], _u[3 * iB], _u[3 * iC]]
    ts = [-_u[3 * iA + 2], -_u[3 * iB + 2], -_u[3 * iC + 2]]
    j = min(bisect.bisect_right(ys, y) - 1, 1)
    h = ys[j + 1] - ys[j]
    t = (y - ys[j]) / h
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1
    h10 = t ** 3 - 2 * t ** 2 + t
    h01 = -2 * t ** 3 + 3 * t ** 2
    h11 = t ** 3 - t ** 2
    return h00 * us[j] + h10 * h * ts[j] + h01 * us[j + 1] + h11 * h * ts[j + 1]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_frame, fig2_bmd, fig3_delta_b):
        f(); print("寫出", f.__name__)
    print(f"\nΔ_c = {D_C:.4f} mm   Δ_b = {D_B:.4f} mm "
          f"（剛體 {D_B_RIGID:.2f} + 彈性 {D_B_ELASTIC:.2f}）")
    print(f"M_cd = {M_CD:+.4f}   M_dc = {M_DC:+.4f}   ⇒ 全梁定值 {BM_BEAM:+.0f} kN·m")
    print(f"梁中點相對弦的撓度 = {V_MID:+.4f} mm  ⇒ "
          f"{'下撓 ⇒ sagging ⇒ 下側受拉' if V_MID < 0 else '上撓'}")
    print(f"K·θ_c = {TH_C:+.2f}   K·θ_d = {TH_D:+.2f}   K·Δ = {D_C / 1000 * K:.2f}")
