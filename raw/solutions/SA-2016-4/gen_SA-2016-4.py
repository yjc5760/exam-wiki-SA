#!/usr/bin/env python3
"""SA-2016-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2016-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2016-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-4"

# ── 判讀清單 #1–#13 ──（座標為圖面格線單位，考卷沒有尺寸）
N_ = {"D": (0, 2), "E": (1, 2), "F": (2, 2), "G": (3, 2), "H": (4, 2),          # #4
      "A": (1, 3), "B": (2, 3), "C": (3, 3), "I": (2, 1), "J": (3, 1), "K": (2, 0), "L": (3, 0),
      "P": (5, 0), "M": (4, 1.3), "N": (5, 1.3), "O": (6, 1.3)}
TR = [("A", "B"), ("B", "C"), ("A", "D"), ("A", "E"), ("A", "F"), ("B", "F"), ("C", "F"), ("C", "G"), ("C", "H"),  # #5
      ("D", "E"), ("E", "F"), ("F", "G"), ("G", "H"),                                                           # #6
      ("F", "I"), ("G", "J"), ("I", "J"), ("F", "J"), ("G", "I"),                                               # #7 交叉不相連
      ("I", "K"), ("J", "L"), ("K", "L"), ("I", "L"), ("J", "K"),                                               # #8 交叉不相連
      ("L", "P"), ("N", "P")]                                                                                   # #9
SPEC = dict(
    nodes=N_, truss=TR,
    members=[{"ij": ("M", "O"), "thick": True}],                                                           # #11 MNO 梁
    joints=[k for k in N_ if k not in ("M", "O")],
    supports=[("A", "pin", 180), ("C", "pin", 180), ("D", "pin", 0), ("M", "pin", 0), ("O", "roller", 0)],  # #1–#3
    loads=[("A", (0.75, 0), "100 kN", (-34, -14)), ("D", (0.75, 0), "100 kN", (-34, -14)),                 # #12
           ("E", (0, -0.75), "100 kN", (0, 16), True), ("N", (0, -0.75), "100 kN", (0, -14))],
    labels={"A": (-14, -12), "B": (0, -16), "C": (16, -12), "D": (-10, -16), "E": (12, 15), "F": (-12, 16),
            "G": (13, 15), "H": (15, -12), "I": (-14, 0), "J": (15, 0), "K": (0, 18), "L": (0, 18),
            "P": (15, 0), "M": (-16, -12), "N": (12, -14), "O": (16, -12)},
    extra_pts=[(-1.0, 3.5), (6.4, -0.3)])

def _post(cv, N):
    spring_between(cv, N["H"], N["M"])                                                                    # #10
    x, y = cv.P(((N["H"][0] + N["M"][0]) / 2, (N["H"][1] + N["M"][1]) / 2)); cv.math_px(x + 16, y, "k", 16, C["text"], "start")

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 700, 520, post=_post,
                              note=["載重只有 A、D 向右與 E、N 向下各 100 kN（I 點沒有載重）；兩組交叉斜桿交點不是節點",
                                    "考卷沒有尺寸，節點位置照圖面格線"],
                              margins=(90, 60, 50, 110))

FIGURES = [(fig1_problem, "把 E 點載重讀到 I 點、交叉斜桿的交點當成節點")]

# ── 解題圖（階段 E，2026-11-08）：直接勁度法（全結構，五組隨機 EA、k；梁 MNO 以 N 點彈性支承模擬），assert 對照 SA-2016-4.md §4–§5：只有 AE = +100 kN，其餘 24 桿與彈簧 0 ──
def _solve(seed):
    import numpy as np
    r = np.random.default_rng(seed); names = list(N_); idx = {n: i for i, n in enumerate(names)}; n = 2 * len(names)
    K = np.zeros((n, n)); F = np.zeros(n); EA = {m: r.uniform(0.5, 5) for m in TR}
    def add(i, j, c, s_, kk):
        v = np.array([c, s_]); kl = kk * np.outer(v, v); d = [2*idx[i], 2*idx[i]+1, 2*idx[j], 2*idx[j]+1]
        K[np.ix_(d, d)] += np.block([[kl, -kl], [-kl, kl]])
    for a, b in TR:
        (x1, y1), (x2, y2) = N_[a], N_[b]; L = np.hypot(x2 - x1, y2 - y1); add(a, b, (x2 - x1) / L, (y2 - y1) / L, EA[(a, b)] / L)
    ks = r.uniform(0.1, 10); add("H", "M", 0, -1, ks)
    K[2*idx["N"], 2*idx["N"]] += 1e3; K[2*idx["N"]+1, 2*idx["N"]+1] += r.uniform(0.1, 10)     # 簡支梁 MNO 對 N 的勁度
    for nd, (fx, fy) in {"A": (100, 0), "D": (100, 0), "E": (0, -100), "N": (0, -100)}.items(): F[2*idx[nd]] += fx; F[2*idx[nd]+1] += fy
    fixed = {"A", "C", "D", "M", "O"}; free = [d for d in range(n) if names[d // 2] not in fixed]
    u = np.zeros(n); u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    out = {}
    for a, b in TR:
        (x1, y1), (x2, y2) = N_[a], N_[b]; L = np.hypot(x2 - x1, y2 - y1); c, s_ = (x2 - x1) / L, (y2 - y1) / L
        out[(a, b)] = EA[(a, b)] / L * (c * (u[2*idx[b]] - u[2*idx[a]]) + s_ * (u[2*idx[b]+1] - u[2*idx[a]+1]))
    out["spring"] = ks * (u[2*idx["H"]+1] - u[2*idx["M"]+1])
    return out

def fig2_loadpath():
    from recipes import truss_forces
    for seed in range(5):
        o = _solve(seed)
        assert abs(o[("A", "E")] - 100) < 1e-6 and all(abs(v) < 1e-6 for k, v in o.items() if k != ("A", "E")), seed
    o = _solve(0); Nf = {k: (100.0 if k == ("A", "E") else 0.0) for k in TR}
    class _Fmt:
        def format(self, v): return "+100" if v > 0 else ""
    cv = truss_forces(N_, [(i, j, Nf[(i, j)]) for i, j in TR], supports=[], loads=[], fmt=_Fmt(), path=None, W=760, H=600, margin=110,
                      title=f"圖 2　{TAG} 載重傳力路徑與零桿（灰虛線＝零桿，共 24 根）",
                      note="只有 AE 受 100 kN 拉；A、D 的水平力直接進支承，N 的力由梁 MNO 傳給 M、O；彈簧 H–M 力 0")
    cv.line(N_["M"], N_["O"], C["member"], 7.0, cap="butt")
    for nd, kind, ang in (("A", "pin", 180), ("C", "pin", 180), ("D", "pin", 0), ("M", "pin", 0), ("O", "roller", 0)):
        cv.support(N_[nd], kind, ang, 14)
    spring_between(cv, N_["H"], N_["M"])
    for nd, (dx, dy), (lx, ly), col in (("A", (0.9, 0), (0, -12), C["load"]), ("D", (0.9, 0), (0, -12), C["load"]),
                                        ("E", (0, -0.9), (-34, 6), C["load"]), ("N", (0, -0.9), (34, 6), C["load"])):
        p = N_[nd]; cv.arrow((p[0] - dx, p[1] - dy) if dx else p, p if dx else (p[0], p[1] + dy), col, 3.0, 11)
        cv.math_px(cv.X(p[0] - dx / 2 if dx else p[0]) + lx, cv.Y(p[1] + (dy if dy else 0)) + ly, "100 kN", 13, col, weight="700")
    for nd, txt, (lx, ly) in (("A", "→ 支承 A", (-66, 30)), ("D", "→ 支承 D", (-6, 34)), ("N", "→ M、O", (40, -22))):
        cv.text_px(cv.X(N_[nd][0]) + lx, cv.Y(N_[nd][1]) + ly, txt, 12.5, C["accent"], weight="700")
    path = f"{OUT}/{TAG}-fig-2-loadpath.svg"; cv.save(path); return path

FIGURES.append((fig2_loadpath, "口訣判出 BF、LP、NP 三根就停；把 E 點載重讀到 I 點（I 有載重時 FI、IK、IL 都會受力）"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
