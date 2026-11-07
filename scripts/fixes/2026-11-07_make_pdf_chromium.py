"""Chromium A4 PDF：details 全展開、等 KaTeX 渲染完、統計 katex／katex-error／pageerror。
用法：python make_pdf.py <html> <out.pdf> [margin_mm]
   本庫講義與單元總覽一律用 margin 0（與既有 PDF 相同；雲端 Playwright＋google-chrome、Noto Sans CJK TC）"""
import sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def main(src, out, mm):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(Path(src).resolve().as_uri(), wait_until="networkidle")
        await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(800)
        k = await pg.evaluate("document.querySelectorAll('.katex').length")
        ke = await pg.evaluate("document.querySelectorAll('.katex-error').length")
        raw = await pg.evaluate(r"""(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n=0,s;
            while(s=w.nextNode()){const p=s.parentElement; if(p.closest('script,style,code,pre,.katex'))continue;
            if(/\\\(|\\\[|\$\$/.test(s.textContent))n++;}return n})()""")
        await pg.emulate_media(media="print")
        m = f"{mm}mm"
        await pg.pdf(path=out, format="A4", print_background=True, margin={"top": m, "bottom": m, "left": m, "right": m})
        await b.close()
        print(f"{Path(src).name}: katex {k}, katex-error {ke}, 未渲染定界符 {raw}, pageerror {len(errs)} {errs[:2]}")


asyncio.run(main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 12))
