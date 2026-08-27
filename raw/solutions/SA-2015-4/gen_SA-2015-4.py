#!/usr/bin/env python3
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, FONT_M

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2015-4"

# ══ 幾何（來自 SA-2015-4.md §1 附圖／圖四）══
# A(0,0) 固定端；AB 長 L 水平，受向下均佈載重 w；B 為 AB-BC 剛接點
# BC 長 L 垂直向下，C(1,-1) 固定端
# B 與 BD 左端以「抗扭彈簧 kθ」＋「水平線性彈簧 ks」連接（無垂直力傳遞）
# BD 長 L 水平，中點受向下集中力 P；D(2,0) 固定端
NA, NB, NC, ND = (0, 0), (1, 0), (1, -1), (2, 0)
NP = (1.5, 0)   # BD 中點，P 作用處


def zigzag(cv, center, half_w=0.075, amp=0.045, n=5, color=None, w=2.4):
    """水平線性彈簧符號：以參數化鋸齒線表示（純示意符號，非數據）"""
    cx, cy = center
    xs = [cx - half_w + 2*half_w*i/n for i in range(n + 1)]
    pts = []
    for i, x in enumerate(xs):
        if i == 0 or i == n:
            pts.append((x, cy))
        else:
            pts.append((x, cy + (amp if i % 2 else -amp)))
    cv.poly(pts, color or C["deform"], w)


def coil(cv, center, r=0.11, turns=3.2, n=90, color=None, w=2.4):
    """抗扭彈簧符號：以參數化螺旋線表示（純示意符號，非數據）"""
    cx, cy = center
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = t * turns * 2 * math.pi
        rad = r * t
        pts.append((cx + rad * math.sin(ang), cy - rad * math.cos(ang) * 0.55))
    cv.poly(pts, color or C["accent"], w)


def frame(cv, color=C["member"], w=6.0, dash=None, with_p=True):
    cv.line(NA, NB, color, w, dash=dash, cap="butt")
    cv.line(NB, ND, color, w, dash=dash, cap="butt")
    cv.line(NB, NC, color, w, dash=dash, cap="butt")


def fig1_frame():
    """題目重繪：取代低解析度截圖，把彈簧接頭型式與跨距固定下來"""
    cv = Canvas(900, 640, sx=230, ox=140, oy=350, bg="#FFFFFF")
    frame(cv)
    # UDL w on AB
    cv.udl(NA, NB, 0.16, n=6, color=C["load"], label=None)
    cv.math((0.5, 0), "w", 17, C["load"], "middle", dy=48, weight="700")
    # P at BD midpoint
    cv.arrow((NP[0], NP[1] + 0.34), NP, C["load"], 3.6, 12)
    cv.math(NP, "P", 18, C["load"], "middle", dy=54, weight="700")
    # spring symbols at B (linear above line, torsional below)
    zigzag(cv, (1.16, 0.10))
    cv.arrow((1.42, 0.30), (1.20, 0.13), C["deform"], 2.2, 8)
    cv.text_px(cv.X(1.42) + 6, cv.Y(0.30) - 4, "線性彈簧 k_{s}", 14, C["deform"], weight="700")
    coil(cv, (1.0, -0.20), r=0.10)
    cv.arrow((1.30, -0.42), (1.06, -0.24), C["accent"], 2.2, 8)
    cv.text_px(cv.X(1.30) + 6, cv.Y(-0.42) + 4, "抗扭彈簧 k_{θ}", 14, C["accent"], weight="700")
    # supports
    cv.fixed_support(NA, ang=90, size=18)
    cv.fixed_support(NC, ang=0, size=18)
    cv.fixed_support(ND, ang=-90, size=18)
    for p, lab, ax, ay in ((NA, "A", -18, 10), (NB, "B", -8, 20),
                            (NC, "C", 16, -8), (ND, "D", 18, 10)):
        cv.dot(p, 5.2); cv.text(p, lab, 15, C["text"], weight="700", dx=ax, dy=ay)
    cv.dim((0, 0), (1, 0), "L", off=52, label_off=16)
    cv.dim((1, 0), (1.5, 0), "L/2", off=52, label_off=16)
    cv.dim((1.5, 0), (2, 0), "L/2", off=52, label_off=16)
    cv.dim((1, 0), (1, -1), "L", off=52, label_off=16)
    cv.text_px(450, 590, "A、C、D 為固定端；B 點 AB－BC 剛接；BD 左端僅以兩彈簧與 B 相連（無垂直力傳遞）",
               13, C["muted"])
    cv.text_px(450, 610, "所有桿件 EI、EA 相同、長度皆為 L；忽略軸向變形",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_dof():
    """自由度辨識：B 拆成 B1(AB-BC)／B2(BD左端)，凸顯 ks 兩端零位移而消失的陷阱"""
    cv = Canvas(940, 660, sx=210, ox=150, oy=340, bg="#FFFFFF")
    B1, B2 = (1.0, 0), (1.55, 0)
    cv.line(NA, B1, "#9AA4B2", 5.0, cap="butt")
    cv.line(B1, (1.0, -1.0), "#9AA4B2", 5.0, cap="butt")
    cv.line(B2, (2.55, 0), "#9AA4B2", 5.0, cap="butt")
    cv.fixed_support(NA, ang=90, size=16)
    cv.fixed_support((1.0, -1.0), ang=0, size=16)
    cv.fixed_support((2.55, 0), ang=-90, size=16)

    # springs between B1 and B2 (drawn separated for clarity)
    zigzag(cv, (1.275, 0.16), half_w=0.14, amp=0.05)
    coil(cv, (1.275, -0.24), r=0.13, turns=2.6)
    cv.line((1.0, 0.16), (1.15, 0.16), C["deform"], 2.0)
    cv.line((1.40, 0.16), (1.55, 0.16), C["deform"], 2.0)
    cv.line((1.0, -0.02), (1.145, -0.10), C["accent"], 2.0)
    cv.line((1.405, -0.10), (1.55, -0.02), C["accent"], 2.0)
    cv.text_px(cv.X(1.275), cv.Y(0.16) + 26, "k_{s}", 14, C["deform"], "middle", weight="700")
    cv.text_px(cv.X(1.275), cv.Y(-0.24) - 12, "k_{θ}", 14, C["accent"], "middle", weight="700")

    # DOFs
    cv.moment_arrow(B1, r=24, ccw=False, color=C["deform"], w=2.8, span=235, start=205)
    cv.text_px(cv.X(B1[0]) - 58, cv.Y(B1[1]) - 30, "r_{1}=θ_{B1}", 16, C["deform"], weight="700", italic=True, font=FONT_M)
    cv.arrow(B2, (B2[0], B2[1] - 0.30), C["deform"], 3.2, 11)
    cv.text_px(cv.X(B2[0]) + 10, cv.Y(B2[1] - 0.30) + 4, "r_{2}=v_{B2}", 16, C["deform"], weight="700", italic=True, font=FONT_M)
    cv.moment_arrow(B2, r=24, ccw=False, color=C["deform"], w=2.8, span=235, start=205)
    cv.text_px(cv.X(B2[0]) + 34, cv.Y(B2[1]) - 40, "r_{3}=θ_{B2}", 16, C["deform"], weight="700", italic=True, font=FONT_M)

    for p, lab, ax, ay in ((NA, "A", -18, 10), (B1, "B1", -16, 22), ((1.0, -1.0), "C", 16, -8),
                            (B2, "B2", -4, 22), ((2.55, 0), "D", 16, 10)):
        cv.dot(p, 5.0, fill="#4A5568"); cv.text(p, lab, 13.5, C["text"], weight="700", dx=ax, dy=ay)

    cv.rect_px(600, 40, 300, 118, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(750, 64, "有效自由度只剩 3 個", 14.5, "#1D4ED8", weight="700")
    cv.text_px(750, 92, "{ r_{1} , r_{2} , r_{3} }", 18, "#1D4ED8", italic=True, font=FONT_M)
    cv.text_px(750, 118, "順時針、向下為正", 12.5, "#1D4ED8")
    cv.text_px(750, 142, "B1、B2 為同一位置，分離繪製僅為清楚標示", 11.5, "#1D4ED8")

    cv.rect_px(30, 380, 330, 96, "#FDF1EC", 12, "#F0C4B0", 1.3)
    cv.text_px(195, 404, "陷阱：k_{s} 兩端水平位移皆為零", 13.5, "#C0392B", "middle", weight="700")
    cv.text_px(195, 428, "(u_{B1}=u_{B2}=0，桿件忽略軸向變形)", 12, "#C0392B", "middle")
    cv.text_px(195, 452, "⇒ k_{s} 不變形、不受力，不進入 [K]", 13, "#C0392B", "middle", weight="700")

    cv.text_px(cv.X(0.5), cv.Y(0) + 26, "u_{B1}=0", 12, C["muted"], "middle")
    cv.text_px(cv.X(2.05), cv.Y(0) + 26, "u_{B2}=0", 12, C["muted"], "middle")

    return cv.save(f"{OUT}/{TAG}-fig-2-dof.svg")


FIGURES = [
    (fig1_frame, "§1", "彈簧接頭型式（k_s／k_θ）與跨距標錯 → 邊界條件與 FEM 全盤皆錯"),
    (fig2_dof,   "§3.5", "誤把 k_s 列入獨立自由度或漏乘 K 矩陣 → 矩陣階數/元素錯"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<40} {section:<8} 攔：{catches}")
