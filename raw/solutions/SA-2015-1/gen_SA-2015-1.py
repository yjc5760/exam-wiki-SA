#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2015-1 — 虛設系統（D點單位力）桿件內力圖"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from recipes import truss_forces

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2015-1"

# 幾何（§1 圖說：AC=4m, CD=4m, BC=3m ⇒ 3-4-5 三角形）
nodes = {"A": (0, 0), "B": (4, 3), "C": (4, 0), "D": (8, 0)}

# 虛設系統內力 u_i（§Step 2，D 點施加向下單位力 1 所得）
u = {"AB": 5/3, "BC": -2, "AC": -4/3, "BD": 5/3, "CD": -4/3}
members = [("A", "B", u["AB"]), ("B", "C", u["BC"]), ("A", "C", u["AC"]),
           ("B", "D", u["BD"]), ("C", "D", u["CD"])]


def fig1_truss():
    """虛設系統之桿件內力圖（u_i）。
    攔下的錯：桿件拉壓判斷錯、或節點法力臂/分量算錯導致 u_i 正負號有誤。"""
    truss_forces(
        nodes, members,
        supports=[("A", "pin", 0), ("C", "roller", 0)],
        loads=[("D", (0, -0.9), "1")],
        title="虛設系統：於 D 點施加單位力後之桿件內力 u_i",
        note="A 為鉸支承、C 為滾支承；u_i 正值為拉力、負值為壓力（本圖無零桿）",
        path=f"{OUT}/{TAG}-fig-1-virtual-truss.svg", fmt="u={:+.3g}")
    return f"{OUT}/{TAG}-fig-1-virtual-truss.svg"


FIGURES = [
    (fig1_truss, "§Step 2", "桿件拉壓/力臂判斷錯 → u_i 正負號有誤，虛功方程式全盤皆錯"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<10} 攔：{catches}")
