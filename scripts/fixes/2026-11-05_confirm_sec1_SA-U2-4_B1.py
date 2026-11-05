#!/usr/bin/env python3
"""SA-U2-4 批 1（14 題）題目正本確認後處理（exam-problem-split §7）
用法：在 repo 根目錄執行  python3 scripts/fixes/2026-11-05_confirm_sec1_SA-U2-4_B1.py
1. <id>-problem.md 判讀狀態「待確認」→「已確認」（使用者 2026-11-05 確認；影響答案項目依使用者選擇定案）
2. question_index.json problemStatus draft → confirmed
3. 解析 §1 改為「指向題目正本＋重繪圖＋常見誤讀＋本解記號」；舊 §1 引用的 png 必須都在 problem.md（assert）；
   舊 §1 內解析自繪的 svg 移到「判讀圖解（解析自繪）」小節
4. SA-2012-4：刪除建立在加字「題幹明示不考慮軸向變形」上的敘述（§3 陷阱三、§5），改為依題文「二個自由度」
5. 頁尾加修正日期（以「§1 改為指向題目正本」開頭）
可重複執行（已處理過的題目會略過）。"""
import json, os, re, sys
DATE = "2026-11-05"
DEC = {"SA-2009-4": "#3 ac = 3 m（c 與 b 同高，考卷未標；使用者確認）",
       "SA-2024-4": "解析答錯題，使用者決定依考卷整題重解（P−Δ 側推曲線，階段 C）",
       "SA-2025-4": "解析座標 x、y 與考卷對調，使用者決定數值不動、§1 加座標對照"}
NOTE = "記號與正負號約定沿用 §4。"
Q = {
 "SA-2004-4": dict(alt="水平梁 A 固定、B 滾支承；C 距 A 為 L，下接軸力彈簧 k；AC 段 EI、CB 段 3EI（長 2L）；w 作用於 A–B 全長",
   cap="依判讀清單 #1–#8 重繪。攔：C 讀成內鉸、CB 段 3EI 漏讀、w 只算到 C。",
   mis=[("C 點", "連續節點（梁不斷），下接軸力彈簧 k = 12EI/L³", "內鉸"), ("CB 剛度", "3EI（長 2L）", "與 AC 同為 EI"),
        ("w 範圍", "A 到 B 全長 3L", "只作用於 AC 或 CB")]),
 "SA-2008-4": dict(alt="剛架 A 固定、AB 柱 4 m、B 剛接、BC 梁 6 m、C 鉸支承；BC 全長 1 kN/m",
   cap="依判讀清單 #1–#7 重繪。攔：C 讀成滾支承、均布載重範圍讀錯。",
   mis=[("C 支承", "鉸支承（水平、垂直皆束制）", "滾支承"), ("軸向變形", "考卷沒寫；考卷也沒給 A", "當成題目條件")],
   note="本解假設不計軸向與剪力變形（考卷未寫，也沒給斷面積 A，只能如此假設）；" + NOTE),
 "SA-2009-4": dict(alt="三桿桁架 a 為自由節點受 100 kN 向下；d（左牆）、b（右牆，高 3 m）、c（天花板，a 正上方）皆鉸支承；位移編號 1–8",
   cap="依判讀清單 #1–#8 重繪。攔：支承方向讀錯、位移編號對錯節點；ac = 3 m 是由 c 與 b 同高推定（考卷未標）。",
   mis=[("ac 長度", "3 m（c 與 b 同高；考卷未標，使用者確認）", "任取或量圖比例"), ("位移編號", "a：1、2；b：3、4；c：5、6；d：7、8", "對錯節點")]),
 "SA-2010-4": dict(alt="三桿桁架 A 為頂點，受 225 kN 向下、100 kN 向右；B(−3,−4)、C(0,−4)、D(4,−3) 皆鉸支承",
   cap="依判讀清單 #1–#6 重繪。攔：C 高程讀錯（AC 長度）、載重方向讀反。",
   mis=[("AC 長度", "4 m（C 與 B 同高；考卷未直接標）", "3 m"), ("D 位置", "A 右方 4 m、下方 3 m", "與 B、C 同高")]),
 "SA-2011-4": dict(alt="三桿桁架 A(3,4) 為自由節點；B(0,4) 接左側牆、C(0,0)、D(6,0) 皆鉸支承；AC 桿短 0.02 m；自由度 1–8",
   cap="依判讀清單 #1–#9 重繪。攔：D 讀成滾支承（舊截圖游標壓在 D）、自由度編號對錯節點。",
   mis=[("D 支承", "鉸支承", "滾支承（舊截圖游標壓在 D）"), ("作用", "只有 AC 桿短 0.02 m，沒有外力", "另加外力")]),
 "SA-2012-4": dict(alt="剛架 a 固定、ab 柱長 L、bc 梁 L/2（EI）、cd 剛性桿 L/2（EI = ∞）、d 鉸支承；R₁、r₁ 在 b、R₂、r₂ 在 d，皆順時針",
   cap="依判讀清單 #1–#8 重繪。攔：d 讀成滾支承、cd 剛桿位置讀錯、自由度轉向讀反。",
   mis=[("方法", "考卷沒有指定方法，只求勁度矩陣", "題目指定直接勁度法"), ("軸向變形", "考卷沒寫；題文「二個自由度」已隱含不計", "題幹明示不考慮軸向變形"),
        ("r₁、r₂", "b、d 的轉角，皆順時針", "逆時針")]),
 "SA-2013-4": dict(alt="桁架 A 鉸、B 滾（14 m 處）、C 鉸（A 正上方 6 m）、D(6,6)；d₁ 為 B 水平、d₂、d₃ 為 D 水平與垂直",
   cap="依判讀清單 #1–#8 重繪。攔：CD 長度讀錯、d₁ 位置或 d₂、d₃ 方向對錯。",
   mis=[("CD 長度", "6 m（C 在 A 正上方；考卷未直接標）", "量圖比例"), ("d₁", "B 點水平（B 為滾支承）", "D 點")]),
 "SA-2015-4": dict(alt="構架 A、C、D 固定；AB、BC 在 B 剛接，BD 以抗扭彈簧與水平線性彈簧接 B；w 作用於 AB 全長，P 作用於 BD 中點；各桿長 L",
   cap="依判讀清單 #1–#9 重繪。攔：B–BD 接合讀成剛接或鉸接、P 作用點與 w 範圍讀錯。",
   mis=[("B–BD 接合", "抗扭彈簧 kθ＋水平線性彈簧 ks，無垂直力傳遞", "剛接或鉸接"), ("P 位置", "BD 中點（距 B 為 L/2）", "D 點或 B 點")]),
 "SA-2018-2": dict(alt="Z 字形構架 A 在上固定、D 在下固定、B、C 剛接，各桿長 L；P 向下作用於 BC 中點",
   cap="依判讀清單 #1–#7 重繪。攔：Z 字形讀成鏡射對稱、P 作用點讀錯。",
   mis=[("固定端位置", "A 在上、D 在下（點對稱 Z 字形）", "兩柱底都固定（門型）"), ("P 位置", "BC 中點", "B 或 C")]),
 "SA-2019-4": dict(alt="構架 A 固定、C 鉸、E 滾；B 處柱頂與梁 BD 以零長度旋轉彈簧相接；P、Q 作用於柱中點、w 作用於 DE、R 作用於 E；右格為自由度 d₁–d₄ 與元素 ①–⑤",
   cap="依判讀清單 #1–#11 重繪。攔：C 讀成固定端、B 讀成剛接、轉角正向讀反。",
   mis=[("C 支承", "鉸支承", "固定端"), ("B 接頭", "柱頂與梁之間的旋轉彈簧 10EI/L（零長度）", "剛接"),
        ("d₂、d₃、d₄", "皆逆時針為正", "順時針")]),
 "SA-2022-4": dict(alt="三層構架四根柱線 a、e、m、n 間距 4 m，樓高各 3.6 m；第一層只有 a–e 一跨梁，m、n 柱直通第二層；梁 EI = ∞；b、c、d 受 100、200、300 kN",
   cap="依判讀清單 #1–#10 重繪。攔：誤以為 m、n 柱在第一層有梁（實為 7.2 m 長柱）。",
   mis=[("m、n 柱", "由地面直通第二層，長 7.2 m", "每層 3.6 m"), ("第一層梁", "只有 a–e 一跨", "全寬")]),
 "SA-2024-4": dict(alt="門型構架 A、D 固定；柱 2EI、長 2L，梁 EI、長 L；P 水平向右作用於 B",
   cap="依判讀清單 #1–#8 重繪。攔：柱、梁的剛度或長度讀反、P 作用點讀錯。",
   mis=[("所求", "以結構勁度矩陣法求 P−Δ 側推曲線至極限承載力（逐次形成塑鉸）", "只求彈性階段的 B 點位移與 C、D 彎矩"),
        ("考卷數值", "EI = 425,000 kN-m²、L = 7 m、Mpb = 300、Mpc = 580 kN-m", "未使用")],
   warn="> ⚠️ **本解 §2–§5 只做彈性階段，沒有回答考卷所求（P−Δ 側推曲線）。** 2026-11-05 題目正本確認時列為讀題錯誤，使用者決定依題目正本整題重解（exam-wiki-pipeline 階段 C）；重解前請勿以本解作答。\n\n"),
 "SA-2025-1": dict(alt="門型剛構架，兩柱底固定、梁柱垂直剛接，梁柱 EI、L 相同；P 水平向右作用於右上角點",
   cap="依判讀清單 #1–#8 重繪（考卷附圖無節點字母，重繪不加）。攔：P 作用點或柱底支承讀錯。",
   mis=[("節點字母", "考卷附圖沒有", "當成考卷給的記號")],
   note="考卷附圖沒有節點字母，本解記左柱底 A、左上 B、右上 C、右柱底 D；" + NOTE),
 "SA-2025-4": dict(alt="xy 平面上的格床 abcd（考卷座標：d 為原點，x 由 d 指向 a、y 由 d 指向 c）；ab、cd 平行 y 軸、bc 平行 x 軸，a、d 固定端；bc 全長受 −z 向 ω",
   cap="依判讀清單 #1–#9 重繪，採考卷座標。攔：桿件與座標軸對應讀反、a–d 細線讀成桿件。",
   mis=[("桿件方向", "ab、cd 平行 y 軸，bc 平行 x 軸（考卷座標）", "ab 沿 x、bc 沿 y"), ("a–d 細線", "不是桿件", "第四根桿")],
   note="**本解座標與考卷不同**：§4 以 b 為原點、a = (L,0,0)、c = (0,L,0)，即**本解 x ＝ 考卷 −y、本解 y ＝ 考卷 −x**，w 向下為正。"
        "因此本解的 θx、Mx 對應考卷座標繞 y 軸的分量，θy、My 對應繞 x 軸的分量；數值不受影響（使用者 2026-11-05 決定不改寫 §3–§5，只加此對照）。"),
}
ADD12 = [("  - *應對*：題幹明確指示「不考慮軸向變形」，應直接封鎖 $u_b, v_b, u_c$ 等位移分量。",
          "  - *應對*：題文寫明剛架只有「二個自由度」（考卷沒有寫「不考慮軸向變形」，但兩個自由度已隱含不計軸向變形），應直接封鎖 $u_b, v_b, u_c$ 等位移分量。"),
         ("  題目特別明示「不考慮軸向變形」。若考量軸向變形",
          "  題文指定「剛架有二個自由度」，等同不計軸向變形（考卷並未明寫）。若考量軸向變形")]

def confirm_problem(qid):
    p = f"raw/solutions/{qid}/{qid}-problem.md"; s = open(p, encoding="utf-8").read()
    if "**已確認**" in s: return False
    old = "| 判讀狀態 | **待確認**（"
    assert old in s, qid
    extra = f"；影響答案項目定案：{DEC[qid]}" if qid in DEC else ""
    s = s.replace(old, f"| 判讀狀態 | **已確認**（{DATE} 使用者確認{extra}。原轉錄：", 1)
    s = s.replace("| 確定（解讀；影響答案，請確認） |", "| 確定（解讀）；使用者確認 |")
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
    if "題目（考卷原文見題目正本）" in s: return False
    d = Q[qid]
    m = re.search(r"\n## (§?)1[\.\s][^\n]*\n(.*?)(?=\n## §?2[\.\s])", s, re.S); assert m, qid
    sec = m.group(1); old = m.group(2)
    prob = open(f"raw/solutions/{qid}/{qid}-problem.md", encoding="utf-8").read()
    for png in re.findall(r"\(([^)]+\.png)\)", old):
        assert os.path.basename(png) in prob, (qid, png)
    own = re.findall(r"(!\[[^\]]*\]\((figs/[^)]+\.svg)\)\s*\n(?:\s*\n)?(?:\*[^\n]*\*\s*\n)?)", old + "\n")
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in d["mis"])
    head = f"## §1 題目（考卷原文見題目正本）" if sec else "## 1. 題目（考卷原文見題目正本）"
    new = (f"\n{head}\n\n"
           f"> 考卷原文、公式／附表、附圖與判讀清單（已確認）見 [`{qid}-problem.md`]({qid}-problem.md)。本節只列解題時最容易讀錯的地方與本解使用的記號；題意以題目正本為準。\n\n"
           + d.get("warn", "") +
           f"![{qid} 重繪題目附圖：{d['alt']}](figs/{qid}-fig-1-problem.svg)\n*重繪自考卷附圖，{d['cap']}*\n\n"
           f"### 常見誤讀\n| 項目 | 正確判讀 | 常見誤讀 |\n|---|---|---|\n{rows}\n\n**本解記號：** {d.get('note', NOTE)}\n")
    if own:
        new += "\n### 判讀圖解（解析自繪）\n\n" + "\n".join(o[0].strip() + "\n" for o in own)
    s = s[:m.start()] + new + s[m.end():]
    extra = ""
    if qid == "SA-2012-4":
        for a, b in ADD12:
            assert a in s, (qid, a); s = s.replace(a, b)
        extra = "；刪除「題幹明示不考慮軸向變形」的加字（§3 陷阱三、§5），改依題文「二個自由度」"
    if qid == "SA-2025-4": extra = "；本解記號加註本解座標與考卷座標的對照（數值不動）"
    if qid == "SA-2024-4": extra = "；§1 加註本解未回答考卷所求、待重解"
    gen = f"gen_{qid}_problem.py" if os.path.exists(f"raw/solutions/{qid}/gen_{qid}_problem.py") else f"gen_{qid}.py"
    what = "§1 改為指向題目正本並放重繪附圖（figs/%s-fig-1-problem.svg）、加常見誤讀" % qid
    if own: what += "；原 §1 解析自繪圖移至「判讀圖解（解析自繪）」"
    s = s.rstrip("\n") + f"\n\n*修正日期：{DATE}（{what}{extra}；圖由 {gen} 產生，可重跑）*\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s); return True

if __name__ == "__main__":
    ids = sys.argv[1:] or list(Q)
    for q in ids:
        print(q, "problem:", confirm_problem(q), " §1:", rewrite(q))
    print("index confirmed:", index_confirm(ids))
    if len(sys.argv) == 1:
        s = open("raw/solutions/SA-2012-4/SA-2012-4.md", encoding="utf-8").read()
        assert "題幹明確指示「不考慮軸向變形」" not in s and "題目特別明示「不考慮軸向變形」" not in s
