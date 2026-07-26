#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xcheck.py v3 — 六科考試知識庫跨檔一致性掃描器（通用符號比對）

偵測 2026-07-26 於 exam-wiki-RC 實際抓到的三類系統性缺陷，設計為**跨科通用**：
SS / RC / SA / SD / SM / MM 皆可直接跑。

  類型 A  符號定義式係數不一致
          自動抽取「符號 = 係數 …」形式（Ec = 15000√f'c、Fcr = 0.658…、γ = 3.2 …），
          依符號分組，比對「證據層 raw/solutions/」與「衍生層 wiki/」。
          🔴 高優先 = 衍生層獨有（wiki 自己生出來、證據層找不到的數字）
  類型 A2 單位制並存
          同一符號的兩個係數比值 ≈ 已知換算常數 → 疑為不同單位制混用
  類型 B  構件名稱＋絕對化語句（條件式規定被寫成絕對規則）
  類型 C  有公式係數但整份檔案未交代單位制

判讀原則（依各科 CLAUDE.md 規則 2）：`raw/solutions/`（verified）為證據錨點。
證據層內部有多種係數屬正常（不同題目用不同公式／單位制），不算缺陷。

⚠️ 這是**分診（triage）工具**，不是判官。輸出為需人工／LLM 判讀的短名單；
   RC 實測真陽性率約 1/6，請以「值得看一眼」而非「一定有錯」的心態使用。

用法：
    python3 xcheck.py <repo>            # 印到 stdout
    python3 xcheck.py <repo> -o out.md  # 寫檔
"""
import argparse, os, re, sys, glob
from collections import defaultdict

# ── 已知單位換算常數（用於 A2 單位制並存偵測）──────────────────
RATIOS = [
    (3.193,  "√型係數 psi↔kgf/cm² 或 MPa↔kgf/cm²"),
    (12.04,  "√型係數 psi↔MPa"),
    (10.197, "直接應力 MPa↔kgf/cm²"),
    (14.223, "直接應力 MPa↔psi"),
    (0.0703, "直接應力 psi↔kgf/cm²"),
    (2.205,  "力 kgf↔lb"),
]

# 符號定義式：$ Sym = 係數 ...$  或  Sym = 係數
# Sym 允許 LaTeX 下標與希臘字母；係數為開頭的純數字（含分數 \frac{a}{b}）
SYM = r"(?:\\[a-zA-Z]+|[A-Za-z][A-Za-z]?)(?:_\{?[A-Za-z0-9,']{1,8}\}?)?"
RE_DEF = re.compile(
    r"(?<![A-Za-z0-9_])(" + SYM + r")\s*(?:&\s*)?[=＝]\s*"
    r"\\?(?:approx|≈|le|leq|ge|geq|≤|≥)?\s*"
    r"(\\frac\{\d+\}\{\d+\}|\d+\.?\d*)\s*"
    r"(?=[\\√a-zA-Z(]|\s*\\?(?:sqrt|times|cdot))"
)
RE_FRAC = re.compile(r"\\frac\{(\d+)\}\{(\d+)\}")

# 只追蹤這些「像物理量」的符號，避免抓到 x = 1 之類的雜訊
SYM_WHITELIST = re.compile(
    r"^(?:[EFVMTKQIJLSPAWRGCND][a-z]?|f|v|k|q|s|w|r|beta|gamma|lambda|mu|phi|rho|sigma|tau|omega|alpha|delta|xi|zeta|eta)"
    r"(?:_.*)?$", re.I)

UNIT_TOKENS = ["kgf/cm", "kgf/m", "MPa", "psi", "ksi", "N/mm", "kN", "tf/m", "kgf-cm", "t/m"]

ABSOLUTE = ["一律", "永遠", "必然", "絕對", "任何情況", "都不可", "均不可", "只能取", "一定取", "不論何種"]
MEMBERS = ["懸臂梁", "倒T型梁", "倒 T 型梁", "深梁", "簡支梁", "連續梁", "T形梁", "T 形梁", "剪力牆",
           "梁柱接頭", "角柱", "邊柱", "內柱", "預力梁", "組合梁", "扁梁", "基腳", "版",
           "槽形鋼", "H型鋼", "H 型鋼", "箱型", "角鋼", "圓管", "格子梁", "桁架", "拱", "剛架", "斜撐"]
B_EXCLUDE = ["不是", "錯的記法", "錯誤推論", "三條件", "判準是", "視條件", "依條件",
             "須確認", "無法確認", "取決於", "端視"]

EVIDENCE_DIRS = ["raw/solutions"]
DERIVED_DIRS = ["wiki/code-ref", "wiki/traps", "wiki/diagnosis", "wiki/concepts",
                "wiki/methods", "wiki/philosophy", "wiki/failure-modes", "wiki/materials"]

RE_ANY_COEF = re.compile(r"\d+\.?\d*\s*\\?(?:sqrt|√|times|cdot)")


def md_files(repo, subdirs):
    out = []
    for d in subdirs:
        out += glob.glob(os.path.join(repo, d, "**", "*.md"), recursive=True)
    return sorted(f for f in out if not f.endswith("log.md"))


def norm_sym(s):
    return s.replace("\\", "").replace("{", "").replace("}", "").strip("_ ").lower()


def to_float(g):
    m = RE_FRAC.fullmatch(g)
    if m:
        return float(m.group(1)) / float(m.group(2))
    try:
        return float(g)
    except ValueError:
        return None


def scan_A(repo):
    res = defaultdict(lambda: {"ev": defaultdict(list), "de": defaultdict(list)})
    for layer, dirs in [("ev", EVIDENCE_DIRS), ("de", DERIVED_DIRS)]:
        for path in md_files(repo, dirs):
            rel = os.path.relpath(path, repo).replace("\\", "/")
            for i, line in enumerate(open(path, encoding="utf-8", errors="replace").read().split("\n"), 1):
                for m in RE_DEF.finditer(line):
                    sym = norm_sym(m.group(1))
                    if not sym or not SYM_WHITELIST.match(sym) or len(sym) > 10:
                        continue
                    v = to_float(m.group(2))
                    if v is None or v == 0:
                        continue
                    res[sym][layer][f"{v:g}"].append(f"{rel}:{i}")
    return res


def ratio_hints(vals):
    hints, nums = [], sorted({float(v) for v in vals})
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] <= 0:
                continue
            r = nums[j] / nums[i]
            for t, lab in RATIOS:
                if t > 1 and abs(r - t) / t < 0.04:
                    hints.append(f"{nums[i]:g} ↔ {nums[j]:g}（比值 {r:.2f} ≈ {t}）→ {lab}")
    return hints


def scan_B(repo):
    out = []
    for path in md_files(repo, DERIVED_DIRS):
        rel = os.path.relpath(path, repo).replace("\\", "/")
        for i, line in enumerate(open(path, encoding="utf-8", errors="replace").read().split("\n"), 1):
            if any(a in line for a in ABSOLUTE) and any(mb in line for mb in MEMBERS) \
               and not any(x in line for x in B_EXCLUDE):
                out.append((rel, i, line.strip()[:140]))
    return out


def scan_C(repo):
    out = []
    for path in md_files(repo, DERIVED_DIRS):
        rel = os.path.relpath(path, repo).replace("\\", "/")
        txt = open(path, encoding="utf-8", errors="replace").read()
        n = len(RE_ANY_COEF.findall(txt))
        if n >= 2 and not any(u in txt for u in UNIT_TOKENS):
            out.append((rel, n))
    return out


def report(repo, out_path):
    subject = os.path.basename(os.path.abspath(repo)).replace("exam-wiki-", "")
    A, B, C = scan_A(repo), scan_B(repo), scan_C(repo)

    rows = []
    for sym, d in A.items():
        ev, de = set(d["ev"]), set(d["de"])
        if not de:
            continue
        only_de = de - ev
        hints = ratio_hints(ev | de)
        if only_de or hints:
            rows.append((sym, d, only_de, hints, len(only_de)))
    rows.sort(key=lambda r: (-r[4], r[0]))

    L = [f"# {subject} 知識庫一致性掃描報告", "",
         f"對象：`{os.path.abspath(repo)}`　工具：`xcheck.py` v3（通用符號比對）", "",
         "> 判讀原則：`raw/solutions/`（verified）為證據錨點；證據層內部多樣性屬正常。",
         "> 🔴 **衍生層獨有** = wiki/ 自己生出來、證據層找不到的數字，優先看這些。",
         "> 本工具為分診用，RC 實測真陽性率約 1/6。", "",
         f"**摘要：** 類型 A 可疑符號 **{len(rows)}** 個（其中含衍生層獨有值 "
         f"**{sum(1 for r in rows if r[2])}** 個）｜類型 B **{len(B)}** 處｜類型 C **{len(C)}** 檔", "",
         "---", "", "## 類型 A：符號定義式係數不一致", ""]
    if not rows:
        L += ["（無可疑項）", ""]
    for sym, d, only_de, hints, _ in rows[:30]:
        L += [f"### `{sym}`", "", "| 係數 | 層級 | 出處（最多 4 處） |", "|---|---|---|"]
        ev, de = set(d["ev"]), set(d["de"])
        for v in sorted(ev | de, key=float):
            src = d["ev"].get(v, []) + d["de"].get(v, [])
            tag = "🔴 **衍生層獨有**" if v in only_de else ("🔒 證據" if v not in de else "證據＋衍生")
            L.append(f"| `{v}` | {tag} | " + "、".join(f"`{s}`" for s in src[:4]) +
                     (" …" if len(src) > 4 else "") + " |")
        if hints:
            L += ["", "**單位制並存提示：**"] + [f"- {h}" for h in hints[:5]]
        L.append("")
    if len(rows) > 30:
        L += [f"*（另有 {len(rows)-30} 個符號未列出，請執行工具查看完整輸出）*", ""]

    L += ["---", "", "## 類型 B：構件名稱＋絕對化語句", ""]
    if not B:
        L += ["（無）", ""]
    else:
        L += ["| 出處 | 內容 |", "|---|---|"]
        for rel, i, line in B[:40]:
            L.append(f"| `{rel}:{i}` | " + line.replace("|", "\\|") + " |")
        L += ["", "> 確認：是規範的**絕對規定**，還是**條件式規定**被簡化成結論？",
              "> 對照 `raw/solutions/` 同型題的實際處理；若兩題處理不同，多半是條件式。", ""]

    L += ["---", "", "## 類型 C：有公式係數但整份檔案未交代單位制", ""]
    if not C:
        L += ["（無）", ""]
    else:
        L += ["| 檔案 | 係數出現次數 |", "|---|---|"]
        for rel, n in sorted(C, key=lambda x: -x[1])[:30]:
            L.append(f"| `{rel}` | {n} |")
        L.append("")

    L += ["---", "", "## 換算速查", "",
          "| 型態 | psi → kgf/cm² | psi → MPa | MPa → kgf/cm² |", "|---|---|---|---|",
          "| `k√X` 型（根號內也換） | × **0.265** | × **0.0830** | × **3.19** |",
          "| 直接應力型 | × **0.0703** | × **0.006895** | × **10.20** |", ""]

    txt = "\n".join(L)
    if out_path:
        open(out_path, "w", encoding="utf-8").write(txt)
    return txt, len(rows), sum(1 for r in rows if r[2]), len(B), len(C)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    if not os.path.isdir(a.repo):
        sys.exit(f"找不到資料夾：{a.repo}")
    txt, nA, nR, nB, nC = report(a.repo, a.out)
    print(f"報告已寫入 {a.out}" if a.out else txt)
    print(f"[{os.path.basename(os.path.abspath(a.repo))}] A={nA}(🔴{nR})  B={nB}  C={nC}", file=sys.stderr)
