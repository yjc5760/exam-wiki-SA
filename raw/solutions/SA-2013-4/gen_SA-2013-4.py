#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "skills"))
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose
from recipes import truss_forces

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2013-4"

# ══ 解題結果（來自 SA-2013-4.md §4）══
# 節點座標（m）
NODES = {"A": (0, 0), "B": (14, 0), "C": (0, 6), "D": (6, 6)}

# §4 Step4 求得外力（近似整數）
P1, P2, P3 = 80, 100, 150   # kN

# §4 Step5 桿件內力（AD、CD 為題目所求）
F_AD = 146.63   # kN 拉力
F_CD = 58.10    # kN 拉力
# 補充驗算（同一組節點位移代入相同公式；用於 §5 平衡驗算，非題目必答）
F_AB = 18.24    # kN 拉力
F_BD = 77.20    # kN 拉力


def fig1_frame():
    """題目重繪：取代低解析度截圖，把節點座標與支承型式固定下來"""
    cv = Canvas(760, 430, sx=38, ox=90, oy=90, bg="#FFFFFF")
    for s, e in (("A", "B"), ("A", "D"), ("B", "D"), ("C", "D")):
        cv.line(NODES[s], NODES[e], C["member"], 5.5, cap="butt")
    cv.support(NODES["A"], "pin", 0)
    cv.support(NODES["C"], "pin", 0)
    cv.support(NODES["B"], "roller", 0)
    for nm, lab, ax, ay in (("A", "A", -18, -14), ("B", "B", 8, -16),
                             ("C", "C", -18, 14), ("D", "D", 8, 16)):
        cv.dot(NODES[nm], 5.5)
        cv.text(NODES[nm], lab, 16, C["text"], weight="700", dx=ax, dy=ay)
    cv.arrow(NODES["B"], (NODES["B"][0] + 2.4, NODES["B"][1]), C["load"], 3.4, 11)
    cv.math((NODES["B"][0] + 2.4, NODES["B"][1]), "P_{1},d_{1}", 15, C["load"], "start", dx=8, weight="700")
    cv.arrow(NODES["D"], (NODES["D"][0] + 2.4, NODES["D"][1]), C["load"], 3.4, 11)
    cv.math((NODES["D"][0] + 2.4, NODES["D"][1]), "P_{2},d_{2}", 15, C["load"], "start", dx=8, weight="700")
    cv.arrow(NODES["D"], (NODES["D"][0], NODES["D"][1] + 2.4), C["load"], 3.4, 11)
    cv.math((NODES["D"][0], NODES["D"][1] + 2.4), "P_{3},d_{3}", 15, C["load"], "start", dy=14, weight="700")
    cv.dim((0, 0), (6, 0), "6 m", off=-46, label_off=-15)
    cv.dim((6, 0), (14, 0), "8 m", off=-46, label_off=-15)
    cv.dim((0, 0), (0, 6), "6 m", off=-46, label_off=-15)
    cv.text_px(310, 396, "自由度：d_{1}=B 點水平、d_{2}=D 點水平、d_{3}=D 點垂直（皆向右／向上為正）",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_forces():
    """桁架力流圖：AD、CD 為題目所求；AB、BD 為節點 D 平衡之補充驗算"""
    members = [("A", "B", F_AB), ("A", "D", F_AD), ("C", "D", F_CD), ("B", "D", F_BD)]
    loads = [("B", (-1.6, 0), "P_{1}=80"), ("D", (-1.6, 0), "P_{2}=100"), ("D", (0, -1.6), "P_{3}=150")]
    cv = truss_forces(
        NODES, members,
        supports=[("A", "pin", 0), ("C", "pin", 0), ("B", "roller", 0)],
        loads=loads,
        title="桿件內力（單位：kN）— AD、CD 為題目所求，AB、BD 為節點 D 平衡驗算",
        note="節點 D 平衡：ΣFx = -58.10-103.68+61.76 ≈ -100（= -P2）；ΣFy = -103.68-46.32 ≈ -150（= -P3）✓",
        fmt="{:+.2f}",
        path=f"{OUT}/{TAG}-fig-2-forces.svg")
    return f"{OUT}/{TAG}-fig-2-forces.svg"


FIGURES = [
    (fig1_frame,   "§1",   "d1/d2/d3 方向與節點對應錯亂 → K 矩陣行列錯位"),
    (fig2_forces,  "§4-5", "AD/CD 內力正負號（拉/壓）判斷錯誤；節點 D 力平衡對不上 P2,P3"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<40} {section:<6} 攔：{catches}")
