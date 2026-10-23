#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2003-3 K 型細分桁架 — 題目重繪，標明桿件 a、b 的確切位置

幾何依原題附圖 SA-2003-3-fig-1.png：
  - 跨度 4×8 m = 32 m，高度 4 m + 4 m = 8 m
  - 左右半各為一組「斜桿 + 中點菱形」：
      左：L0–M1–U1 與 U1–M2–L2 兩斜桿，M1–M2 水平桿（a），M1–L1、M2–L1 斜腹桿
      右：L2–M3–U3 與 U3–M4–L4 兩斜桿，M3–M4 水平桿，M3–L3、M4–L3 斜腹桿
  - 中央 U2–L2 直桿；上弦 U1–U2–U3；下弦 L0–L4
"""
import sys, os
SKILL = os.environ.get(
    "STRUCTDRAW",
    "/root/.claude/skills/synced/6983ec08-a01a-44e4-a131-56c9e592c524_ab4f317b-1625-4c71-b32d-871e33fbc9cc/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2003-3"

# ══════════════════════════════════════════════════════════
# 幾何（§4 節點命名；原題附圖左右對稱）
# ══════════════════════════════════════════════════════════
PANEL, H1, H2 = 8.0, 4.0, 4.0          # 節間 8 m、下半高 4 m、上半高 4 m
HT = H1 + H2

nodes = {f"L{i}": (i * PANEL, 0.0) for i in range(5)}
nodes.update({"U1": (PANEL, HT), "U2": (2 * PANEL, HT), "U3": (3 * PANEL, HT)})
# M 點 = 斜桿中點（高度 H1）
nodes.update({
    "M1": (PANEL / 2, H1), "M2": (1.5 * PANEL, H1),
    "M3": (2.5 * PANEL, H1), "M4": (3.5 * PANEL, H1),
})

bottom_chord = [("L0", "L1"), ("L1", "L2"), ("L2", "L3"), ("L3", "L4")]
top_chord    = [("U1", "U2"), ("U2", "U3")]
main_diag    = [("L0", "M1"), ("M1", "U1"), ("U1", "M2"), ("M2", "L2"),     # 左半
                ("L2", "M3"), ("M3", "U3"), ("U3", "M4"), ("M4", "L4")]     # 右半
web          = [("M1", "L1"), ("M2", "L1"), ("M3", "L3"), ("M4", "L3"),     # 菱形下半
                ("M3", "M4"),                                               # 右側水平桿
                ("U2", "L2")]                                               # 中央直桿

MEMBER_A = ("M1", "M2")     # 桿件 a（左側水平桿）
MEMBER_B = ("U1", "M2")     # 桿件 b（左側右上斜桿）

LOADS = [("L1", 2), ("L2", 2)]     # §1：x=8, x=16 下弦節點各 2 t 向下
SUPPORTS = [("L0", "pin"), ("L4", "roller")]

# 靜定性檢核：m + r = 2j（舊圖畫錯時此式不成立 → 不穩定）
_members = bottom_chord + top_chord + main_diag + web + [MEMBER_A]
_r = sum(2 if k == "pin" else 1 for _, k in SUPPORTS)
assert len(_members) + _r == 2 * len(nodes), (len(_members), _r, len(nodes))


def fig1_frame():
    """題目重繪：標明桿件 a (M1-M2) 與 b (U1-M2) 的確切位置與全桁架幾何。
    攔下的錯：K 型細分桁架節點多，容易搞混 a、b 是哪一根，或把右半畫成不對稱的不穩定構架。"""
    W = 1080
    Lm, Rm, T, B = 70, 140, 100, 150
    sx = (W - Lm - Rm) / (4 * PANEL)
    Hc = int(T + B + HT * sx)
    cv = Canvas(W, Hc, sx=sx, ox=Lm, oy=B, bg="#FFFFFF")

    for a, b in bottom_chord + top_chord + main_diag:
        cv.line(nodes[a], nodes[b], C["member"], 4.0, cap="butt")
    for a, b in web:
        cv.line(nodes[a], nodes[b], C["member2"], 3.0, cap="butt")
    cv.line(nodes[MEMBER_A[0]], nodes[MEMBER_A[1]], C["accent"], 6.0, cap="butt")
    cv.line(nodes[MEMBER_B[0]], nodes[MEMBER_B[1]], C["tension"], 6.0, cap="butt")

    for p in nodes.values():
        cv.dot(p, 5.0)

    # 節點名稱
    for n in ("U1", "U2", "U3"):
        cv.text(nodes[n], n, 14, C["text"], weight="700", dy=-18)
    cv.text(nodes["L0"], "L0", 14, C["text"], weight="700", dx=-26, dy=0)
    cv.text(nodes["L4"], "L4", 14, C["text"], weight="700", dx=24, dy=-16)
    for n in ("L1", "L2"):
        cv.text(nodes[n], n, 14, C["text"], weight="700", dx=20, dy=18)
    cv.text(nodes["L3"], "L3", 14, C["text"], weight="700", dy=20)
    for n, dx in (("M1", -24), ("M2", 24), ("M3", -24), ("M4", 24)):
        cv.text(nodes[n], n, 13, C["muted"], weight="700", dx=dx)

    # 桿件 a、b 標籤
    ax = (nodes["M1"][0] + nodes["M2"][0]) / 2
    cv.math_px(cv.X(ax), cv.Y(H1) - 16, "a", 20, C["accent"], weight="700")
    bx = (nodes["U1"][0] + nodes["M2"][0]) / 2
    by = (nodes["U1"][1] + nodes["M2"][1]) / 2
    cv.math_px(cv.X(bx) + 16, cv.Y(by) - 14, "b", 20, C["tension"], weight="700")

    for n, k in SUPPORTS:
        cv.support(nodes[n], k)

    # 載重（下弦節點下方）
    for n, p in LOADS:
        x = nodes[n][0]
        cv.arrow((x, -0.25), (x, -2.0), C["load"], 3.4, 11)
        cv.math_px(cv.X(x), cv.Y(-2.0) + 16, f"{p} t", 15, C["load"], weight="700")

    # 尺寸
    cv.dim((0, 0), (4 * PANEL, 0), f"4 × {PANEL:g} m = {4*PANEL:g} m", off=108, label_off=18)
    cv.dim((4 * PANEL, 0), (4 * PANEL, H1), f"{H1:g} m", off=72, label_off=24)
    cv.dim((4 * PANEL, H1), (4 * PANEL, HT), f"{H2:g} m", off=72, label_off=24)

    cv.text_px(cv.X(2 * PANEL) - 20, 28, "橘色 = 桿件 a (M1–M2)", 14, C["accent"], weight="700", anchor="end")
    cv.text_px(cv.X(2 * PANEL) + 20, 28, "紅色 = 桿件 b (U1–M2)", 14, C["tension"], weight="700", anchor="start")
    cv.text_px(cv.X(2 * PANEL), 54,
               "左右對稱：兩組「斜桿 + 菱形」，中央 U2–L2 直桿；斜桿皆 45°；左鉸右滾",
               12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


FIGURES = [
    (fig1_frame, "§1", "K 型細分桁架節點多 → 誤把 a、b 對應到錯的桿件"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<10} 攔：{catches}")
