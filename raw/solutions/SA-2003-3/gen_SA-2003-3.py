#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2003-3 K型細分桁架 — 題目重繪，標明桿件 a、b 的確切位置"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2003-3"

# ══════════════════════════════════════════════════════════
# 幾何（§Step 4 節點命名，全桁架依左右對稱補齊）
# ══════════════════════════════════════════════════════════
nodes = {
    "L0": (0, 0), "L1": (8, 0), "L2": (16, 0), "L3": (24, 0), "L4": (32, 0),
    "U1": (8, 8), "U2": (16, 8), "U3": (24, 8),
    "M1": (4, 4), "M2": (12, 4), "M3": (20, 4), "M4": (28, 4),
}

bottom_chord = [("L0", "L1"), ("L1", "L2"), ("L2", "L3"), ("L3", "L4")]
top_chord = [("U1", "U2"), ("U2", "U3")]
diagonals = [("L0", "M1"), ("M1", "U1"), ("U1", "M2"), ("M2", "L2"),
             ("L2", "M3"), ("M3", "U2"), ("U2", "M4"), ("M4", "L4")]
verticals = [("M1", "L1"), ("M3", "L3")]     # §Step4 已用到 M1-L1；右半對稱補上 M3-L3

MEMBER_A = ("M1", "M2")     # 桿件 a
MEMBER_B = ("U1", "M2")     # 桿件 b

LOADS = [("L1", 2), ("L2", 2)]     # §1：x=8, x=16 處各 2t 向下
SUPPORTS = [("L0", "pin"), ("L4", "roller")]


def fig1_frame():
    """題目重繪：標明桿件 a (M1-M2) 與 b (U1-M2) 的確切位置與全桁架幾何。
    攔下的錯：K 型細分桁架節點多，容易搞混 a、b 究竟是哪一根桿件。"""
    W, H = 1080, 480
    xr, yr = 32, 8
    Lm, Rm, T, B = 70, 70, 70, 110
    sx = min((W - Lm - Rm) / xr, (H - T - B) / yr)
    cv = Canvas(W, H, sx=sx, ox=Lm, oy=B, bg="#FFFFFF")

    for a, b in bottom_chord + top_chord + verticals:
        cv.line(nodes[a], nodes[b], C["member"], 4.0, cap="butt")
    for a, b in diagonals:
        cv.line(nodes[a], nodes[b], C["member2"], 3.0, cap="butt")
    cv.line(nodes[MEMBER_A[0]], nodes[MEMBER_A[1]], C["accent"], 6.0, cap="butt")
    cv.line(nodes[MEMBER_B[0]], nodes[MEMBER_B[1]], C["tension"], 6.0, cap="butt")

    for n, p in nodes.items():
        cv.dot(p, 5.0)
    for n in ("L0", "L1", "L2", "L3", "L4"):
        cv.text(nodes[n], n, 14.5, C["text"], weight="700", dy=-22)
    for n in ("U1", "U2", "U3"):
        cv.text(nodes[n], n, 14.5, C["text"], weight="700", dy=20)
    for n in ("M1", "M2", "M3", "M4"):
        cv.text(nodes[n], n, 13, C["muted"], weight="700", dx=-2, dy=-20)

    cv.support(nodes["L0"], "pin")
    cv.support(nodes["L4"], "roller")

    for n, p in LOADS:
        cv.arrow((nodes[n][0], nodes[n][1] + 1.6), nodes[n], C["load"], 3.4, 11)
        cv.math_px(cv.X(nodes[n][0]), cv.Y(nodes[n][1] + 1.6) - 14, f"{p} t", 14, C["load"], weight="700")

    cv.dim((0, 0), (8, 0), "8 m", off=-46, label_off=-15)
    cv.text_px(cv.X(16), 28, "橘色＝桿件 a (M1-M2)　　紅色＝桿件 b (U1-M2)", 14, C["text"], weight="700")
    cv.text_px(cv.X(16), H - 20,
               "斜桿角度皆為 45°（節間 8 m、上下弦高差 4 m）；A 為鉸支承、右端為滾支承", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


FIGURES = [
    (fig1_frame, "§Step 4", "K 型細分桁架節點多 → 誤把 a、b 對應到錯的桿件"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<10} 攔：{catches}")
