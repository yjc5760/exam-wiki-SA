#!/usr/bin/env python3
"""列出一批題目目前在題庫流程的哪個階段（唯讀）
  python pipeline_status.py <repo根目錄> <科目> --unit XX-Un-m [--years 2002-2013]
判定（啟發式，結果有疑時以實際檔案為準）：
  A  題目正本 <id>-problem.md 判讀狀態含「已確認」，且 figs/ 下有 <id>-fig-*-problem.svg（題目附圖重繪）
  B  wiki/queries/audit-ledger-XX.json 有該題
  C  ledger 結果為一致（不需勘誤），或 fixed >= date
  D  不需勘誤，或 recheck.date >= fixed 且 recheck.result == 落實
  E  解析 .md 引用了 figs/ 下的「解題圖」svg：不是 -problem.svg，也不是早期的題目重繪
     <id>-fig-1-{beam,frame,truss,grid}.svg（2026-11-07 更正：舊判定「檔名不含 -fig-」與命名規範
     <id>-fig-N-<語意>.svg 矛盾，全科一律判為未完成）
  F  question_index.json verificationStatus == verified"""
import argparse, json, re

PROBLEM_REDRAW = re.compile(r"-fig-\d+[a-z]?-problem\.svg$|-fig-1-(beam|frame|truss|grid)\.svg$")
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("subject")
ap.add_argument("--unit", required=True); ap.add_argument("--years")
a = ap.parse_args()
root, S = Path(a.root), a.subject
q = json.loads((root / "raw/json/question_index.json").read_text(encoding="utf-8"))
Q = [x for x in (q["questions"] if isinstance(q, dict) else q)
     if (x.get("moduleId") or "").startswith(S + "-") and x.get("primaryTopicId") == a.unit]
if a.years:
    y0, y1 = map(int, a.years.split("-"))
    Q = [x for x in Q if y0 <= int(x["moduleId"].split("-")[1]) <= y1]
Q.sort(key=lambda x: (int(x["moduleId"].split("-")[1]), int(x["moduleId"].split("-")[2])))
lp = root / f"wiki/queries/audit-ledger-{S}.json"
led = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}

rows = []
for x in Q:
    qid = x["moduleId"]; d = root / f"raw/solutions/{qid}"
    pm = d / f"{qid}-problem.md"
    ptxt = pm.read_text(encoding="utf-8", errors="replace") if pm.exists() else ""
    m = re.search(r"判讀狀態[^\n]*", ptxt)
    pstat = "—" if not pm.exists() else ("已確認" if m and "已確認" in m.group(0) else "待確認")
    figs = list((d / "figs").glob("*.svg")) if (d / "figs").exists() else []
    redraw = any(f.name.endswith("-problem.svg") for f in figs)
    stxt = (d / f"{qid}.md").read_text(encoding="utf-8", errors="replace") if (d / f"{qid}.md").exists() else ""
    diag = any(f.name in stxt for f in figs if not PROBLEM_REDRAW.search(f.name))
    e = led.get(qid, {}); res = e.get("result", "")
    need_fix = bool(e) and not res.startswith("一致")
    fixed = bool(e) and (not need_fix or (e.get("fixed") or "") >= e.get("date", "9"))
    rc = e.get("recheck") or {}
    landed = bool(e) and (not need_fix or (fixed and rc.get("date", "") >= (e.get("fixed") or "") and rc.get("result") == "落實"))
    ver = x.get("verificationStatus") == "verified"
    A = pstat == "已確認" and redraw
    stage = next((s for s, ok in [("A", A), ("B", bool(e)), ("C", fixed), ("D", landed), ("E", diag), ("F", ver)] if not ok), "完成")
    rows.append((qid, pstat, "✓" if redraw else "—", res or "—", "✓" if fixed else "—",
                 "✓" if landed else "—", "✓" if diag else "—", "✓" if ver else "—", stage))

print(f"{S} {a.unit} {a.years or ''}：{len(rows)} 題")
print("題號\t題目正本\t附圖重繪\t盲解結果\t勘誤\t落實\t圖解\tverified\t卡在")
for r in rows:
    print("\t".join(r))
from collections import Counter
print("各階段題數：", dict(Counter(r[-1] for r in rows)))
