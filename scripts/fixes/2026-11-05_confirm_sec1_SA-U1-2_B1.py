#!/usr/bin/env python3
"""SA-U1-2 批 1（12 題）題目正本確認後處理（exam-problem-split §7）
用法：在 repo 根目錄執行  python3 scripts/fixes/2026-11-05_confirm_sec1_SA-U1-2_B1.py
1. <id>-problem.md 判讀狀態「待確認」→「已確認」（使用者 2026-11-05 確認；影響答案兩項依使用者選擇定案）
2. question_index.json problemStatus draft → confirmed
3. 解析 §1 改為「指向題目正本＋重繪圖＋常見誤讀＋本解記號」；舊 §1 引用的 png 必須都在 problem.md（assert）；
   舊 §1 內解析自繪的 svg 移到「判讀圖解（解析自繪）」小節
   （SA-2016-1、SA-2002-2 已於同日解析勘誤時改好 §1，本腳本略過）
4. 頁尾加修正日期
可重複執行（已處理過的題目會略過）。"""
import json, os, re, sys
DATE = "2026-11-05"
DEC = {"SA-2016-1": "#2 E 為固定端（使用者確認）",
       "SA-2002-2": "#3 B 為鉸支承、#5 A–B 虛線不是桿件（使用者確認）"}
NOTE = "記號與正負號約定沿用 §4。"
Q = {
 "SA-2002-1": dict(alt="內鉸剛架，A、H 鉸支承、F 內鉸；C 點 10 kN 向右、E 點 8 kN 向下、C–D 分布力矩、B 與 F 兩側力偶、G–H 水平均布 2 kN/m",
   cap="依判讀清單 #1–#14 重繪。攔：C–D 分布力矩讀成均布力、F 兩側力偶轉向讀反。",
   mis=[("C–D 載重", "均布彎矩 2 kN-m/m（順時針），不進力平衡", "均布力 2 kN/m"),
        ("F 兩側力偶", "梁端 4 kN-m 逆時針、柱頂 4 kN-m 順時針，各作用在所屬桿端", "同向，或視為互相抵銷"),
        ("E 位置", "距 C 3 m（梁中點）", "D 點")]),
 "SA-2003-2": dict(alt="剛梁 A–B–C 以連桿 AD、AE、BE 支撐，D、E 鉸支承，C 端受 F 向下",
   cap="依判讀清單 #1–#9 重繪。攔：AE 斜桿接錯節點、F 讀成節點名稱。",
   mis=[("F", "C 端向下的力（大小 F）", "節點名稱"), ("AE", "A 至 E 的斜桿，長 5λ", "接到 B 或 D")]),
 "SA-2003-3": dict(alt="跨度 32 m、高 8 m 的菱形腹桿桁架，左鉸右滾，下弦 8 m、16 m 處各 2t",
   cap="依判讀清單 #1–#8 重繪。攔：a、b 桿位置認錯、右端支承讀成鉸。",
   mis=[("桿 a", "左側水平腹桿 (4,4)–(12,4)", "上弦桿"), ("桿 b", "(8,8)–(12,4) 斜桿", "(4,4)–(8,8) 斜桿"),
        ("右端支承", "滾支承", "鉸支承")]),
 "SA-2004-1": dict(alt="柱 AB 4 m 固定於 A、B 鉸接梁 B–C–右端，C 滾支承；梁全長 2 t/m，柱中點 4t 向右",
   cap="依判讀清單 #1–#7 重繪。攔：均布載重只算到 C、4t 作用點讀成柱頂。",
   mis=[("均布載重範圍", "梁全長 6 m（含 C 外伸 2 m）", "只到 C"), ("4t 作用點", "柱中點（距 A 2 m）", "柱頂 B")],
   note="梁右端考卷未標名，本解記為 D；" + NOTE),
 "SA-2004-3": dict(alt="複合梁 A 固定、B 內鉸、C 彈簧支承、D 自由端；AB 30 m（2EI）、BC 18 m、CD 12 m；B、D 各 36t",
   cap="依判讀清單 #1–#8 重繪。攔：B 讀成剛接、AB 段 2EI 漏讀。",
   mis=[("B", "內鉸（AB、BC 鉸接）", "剛接"), ("AB 剛度", "2EI", "EI")]),
 "SA-2010-1": dict(alt="桁架 G 鉸支承、B 靠右側垂直牆的滾支承，H 點 30 kN 向下，格距 2 m",
   cap="依判讀清單 #1–#6 重繪。攔：B 的反力方向讀錯、多畫 E–H 豎桿。",
   mis=[("B 支承", "靠右側垂直牆的滾支承，只有水平反力", "只有垂直反力"), ("E–H", "兩點之間沒有桿", "有豎桿")]),
 "SA-2012-1": dict(alt="梁 a 固接、c 內鉸、d 滾支承、e 自由端，各段 4 m；b、e 各 40 kN；a–c 段 2EI、c–e 段 EI",
   cap="依判讀清單 #1–#7 重繪。攔：c 讀成剛接、剛度分段讀錯。",
   mis=[("c", "內鉸", "剛接"), ("剛度", "a–c 段 2EI、c–e 段 EI", "全梁同 EI")]),
 "SA-2013-1": dict(alt="門型桁架，a、i 鉸支承（i 高 10 m），上弦 c–g 受 5、10、10、10、5 kN",
   cap="依判讀清單 #1–#7 重繪。攔：i 讀成滾支承、a–b 中段多一個節點。",
   mis=[("i 支承", "鉸支承，比 a 高 10 m", "滾支承"), ("a–b", "一根連續豎桿，l 的高度處沒有節點", "中段有節點")]),
 "SA-2014-1": dict(alt="屋架桁架 6@12 m，上弦 H、L 高 12 m，I、K 高 17 m，J 高 22 m；A 鉸、G 滾",
   cap="依判讀清單 #1–#8 重繪（考卷附圖未畫載重）。攔：上弦高度讀錯、斜桿方向讀反。",
   mis=[("上弦高度", "H、L 12 m；I、K 17 m；J 22 m", "等高或線性變化"), ("斜桿", "HC、ID、KD、LE（皆向中央 D 傾斜）", "方向畫反")]),
 "SA-2015-1": dict(alt="桁架 A 鉸、C 滾支承，B 高 3 m，D 點 50 kN 向下，B 點水平力 T 向左",
   cap="依判讀清單 #1–#10 重繪。攔：T 方向讀反、C 支承讀成鉸。",
   mis=[("T 方向", "圖上箭頭向左", "向右"), ("C 支承", "滾支承（下陷 0.4 cm）", "鉸支承")]),
}

def confirm_problem(qid):
    p = f"raw/solutions/{qid}/{qid}-problem.md"; s = open(p, encoding="utf-8").read()
    if "**已確認**" in s: return False
    old = "| 判讀狀態 | **待確認**（"
    assert old in s, qid
    extra = f"；影響答案項目定案：{DEC[qid]}" if qid in DEC else ""
    s = s.replace(old, f"| 判讀狀態 | **已確認**（{DATE} 使用者確認{extra}。原轉錄：", 1)
    for k in ("不確定（影響答案，請確認）", "確定（解讀）"):
        s = s.replace(f"| {k} |", f"| {k}；使用者確認 |")
    s = s.rstrip("\n") + f"\n*確認：{DATE} 使用者確認*\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s); return True

def index_confirm(ids):
    p = "raw/json/question_index.json"; s = open(p, encoding="utf-8").read(); n = 0
    for q in ids:
        i = s.index(f'"moduleId": "{q}"'); a = s.rfind("{", 0, i); j = s.index("}", i)
        obj = s[a:j + 1]; o2 = obj.replace('"problemStatus": "draft"', '"problemStatus": "confirmed"')
        if o2 != obj: s = s[:a] + o2 + s[j + 1:]; n += 1
    json.loads(s); open(p, "w", encoding="utf-8", newline="").write(s); return n

def rewrite(qid):
    p = f"raw/solutions/{qid}/{qid}.md"; s = open(p, encoding="utf-8").read()
    if "## 1. 題目（考卷原文見題目正本）" in s: return False
    d = Q[qid]
    m = re.search(r"\n## 1\.[^\n]*\n(.*?)(?=\n## 2)", s, re.S); assert m, qid
    old = m.group(1); prob = open(f"raw/solutions/{qid}/{qid}-problem.md", encoding="utf-8").read()
    for png in re.findall(r"\(([^)]+\.png)\)", old):
        assert os.path.basename(png) in prob, (qid, png)
    own = re.findall(r"(!\[[^\]]*\]\((figs/[^)]+\.svg)\)\s*\n(?:\s*\n)?(?:\*[^\n]*\*\s*\n)?)", old + "\n")
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in d["mis"])
    new = (f"\n## 1. 題目（考卷原文見題目正本）\n\n"
           f"> 考卷原文、公式／附表、附圖與判讀清單（已確認）見 [`{qid}-problem.md`]({qid}-problem.md)。本節只列解題時最容易讀錯的地方與本解使用的記號；題意以題目正本為準。\n\n"
           f"![{qid} 重繪題目附圖：{d['alt']}](figs/{qid}-fig-1-problem.svg)\n*重繪自考卷附圖，{d['cap']}*\n\n"
           f"### 常見誤讀\n| 項目 | 正確判讀 | 常見誤讀 |\n|---|---|---|\n{rows}\n\n**本解記號：** {d.get('note', NOTE)}\n")
    if own:
        new += "\n### 判讀圖解（解析自繪）\n\n" + "\n".join(o[0].strip() + "\n" for o in own)
    s = s[:m.start()] + new + s[m.end():]
    gen = f"gen_{qid}_problem.py" if os.path.exists(f"raw/solutions/{qid}/gen_{qid}_problem.py") else f"gen_{qid}.py"
    what = "§1 改為指向題目正本並放重繪附圖（figs/%s-fig-1-problem.svg）、加常見誤讀" % qid
    if own: what += "；原 §1 解析自繪圖移至「判讀圖解（解析自繪）」"
    s = s.rstrip("\n") + f"\n\n*修正日期：{DATE}（{what}；圖由 {gen} 產生，可重跑）*\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s); return True

if __name__ == "__main__":
    ids = sys.argv[1:] or (list(Q) + list(DEC))
    for q in ids:
        print(q, "problem:", confirm_problem(q), " §1:", rewrite(q) if q in Q else "（勘誤時已改）")
    print("index confirmed:", index_confirm(ids))
