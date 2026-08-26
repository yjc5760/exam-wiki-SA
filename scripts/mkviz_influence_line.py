#!/usr/bin/env python3
"""重寫 SA-2015-2 / SA-2025-2 的互動影響線頁（原檔內容為勘誤前的錯誤數值）。

SA-2015-2：原檔寫 IL(F−)=+79/128、IL(F+)=−49/128（正負與大小皆錯）
SA-2025-2：原檔整份建立在誤讀幾何上（2+4+4+4+4=18 m、F 當自由端、V_F≡0）

本腳本產生的兩份 HTML 自帶 IL 函數（JS），拖動載重即時顯示縱距，
數值與 gen_SA-*.py／解析 .md 同源。
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

CSS = """
:root{--ac:#1565c0;--ink:#263238;--mut:#607d8b;--bd:#dfe6ea;--pos:#2e7d6f;--neg:#7c3aed}
*{box-sizing:border-box}
body{margin:0;padding:18px;font-family:"Microsoft JhengHei","Noto Sans TC",-apple-system,sans-serif;
  background:#f7f9fb;color:var(--ink);line-height:1.7}
.wrap{max-width:900px;margin:0 auto;background:#fff;border:1px solid var(--bd);
  border-radius:12px;padding:20px 22px}
h1{font-size:1.12em;margin:0 0 4px;color:#0d47a1}
.sub{font-size:.85em;color:var(--mut);margin-bottom:14px}
canvas{display:block;width:100%;height:auto;margin:10px 0}
.ctl{display:flex;align-items:center;gap:12px;margin:14px 0 6px;flex-wrap:wrap}
.ctl input[type=range]{flex:1;min-width:220px}
.read{font-variant-numeric:tabular-nums;font-size:.92em}
.read b{color:var(--ac)}
table{width:100%;border-collapse:collapse;font-size:.86em;margin-top:12px}
th,td{border:1px solid var(--bd);padding:5px 8px;text-align:center}
th{background:#eceff1}
tbody tr:nth-child(even){background:#fafcfd}
.note{font-size:.82em;color:var(--mut);margin-top:12px;border-top:1px solid var(--bd);padding-top:10px}
.warn{background:#fff8e1;border-left:4px solid #f9a825;padding:8px 12px;font-size:.84em;margin:12px 0}
"""

HEAD = """<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head><body><div class="wrap">
<h1>{h1}</h1><div class="sub">{sub}</div>{warn}"""

TAIL = """</div></body></html>\n"""


# ══════════════════════════════════════════════════════════
V2015 = r"""
<canvas id="cv" width="1720" height="620"></canvas>
<div class="ctl">
  <label for="s">單位載重位置 x =</label>
  <input id="s" type="range" min="0" max="80" step="0.1" value="24">
  <span class="read">x = <b id="xv">24.0</b> m　｜　IL of V<sub>F</sub> = <b id="yv"></b></span>
</div>
<table>
 <thead><tr><th>位置</th><th>A (0)</th><th>F⁻ (15)</th><th>F⁺ (15)</th><th>B (30)</th>
 <th>C (40)</th><th>D (50)</th><th>DE 極大</th><th>E (80)</th></tr></thead>
 <tbody><tr><td>IL<sub>V<sub>F</sub></sub></td><td>0</td>
 <td><b>−73/128<br>= −0.5703</b></td><td><b>+55/128<br>= +0.4297</b></td><td>0</td>
 <td><b>−1/6<br>= −0.1667</b></td><td>0</td><td>+0.0722<br>@ x≈62.7</td><td>0</td></tr></tbody>
</table>
<div class="note">
分段方程（x 由 A 起算，m）：<br>
0–15：x(x²−5700)/144000　｜　15–30：(x−30)(x²+30x−4800)/144000<br>
30–40：−(x−30)(x²−90x+2800)/48000　｜　40–50：−(x−50)(x²−70x+400)/48000<br>
50–80：(x−110)(x−80)(x−50)/144000<br>
V<sub>F</sub> 以「斷面左側向上」為正。四個支承（A、B、D、E）處縱距皆為 0；
F 處跳躍恰為 1；C 為內部鉸，斜率在此轉折。
</div>
<script>
const KN=[0,15,30,40,50,80], NM=['A','F','B','C','D','E'];
function IL(x,right){
  if(x<15||(x===15&&!right)) return x*(x*x-5700)/144000;
  if(x<=30) return (x-30)*(x*x+30*x-4800)/144000;
  if(x<=40) return -(x-30)*(x*x-90*x+2800)/48000;
  if(x<=50) return -(x-50)*(x*x-70*x+400)/48000;
  return (x-110)*(x-80)*(x-50)/144000;
}
const cv=document.getElementById('cv'),g=cv.getContext('2d');
const W=1720,H=620,L=90,R=60,T=150,B=90,PW=W-L-R;
const Y0=T+(H-T-B)*0.46, KY=(H-T-B)*0.46/0.62;
const PX=x=>L+x/80*PW, PY=v=>Y0-v*KY;
function draw(xl){
  g.clearRect(0,0,W,H); g.lineJoin='round';
  // 梁示意
  g.strokeStyle='#3F4A5A'; g.lineWidth=7; g.beginPath();
  g.moveTo(PX(0),70); g.lineTo(PX(80),70); g.stroke();
  g.fillStyle='#3F4A5A';
  [[0,'pin'],[30,'rol'],[50,'rol'],[80,'rol']].forEach(([x,k])=>{
    g.beginPath(); g.moveTo(PX(x),74); g.lineTo(PX(x)-13,98); g.lineTo(PX(x)+13,98);
    g.closePath(); g.fill();
    if(k==='rol'){g.beginPath();g.arc(PX(x),104,5,0,7);g.fill();}
  });
  g.fillStyle='#fff'; g.strokeStyle='#3F4A5A'; g.lineWidth=3;
  g.beginPath(); g.arc(PX(40),70,8,0,7); g.fill(); g.stroke();
  g.setLineDash([6,5]); g.strokeStyle='#B45309'; g.lineWidth=3;
  g.beginPath(); g.moveTo(PX(15),44); g.lineTo(PX(15),96); g.stroke(); g.setLineDash([]);
  g.font='700 22px sans-serif'; g.textAlign='center';
  KN.forEach((x,i)=>{ g.fillStyle=(NM[i]==='F')?'#B45309':'#1F2733';
    g.fillText(NM[i],PX(x),132); });
  g.fillStyle='#6B7684'; g.font='16px sans-serif';
  g.fillText('內部鉸',PX(40),40); g.fillText('剪力斷面',PX(15),34);
  // 載重
  g.strokeStyle='#C0392B'; g.fillStyle='#C0392B'; g.lineWidth=4;
  g.beginPath(); g.moveTo(PX(xl),14); g.lineTo(PX(xl),64); g.stroke();
  g.beginPath(); g.moveTo(PX(xl),70); g.lineTo(PX(xl)-8,54); g.lineTo(PX(xl)+8,54);
  g.closePath(); g.fill();
  // 影響線
  g.strokeStyle='#9AA4B2'; g.lineWidth=1.5;
  g.beginPath(); g.moveTo(L,Y0); g.lineTo(W-R,Y0); g.stroke();
  g.setLineDash([3,5]); g.strokeStyle='#E1E6ED';
  KN.forEach(x=>{g.beginPath();g.moveTo(PX(x),T);g.lineTo(PX(x),H-B+10);g.stroke();});
  g.setLineDash([]);
  [[0,15,false],[15,80,true]].forEach(([a,b,rt])=>{
    g.beginPath(); g.moveTo(PX(a),Y0);
    for(let i=0;i<=400;i++){const x=a+(b-a)*i/400; g.lineTo(PX(x),PY(IL(x,rt||x>15)));}
    g.lineTo(PX(b),Y0); g.closePath();
    g.fillStyle='rgba(124,58,237,0.16)'; g.fill();
    g.strokeStyle='#7C3AED'; g.lineWidth=3.4; g.stroke();
  });
  g.setLineDash([5,4]); g.strokeStyle='#B45309'; g.lineWidth=3;
  g.beginPath(); g.moveTo(PX(15),PY(IL(15,false))); g.lineTo(PX(15),PY(IL(15,true)));
  g.stroke(); g.setLineDash([]);
  // 讀值
  const v=IL(xl,xl>15);
  g.strokeStyle='#C0392B'; g.setLineDash([4,4]); g.lineWidth=2;
  g.beginPath(); g.moveTo(PX(xl),Y0); g.lineTo(PX(xl),PY(v)); g.stroke(); g.setLineDash([]);
  g.fillStyle='#C0392B'; g.beginPath(); g.arc(PX(xl),PY(v),7,0,7); g.fill();
  g.font='700 20px sans-serif'; g.textAlign='center';
  g.fillText(v.toFixed(4),PX(xl),PY(v)+(v>0?-18:32));
  [[15,false,'−73/128'],[15,true,'+55/128'],[40,true,'−1/6']].forEach(([x,rt,lb])=>{
    const y=IL(x,rt); g.fillStyle='#7C3AED';
    g.beginPath(); g.arc(PX(x),PY(y),5,0,7); g.fill();
    g.font='700 18px sans-serif';
    g.fillText(lb,PX(x)+(rt&&x===15?58:(x===15?-58:0)),PY(y)+(y>0?-16:30));
  });
  document.getElementById('xv').textContent=xl.toFixed(1);
  document.getElementById('yv').textContent=v.toFixed(4);
}
const s=document.getElementById('s');
s.addEventListener('input',()=>draw(parseFloat(s.value))); draw(24);
</script>
"""

V2025 = r"""
<canvas id="cv" width="1720" height="1180"></canvas>
<div class="ctl">
  <label for="s">單位載重位置 x =</label>
  <input id="s" type="range" min="0" max="16" step="0.05" value="10">
  <span class="read">x = <b id="xv">10.00</b> m　｜　<span id="yv"></span></span>
</div>
<table>
 <thead><tr><th>位置</th><th>A (0)</th><th>B (4)</th><th>F (6)</th><th>C (8)</th>
 <th>D (12)</th><th>E (16)</th></tr></thead>
 <tbody>
  <tr><td>IL<sub>R<sub>A</sub></sub></td><td>1</td><td>1</td><td>0.5</td><td>0</td><td>−1</td><td>0</td></tr>
  <tr><td>IL<sub>R<sub>C</sub></sub></td><td>0</td><td>0</td><td>0.5</td><td>1</td><td><b>2</b></td><td>0</td></tr>
  <tr><td>IL<sub>R<sub>E</sub></sub></td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
  <tr><td>IL<sub>M<sub>A</sub></sub>（m）</td><td>0</td><td><b>4</b></td><td>2</td><td>0</td><td><b>−4</b></td><td>0</td></tr>
  <tr><td>IL<sub>V<sub>F</sub></sub></td><td>0</td><td>0</td><td><b>−0.5 ／ +0.5</b></td><td>0</td><td>−1</td><td>0</td></tr>
 </tbody>
</table>
<div class="note">
F 是 B、C 之間的<b>剪力斷面</b>（位於 C 左方 2 m），<b>不是自由端</b>——
IL<sub>V<sub>F</sub></sub> 在 F 處有單位跳躍，並在 D 達到 −1。
IL<sub>R<sub>C</sub></sub> 在 D 的峰值 2 大於 1 是槓桿效應：D 為內鉸，DE 段對 C 形同懸臂。
所有影響線分段線性，折點只在支承、內鉸與剪力斷面。
</div>
<script>
const XA=0,XB=4,XF=6,XC=8,XD=12,XE=16;
const RE=x=>Math.max(x-XD,0)/(XE-XD);
const RC=x=>(Math.max(x-XB,0)-(XE-XB)*RE(x))/(XC-XB);
const RA=x=>1-RC(x)-RE(x);
const MA=x=>x-XC*RC(x)-XE*RE(x);
const VF=(x,r)=>RA(x)-((r?x<XF:x<=XF)?1:0);
const ILS=[
 {n:'IL of R_A',lab:'IL of R  (A 點反力)',f:RA,u:'',k:[XA,XB,XD,XE],c:'#2E7D6F'},
 {n:'IL of R_C',lab:'IL of R  (C 點反力)',f:RC,u:'',k:[XA,XB,XD,XE],c:'#2E7D6F'},
 {n:'IL of R_E',lab:'IL of R  (E 點反力)',f:RE,u:'',k:[XA,XD,XE],c:'#2E7D6F'},
 {n:'IL of M_A',lab:'IL of M  (A 端固定彎矩)',f:MA,u:' m',k:[XA,XB,XD,XE],c:'#2E7D6F'},
 {n:'IL of V_F',lab:'IL of V  (F 斷面剪力)',f:null,u:'',k:[XA,XB,XF,XD,XE],c:'#7C3AED'}
];
const KN=[XA,XB,XF,XC,XD,XE], NM=['A','B','F','C','D','E'];
const cv=document.getElementById('cv'),g=cv.getContext('2d');
const W=1720,L=110,R=70,PW=W-L-R, PX=x=>L+x/XE*PW;
const H0=110, PH=205;
function draw(xl){
  g.clearRect(0,0,W,1180); g.textAlign='center';
  // 結構
  g.strokeStyle='#3F4A5A'; g.lineWidth=7;
  g.beginPath(); g.moveTo(PX(0),56); g.lineTo(PX(XE),56); g.stroke();
  g.lineWidth=5; g.beginPath(); g.moveTo(PX(0),22); g.lineTo(PX(0),90); g.stroke();
  g.fillStyle='#3F4A5A';
  [XC,XE].forEach(x=>{g.beginPath();g.moveTo(PX(x),60);g.lineTo(PX(x)-13,84);
    g.lineTo(PX(x)+13,84);g.closePath();g.fill();
    g.beginPath();g.arc(PX(x),90,5,0,7);g.fill();});
  g.fillStyle='#fff'; g.strokeStyle='#3F4A5A'; g.lineWidth=3;
  [XB,XD].forEach(x=>{g.beginPath();g.arc(PX(x),56,8,0,7);g.fill();g.stroke();});
  g.setLineDash([6,5]); g.strokeStyle='#B45309'; g.lineWidth=3;
  g.beginPath(); g.moveTo(PX(XF),30); g.lineTo(PX(XF),82); g.stroke(); g.setLineDash([]);
  g.font='700 22px sans-serif';
  KN.forEach((x,i)=>{g.fillStyle=(NM[i]==='F')?'#B45309':'#1F2733';
    g.fillText(NM[i],PX(x),H0+8);});
  g.fillStyle='#B45309'; g.font='15px sans-serif'; g.textAlign='right';
  g.fillText('剪力斷面（非自由端）',PX(XF)-14,26); g.textAlign='center';
  g.strokeStyle='#C0392B'; g.fillStyle='#C0392B'; g.lineWidth=4;
  g.beginPath(); g.moveTo(PX(xl),0); g.lineTo(PX(xl),50); g.stroke();
  g.beginPath(); g.moveTo(PX(xl),56); g.lineTo(PX(xl)-8,40); g.lineTo(PX(xl)+8,40);
  g.closePath(); g.fill();
  let out=[];
  ILS.forEach((s,i)=>{
    const top=H0+30+i*PH, y0=top+PH*0.52;
    const vals=s.n==='IL of V_F'
      ? s.k.map(x=>[x,VF(x,false)]) : s.k.map(x=>[x,s.f(x)]);
    const mx=Math.max(1e-9,...vals.map(v=>Math.abs(v[1])),
      s.n==='IL of V_F'?Math.abs(VF(XF,true)):0);
    const ky=PH*0.34/mx;
    g.strokeStyle='#9AA4B2'; g.lineWidth=1.4;
    g.beginPath(); g.moveTo(L,y0); g.lineTo(W-R,y0); g.stroke();
    g.setLineDash([3,5]); g.strokeStyle='#E1E6ED';
    KN.forEach(x=>{g.beginPath();g.moveTo(PX(x),top);g.lineTo(PX(x),top+PH-16);g.stroke();});
    g.setLineDash([]);
    const seg = s.n==='IL of V_F'
      ? [[[XA,0],[XB,0],[XF,VF(XF,false)]],[[XF,VF(XF,true)],[XD,VF(XD,true)],[XE,VF(XE,true)]]]
      : [vals];
    seg.forEach(pts=>{
      g.beginPath(); g.moveTo(PX(pts[0][0]),y0);
      pts.forEach(p=>g.lineTo(PX(p[0]),y0-p[1]*ky));
      g.lineTo(PX(pts[pts.length-1][0]),y0); g.closePath();
      g.fillStyle=s.c==='#7C3AED'?'rgba(124,58,237,.16)':'rgba(46,125,111,.18)';
      g.fill(); g.strokeStyle=s.c; g.lineWidth=3; g.stroke();
      g.fillStyle=s.c; g.font='700 17px sans-serif';
      pts.forEach(p=>{g.beginPath();g.arc(PX(p[0]),y0-p[1]*ky,5,0,7);g.fill();
        if(Math.abs(p[1])>1e-9)
          g.fillText(p[1].toFixed(2).replace(/\.00$/,''),PX(p[0]),y0-p[1]*ky+(p[1]>0?-14:26));});
    });
    const cur = s.n==='IL of V_F' ? VF(xl,xl>XF) : s.f(xl);
    g.strokeStyle='#C0392B'; g.setLineDash([4,4]); g.lineWidth=2;
    g.beginPath(); g.moveTo(PX(xl),y0); g.lineTo(PX(xl),y0-cur*ky); g.stroke(); g.setLineDash([]);
    g.fillStyle='#C0392B'; g.beginPath(); g.arc(PX(xl),y0-cur*ky,6,0,7); g.fill();
    g.font='700 21px sans-serif'; g.fillStyle='#1F2733';
    g.fillText(s.lab + (s.u?'（m）':''), W/2, top+18);
    out.push(s.n.replace('IL of ','')+' = <b>'+cur.toFixed(3)+'</b>'+s.u);
  });
  document.getElementById('xv').textContent=xl.toFixed(2);
  document.getElementById('yv').innerHTML=out.join('　｜　');
}
const s=document.getElementById('s');
s.addEventListener('input',()=>draw(parseFloat(s.value))); draw(10);
</script>
"""

FILES = [
    ("SA-2015-2/SA-2015-2-influence-line-viz.html",
     "SA-2015-2 F 點剪力影響線",
     "SA-2015-2　F 點剪力影響線（Müller-Breslau ＋ 共軛梁法）",
     "梁 A–F–B–C–D–E：AF = FB = 15 m，BC = CD = 10 m，DE = 30 m，C 為內部鉸。"
     "拖動下方滑桿改變單位載重位置，即時讀出 V<sub>F</sub> 的影響線縱距。",
     "⚠ 2026-08-26 更新：本頁原本標示 IL(F⁻)=+79/128、IL(F⁺)=−49/128，"
     "係共軛梁彎矩多冠一個負號所致，正負與大小皆錯。已更正為 "
     "<b>IL(F⁻)=−73/128</b>、<b>IL(F⁺)=+55/128</b>，並補上原本缺少的完整曲線。",
     V2015),
    ("SA-2025-2/SA-2025-2-influence-line-viz.html",
     "SA-2025-2 影響線視覺化",
     "SA-2025-2　R<sub>A</sub>、R<sub>C</sub>、R<sub>E</sub>、M<sub>A</sub>、V<sub>F</sub> 影響線",
     "A 固定端｜B、D 內鉸｜C、E 滾支承｜F 為 B–C 間的剪力斷面（C 左方 2 m）｜4 @ 4 m = 16 m",
     "⚠ 2026-08-26 更新：本頁原本依誤讀的幾何繪製（2+4+4+4+4 = 18 m、"
     "F 當成自由端、IL<sub>V<sub>F</sub></sub> ≡ 0）。已依考卷附圖更正為 "
     "<b>4 @ 4 m = 16 m</b>、<b>F 為 B–C 間的剪力斷面</b>，"
     "V<sub>F</sub> 在 F 處有單位跳躍（−0.5 → +0.5）。",
     V2025),
]

for path, title, h1, sub, warn, body in FILES:
    full = os.path.join(OUT, "viz", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    html = (HEAD.format(title=title, css=CSS, h1=h1, sub=sub,
                        warn=f'<div class="warn">{warn}</div>')
            + body + TAIL)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("寫出", path, len(html), "bytes")
