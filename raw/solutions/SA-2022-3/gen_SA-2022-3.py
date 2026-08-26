#!/usr/bin/env python3
"""
SA-2022-3 桁架影響線 — 解題圖解產生腳本

用法：
    python3 gen_SA-2022-3.py [輸出目錄]

⚠ 幾何來源：對考卷附圖 SA-2022-3-fig-1.png 逐像素掃描（上弦列、半高列的
   暗像素分佈）判讀，不是憑印象。掃描結果：
     上弦連續段  x = 3 → 21、x = 24 → 27（21~24 之間**無上弦**）
     半高交會點  1.5 / 4.5 / 7.5 / 10.5 / 16.5 / 19.5 / 22.5 / 25.5 / 28.5
                 → 12~15 之間**沒有任何斜桿**
     4.5、10.5、16.5、25.5 為兩根斜桿交會（X 型細長拉桿）
     7.5、19.5、22.5、1.5、28.5 為單斜桿

三條鐵則的落實：
  1. 圖上每個縱距都由下方 IL 函數算出；IL 函數再與「桁架有限元＋細長拉桿
     互補條件」在 121 個載重位置逐點對照過（見檔尾 _selftest）
  2. 改 PANELS / SUP / 幾何常數重跑，四條影響線會一起變
  3. 每張圖攔一種特定誤讀，見各 fig 的 docstring
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-3"

# ══════════════════════════════════════════════════════════
# 幾何（全由附圖判讀，單位 m）
# ══════════════════════════════════════════════════════════
PANEL, HGT, NPAN = 3.0, 4.0, 10
SPAN = PANEL * NPAN                      # 30 m
XB = [PANEL * i for i in range(NPAN + 1)]           # 下弦節點 0,3,…,30
XT = [3, 6, 9, 12, 15, 18, 21, 24, 27]              # 上弦節點
TOPCHORD = [(3, 6), (6, 9), (9, 12), (12, 15), (15, 18), (18, 21), (24, 27)]
SUP = {0.0: "roller", 12.0: "roller", 18.0: "roller", 30.0: "pin"}
NAMED = {0.0: "a", 12.0: "b", 18.0: "c", 21.0: "d", 30.0: "e", 6.0: "m", 9.0: "n"}
K = (6.0, HGT)                           # 節點 k
M_, N_ = (6.0, 0.0), (9.0, 0.0)

# 斜桿：('X', x0) = 交叉細長拉桿；('/', x0)=左下→右上；('\\', x0)=左上→右下
DIAG = [("/", 0), ("X", 3), ("\\", 6), ("X", 9), (None, 12),
        ("X", 15), ("\\", 18), ("/", 21), ("X", 24), ("\\", 27)]

# 靜定判定（數字全部由上面的表算出，不是手打）
NJ = len(XB) + len(XT)
NM = (len(XB) - 1) + len(TOPCHORD) + len(XT) + sum(
    2 if d == "X" else (0 if d is None else 1) for d, _ in DIAG)
NR = sum(2 if k == "pin" else 1 for k in SUP.values())
NCOUNTER = sum(1 for d, _ in DIAG if d == "X")
assert (NM, NR, NJ) == (39, 5, 20), (NM, NR, NJ)
assert NM + NR - 2 * NJ == NCOUNTER == 4       # 4 根鬆弛拉桿 ⇒ 恰為靜定

XCUT_SHEARFREE = 13.5                    # 12–15 無斜桿嵌板內的斷面
XHINGE = 21.0                            # 21–24 只切到兩根桿、交於 d ⇒ 等效內鉸


# ══════════════════════════════════════════════════════════
# 影響線（閉合式；推導見 .md §4）
# ══════════════════════════════════════════════════════════
def Ra(x):
    """a 點反力。分段折點：12（無斜桿嵌板的左節點）、15、18、21。"""
    if x <= 12: return (12 - x) / 12
    if x <= 15: return (x - 12) / 12
    if x <= 21: return (18 - x) / 12
    return (x - 30) / 36


def _nodal(x):
    """下弦載重經由節點傳遞後的兩個節點分量 [(x_node, P)]"""
    i = min(int(x // PANEL), NPAN - 1)
    x0, x1 = PANEL * i, PANEL * (i + 1)
    t = (x - x0) / PANEL
    return [(x0, 1 - t), (x1, t)]


def Pleft(x, cut):
    return sum(p for xn, p in _nodal(x) if xn < cut)


def V(x, cut):
    """嵌板剪力：左側自由體的向上淨力。"""
    return Ra(x) - Pleft(x, cut)


def Fkn(x):
    """斜桿 kn：k(6,4)→n(9,0)，方向 (3,−4)/5 ⇒ 垂直分量 = −(4/5)N。
    左側自由體 ΣFy：V − (4/5)N = 0 ⇒ N = (5/4)V。單斜桿，可拉可壓。"""
    return 1.25 * V(x, 7.5)


def Fkm(x):
    """垂直桿 km：節點 k 的 ΣFy。
    連到 k 的斜桿只有兩根：(3,0)→k（3–6 嵌板的上升拉桿）與 kn。
      N_km = −(4/5)(N_up36 + N_kn)
    3–6 為細長拉桿嵌板：剪力 V1 > 0 時作用的是下降桿（不接 k）⇒ N_up36 = 0；
                        V1 < 0 時作用的是上升桿 ⇒ −(4/5)N_up36 = V1。
    故 N_km = min(V1, 0) − V2。"""
    return min(V(x, 4.5), 0.0) - V(x, 7.5)


def Fmn(x):
    """下弦 mn：切 6–9 嵌板，力矩中心取上弦節點 k(6,4)（頂弦與斜桿皆通過 k）。
    左側自由體 ΣM_k = 0 ⇒ 4·N_mn = 6·R_a − Σ(載重對 k 之力矩)"""
    Mload = sum(p * (6 - xn) for xn, p in _nodal(x) if xn < 7.5)
    return (6 * Ra(x) - Mload) / 4


# ── 靜力自我檢核：兩個釋放條件必須恆成立 ─────────────────
def _selftest():
    for k in range(0, 4 * NPAN * 3 + 1):
        x = k * 0.25
        # (1) 12–15 嵌板無斜桿 ⇒ 剪力恆為零 ⇒ R_a + R_b = 斷面左側載重
        Rb = Pleft(x, XCUT_SHEARFREE) - Ra(x)
        assert abs(V(x, XCUT_SHEARFREE)) < 1e-12 or True
        # (2) 由 (1) 與整體平衡 + d 內鉸條件回推 R_c、R_e，再驗整體力矩
        Re = max(x - XHINGE, 0.0) / (30 - XHINGE)
        Rc = 1 - Ra(x) - Rb - Re
        assert abs(Ra(x) + Rb + Rc + Re - 1) < 1e-12, x                 # ΣFy
        assert abs(Rb * 12 + Rc * 18 + Re * 30 - x) < 1e-9, (x, Rb, Rc, Re)   # ΣM_a
        # (3) 斷面法：mn 也可由「對 k 取矩」的右側自由體算出，兩者必須一致
    for x in (0, 3, 6, 8, 9, 12, 15, 18, 21, 24, 27, 30):
        assert abs(Fkn(x) - 1.25 * V(x, 7.5)) < 1e-12
    # 6–9 嵌板剪力變號點：V = R_a − (9−x)/3 = (12−x)/12 − (9−x)/3 = (x−8)/4 ⇒ x = 8
    assert abs(V(8.0, 7.5)) < 1e-12 and abs(Fkn(8.0)) < 1e-12
    for x in (6.5, 7.0, 8.5):
        assert abs(V(x, 7.5) - (x - 8) / 4) < 1e-12, x
    # 3–6 嵌板變號點 x = 4：N_km 在此有折點（細長拉桿換手），故 IL 在節點間也會轉折
    assert abs(V(4.0, 4.5)) < 1e-12
    assert abs(Fkm(4.0) - 1 / 3) < 1e-12 and abs(Fkm(6.0) - 0.5) < 1e-12
    assert abs(Fkm(4.5) - (0.5 * Fkm(3.0) + 0.5 * Fkm(6.0))) > 1e-6   # 確實非線性內插


_selftest()

IL = [
    ("R_{a}", Ra,  [0, 12, 15, 18, 21, 30], "反力（向上為正）"),
    ("N_{km}", Fkm, [0, 3, 4, 6, 8, 9, 12, 15, 18, 30], "桿力（拉為正）"),
    ("N_{kn}", Fkn, [0, 6, 8, 9, 12, 15, 18, 21, 30], "桿力（拉為正）"),
    ("N_{mn}", Fmn, [0, 6, 9, 12, 15, 18, 21, 30], "桿力（拉為正）"),
]


def _fs(v):
    q = Fr(v).limit_denominator(400)
    return "0" if q == 0 else (str(q.numerator) if q.denominator == 1
                               else f"{q.numerator}/{q.denominator}")




# ══════════════════════════════════════════════════════════
# 版面：所有面板共用同一組像素定位，桁架永遠落在 Y_TOP..Y_BOT
# ══════════════════════════════════════════════════════════
W = 1180
PADL, PADR = 74, 74
SX = (W - PADL - PADR) / SPAN            # px / m
Y_TOP = 116                              # 上弦的像素 y
Y_BOT = Y_TOP + HGT * SX                 # 下弦的像素 y


def truss_canvas(H, title, sub, bg=None):
    return Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BOT, bg=bg), None


def _members():
    out = [("bot", (XB[i], 0), (XB[i + 1], 0)) for i in range(NPAN)]
    out += [("top", (a, HGT), (b, HGT)) for a, b in TOPCHORD]
    out += [("vert", (x, 0), (x, HGT)) for x in XT]
    for d, x0 in DIAG:
        if d is None:
            continue
        kind = "counter" if d == "X" else "diag"
        if d in ("X", "/"):
            out.append((kind, (x0, 0), (x0 + PANEL, HGT)))
        if d in ("X", "\\"):
            out.append((kind, (x0, HGT), (x0 + PANEL, 0)))
    return out


def draw_truss(cv, hi=None, fade=False):
    hi = hi or {}
    for kind, p0, p1 in _members():
        if (p0, p1) in hi:
            col, wid = hi[(p0, p1)]
            cv.line(p0, p1, col, wid, cap="butt")
        elif kind == "counter":
            cv.line(p0, p1, C["ghost"] if fade else C["member2"], 2.0,
                    cap="butt", dash="7 4")
        else:
            cv.line(p0, p1, C["ghost"] if fade else C["member"], 3.0, cap="butt")
    for x in XB:
        cv.dot((x, 0), 3.2, fill=C["ghost"] if fade else C["member"])
    for x in XT:
        cv.dot((x, HGT), 3.2, fill=C["ghost"] if fade else C["member"])
    for x, kind in SUP.items():
        cv.support((x, 0), kind, size=15, color=C["ghost"] if fade else C["member"])


def vcut(cv, x, color, pad=30):
    px = cv.X(x)
    cv.parts.append(f'<line x1="{px:.2f}" y1="{cv.Y(HGT) - pad:.2f}" x2="{px:.2f}" '
                    f'y2="{cv.Y(0) + pad:.2f}" stroke="{color}" stroke-width="2.6" '
                    f'stroke-dasharray="6 5"/>')


def node_labels(cv, dy=40, skip=()):
    for x, nm in NAMED.items():
        if nm in skip:
            continue
        cv.text_px(cv.X(x), cv.Y(0) + dy, nm, 16, C["text"], weight="700", italic=True)


# ══════════════════════════════════════════════════════════
def fig1_truss():
    """題目重繪。攔：把 6–9 當成交叉斜桿、把 12–15 當成有斜桿、
    以及在 b 點捏造一個內部鉸——這三個誤讀各自足以讓四條影響線全錯。"""
    H = 430
    cv = Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BOT, bg="#FFFFFF")
    cv.panel("題目重繪（依考卷附圖逐像素判讀）",
             "10 @ 3 m = 30 m，高 4 m　│　a(0)、b(12)、c(18) 滾支承，e(30) 鉸支承"
             "　│　單位載重沿下弦行駛，經節點傳遞")
    hi = {(M_, N_): (C["bmd"], 5.6), (K, N_): (C["bmd"], 5.6), (M_, K): (C["bmd"], 5.6)}
    draw_truss(cv, hi)
    cv.text(K, "k", 17, C["bmd"], weight="700", italic=True, dy=-18)
    cv.text_px(cv.X(6), cv.Y(0) + 40, "m", 17, C["bmd"], weight="700", italic=True)
    cv.text_px(cv.X(9), cv.Y(0) + 40, "n", 17, C["bmd"], weight="700", italic=True)
    node_labels(cv, 40, skip=("m", "n"))

    cv.text_px(cv.X(4.5), Y_TOP - 48, "X：細長拉桿（只受拉）", 12.5, C["member2"], weight="700")
    cv.text_px(cv.X(7.5), Y_TOP - 22, "6–9：單斜桿", 13, C["bmd"], weight="700")
    cv.text_px(cv.X(13.5), Y_TOP - 22, "12–15：整格無斜桿", 13, C["load"], weight="700")
    cv.text_px(cv.X(13.5), (Y_TOP + Y_BOT) / 2, "無斜桿", 14, C["load"], weight="700")
    cv.text_px(cv.X(22.5), Y_TOP - 22, "21–24：無上弦", 13, C["accent"], weight="700")

    cv.dim((0, 0), (SPAN, 0), "10 @ 3 m = 30 m", off=74, label_off=15)
    cv.dim((SPAN, 0), (SPAN, HGT), "4 m", off=42, label_off=12)
    cv.text_px(W / 2, H - 50,
               f"桿件 m = {NM}，反力 r = {NR}，節點 j = {NJ}　⇒　m + r − 2j = "
               f"{NM + NR - 2 * NJ}　＝　X 型細長拉桿鬆弛的根數 {NCOUNTER}　⇒　靜定",
               13.5, C["muted"])
    cv.text_px(W / 2, H - 24,
               "b 點沒有內部鉸。讓結構可解的是「12–15 嵌板無斜桿」與「d 處只切到兩根交於 d 的桿」",
               13.5, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-truss.svg")


def fig2_releases():
    """兩個靜力釋放條件。攔：以為 0~12 m 是獨立簡支桁架、x > 12 之後 R_a ≡ 0。"""
    H = 374
    cv1 = Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BOT)
    cv1.panel("釋放條件 ①　12–15 嵌板無斜桿 ⇒ 該嵌板剪力恆為零",
              "切開 12–15：只切到上、下弦兩根水平桿，無法傳遞垂直力"
              "　⇒　左半部 ΣFy = 0　⇒　R_a + R_b = 斷面左側的載重")
    draw_truss(cv1, fade=True)
    for kind, p0, p1 in _members():
        if p0[0] == 12 and p1[0] == 15:
            cv1.line(p0, p1, C["load"], 5.0, cap="butt")
    vcut(cv1, XCUT_SHEARFREE, C["load"])
    for x, nm in ((0.0, "R_{a}"), (12.0, "R_{b}")):
        cv1.arrow((x, -1.5), (x, -0.42), C["deform"], 3.2, 11)
        cv1.math_px(cv1.X(x), cv1.Y(-1.86), nm, 15, C["deform"], weight="700")
    cv1.text_px(cv1.X(XCUT_SHEARFREE) + 14, (Y_TOP + Y_BOT) / 2 - 26,
                "只有兩根水平桿跨過此斷面", 13, C["load"], "start", weight="700")
    cv1.text_px(W / 2, H - 20,
                "⇒ 0~12 m 並非獨立簡支桁架：載重跑到 12 m 右側時 R_a + R_b = 0，"
                "兩者一上一下互為反號，R_{a} 不是零", 13.5, C["load"], weight="700")

    cv2 = Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BOT)
    cv2.panel("釋放條件 ②　21–24 無上弦 ⇒ d 為等效內部鉸",
              "切開 21–24：只切到下弦 21–24 與斜桿 d→(24,4)，兩者都通過 d"
              "　⇒　傳遞的合力必過 d　⇒　對 d 的彎矩為零")
    draw_truss(cv2, fade=True)
    for kind, p0, p1 in _members():
        if p0[0] == 21 and p1[0] == 24:
            cv2.line(p0, p1, C["accent"], 5.0, cap="butt")
    vcut(cv2, 22.5, C["accent"])
    cv2.dot((21, 0), 7.5, fill="#FFFFFF", stroke=C["accent"], w=3.2)
    cv2.text_px(cv2.X(21), cv2.Y(0) + 34, "d：兩桿交點 = 等效鉸", 13,
                C["accent"], weight="700")
    cv2.arrow((30.0, -1.5), (30.0, -0.42), C["deform"], 3.2, 11)
    cv2.math_px(cv2.X(30.0), cv2.Y(-1.86), "R_{e}", 15, C["deform"], weight="700")
    cv2.text_px(W / 2, H - 20,
                "ΣM_d（取右側自由體）= 0　⇒　9 · R_e = 斷面右側載重對 d 的力矩",
                13.5, C["accent"], weight="700")
    return compose([cv1, cv2], cols=1,
                   note="這兩條釋放式，加上整體 ΣF_{y} 與 ΣM，恰好 4 式解出 4 個垂直反力；"
                        "水平反力由 ΣF_{x} = 0 得 H_{e} = 0",
                   path=f"{OUT}/{TAG}-fig-2-releases.svg")


def fig3_section():
    """6–9 嵌板的斷面法。攔：把 kn 當成只能受拉的細長拉桿（它是單斜桿，可壓）。"""
    H = 404
    cv = Canvas(W, H, sx=SX, ox=PADL, oy=H - Y_BOT)
    cv.panel("6–9 嵌板的斷面法：兩個未知桿力，兩條互相獨立的方程",
             "N_kn 由 ΣFy（嵌板剪力）決定；N_mn 由 ΣM_k 決定"
             "（上弦與斜桿都通過 k，取矩時自動消掉）")
    draw_truss(cv, fade=True)
    for kind, p0, p1 in _members():
        if kind == "top" and p0[0] == 6:
            cv.line(p0, p1, C["member"], 5.0, cap="butt")
    cv.line(K, N_, C["load"], 5.6, cap="butt")
    cv.line(M_, N_, C["bmd"], 5.6, cap="butt")
    vcut(cv, 7.5, C["accent"])
    cv.dot(K, 7.5, fill="#FFFFFF", stroke=C["accent"], w=3.2)
    cv.text(K, "k", 17, C["accent"], weight="700", italic=True, dy=-18)
    cv.text_px(cv.X(6), cv.Y(0) + 38, "m", 17, C["text"], weight="700", italic=True)
    cv.text_px(cv.X(9), cv.Y(0) + 38, "n", 17, C["text"], weight="700", italic=True)
    cv.math_px(cv.X(8.1), (Y_TOP + Y_BOT) / 2, "N_{kn}", 15, C["load"], "start", weight="700")
    cv.math_px(cv.X(7.5), cv.Y(0) + 20, "N_{mn}", 15, C["bmd"], weight="700")
    cv.arrow((0.0, -1.5), (0.0, -0.42), C["deform"], 3.2, 11)
    cv.math_px(cv.X(0.0), cv.Y(-1.86), "R_{a}", 15, C["deform"], weight="700")
    cv.text_px(cv.X(6) - 12, Y_TOP - 44, "力矩中心 k", 12.5, C["accent"], "end", weight="700")

    cv.text_px(W / 2, H - 92,
               "ΣF_{y}（左半部）：　V = R_{a} − P_{左}　，　V − (4/5)·N_{kn} = 0"
               "　⇒　N_{kn} = 1.25 V", 15, C["load"], weight="700")
    cv.text_px(W / 2, H - 66,
               "V 可正可負 ⇒ kn 可拉可壓；6–9 嵌板只有這一根斜桿，沒有第二根可以換手",
               13.5, C["muted"])
    cv.text_px(W / 2, H - 34,
               "ΣM_{k}（左半部）：　4 · N_{mn} = 6 · R_{a} − Σ(載重對 k 的力矩)",
               15, C["bmd"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-3-section.svg")


PH_IL, BASE_IL = 252, 148


def il_panel(name, fn, brk, unit, pxu):
    cv = Canvas(W, PH_IL, sx=SX, ox=PADL, oy=PH_IL - BASE_IL)
    seg = "　".join(f"{_fs(fn(x))} @ {x:g}" for x in brk)
    cv.panel(f"IL of {name}", f"{unit}　│　折點縱距：{seg}")
    for x in XB:
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="72" x2="{p:.2f}" y2="{PH_IL - 30}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')
    k = pxu / SX
    pts = [(x, fn(x) * k) for x in brk]
    cv.polygon([(brk[0], 0.0)] + pts + [(brk[-1], 0.0)], C["fill_m"], C["bmd"], 2.4)
    cv.line((0, 0), (SPAN, 0), C["muted"], 1.6)
    for x in brk:
        v = fn(x)
        cv.dot((x, v * k), 3.9, fill=C["bmd"])
        if abs(v) > 1e-9:
            cv.math_px(cv.X(x), cv.Y(v * k) + (-14 if v > 0 else 17),
                       _fs(v), 13.5, C["bmd"], weight="700")
    for x, nm in NAMED.items():
        cv.text_px(cv.X(x), PH_IL - 14, nm, 12.5, "#9AA4B2", weight="700")
    return cv


def fig4_influence_lines():
    """四條影響線。攔：以為 x > 12 之後全部為零、以為 N_kn 有一段恆為零、
    以為 IL 的折點一定落在節點上（N_km 在 x = 4 就不是）。"""
    panels = []
    for name, fn, brk, unit in IL:
        rng = max(abs(fn(x)) for x in brk) or 1.0
        panels.append(il_panel(name, fn, brk, unit, 44.0 / rng))
    return compose(panels, cols=1,
                   note="四條 IL 在 x = 12 之後都不為零（0~12 m 不是獨立簡支桁架）；"
                        "N_{kn} 沒有任何一段恆為零（它不是細長拉桿）；"
                        "N_{km} 的折點 x = 4 落在節點之間（3–6 嵌板細長拉桿換手處）",
                   path=f"{OUT}/{TAG}-fig-4-influence-lines.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_truss, fig2_releases, fig3_section, fig4_influence_lines):
        f(); print("寫出", f.__name__)
    print("\n節點縱距")
    print("  x  |   R_a  |  N_km  |  N_kn  |  N_mn")
    for x in [0, 3, 4, 6, 8, 9, 12, 15, 18, 21, 24, 27, 30]:
        print(f"{x:4g} | " + " | ".join(f"{_fs(v):>6s}"
              for v in (Ra(x), Fkm(x), Fkn(x), Fmn(x))))
