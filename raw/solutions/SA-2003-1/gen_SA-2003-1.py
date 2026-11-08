#!/usr/bin/env python3
"""SA-2003-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2003-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2003-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2003-1"

# ── 判讀清單 #1–#8 ──（單位 ft）
N_ = {"a": (0, 0), "b": (30, 0), "c": (60, 0), "d": (90, 0),                 # #3 三跨各 30 ft
      "p1": (15, 0), "p2": (40, 0), "p3": (50, 0), "p4": (75, 0)}            # #4 #6 #7 載重點
SPEC = dict(
    nodes=N_,
    members=[{"ij": ("a", "b")}, {"ij": ("b", "c")}, {"ij": ("c", "d")}],
    supports=[("a", "fixed"), ("d", "fixed"), ("b", "pin", 0), ("c", "pin", 0)],   # #1 #2（b、c 鉸／滾不分）
    udl=[("b", "c", 4.0, None)],                                          # #5
    loads=[("p1", (0, -7), "8^{k}", (0, -12)), ("p4", (0, -7), "8^{k}", (0, -12)),     # #4 #7
           ("p2", (0, -10), "3^{k}", (0, -12)), ("p3", (0, -10), "3^{k}", (0, -12))],  # #6
    labels={"a": (-24, -14), "b": (0, 44), "c": (0, 44), "d": (24, -14)},
    ptexts=[((64, 5.2), "w = 1 k/ft", 15, C["load"], "start")],
    dims=[((0, 0), (15, 0), "15 ft", 70), ((15, 0), (30, 0), "15 ft", 70),
          ((30, 0), (40, 0), "10 ft", 70), ((40, 0), (50, 0), "10 ft", 70), ((50, 0), (60, 0), "10 ft", 70),
          ((60, 0), (75, 0), "15 ft", 70), ((75, 0), (90, 0), "15 ft", 70)],
    extra_pts=[(-4, 12), (94, -8)])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 360,
                              note="a、d 固定端；b、c 支承符號鉸／滾不分（只受垂直載重，不影響答案）；EI＝常數",
                              margins=(60, 60, 60, 110))

FIGURES = [(fig1_problem, "3k 位置讀成跨中、均佈只畫半跨、a、d 讀成鉸支承")]

# ── 解題圖（階段 E，2026-11-08）：勁度法重解（EI = 1；集中載重處加節點），assert 對照 SA-2003-1.md §4 桿端彎矩（順時針為正）：
#    M_ab −8.33、M_ba +73.33、M_bc −73.33、M_cb +73.33、M_cd −73.33、M_dc +8.33 k-ft（= ∓25/3、±220/3）
def _solve():
    from frame2d import Frame
    f = Frame()
    pts = {"a": 0, "p1": 15, "b": 30, "q1": 40, "q2": 50, "c": 60, "p2": 75, "d": 90}
    for n, x in pts.items(): f.node(n, x, 0)
    f.support("a", 1, 1, 1); f.support("d", 1, 1, 1); f.support("b", 0, 1, 0); f.support("c", 0, 1, 0)
    seq = list(pts)
    for i, j in zip(seq, seq[1:]): f.member(i + j, i, j, 1.0, w=(1.0 if pts[i] >= 30 and pts[j] <= 60 else 0.0))
    f.load("p1", fy=-8); f.load("p2", fy=-8); f.load("q1", fy=-3); f.load("q2", fy=-3)
    f.solve()
    cw = lambda nm, end: -f.end[nm][2 if end == 0 else 5]                     # 桿端彎矩，順時針為正
    got = [cw("ap1", 0), cw("p1b", 1), cw("bq1", 0), cw("q2c", 1), cw("cp2", 0), cw("p2d", 1)]
    for g_, e_ in zip(got, [-25/3, 220/3, -220/3, 220/3, -220/3, 25/3]): assert abs(g_ - e_) < 1e-6, (got,)
    return f

def fig2_bmd():
    from beamfig import beam_strip
    f = _solve()
    names = [m["name"] for m in f.M]
    return beam_strip(f, names, f"{OUT}/{TAG}-fig-2-bmd.svg", "圖 2　SA-2003-1 變形形狀與彎矩圖", W=960, H1=230, H2=370, prec=2, yc=0.56,
        supports=[("a", "fixed"), ("b", "roller"), ("c", "roller"), ("d", "fixed")],
        mlabels=[("ap1", 0.0, "R", True), ("ap1", 1.0, "C", False), ("p1b", 1.0, "C", True), ("q1q2", 0.5, "C", True),
                 ("q2c", 1.0, "C", False), ("p2d", 1.0, "L", True)],
        sub_def="中跨載重較重：b、c 節點向中跨轉動（對稱）",
        sub_bmd="a −8.33 → 載重點 +19.17 → b −73.33 → 中跨中點 +69.17 → c −73.33 → d −8.33（k-ft）",
        note="a 端彎矩只有 −8.33：b 點向中跨轉動，把 ab 跨的 a 端彎矩從固端 −30 減小", unit_m="k-ft")

FIGURES.append((fig2_bmd, "a、d 端彎矩照固端 30 寫；b、c 支承誤當成負彎矩較小的一側；中跨極值位置（三分點載重＋均佈）算錯"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)
