#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2024-2 Pratt 桁架（含垂直桿）— 題目重繪

本次解析發現：原圖說僅描述斜桿（Pratt V 型），漏提每個節點的垂直桿，
不影響本題答案但屬幾何誤讀風險。本圖把全部 25 根桿件明確畫出。
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2024-2"

# ══════════════════════════════════════════════════════════
# 幾何（§1 圖說 + 本次校正後之完整節點/桿件清單）
# ══════════════════════════════════════════════════════════
BOT = ["A", "B", "C", "D", "E", "F", "G"]      # 下弦，y=0
TOP = ["H", "I", "J", "K", "L", "M", "N"]      # 上弦，y=3
XS = [0, 4, 8, 12, 16, 20, 24]                  # 節間 4m
bot = {n: (x, 0) for n, x in zip(BOT, XS)}
top = {n: (x, 3) for n, x in zip(TOP, XS)}
nodes = {**bot, **top}

verticals = list(zip(TOP, BOT))                              # H-A, I-B, ... N-G（7 根）
bottom_chord = list(zip(BOT, BOT[1:]))                        # 6 根
top_chord = list(zip(TOP, TOP[1:]))                            # 6 根
diagonals = [("H", "B"), ("B", "J"), ("J", "D"), ("D", "L"), ("L", "F"), ("F", "N")]  # 6 根（Pratt）

CD, DE = ("C", "D"), ("D", "E")                                 # 本題未知項所在桿件

SUP_B, SUP_F = "B", "F"      # 滾支承 B、鉸支承 F


def fig1_frame():
    """題目重繪：把全部 25 根桿件明確畫出，CD／DE 桿與 v_F、ΔC、ΔE 標明。
    攔下的錯：只看斜桿而漏看垂直桿 → 誤判桁架幾何或靜定度 m=2j-r。"""
    W, H = 1180, 400
    xr, yr = 24, 3
    L, R, T, B = 70, 70, 90, 118
    sx = min((W - L - R) / xr, (H - T - B) / yr)
    cv = Canvas(W, H, sx=sx, ox=L, oy=B, bg="#FFFFFF")

    for a, b in bottom_chord + top_chord + verticals:
        cv.line(nodes[a], nodes[b], C["member"], 4.4, cap="butt")
    for a, b in diagonals:
        cv.line(nodes[a], nodes[b], C["member2"], 3.2, cap="butt")
    # 標示本題未知項所在桿件
    cv.line(nodes[CD[0]], nodes[CD[1]], C["accent"], 6.0, cap="butt")
    cv.line(nodes[DE[0]], nodes[DE[1]], C["accent"], 6.0, cap="butt")

    for n, p in nodes.items():
        cv.dot(p, 4.6)
    for n in BOT:
        cv.text(bot[n], n, 14, C["text"], weight="700", dy=-20)
    for n in TOP:
        cv.text(top[n], n, 14, C["text"], weight="700", dy=18)

    cv.roller_support(bot[SUP_B])
    cv.pin_support(bot[SUP_F])
    cv.text_px(cv.X(bot[SUP_B][0]), cv.Y(0) + 58, "滾支承 B", 12, C["muted"])
    cv.text_px(cv.X(bot[SUP_F][0]) - 34, cv.Y(0) + 58, "鉸支承 F", 12, C["muted"], "end")

    # 支承沉陷 v_F（畫在支承右側，避開支承文字）
    cv.arrow((bot[SUP_F][0] + 0.9, 1.05), (bot[SUP_F][0] + 0.9, 0.1), C["load"], 3.0, 10)
    cv.math_px(cv.X(bot[SUP_F][0] + 0.9) + 10, cv.Y(0.55), "v_{F}=12 mm", 13, C["load"], "start", weight="700")

    # C、E 兩點的量測位移
    for n, dlab in (("C", "Δ_{C}=4.8 mm ↓"), ("E", "Δ_{E}=6.4 mm ↓")):
        cv.math_px(cv.X(bot[n][0]), cv.Y(0) - 46, dlab, 12.5, C["accent"], weight="700")

    cv.dim((0, 0), (4, 0), "4 m", off=-46, label_off=-15)
    cv.text_px(cv.X(12), H - 20, "上弦節點 H~N 高度 3 m；每一節間垂直桿與 Pratt 斜桿並存（共 7 根垂直＋6 根斜桿）",
               12.5, C["muted"])
    cv.text_px(cv.X(12), 22, "橘色＝待求誤差桿 CD（製造誤差 δ）與 DE（溫度變化 ΔT）", 13, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


FIGURES = [
    (fig1_frame, "§1", "只畫斜桿、漏畫垂直桿 → 誤判桁架幾何（m=2j−r 靜定度算錯）"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<8} 攔：{catches}")
