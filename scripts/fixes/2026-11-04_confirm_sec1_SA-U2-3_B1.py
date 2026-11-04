#!/usr/bin/env python3
"""SA-U2-3 批 1（12 題）題目正本確認後處理（exam-problem-split §7）＋解題圖解插入（struct-diagram）
用法：在 repo 根目錄執行  python3 scripts/fixes/2026-11-04_confirm_sec1_SA-U2-3_B1.py
1. <id>-problem.md 判讀狀態「待確認」→「已確認」（使用者 2026-11-04 確認；影響答案三項依使用者選擇定案）
2. question_index.json problemStatus draft → confirmed
3. 解析 §1 改為「指向題目正本＋重繪圖＋常見誤讀＋本解記號」；舊 §1 引用的 png 必須都在 problem.md（assert）；
   舊 §1 內解析自繪的 svg 移到「判讀圖解（解析自繪）」小節
4. 有解題圖解的題目，把圖插在 §5 標題之下
5. SA-2012-3 刪除建立在虛構「EA 相同」條件上的兩段
6. 頁尾加修正日期
可重複執行（已處理過的題目會略過）。"""
import json, os, re, sys
ROOT = os.getcwd()
DATE = "2026-11-04"
DEC = {   # 影響答案的判讀項目：使用者 2026-11-04 明確選擇
    "SA-2006-4": "#5 柱底固接（使用者確認）",
    "SA-2007-4": "#5 B 在 A 正上方（使用者確認）",
    "SA-2012-3": "#2 b 為鉸支承、框身連續（使用者確認）",
}
SW = "桿端彎矩、節點轉角、弦位角一律順時針為正（傾角變位法慣例）。"
Q = {
 "SA-2002-4": dict(alt="門型剛架，A、D 固接，B 點水平 13 kN，柱 I、梁 2I，各 6 m",
   cap="依判讀清單 #1–#7 重繪。攔：A、D 支承誤讀、梁柱慣性矩 I／2I 標反。",
   mis=[("A、D 支承", "固接", "鉸接"), ("彎矩圖受拉側", "柱底外側（迎風側）、柱頂內側；梁 B 端下側、C 端上側", "四處全部畫反（本題舊版解析）")],
   note=SW, sol=("SA-2002-4-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖：柱雙曲率、梁反對稱",
   "左：側推下兩柱雙曲率、梁反對稱，反曲點在柱距底 3.23 m 與梁中點；右：彎矩畫在受拉側。攔：受拉側畫反（柱底畫成內側、梁 B 端畫成上側）。")),
 "SA-2005-2": dict(alt="剛架 A、E 固接、C 鉸支承，B 點 10 N 向下",
   cap="依判讀清單 #1–#8 重繪。攔：C 讀成內鉸、D 讀成鉸接。",
   mis=[("C", "鉸支承（三角形支承）", "框身內鉸"), ("D", "BD 與 ED 剛接之角點", "鉸接")], note=SW),
 "SA-2006-4": dict(alt="剛性梁 A–E 以五根柱支撐，長柱 AF、BG 3 m 落地，短柱 CJ、DK、EL 2 m 落於剛性矮牆頂，A 點 100 kN",
   cap="依判讀清單 #1–#8 重繪，只畫考卷給的東西。攔：長柱高度看成 2 m（矮牆之上才是 2 m）。",
   mis=[("長柱 AF、BG 高度", "3 m（2 m＋1 m）", "2 m"), ("柱底", "固接（考卷未明寫；題目問柱底彎矩比值，鉸接則無意義）", "鉸接")], note=SW),
 "SA-2007-2": dict(alt="剛架 A、B 固接、E 鉸支承，梁 C–E 2 kN/m，AC 中點 8 kN",
   cap="依判讀清單 #1–#6 重繪。攔：均布載重範圍、8 kN 作用點、E 支承誤讀。",
   mis=[("8 kN 作用點", "AC 柱中點（距 A 2 m）", "柱頂 C"), ("均布載重範圍", "C 至 E 全長 12 m", "只在 CD 跨")], note=SW),
 "SA-2007-4": dict(alt="斜柱 AC 剛架，A 斜置固接、B 滾支承在 A 正上方，C 點水平 20 N",
   cap="依判讀清單 #1–#7 重繪。攔：B 的水平位置、A 支承方向誤讀。",
   mis=[("B 水平位置", "A 正上方，BC = 4 m（使用者確認）", "未定位置"), ("AC 彎矩圖", "雙曲率，反曲點距 A 4.38 m", "兩端同為逆時針便畫在同側、無反曲點（本題舊版解析）"),
        ("側移虛功式", "$\\sum M\\,\\delta\\psi + P\\,\\delta\\Delta = 0$", "外功＝內功，再臨場改號（本題舊版解析）")], note=SW,
   sol=("SA-2007-4-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖：斜柱 AC 雙曲率",
   "左：C 沿垂直 AC 方向（右下）移動；右：AC 兩端梁彎矩異號，反曲點距 A 約 4.38 m。攔：把兩端同為逆時針的桿端彎矩畫成同側。")),
 "SA-2008-2": dict(alt="五跨連續梁 A–H，A、H 固接、C～F 滾支，B、G 10 kN，CD、EF 1.2 kN/m",
   cap="依判讀清單 #1–#4 重繪。攔：均布載重範圍、跨距與支承誤讀。",
   mis=[("均布載重範圍", "CD、EF 全跨；DE 無載重", "DE 也有均布載重"), ("集中載重位置", "B、G，距固端 3 m", "跨中")], note=SW,
   sol=("SA-2008-2-fig-2-vm.svg", "載重、剪力圖與彎矩圖",
   "剪力圖反對稱、彎矩圖對稱；DE 跨剪力為 0、彎矩為常數 −0.955 kN·m。攔：不對稱或 DE 跨剪力不為零 → 前面必有錯。")),
 "SA-2009-3": dict(alt="π 型構架，梁 a–d 三跨各 L，a、d 滾支，柱 be、cf 高 L、底部固接，a 點水平 P",
   cap="依判讀清單 #1–#6 重繪。攔：a、d 讀成鉸支（多一個水平束制、側移變零）。",
   mis=[("a、d 支承", "滾支承（只有垂直反力）", "鉸支承")], note=SW,
   sol=("SA-2009-3-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖（P = 100 kN、L = 10 m）",
   "兩柱雙曲率，柱底 275、柱頂 225 kN·m；每柱剪力 50 kN。攔：柱底柱頂畫成同側、或 a、d 端有彎矩。")),
 "SA-2010-2": dict(alt="L 形剛架，A 固接、柱 AC 10 m（EI）、B 為中點，梁 CD 10 m（2EI）、D 滾支",
   cap="依判讀清單 #1–#7 重繪（考卷附圖未畫載重）。攔：B 讀成鉸、D 讀成鉸支。",
   mis=[("B", "柱中點（實心點，非鉸）", "內鉸"), ("D", "滾支承（只有垂直反力）", "鉸支承")], note=SW),
 "SA-2010-3": dict(alt="梯形剛架，A、D 固接，斜柱長 L、傾角 60°，B 點 P、BC 中點 E 2P",
   cap="依判讀清單 #1–#5 重繪。攔：斜柱長度與傾角、E 位置誤讀。",
   mis=[("斜柱 AB、CD", "長 L、傾角 60°（水平投影 L/2）", "長 √3L/2"), ("E", "BC 中點", "B、C 之間任一點")], note=SW),
 "SA-2011-2": dict(alt="剛架 A 固接、D、E 鉸支，AB 2EI，B 點 30 kN，CD 中點 16 kN",
   cap="依判讀清單 #1–#8 重繪。攔：AB 慣性矩、16 kN 作用點、D／E 支承誤讀。",
   mis=[("AB 剛度", "2EI", "EI"), ("16 kN 作用點", "CD 中點（距 C 1.5 m）", "D 點")], note=SW,
   sol=("SA-2011-2-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖",
   "無側移剛架；C 節點 16.40 − 12.70 − 3.70 = 0。攔：C 節點彎矩不平衡、AB 段畫成單一斜率。")),
 "SA-2012-3": dict(alt="封閉矩形框 a–h，b 鉸支、c 滾支，f、g 各 P",
   cap="依判讀清單 #1–#9 重繪。攔：b 讀成框身內鉸、P 不在支承正上方。",
   mis=[("b", "鉸支承、框身於 b 連續（使用者確認）", "框身內鉸"), ("考卷給的條件", "只有「E、I 相同，EI 為常數」", "加上「EA 相同」（本題舊版解析）"),
        ("所求", "㈠ 各桿彎矩＋彎矩圖（20 分）；㈡ 變形曲線並標反曲點（5 分）", "只寫「繪彎矩圖與變形曲線」（本題舊版解析）")], note=SW,
   sol=("SA-2012-3-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖",
   "各角點與中段彎矩均為 PL/2；柱與中段為常數彎矩，反曲點在四段懸伸中點。攔：懸伸段漏掉反曲點、中段受拉側畫反。")),
 "SA-2013-3": dict(alt="剛架 A、D 固接，B 內鉸，梁 BC 2EI 受均布 w，斜桿 CD",
   cap="依判讀清單 #1–#9 重繪。攔：B 內鉸、CD 斜桿方向與固接面誤讀。",
   mis=[("B", "內鉸（空心圓）", "剛接"), ("側移虛功式", "桿端彎矩虛功＋載重虛功＝0，右端 $+0.5wL^2$", "內虛功＝外虛功，右端 $-0.5wL^2$（本題舊版解析）")],
   note=SW + "$R=u/L$，$u$ 為 B 點水平位移（假設向右為正，解出負值即向左）。",
   sol=("SA-2013-3-fig-2-deflected-bmd.svg", "變形形狀與彎矩圖",
   "載重向下，C 往左下移；BC 全跨正彎矩，C 端 +0.128wL²。攔：側移方向反（C 往右上）、C 端畫成負彎矩。")),
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
    d = Q[qid]; p = f"raw/solutions/{qid}/{qid}.md"; s = open(p, encoding="utf-8").read()
    if "## 1. 題目（考卷原文見題目正本）" in s: return False
    m = re.search(r"\n## 1\.[^\n]*\n(.*?)(?=\n## 2)", s, re.S); assert m, qid
    old = m.group(1); prob = open(f"raw/solutions/{qid}/{qid}-problem.md", encoding="utf-8").read()
    for png in re.findall(r"\(([^)]+\.png)\)", old):
        assert os.path.basename(png) in prob, (qid, png)
    own = re.findall(r"(!\[[^\]]*\]\((figs/[^)]+\.svg)\)\s*\n(?:\*[^\n]*\*\s*\n)?)", old + "\n")
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in d["mis"])
    new = (f"\n## 1. 題目（考卷原文見題目正本）\n\n"
           f"> 考卷原文、公式／附表、附圖與判讀清單（已確認）見 [`{qid}-problem.md`]({qid}-problem.md)。本節只列解題時最容易讀錯的地方與本解使用的記號；題意以題目正本為準。\n\n"
           f"![{qid} 重繪題目附圖：{d['alt']}](figs/{qid}-fig-1-problem.svg)\n*重繪自考卷附圖，{d['cap']}*\n\n"
           f"### 常見誤讀\n| 項目 | 正確判讀 | 常見誤讀 |\n|---|---|---|\n{rows}\n\n**本解記號：** {d['note']}\n")
    if own:
        new += "\n### 判讀圖解（解析自繪）\n\n" + "\n".join(o[0].strip() + "\n" for o in own)
    s = s[:m.start()] + new + s[m.end():]
    if "sol" in d:
        fn, alt, cap = d["sol"]
        h = re.search(r"\n## 5\.[^\n]*\n", s); assert h, qid
        blk = f"\n![{qid} {alt}](figs/{fn})\n*圖解：{cap}*\n"
        s = s[:h.end()] + blk + s[h.end():]
    if qid == "SA-2012-3":
        s, k1 = re.subn(r"\n3\. \*\*軸向剛度 \(\$EA\$\) 相同的迷惑性\*\*[^\n]*", "", s)
        s, k2 = re.subn(r"\n### \(三\) 進階探討：EA 的影響\n.*?(?=\n## |\n---|\Z)", "", s, flags=re.S)
        assert k1 == 1 and k2 == 1, (k1, k2)
    what = "§1 改為指向題目正本並放重繪附圖（figs/%s-fig-1-problem.svg）、加常見誤讀" % qid
    if "sol" in d: what += "；§5 補解題圖解 figs/%s" % d["sol"][0]
    if qid == "SA-2012-3": what += "；刪除建立在虛構「EA 相同」條件上的 §2 第 3 點與 §5(三)"
    s = s.rstrip("\n") + f"\n\n*修正日期：{DATE}（{what}；圖由 gen_{qid}.py 產生，可重跑）*\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s); return True

if __name__ == "__main__":
    ids = sys.argv[1:] or list(Q)
    for q in ids:
        print(q, "problem:", confirm_problem(q), " §1:", rewrite(q))
    print("index confirmed:", index_confirm(ids))
