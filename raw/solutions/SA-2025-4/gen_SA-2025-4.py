#!/usr/bin/env python3
"""
SA-2025-4 格床（Grid）結構之矩陣位移法 — 解題圖解產生腳本

用法：
    python3 gen_SA-2025-4.py [輸出目錄]

幾何與 SA-2025-4.md §4 Step 1 一致（亦與考卷附圖相符）：
    b = (0, 0, 0)　a = (L, 0, 0)　c = (0, L, 0)　d = (L, L, 0)
    ab 沿 x、bc 沿 y、cd 沿 x；a、d 為固定端；ω 沿 −z 作用於 bc。
    d–a 之間沒有桿件（附圖為細線，僅示意平面）。

三條鐵則的落實：
  1. 圖上的符號式全部來自 .md §4；下方以一組具體數值把每條式子驗算一遍
  2. 改 PROJ 投影向量或 L 重跑，三張立體圖的幾何會一起變
  3. fig-4 用「等效懸臂梁」這條完全獨立的路徑重算 w_b、θ_yb、M_ya 並 assert
"""
import sys, os, math

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose, hermite

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-4"

# ══════════════════════════════════════════════════════════
# 幾何與投影
# ══════════════════════════════════════════════════════════
L = 1.0
EX, EY, EZ = (1.00, -0.34), (0.62, 0.52), (0.00, 1.00)      # 軸測投影基底


def P3(x, y, z=0.0):
    return (x * EX[0] + y * EY[0] + z * EZ[0],
            x * EX[1] + y * EY[1] + z * EZ[1])


NODE = {"b": (0, 0, 0), "a": (L, 0, 0), "c": (0, L, 0), "d": (L, L, 0)}
MEMBERS = [("a", "b"), ("b", "c"), ("c", "d")]

# 桿件在投影平面上的方向角（用於擺固定端符號）
_ang_x = math.degrees(math.atan2(EX[1], EX[0]))              # ab、cd 的方向
SUP_ANG = _ang_x + 90.0                                       # 支承面與桿軸垂直


# ══════════════════════════════════════════════════════════
# .md §4 的公式，用一組具體數值驗算（符號式本身列在圖上）
# ══════════════════════════════════════════════════════════
def verify(E=200e6, G=77e6, I=1.2e-4, Lv=3.0, w=12.0):
    J = 2 * I                                    # 實心圓桿：J = Ix + Iy = 2I
    P_zb = w * Lv / 2
    P_mxb = w * Lv ** 2 / 12

    # ΣMx：ab 桿扭轉 GJ/L ＋ bc 桿彎曲（θxc = −θxb ⇒ 4EI/L − 2EI/L）
    th_xb = P_mxb / (G * J / Lv + 2 * E * I / Lv)
    assert abs(th_xb - w * Lv ** 3 / (24 * I * (E + G))) < 1e-15 * abs(th_xb) + 1e-18

    # ΣMy：bc 桿因 θyb = θyc 無相對扭轉 ⇒ 只剩 ab 桿的彎曲
    #      4EI/L·θyb − 6EI/L²·w_b = 0
    # ΣFz：12EI/L³·w_b − 6EI/L²·θyb = P_zb
    #      代入 θyb = 3w_b/(2L) ⇒ (12 − 9)EI/L³·w_b = P_zb
    w_b = P_zb / (3 * E * I / Lv ** 3)
    th_yb = 1.5 * w_b / Lv
    assert abs(w_b - w * Lv ** 4 / (6 * E * I)) < 1e-9 * w_b
    assert abs(th_yb - w * Lv ** 3 / (4 * E * I)) < 1e-9 * th_yb
    assert abs(12 * E * I / Lv ** 3 * w_b - 6 * E * I / Lv ** 2 * th_yb - P_zb) < 1e-6

    # 支承反力
    M_xa = G * J / Lv * th_xb
    M_ya = 6 * E * I / Lv ** 2 * w_b - 2 * E * I / Lv * th_yb
    assert abs(M_xa - w * Lv ** 2 * G / (12 * (E + G))) < 1e-9 * M_xa
    assert abs(M_ya - w * Lv ** 2 / 2) < 1e-9 * M_ya

    # ── 獨立路徑：ab 桿視為自由端受 P = ωL/2 的懸臂梁 ──
    P = w * Lv / 2
    assert abs(P * Lv ** 3 / (3 * E * I) - w_b) < 1e-9 * w_b          # 撓度
    assert abs(P * Lv ** 2 / (2 * E * I) - th_yb) < 1e-9 * th_yb      # 端點轉角
    assert abs(P * Lv - M_ya) < 1e-9 * M_ya                           # 根部彎矩
    return dict(J=J, P_zb=P_zb, P_mxb=P_mxb, th_xb=th_xb, w_b=w_b,
                th_yb=th_yb, M_xa=M_xa, M_ya=M_ya, P=P, E=E, G=G, I=I, L=Lv, w=w)


V = verify()

# 圖上使用的符號式（與 .md §4 一字不差）
SYM = {
    "P_zb":  "P_{zb} = ωL/2",
    "P_mxb": "P_{mxb} = ωL^{2}/12",
    "th_xb": "θ_{xb} = ωL^{3}/[24I(E+G)]",
    "w_b":   "w_{b} = ωL^{4}/(6EI)",
    "th_yb": "θ_{yb} = ωL^{3}/(4EI)",
    "M_xa":  "M_{xa} = ωL^{2}G/[12(E+G)]",
    "M_ya":  "M_{ya} = ωL^{2}/2",
    "R_za":  "R_{za} = ωL/2",
}


# ══════════════════════════════════════════════════════════
# 立體圖元
# ══════════════════════════════════════════════════════════
def grid(cv, w=7.0, color=C["member"], nodes=True, closing=True):
    if closing:                                   # d–a 無桿件，附圖以細線示意
        cv.line(P3(*NODE["d"]), P3(*NODE["a"]), C["ghost"], 1.4, dash="6 5")
    for s, e in MEMBERS:
        cv.line(P3(*NODE[s]), P3(*NODE[e]), color, w, cap="butt")
    if nodes:
        for nm, p in NODE.items():
            cv.dot(P3(*p), 5.6)


def node_labels(cv, size=17, off=((-20, 20), (18, 24), (18, -16), (22, -14))):
    for (nm, p), (dx, dy) in zip((("b", NODE["b"]), ("a", NODE["a"]),
                                  ("c", NODE["c"]), ("d", NODE["d"])), off):
        cv.math(P3(*p), nm, size, C["text"], weight="700", dx=dx, dy=dy)


def triad(cv, origin=(-0.55, 0.0, -0.537), ln=0.36, color=C["muted"]):
    """座標三向量（畫在空白處，避免壓到桿件）"""
    ox, oy, oz = origin
    for d, lab, dx, dy in (((1, 0, 0), "x", 8, 8), ((0, 1, 0), "y", 8, 4),
                           ((0, 0, 1), "z", 2, -14)):
        tip = P3(ox + d[0] * ln, oy + d[1] * ln, oz + d[2] * ln)
        cv.arrow(P3(ox, oy, oz), tip, color, 1.8, 9)
        cv.math(tip, lab, 14, color, "start", dx=dx, dy=dy)
    cv.text_px(cv.X(P3(ox, oy, oz)[0]), cv.Y(P3(ox, oy, oz)[1]) + 22,
               "座標方向", 11.5, color)


def moment_vec(cv, p3, d3, ln, color, label=None, ldx=0, ldy=0):
    """右手定則的力矩／轉角向量：同一方向畫兩個箭頭（雙箭頭 = 力矩）"""
    p0 = P3(*p3)
    tip = P3(p3[0] + d3[0] * ln, p3[1] + d3[1] * ln, p3[2] + d3[2] * ln)
    mid = P3(p3[0] + d3[0] * ln * 0.78, p3[1] + d3[1] * ln * 0.78,
             p3[2] + d3[2] * ln * 0.78)
    cv.arrow(p0, tip, color, 2.8, 10)
    cv.arrow(p0, mid, color, 2.8, 10)
    if label:
        cv.math_px(cv.X(tip[0]) + ldx, cv.Y(tip[1]) + ldy, label, 14.5, color,
                   "middle", weight="700")


def udl_bc(cv, h=0.30, n=8, color=C["load"], label=True):
    """bc 桿上的 −z 向均布載重"""
    for i in range(n + 1):
        t = i / n
        base = (0.0, t * L, 0.0)
        cv.arrow(P3(base[0], base[1], h), P3(*base), color, 2.0, 8)
    cv.line(P3(0, 0, h), P3(0, L, h), color, 2.0)
    if label:
        cv.math(P3(0, L * 0.5, h), "ω", 19, color, dx=-24, dy=-8, weight="700")


# ══════════════════════════════════════════════════════════
def fig1_grid():
    """題目重繪：把桿件方向與座標軸的對應一次釘死"""
    W, H = 1000, 590
    cv = Canvas(W, H, sx=286, ox=286, oy=252, bg="#FFFFFF")
    grid(cv)
    udl_bc(cv)
    for nd in ("a", "d"):
        cv.fixed_support(P3(*NODE[nd]), ang=SUP_ANG, size=24)
    node_labels(cv)
    triad(cv)

    for (s_, e_), (dx, dy) in zip(MEMBERS, ((0, 32), (36, 26), (16, 28))):
        ps, pe = P3(*NODE[s_]), P3(*NODE[e_])
        cv.math(((ps[0] + pe[0]) / 2, (ps[1] + pe[1]) / 2), "L", 17, C["muted"],
                dx=dx, dy=dy)

    cv.rect_px(W - 322, 68, 300, 128, "#F5F7FA", 12, C["border"], 1.2)
    cv.text_px(W - 302, 92, "三根桿件皆為長度 L 的實心圓桿", 13, C["text"], "start",
               weight="700")
    cv.math_px(W - 302, 118, "J = I_{x} + I_{y} = 2I", 16, C["accent"], "start",
               weight="700")
    cv.text_px(W - 302, 142, "（實心圓斷面的極慣性矩）", 12, C["muted"], "start")
    cv.text_px(W - 302, 168, "a、d 為固定端；b、c 為剛接", 12.5, C["muted"], "start")
    cv.text_px(W - 302, 188, "d–a 之間沒有桿件（細虛線僅示意平面）", 12, C["muted"], "start")

    cv.text_px(W / 2, H - 46,
               "載重在 −z 向、結構在 xy 平面 ⇒ 每個節點的三個自由度是 "
               "w（z 向位移）、θx、θy（繞 x、y 的轉角）", 13.5, C["muted"])
    cv.text_px(W / 2, H - 22,
               "ab 沿 x ⇒ 繞 x 的作用對它是「扭轉」、繞 y 的是「彎曲」；bc 沿 y 則相反",
               13.5, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-grid.svg")


# ══════════════════════════════════════════════════════════
def _dof_panel(title, sub, mode):
    PW, PH = 700, 520
    cv = Canvas(PW, PH, sx=250, ox=176, oy=150)
    cv.panel(title, sub)
    grid(cv, w=5.4, color="#9AA4B2")
    node_labels(cv, 15, ((-16, 20), (18, 18), (22, 6), (-6, -18)))

    if mode == "full":
        for nd in ("b", "c"):
            p = NODE[nd]
            cv.arrow(P3(*p), P3(p[0], p[1], -0.30), C["deform"], 2.8, 10)
            cv.math(P3(p[0], p[1], -0.30), f"w_{{{nd}}}", 14.5, C["deform"],
                    dx=-18, dy=12, weight="700")
            moment_vec(cv, p, (1, 0, 0), 0.34, C["accent"], f"θ_{{x{nd}}}", 14, -12)
            moment_vec(cv, p, (0, 1, 0), 0.34, C["bmd"], f"θ_{{y{nd}}}", 16, -10)
        cv.rect_px(PW - 250, 70, 230, 92, "#EEF4FF", 12, "#C7D9F5", 1.3)
        cv.text_px(PW - 135, 96, "活動節點 2 個 × 每點 3 個", 12.5, "#1D4ED8",
                   weight="700")
        cv.text_px(PW - 135, 122, "⇒ 整體勁度矩陣 6 × 6", 15, "#1D4ED8", weight="700")
        cv.text_px(PW - 135, 146, "考場手算幾乎必錯", 12, "#1D4ED8")
    else:
        # 對稱面 y = L/2
        mid = (0.0, L / 2, 0.0)
        cv.line(P3(-0.42, L / 2, 0), P3(1.32, L / 2, 0), C["accent"], 1.8, dash="7 5")
        cv.math(P3(1.32, L / 2, 0), "對稱面 y = L/2", 13, C["accent"], "start",
                dx=8, dy=-12, weight="700")
        for nd, s in (("b", +1), ("c", +1)):
            p = NODE[nd]
            cv.arrow(P3(*p), P3(p[0], p[1], -0.30), C["deform"], 2.8, 10)
        for nd, sx_ in (("b", +1), ("c", -1)):
            moment_vec(cv, NODE[nd], (sx_, 0, 0), 0.32, C["accent"])
        for nd in ("b", "c"):
            moment_vec(cv, NODE[nd], (0, 1, 0), 0.32, C["bmd"])
        cv.rect_px(PW - 262, 70, 242, 150, "#FFF6F1", 12, "#F0C9B8", 1.3)
        cv.text_px(PW - 141, 94, "幾何與載重對稱 ⇒", 12.5, "#9A3412", weight="700")
        for i, t in enumerate(("w_{b} = w_{c}",
                               "θ_{xb} = −θ_{xc}　（反對稱）",
                               "θ_{yb} = θ_{yc}　（對稱）")):
            cv.math_px(PW - 141, 122 + i * 26, t, 14.5, "#9A3412", weight="700")
        cv.text_px(PW - 141, 204, "⇒ 獨立未知數只剩 3 個", 13, "#9A3412", weight="700")
        cv.math_px(PW / 2 - 108, PH - 46, "θ_{yb} = θ_{yc}", 15, C["bmd"],
                   "middle", weight="700")
        cv.text_px(PW / 2 + 26, PH - 46, "⇒ bc 桿沿自身軸線無相對扭轉", 13.5,
                   C["bmd"], "middle", weight="700")
        cv.text_px(PW / 2, PH - 22, "這一條就是後面「bc 桿不提供扭矩」的來源", 12.5,
                   C["muted"])
    return cv


def fig2_dof_symmetry():
    """自由度與對稱性：6×6 縮到 3 個未知數的依據"""
    compose([_dof_panel("① 完整自由度：b、c 各 3 個", "w、θx、θy（雙箭頭＝力矩／轉角向量，右手定則）",
                        "full"),
             _dof_panel("② 用對稱性降階", "對稱面 y = L/2；θx 反對稱、w 與 θy 對稱",
                        "sym")],
            title="先數自由度、再用對稱性降階——這一步錯，後面整個矩陣都白算",
            sub="藍＝z 向位移 w　橙＝繞 x 轉角 θx　綠＝繞 y 轉角 θy",
            note="θx 在對稱面兩側反向（反對稱），w 與 θy 同向（對稱）。"
                 "把這三條關係寫錯號，bc 桿的貢獻就會從 2EI/L 變成 6EI/L。",
            path=f"{OUT}/{TAG}-fig-2-dof-symmetry.svg")
    return f"{OUT}/{TAG}-fig-2-dof-symmetry.svg"


# ══════════════════════════════════════════════════════════
def _eq_panel(title, sub, ab_role, bc_role, lines, result, hi=None):
    PW, PH = 640, 520
    cv = Canvas(PW, PH, sx=190, ox=150, oy=286)
    cv.panel(title, sub)
    # 只畫節點 b 附近的兩根桿
    cv.line(P3(0, 0, 0), P3(0.72, 0, 0), C["member"], 6.5, cap="butt")
    cv.line(P3(0, 0, 0), P3(0, 0.72, 0), C["member"], 6.5, cap="butt")
    cv.line(P3(0.72, 0, 0), P3(0.92, 0, 0), C["ghost"], 3.0, dash="5 4")
    cv.line(P3(0, 0.72, 0), P3(0, 0.92, 0), C["ghost"], 3.0, dash="5 4")
    cv.dot(P3(0, 0, 0), 6.2)
    cv.math(P3(0, 0, 0), "b", 16, C["text"], weight="700", dx=-16, dy=20)
    cv.math(P3(0.92, 0, 0), "→ a", 13, C["muted"], "start", dx=6, dy=8)
    cv.math(P3(0, 0.92, 0), "→ c", 13, C["muted"], "start", dx=6, dy=-6)

    for j, (txt, col) in enumerate((ab_role, bc_role)):
        yy = 104 + j * 62
        cv.rect_px(296, yy, 322, 50, "#FFFFFF", 9, col, 1.4)
        cv.text_px(310, yy + 25, txt, 12.5, col, "start", weight="700")

    for i, (txt, col) in enumerate(lines):
        cv.math_px(30, PH - 152 + i * 27, txt, 14.5, col, "start", weight="700")
    cv.math_px(PW / 2, PH - 44, result, 17, C["accent"], weight="700")
    if hi:
        cv.rect_px(296, 232, 322, 48, "#FFF6F1", 10, "#F0C9B8", 1.3)
        cv.math_px(457, 256, hi, 16, "#9A3412", weight="700")
    return cv


def fig3_node_b():
    """節點 b 的三條平衡方程：哪根桿貢獻什麼，一眼看出來"""
    p1 = _eq_panel(
        "① ΣM_x 平衡（繞 x 軸）", "ab 桿沿 x ⇒ 扭轉；bc 桿垂直於 x ⇒ 彎曲",
        ("ab：扭轉　GJ/L = 2GI/L", C["accent"]),
        ("bc：彎曲　4EI/L·θxb + 2EI/L·θxc", C["bmd"]),
        [("θ_{xc} = −θ_{xb}　⇒　(4−2)EI/L = 2EI/L", C["bmd"]),
         ("(2GI/L + 2EI/L)·θ_{xb} = " + SYM["P_mxb"], C["text"])],
        SYM["th_xb"], "J = 2I")
    p2 = _eq_panel(
        "② ΣM_y 平衡（繞 y 軸）", "bc 桿沿 y ⇒ 扭轉；但 θyb = θyc ⇒ 無相對扭轉",
        ("ab：彎曲　4EI/L·θyb − 6EI/L²·w_b", C["bmd"]),
        ("bc：扭矩 = 0（θyb = θyc ⇒ 無相對扭轉）", C["muted"]),
        [("4EI/L·θ_{yb} − 6EI/L^{2}·w_{b} = 0", C["text"]),
         ("⇒ θ_{yb} = 3w_{b}/(2L)", C["bmd"])],
        SYM["th_yb"], None)
    p3 = _eq_panel(
        "③ ΣF_z 平衡（z 向）", "ab 桿提供剪力勁度；bc 的剪力由對稱性抵銷",
        ("ab：剪力　12EI/L³·w_b − 6EI/L²·θyb", C["deform"]),
        ("bc：剪力由對稱性抵銷", C["muted"]),
        [("代入 θ_{yb} = 3w_{b}/(2L)：", C["muted"]),
         ("(12 − 9)EI/L^{3}·w_{b} = " + SYM["P_zb"], C["text"])],
        SYM["w_b"], None)
    compose([p1, p2, p3], cols=3,
            title="節點 b 的三條平衡方程：每一條的勁度是「哪一根桿、以哪一種行為」提供的",
            sub="ab 沿 x、bc 沿 y ⇒ 同一個轉角對兩根桿分別是扭轉與彎曲，不能混用",
            note="兩個最常見的失分：把 J 直接寫成 J 而不換成 2I（實心圓桿），"
                 "以及誤以為 bc 桿有扭轉——θyb = θyc 使它沿自身軸線的相對扭角為零。",
            path=f"{OUT}/{TAG}-fig-3-node-b.svg")
    return f"{OUT}/{TAG}-fig-3-node-b.svg"


# ══════════════════════════════════════════════════════════
def fig4_cantilever_check():
    """獨立檢核：ab 桿等同自由端受 ωL/2 的懸臂梁"""
    PW, PH = 760, 470

    a = Canvas(PW, PH, sx=430, ox=150, oy=250)
    a.panel("① 等效懸臂梁（ab 桿的側視圖）", "a 端固定；b 端自由，承受 P = ωL/2")
    a.line((0, 0), (1, 0), C["ghost"], 3.0, dash="7 5", cap="butt")
    D = 0.30
    a.poly([(x, -D * (3 * x ** 2 - x ** 3) / 2) for x in
            [i / 120 for i in range(121)]], C["deform"], 5.4)
    a.fixed_support((0, 0), ang=-90, size=24)
    a.arrow((1, 0.30), (1, -D + 0.04), C["load"], 3.4, 12)
    a.math_px(a.X(1) + 14, a.Y(0.17), "P = ωL/2", 15, C["load"], "start", weight="700")
    a.dot((0, 0), 5.4); a.dot((1, -D), 5.4, fill=C["deform"])
    a.math((0, 0), "a", 16, C["text"], "end", dx=-14, dy=-18)
    a.math((1, -D), "b", 16, C["text"], "start", dx=14, dy=8)
    a.arrow((1.06, 0), (1.06, -D), C["deform"], 2.2, 9)
    a.math_px(a.X(1.06) + 12, a.Y(-D / 2), "w_{b}", 15, C["deform"], "start",
              weight="700")
    a.dim((0, 0), (1, 0), "L", off=106, label_off=16)
    a.math_px(PW / 2, PH - 86, "w_{b} = PL^{3}/3EI　　θ_{yb} = PL^{2}/2EI　　M_{ya} = PL",
              15, C["muted"], weight="700")
    a.text_px(PW / 2, PH - 56, "為什麼可以這樣看：θ_yb = θ_yc ⇒ bc 桿無扭轉",
              13, C["accent"], weight="700")
    a.text_px(PW / 2, PH - 32, "⇒ 對 ab 桿而言，b 端只承受 ωL/2 的剪力、繞 y 的轉角完全自由",
              13, C["accent"])

    b = Canvas(PW, PH, sx=430, ox=150, oy=250)
    b.panel("② 兩條路徑的數字必須一模一樣", "左＝矩陣位移法（§4）　右＝懸臂梁公式（§5）")
    rows = [("節點 b 的 z 向位移", SYM["w_b"], "PL^{3}/3EI = ωL^{4}/6EI"),
            ("節點 b 繞 y 的轉角", SYM["th_yb"], "PL^{2}/2EI = ωL^{3}/4EI"),
            ("a 端繞 y 的反彎矩", SYM["M_ya"], "PL = ωL^{2}/2"),
            ("a 端 z 向反力", SYM["R_za"], "P = ωL/2")]
    for i, (nm, lhs, rhs) in enumerate(rows):
        y = 108 + i * 74
        b.rect_px(34, y - 26, PW - 68, 62, "#F5F7FA", 10, C["border"], 1.1)
        b.text_px(50, y - 6, nm, 12.5, C["muted"], "start")
        b.math_px(50, y + 18, lhs, 15, C["bmd"], "start", weight="700")
        b.text_px(PW / 2 + 24, y + 6, "＝", 16, C["accent"], weight="700")
        b.math_px(PW / 2 + 56, y + 6, rhs, 15, C["deform"], "start", weight="700")
    b.text_px(PW / 2, PH - 40,
              f"腳本已以 E = {V['E']:.3g}、G = {V['G']:.3g}、I = {V['I']:.3g}、"
              f"L = {V['L']:g}、ω = {V['w']:g} 逐條 assert",
              12.5, C["muted"])

    compose([a, b],
            title="用一條與矩陣完全無關的路徑，把 b 點的位移與轉角、a 端的反彎矩重算一遍",
            sub="矩陣法算完不檢核，量級錯了也看不出來；懸臂梁公式是考場上最快的驗算",
            note="a 端的繞 y 反彎矩 ωL²/2 恰等於懸臂梁根部彎矩 P·L —— "
                 "這個巧合不是巧合，而是「ab 桿就是一根懸臂梁」的必然結果。",
            path=f"{OUT}/{TAG}-fig-4-cantilever-check.svg")
    return f"{OUT}/{TAG}-fig-4-cantilever-check.svg"


# ══════════════════════════════════════════════════════════
FIGURES = [
    (fig1_grid,              "§1",   "桿件方向與座標軸對錯 → 扭轉與彎曲張冠李戴"),
    (fig2_dof_symmetry,      "§4.1", "硬組 6×6 手算出錯；對稱關係 θxb = −θxc 寫成同號"),
    (fig3_node_b,            "§4.3", "J 沒換成 2I；誤以為 bc 桿有扭轉"),
    (fig4_cantilever_check,  "§5",   "w_b、θ_yb 量級錯（與懸臂梁公式互為獨立檢核）"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<46} {section:<6} 攔：{catches}")
    print(f"""
數值驗算（E = {V['E']:.4g}、G = {V['G']:.4g}、I = {V['I']:.4g}、L = {V['L']:g}、ω = {V['w']:g}）
  J = 2I            {V['J']:.6g}
  P_zb  = ωL/2      {V['P_zb']:.6g}
  P_mxb = ωL²/12    {V['P_mxb']:.6g}
  θ_xb              {V['th_xb']:.6g}
  w_b               {V['w_b']:.6g}   （懸臂梁 PL³/3EI 一致）
  θ_yb              {V['th_yb']:.6g}   （懸臂梁 PL²/2EI 一致）
  M_xa              {V['M_xa']:.6g}
  M_ya              {V['M_ya']:.6g}   （懸臂梁 P·L 一致）""")
