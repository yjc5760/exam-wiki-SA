#!/usr/bin/env python3
"""SA-2010-1：桁架力流圖（struct-diagram，2026-11-05）
桿力取自 SA-2010-1.md §4「全桿件軸力一覽」（2026-11-05 勘誤後），以節點法聯立重算核對後才畫。
用法：python3 gen_SA-2010-1_truss.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from recipes import truss_forces
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2010-1"
r2 = math.sqrt(2)
N_ = {"G": (0, 0), "H": (4, 0), "C": (0, 2), "D": (2, 2), "E": (4, 2), "F": (6, 2), "A": (2, 4), "B": (6, 4)}
# ── §4 全桿件軸力一覽（kN，拉＋）──
F_ = {("A", "B"): -20, ("A", "C"): -10*r2, ("A", "E"): 10*r2, ("E", "B"): -10*r2, ("B", "F"): 10,
      ("C", "D"): 10, ("D", "E"): -30, ("E", "F"): -10, ("C", "G"): -10, ("G", "D"): -20*r2,
      ("D", "H"): 20*r2, ("G", "H"): -10, ("H", "F"): 10*r2}
P = 30.0
Bx, Gx, Gy = -30.0, 30.0, 30.0       # §4 步驟 1

def check():
    """每個節點平衡殘差（含反力與載重），全部須為 0，否則不畫。"""
    R = {n: [0.0, 0.0] for n in N_}
    for (i, j), f in F_.items():
        (xi, yi), (xj, yj) = N_[i], N_[j]; L = math.hypot(xj-xi, yj-yi)
        ux, uy = (xj-xi)/L, (yj-yi)/L
        R[i][0] += f*ux; R[i][1] += f*uy; R[j][0] -= f*ux; R[j][1] -= f*uy
    R["B"][0] += Bx; R["G"][0] += Gx; R["G"][1] += Gy; R["H"][1] -= P
    worst = max(abs(v) for r in R.values() for v in r)
    assert worst < 1e-9, f"節點不平衡 {worst}"

def fig2_truss():
    check()
    mem = [(i, j, f) for (i, j), f in F_.items()]
    return truss_forces(N_, mem, supports=[("G", "pin", 0), ("B", "roller", 90)],
                        loads=[("H", (0, -1.0), "30 kN")], fmt="{:+.1f}",
                        title=f"圖 2　{TAG} 桿力分布（kN，拉＋）",
                        note="G 點接 CG、GD、GH 三桿，全桁架沒有零力桿；AC −14.1、BF +10、DE −30",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=760, H=560)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_truss(); print(f"{TAG}-fig-2-truss.svg 攔：節點 G 漏 GH 桿誤判 AC、AB、AE、CG 為零桿")
