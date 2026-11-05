"""frameviz — 依判讀清單畫題目附圖、依勁度法結果畫變形圖與彎矩圖（exam-wiki-SA，2026-11-04）
幾何、載重、支承全由呼叫端的 spec 給定；變形與彎矩全由 frame2d.Frame 解出，不寫死任何形狀。"""
import math
from structdraw import Canvas, C, compose, hermite

def sup_ang(d):
    """支承面垂直於 d（由支承指向結構的單位向量），剖線落在 -d 側。"""
    return math.degrees(math.atan2(-d[0], d[1]))

def fit(pts, W, H, L=70, R=70, T=70, B=70):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    xr=max(xs)-min(xs) or 1; yr=max(ys)-min(ys) or 1
    sx=min((W-L-R)/xr,(H-T-B)/yr)
    ox=L+((W-L-R)-xr*sx)/2-min(xs)*sx; oy=B+((H-T-B)-yr*sx)/2-min(ys)*sx
    return sx,ox,oy

def unit(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); return (dx/L,dy/L),L

def draw_members(cv, N, members, color=C["member"], scale_w=True, dash=None):
    for m in members:
        i,j=m['ij']; w=(8.5 if m.get('thick') else 6.0) if scale_w else 3.2
        cv.line(N[i],N[j],color,w,dash=dash,cap="butt")

def draw_supports(cv, N, members, supports, size=18):
    for nd,kind in supports:
        # 找與此節點相連的桿件方向
        for m in members:
            i,j=m['ij']
            if nd in (i,j):
                o=j if nd==i else i; d,_=unit(N[nd],N[o]); break
        if kind=='fixed': ang=sup_ang(d); cv.fixed_support(N[nd],ang,size)
        else:
            # 鉸／滾支承：支承面一律水平（考卷畫法），除非指定
            cv.support(N[nd],kind,0,size*0.85)

def draw_problem(cv, sp):
    N=sp['nodes']
    draw_members(cv,N,sp['members'])
    draw_supports(cv,N,sp['members'],sp['supports'])
    for nd in sp.get('hinges',[]):
        cv.dot(N[nd],7,fill="#FFFFFF",stroke=C["member"],w=2.6)
    for (a,b,h,lab) in sp.get('udl',[]):
        cv.udl(N[a],N[b],h,n=sp.get('udl_n',9),label=lab)
    for ld in sp.get('loads',[]):
        nd,(dx,dy),lab,lo=ld[:4]; away=len(ld)>4 and ld[4]
        p=N[nd]
        if away: tail,head=(p[0]+dx*0.12,p[1]+dy*0.12),(p[0]+dx,p[1]+dy); lp=head
        else: tail,head=(p[0]-dx,p[1]-dy),p; lp=tail
        cv.arrow(tail,head,C["load"],3.4,12)
        if lab: cv.math(lp,lab,17,C["load"],"middle",dx=lo[0],dy=lo[1],weight="700")
    for (nd,ccw,lab,lo) in sp.get('moments',[]):
        cv.moment_arrow(N[nd],r=24,ccw=ccw,color=C["load"],w=2.8,span=250,start=110)
        cv.math(N[nd],lab,16,C["load"],"middle",dx=lo[0],dy=lo[1],weight="700")
    for nd,(dx,dy) in sp.get('labels',{}).items():
        cv.text(N[nd],nd,17,C["text"],weight="700",dx=dx,dy=dy)
    for (p,s,col,anchor) in sp.get('mlabels',[]):
        cv.math(p,s,15,C["muted"] if col is None else col,anchor)
    for (p0,p1,lab,off) in sp.get('dims',[]):
        cv.dim(p0,p1,lab,off=off,label_off=(15 if off>=0 else -15))
    for (p,s) in sp.get('texts',[]):
        cv.text(p,s,14,C["muted"])

# ── 由勁度法結果取桿件內力與變形 ──
def member_moment(f, m, xi):
    """梁彎矩（正彎矩＝桿軸右手側受拉），由桿端彎矩與跨內均布載重算出。"""
    q=f.end[m['name']]; (_,L)=unit(f.N[m['i']],f.N[m['j']]); x=xi*L
    Mi=-q[2]; Vi=q[1]            # q[2] 為作用於桿端之逆時針彎矩
    # 截面彎矩（正彎矩＝右手側受拉）：M(x)= -q2 + Vi*x - w x^2/2
    return Mi + Vi*x - m['w']*x*x/2

def draw_bmd(cv, f, scale, color=C["bmd"], fill=C["fill_m"], marks=True, fmt="{:.2f}", skip=(), min_mark=1e-6, mark_px=13):
    out=[]
    for m in f.M:
        if m['name'] in skip: continue
        p0,p1=f.N[m['i']],f.N[m['j']]; d,L=unit(p0,p1); n=(-d[1],d[0])
        pts=[]; vals=[]
        for k in range(41):
            xi=k/40; M=member_moment(f,m,xi); vals.append(M)
            base=(p0[0]+d[0]*xi*L,p0[1]+d[1]*xi*L)
            pts.append((base[0]-n[0]*M*scale, base[1]-n[1]*M*scale))   # 畫在受拉側（右手側＝-n）
        cv.polygon([p0]+pts+[p1],fill,color,2)
        out.append((m,vals,d,n,L))
    return out

def deformed(f, m, scale, n=40):
    p0,p1=f.N[m['i']],f.N[m['j']]; d,L=unit(p0,p1); nn=(-d[1],d[0])
    ui=f.d[m['i']]; uj=f.d[m['j']]
    loc=lambda u:(u[0]*d[0]+u[1]*d[1], -u[0]*d[1]+u[1]*d[0])
    ai,vi=loc(ui); aj,vj=loc(uj)
    ti=ui[2]; tj=uj[2]
    rel=m['rel']
    EI=m['EI']; w=m['w']
    # 端點轉角（釋放端用桿件實際切線，由 Hermite 補算）
    if rel[1]: tj=(3*(vj-vi)/L - ti)/2 + (-w*L**3/(48*EI))*0  # 近似：鉸端以端點條件
    if rel[0]: ti=(3*(vj-vi)/L - tj)/2
    pts=[]
    for k in range(n+1):
        xi=k/n; x=xi*L
        N1=1-3*xi**2+2*xi**3; N2=L*(xi-2*xi**2+xi**3); N3=3*xi**2-2*xi**3; N4=L*(-xi**2+xi**3)
        v=vi*N1+ti*N2+vj*N3+tj*N4
        v+= -w*x*x*(L-x)**2/(24*EI)          # 固端梁均布載重之撓度（局部 -y 方向）
        a=ai+(aj-ai)*xi
        base=(p0[0]+d[0]*x,p0[1]+d[1]*x)
        pts.append((base[0]+(d[0]*a+nn[0]*v)*scale, base[1]+(d[1]*a+nn[1]*v)*scale))
    return pts

def inflections(f, m):
    vals=[member_moment(f,m,k/400) for k in range(401)]
    out=[]
    for k in range(400):
        a,b=vals[k],vals[k+1]
        if a==0: continue
        if a*b<0:
            xi=(k+a/(a-b))/400
            if 0.02<xi<0.98: out.append(xi)      # 桿端彎矩為零（鉸端）不算反曲點
    return out

def _extent(sp):
    pts=list(sp['nodes'].values())
    for ld in sp.get('loads',[]):
        p=sp['nodes'][ld[0]]; dx,dy=ld[1]; pts.append((p[0]-dx,p[1]-dy)); pts.append((p[0]+dx,p[1]+dy))
    for (a,b,h,lab) in sp.get('udl',[]):
        for nd in (a,b): p=sp['nodes'][nd]; pts.append((p[0],p[1]+h))
    for q in sp.get('extra_pts',[]): pts.append(q)
    return pts

def problem_figure(sp, path, W=760, H=520, title=None, note=None, margins=(115,115,80,135)):
    sx,ox,oy=fit(_extent(sp),W,H,*margins)
    cv=Canvas(W,H,sx=sx,ox=ox,oy=oy,bg="#FFFFFF")
    if 'pre' in sp: sp['pre'](cv)
    draw_problem(cv,sp)
    if title: cv.text_px(W/2,26,title,15.5,C["text"],weight="700")
    if note: cv.text_px(W/2,H-18,note,12.5,C["muted"])
    return cv.save(path)

def solution_figure(f, sp, path, dscale, mscale, title, sub_def, sub_bmd, munit="", fmt="{:.2f}",
                    W=520, H=470, notes=("",""), skip_mark=(), label_px=14, margins=(70,70,95,95), extra_pts_m=()):
    """左：變形形狀（灰虛線＝原位置）；右：彎矩圖（畫在受拉側），反曲點以 ○ 標示。"""
    N=sp['nodes']; members=[{'ij':(m['i'],m['j']),'thick':sp.get('thick',{}).get(m['name'],False)} for m in f.M]
    # 版面：涵蓋節點＋變形＋彎矩外擴
    pts=list(N.values())
    for m in f.M: pts+=deformed(f,m,dscale,10)
    for m in f.M:
        p0,p1=f.N[m['i']],f.N[m['j']]; d,L=unit(p0,p1); n=(-d[1],d[0])
        for k in range(11):
            M=member_moment(f,m,k/10); b=(p0[0]+d[0]*k/10*L,p0[1]+d[1]*k/10*L); pts.append((b[0]-n[0]*M*mscale,b[1]-n[1]*M*mscale))
    pts+=list(extra_pts_m)
    sx,ox,oy=fit(pts,W,H,*margins)
    a=Canvas(W,H,sx=sx,ox=ox,oy=oy); a.panel("變形形狀（示意放大）",sub_def)
    draw_members(a,N,members,C["ghost"],False,dash="6 5")
    for m in f.M: a.poly(deformed(f,m,dscale),C["deform"],5.0)
    draw_supports(a,N,members,sp['supports'],15)
    for nd in sp.get('hinges',[]): a.dot(N[nd],6,fill="#FFFFFF",stroke=C["deform"],w=2.4)
    for m in f.M:
        for xi in inflections(f,m):
            pt=deformed(f,m,dscale,400)[round(xi*400)]
            a.dot(pt,5.4,fill="#FFFFFF",stroke=C["accent"],w=2.9)
    if notes[0]: a.math_px(W/2,H-40,notes[0],14,C["deform"],weight="700")
    a.text_px(W/2,H-16,"○ ＝ 反曲點（彎矩為零）",12.5,C["accent"],weight="700")
    b=Canvas(W,H,sx=sx,ox=ox,oy=oy); b.panel("彎矩圖（畫在受拉側）",sub_bmd)
    res=draw_bmd(b,f,mscale)
    draw_members(b,N,members,"#4A5568",False)
    draw_supports(b,N,members,sp['supports'],15)
    for nd in sp.get('hinges',[]): b.dot(N[nd],6,fill="#FFFFFF",stroke="#4A5568",w=2.4)
    seen=set()
    for (m,vals,d,n,L) in res:
        p0=f.N[m['i']]
        cand=[(0.0,vals[0]),(1.0,vals[-1])]
        k=max(range(41),key=lambda k:abs(vals[k]))
        if 0<k<40 and abs(vals[k])>max(abs(vals[0]),abs(vals[-1]))*1.02: cand.append((k/40,vals[k]))
        for xi,M in cand:
            if abs(M)<1e-6 or (m['name'],round(xi,2)) in skip_mark: continue
            if xi in (0.0,1.0):
                key=(m['i'] if xi==0.0 else m['j'],round(abs(M),3))
                if key in seen: continue          # 兩桿相接、彎矩相等的節點只標一次
                seen.add(key)
            xs=min(max(xi,0.16),0.84) if xi in (0.0,1.0) else xi
            base=(p0[0]+d[0]*xs*L,p0[1]+d[1]*xs*L); off=-1 if M>0 else 1
            q=(base[0]-n[0]*M*mscale,base[1]-n[1]*M*mscale)
            sgn=1 if M>0 else -1
            px=b.X(q[0])+(-n[0])*sgn*label_px*1.6; py=b.Y(q[1])-(-n[1])*sgn*label_px*1.6
            b.text_px(px,py,(fmt.format(abs(M))+munit).strip(),label_px,C["bmd"],weight="700")
        for xi in inflections(f,m):
            b.dot((p0[0]+d[0]*xi*L,p0[1]+d[1]*xi*L),5,fill="#FFFFFF",stroke=C["accent"],w=2.6)
    if notes[1]: b.text_px(W/2,H-28,notes[1],12.5,C["bmd"],weight="700")
    compose([a,b],title=title,path=path)
    return path

def build_frame(sp):
    """由 spec 建立勁度法模型（EA→∞ 模擬不計軸向變形）。"""
    from frame2d import Frame
    f=Frame()
    for n,p in sp['nodes'].items(): f.node(n,*p)
    R={'fixed':(1,1,1),'pin':(1,1,0),'roller':(0,1,0)}
    for nd,kind in sp['supports']: f.support(nd,*R[kind])
    for nd,r in sp.get('extra_restraints',{}).items(): f.support(nd,*r)
    for m in sp['members']:
        i,j=m['ij']; f.member(m.get('name',i+j),i,j,m['EI'],w=m.get('w',0.0),rel=m.get('rel',(0,0)))
    for nd,fx,fy,mz in sp.get('fe_loads',[]): f.load(nd,fx,fy,mz)
    return f.solve()

def end_moments(f):
    """順時針為正之桿端彎矩 {'AB':(M_AB, M_BA)}"""
    return {m['name']:(-f.end[m['name']][2],-f.end[m['name']][5]) for m in f.M}
