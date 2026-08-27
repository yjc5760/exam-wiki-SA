#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2012-1 — 含內鉸、變剛度外伸梁 三聯圖（載重／SFD／BMD）"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from recipes import beam_vm

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2012-1"

L = 4          # 每小段長度（§1）
P = 40         # b、e 點集中載重（§1）

# 節點座標
xa, xb, xc, xd, xe = 0, L, 2*L, 3*L, 4*L

# §Step2 彎矩函數（分段，以下方受拉為正）
M_ab = P * 4          # 160，a-b 段（常數，因 R_a=0）
M_c = 0               # b-c 段線性遞減至 0（內鉸條件）
M_d = -P * L          # -160，c-d 段線性遞減至 -160
M_e = 0               # d-e 段線性遞增回 0

xs = [xa, xb, xb, xc, xc, xd, xd, xe]
V  = [0,  0,  -P, -P, -P, -P, P,  P]      # §Step2 對 M(x) 微分（b、d 兩處因外力/反力跳躍）
M  = [0, M_ab, M_ab, M_c, M_c, M_d, M_d, M_e]


def fig1_beam():
    """梁三聯圖：載重／SFD／BMD。
    攔下的錯：剪力跳躍位置與彎矩極值/內鉸零彎矩位置不吻合 → 反力或分段彎矩式算錯。"""
    beam_vm(
        span=xe, xs=xs, V=V, M=M,
        supports=[(xa, "fixed"), (xd, "roller")],
        point_loads=[(xb, "40 kN"), (xe, "40 kN")],
        title="SA-2012-1：a 固定端／c 內鉸／d 滾支承 外伸梁",
        note="c 點 (x=8m) 為內鉸，BMD 在此精確通過 0，可交叉驗證反力與分段彎矩式無誤",
        v_unit="kN", m_unit="kN-m",
        key_V=[(xb, "0→−40", -18), (xd, "−40→+40", 18)],
        key_M=[(xa, "0", -16), (xb, "160", -16), (xc, "0", 18),
               (xd, "−160", 16), (xe, "0", -16)],
        path=f"{OUT}/{TAG}-fig-1-beam-vm.svg")
    return f"{OUT}/{TAG}-fig-1-beam-vm.svg"


FIGURES = [
    (fig1_beam, "§Step 1/2", "內鉸 c 處 BMD 未精確歸零 → 反力方向或分段彎矩式有誤"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<10} 攔：{catches}")
