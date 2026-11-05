#!/usr/bin/env python3
"""SA-2024-4 解題圖解（struct-diagram；2026-11-05 階段 E）
  圖 3  P−Δ 側推曲線（左）＋各事件的塑鉸位置（右）。
  攔：只畫彈性直線就停（沒走到極限承載力）、把節點塑鉸放在柱頂（柱頂受梁端 300 限制，到不了 580）、
      第二段仍用彈性勁度、柱底彎矩從 0 重算而不是 400 + 增量。
所有數值由本腳本以 3×3 結構勁度矩陣逐階段解出（事件到事件），再與解析 §4 Step 2–6 的值 assert。
用法：python3 gen_SA-2024-4_pushover.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2024-4"

# ── 題目正本：EI = 425,000 kN-m²、L = 7 m；柱 2EI、高 2L；梁 EI、長 L；Mpb = 300、Mpc = 580 kN-m ──
EI, L, MPB, MPC = 425000.0, 7.0, 300.0, 580.0
u = EI / L**3


def solve3(K, b):
    """3×3 線性方程（Cramer），不依賴 numpy，好在任何電腦重跑"""
    def det(M):
        return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
                + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
    d = det(K); out = []
    for i in range(3):
        Mi = [row[:] for row in K]
        for r in range(3): Mi[r][i] = b[r]
        out.append(det(Mi) / d)
    return out


def stage(beam_hinged):
    """回傳單位 P 下：Δ、θ、梁端／柱頂／柱底彎矩增量。自由度 Δ（右）、θ_B、θ_C（逆時針）。"""
    kb4, kb2 = (0.0, 0.0) if beam_hinged else (4*EI/L, 2*EI/L)
    K = [[6*u, 3*u*L, 3*u*L],
         [3*u*L, 4*EI/L + kb4, kb2],
         [3*u*L, kb2, 4*EI/L + kb4]]
    D, tB, tC = solve3(K, [1.0, 0.0, 0.0])
    m_beam = 0.0 if beam_hinged else abs(kb4*tB + kb2*tC)
    m_top = 4*EI/L*tB + 3*EI/L**2*D
    m_base = 2*EI/L*tB + 3*EI/L**2*D
    return dict(K=1/D, D=D, th=tB, beam=m_beam, top=m_top, base=m_base)


s1 = stage(False)
P1 = min(MPB / s1["beam"], MPC / s1["base"], MPC / s1["top"])
assert abs(P1 - MPB / s1["beam"]) < 1e-9, "梁端先降伏"
D1 = P1 * s1["D"]; base1 = P1 * s1["base"]; top1 = P1 * s1["top"]
s2 = stage(True)
assert abs(s2["top"]) < 1e-9, "梁端塑鉸後柱頂彎矩不再增加"
dP2 = (MPC - base1) / s2["base"]
P2 = P1 + dP2; D2 = D1 + dP2 * s2["D"]
PU_MECH = (2*MPC + 2*MPB) / (2*L)
DMAX = 45.0                                      # 圖上平台畫到 45 mm

# ── 與解析 §4 對照 ──
for got, exp, tol in ((s1["K"], 5204.1, 0.05), (P1, 100.0, 1e-9), (D1*1000, 19.22, 0.005),
                      (base1, 400.0, 1e-6), (top1, 300.0, 1e-6), (s2["K"], 1858.6, 0.05),
                      (s2["base"], 7.0, 1e-9), (dP2, 25.71, 0.005), (P2, 125.71, 0.005),
                      (D2*1000, 33.05, 0.005), (PU_MECH, P2, 1e-9)):
    assert abs(got - exp) <= tol, (got, exp)

PTS = [(0.0, 0.0), (D1*1000, P1), (D2*1000, P2)]
YK = 0.30                                        # 圖上 1 kN 對應的模型長度（以 mm 為 x 單位）


def chart():
    W, H = 680, 640
    Lm, Rm, Tm, Bm = 86, 40, 92, 74
    xr, yr = (0.0, DMAX), (0.0, 145 * YK)
    sx = min((W - Lm - Rm) / (xr[1] - xr[0]), (H - Tm - Bm) / (yr[1] - yr[0]))
    cv = Canvas(W, H, sx=sx, ox=Lm, oy=Bm)
    cv.panel("P−Δ 側推曲線（結構勁度矩陣法，逐次形成塑鉸）", "Δ 為 B 點（受力點）水平位移；三段折線，最後一段勁度為 0")
    for x in range(0, int(DMAX) + 1, 5):
        cv.line((x, 0), (x, 140 * YK), C["border"], 1.0)
        cv.text_px(cv.X(x), cv.Y(0) + 18, f"{x}", 12, C["muted"])
    for p in range(0, 141, 20):
        cv.line((0, p * YK), (DMAX, p * YK), C["border"], 1.0)
        cv.text_px(cv.X(0) - 10, cv.Y(p * YK), f"{p}", 12, C["muted"], "end")
    cv.line((0, 0), (DMAX, 0), C["muted"], 1.8); cv.line((0, 0), (0, 140 * YK), C["muted"], 1.8)
    cv.text_px(cv.X(DMAX / 2), H - 30, "Δ（mm）", 13.5, C["muted"])
    cv.text_px(28, cv.Y(70 * YK), "P（kN）", 13.5, C["muted"])
    # 機構法水平線
    cv.line((0, PU_MECH * YK), (DMAX, PU_MECH * YK), C["accent"], 1.4, dash="6 5")
    cv.text_px(cv.X(1.0), cv.Y(PU_MECH * YK) + 16, f"機構法 P_u = (2×580 + 2×300)/14 = {PU_MECH:.2f} kN", 12.5, C["accent"], "start", weight="700")
    # 曲線
    pts = [(d, p * YK) for d, p in PTS] + [(DMAX, P2 * YK)]
    cv.poly(pts[:3], C["deform"], 4.0)
    cv.line(pts[2], pts[3], C["deform"], 4.0, dash="10 6")
    for (d, p), t, dx, dy, anc in ((PTS[1], f"① ({D1*1000:.2f} mm, {P1:.0f} kN) 梁端塑鉸", 10, 22, "start"),
                                   (PTS[2], f"② ({D2*1000:.2f} mm, {P2:.2f} kN) 柱底塑鉸", -10, -18, "end")):
        cv.dot((d, p * YK), 6.0, fill="#FFFFFF", stroke=C["load"], w=2.8)
        cv.text_px(cv.X(d) + dx, cv.Y(p * YK) + dy, t, 13, C["load"], anc, weight="700")
    # 斜率標註（放在各段中點旁）
    m1 = (PTS[1][0] / 2, PTS[1][1] / 2 * YK)
    cv.text_px(cv.X(m1[0]) + 12, cv.Y(m1[1]) + 6, f"K_{1} = {s1['K']:.1f} kN/m（彈性）", 12.5, C["deform"], "start", weight="700")
    m2 = ((PTS[1][0] + PTS[2][0]) / 2, (PTS[1][1] + PTS[2][1]) / 2 * YK)
    cv.text_px(cv.X(m2[0]) + 14, cv.Y(m2[1]) + 30, f"K_{2} = {s2['K']:.1f} kN/m", 12.5, C["deform"], "start", weight="700")
    cv.text_px(cv.X((D2 * 1000 + DMAX) / 2), cv.Y(P2 * YK) + 22, "K_{3} = 0 側移機構", 12.5, C["deform"], weight="700")
    return cv


def hinge(cv, p):
    cv.dot(p, 6.0, fill="#FFFFFF", stroke=C["load"], w=2.6)


def events():
    W, H = 680, 640
    sx = 50.0
    cv = Canvas(W, H, sx=sx, ox=70, oy=0)
    cv.panel("各事件的塑鉸位置", "節點 B、C 只連兩桿：梁端 300 小於柱 580，塑鉸出現在梁端")
    rows = [(f"① P = {P1:.0f} kN", [f"梁端 B、C 達 Mpb = {MPB:.0f}（形成塑鉸）", f"此時柱底 {base1:.0f}、柱頂 {top1:.0f}"], "beam"),
            (f"② P = {P2:.2f} kN", [f"柱底 A、D 達 Mpc = {MPC:.0f}", f"（{base1:.0f} + {s2['base']:.0f} × {dP2:.2f}）；柱頂停在 {MPB:.0f}"], "base"),
            ("③ 機構", ["梁端 2 ＋ 柱底 2 個塑鉸 → 側移機構", f"P_u = {P2:.2f} kN，勁度為 0"], "mech")]
    for i, (t1, t2, kind) in enumerate(rows):
        y0 = (H - 140 - i * 172) / sx - 2.0       # 每列柱底高程（模型單位）
        sway = 0.32 if kind == "mech" else 0.0
        A, D = (0.0, y0), (1.0, y0)
        B, Cc = (sway, y0 + 2.0), (1.0 + sway, y0 + 2.0)
        if kind == "mech":
            for p, q in (((0, y0), (0, y0 + 2)), ((1, y0), (1, y0 + 2)), ((0, y0 + 2), (1, y0 + 2))):
                cv.line(p, q, C["ghost"], 2.4, dash="5 4")
        for p, q in ((A, B), (B, Cc), (D, Cc)):
            cv.line(p, q, C["member"], 4.0, cap="butt")
        cv.support(A, "fixed", size=14); cv.support(D, "fixed", size=14)
        cv.arrow((B[0] - 0.55, B[1]), (B[0] - 0.04, B[1]), C["load"], 2.6, 9)
        cv.math(((B[0] - 0.62), B[1] + 0.02), "P", 13, C["load"], "end", weight="700")
        beam_h = [(B[0] + 0.13, B[1]), (Cc[0] - 0.13, Cc[1])]
        base_h = [(0.0, y0 + 0.16), (1.0, y0 + 0.16)]
        for p in beam_h: hinge(cv, p)
        if kind in ("base", "mech"):
            for p in base_h: hinge(cv, p)
        cv.text_px(cv.X(1.6), cv.Y(y0 + 1.45), t1, 14, C["text"], "start", weight="700")
        for j, line in enumerate(t2):
            cv.text_px(cv.X(1.6), cv.Y(y0 + 1.45) + 26 + 22 * j, line, 12.5, C["muted"], "start")
    cv.text_px(W / 2, H - 22, "○ 塑鉸（彎矩維持 Mp，轉角不再受束制）", 12.5, C["load"])
    return cv


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    compose([chart(), events()], cols=2, path=f"{OUT}/{TAG}-fig-3-pushover.svg")
    print(f"K1 = {s1['K']:.1f} kN/m, P1 = {P1:.2f} kN, Δ1 = {D1*1000:.2f} mm；K2 = {s2['K']:.1f} kN/m, "
          f"P2 = {P2:.2f} kN, Δ2 = {D2*1000:.2f} mm；機構法 {PU_MECH:.2f} kN")
