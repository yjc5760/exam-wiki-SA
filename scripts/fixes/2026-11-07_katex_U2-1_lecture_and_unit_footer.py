"""KaTeX 未渲染兩處（舊版即有）：lecture-SA-U2-1 Macaulay 式裸「<」；單元總覽模板頁尾未呼叫 mathIn。可重複執行。"""
from pathlib import Path
R = Path(__file__).resolve().parents[2]
p = R / "study/lecture-SA-U2-1.html"; t = p.read_text(encoding="utf-8")
t = t.replace(r"\begin{cases}0 & x<a\\ (x-a)^n", r"\begin{cases}0 & x&lt;a\\ (x-a)^n")
p.write_text(t, encoding="utf-8")
p = R / "scripts/unit_page_template.html"; t = p.read_text(encoding="utf-8")
old = "mathIn(document.getElementById('strat'));mathIn(document.getElementById('s1'));mathIn(document.getElementById('mxsum'));"
if old + "mathIn(document.querySelector('footer'));" not in t:
    assert old in t
    t = t.replace(old, old + "mathIn(document.querySelector('footer'));")
p.write_text(t, encoding="utf-8")
print("ok")
