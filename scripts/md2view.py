#!/usr/bin/env python3
"""md2view.py — 由解析正本重新產生 study/problems-view/<ID>.html

用法：
    python3 scripts/md2view.py SA-2022-3 [SA-2011-3 ...]
    python3 scripts/md2view.py --all

讀 raw/solutions/<ID>/<ID>.md（唯一正本），只替換目標 HTML 的 <main>…</main>，
header／footer／KaTeX 設定一律沿用該檔既有內容，不重建模板。
另同步 header 的「分析法」欄位（取自 .md 標頭的 **分析法：**）。

轉換設定是逆推自既有 74 個頁面的輸出風格：
  markdown(extensions=['tables','nl2br']) ＋「清單前補空行」的前處理。
圖片相對路徑改寫為 ../../raw/solutions/<ID>/…（HTML 在 study/problems-view/ 下）。
"""
import os
import re
import sys

import markdown

FENCE = re.compile(r'^\s*(```|~~~)')
ITEM = re.compile(r'^\s{0,3}(?:[-*+]|\d+[.)])\s')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pre(md: str) -> str:
    """在「清單前一行是普通文字」處補一個空行 —— 原產生器就是這個行為。"""
    out, infence, prev = [], False, ''
    for line in md.split('\n'):
        if FENCE.match(line):
            infence = not infence
        if (not infence and ITEM.match(line) and prev.strip()
                and not ITEM.match(prev)
                and not prev.startswith(('    ', '\t', '|', '>'))):
            out.append('')
        out.append(line)
        prev = line
    return '\n'.join(out)


def render(mid: str, root: str = ROOT) -> str:
    src = os.path.join(root, 'raw', 'solutions', mid, mid + '.md')
    dst = os.path.join(root, 'study', 'problems-view', mid + '.html')
    md = open(src, encoding='utf-8').read()

    body = markdown.markdown(pre(md), extensions=['tables', 'nl2br'])
    body = re.sub(r'src="(?!\.\./|https?:|data:)([^"]+)"',
                  rf'src="../../raw/solutions/{mid}/\1"', body)

    html = open(dst, encoding='utf-8').read()
    head, rest = html.split('<main>', 1)
    _, tail = rest.rsplit('</main>', 1)

    m = re.search(r'^\*\*分析法：\*\*\s*(.+?)\s*$', md, re.M)   # 同步 header 的分析法
    if m:
        head = re.sub(r'(<p class="meta2">.*?｜ )[^｜<]*(</p>)',
                      lambda g: g.group(1) + m.group(1) + g.group(2),
                      head, count=1, flags=re.S)

    open(dst, 'w', encoding='utf-8', newline='\n').write(
        head + '<main>' + body + '</main>' + tail)
    return os.path.relpath(dst, root)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--all']:
        d = os.path.join(ROOT, 'study', 'problems-view')
        args = sorted(f[:-5] for f in os.listdir(d) if f.endswith('.html'))
    for mid in args:
        print('寫出', render(mid))
