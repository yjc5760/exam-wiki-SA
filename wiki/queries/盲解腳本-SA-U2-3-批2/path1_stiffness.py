"""SA-U2-3 批 2 盲解路徑 1：平面剛架勁度法（frame.py）。python path1_stiffness.py"""
from frame import Frame
def run(t, build):
    print('=====', t); f = Frame(); build(f); f.solve(); f.report(); return f
def p2015_3(f):
    for n,x,y in [('A',0,0),('B',0,4),('C',1,4),('D',4,4),('G',4,0),('E',7,4),('F',8,4),('H',8,0)]: f.node(n,x,y)
    for n in 'AGH': f.support(n)
    f.member('AB','A','B'); f.member('GD','G','D'); f.member('HF','H','F')
    f.member('BC','B','C',hinge_j=True); f.member('CD','C','D',hinge_i=True)
    f.member('DE','D','E',hinge_j=True); f.member('EF','E','F',hinge_i=True)
    for m in ['BC','CD','DE','EF']: f.mload(m,'udl',wy=-4)
def p2017_3(f):
    for n,x,y in [('A',0,0),('B',0,4),('C',6,4),('D',6,0)]: f.node(n,x,y)
    f.support('A',1,1,0); f.support('D',1,1,0)
    f.member('AB','A','B'); f.member('BC','B','C'); f.member('DC','D','C')
    f.mload('BC','udl',wy=-45); f.mload('DC','pt',px=-60,a=2); f.load('C',fx=-60)
def p2019_3(f, d=1/12, w=1):
    for i,n in enumerate('ABCD'): f.node(n,i,0)
    f.support('A',1,1,0)
    for n in 'BCD': f.support(n,0,1,0)
    for a,b in ['AB','BC','CD']: f.member(a+b,a,b); f.mload(a+b,'udl',wy=-w)
    f.settle('B',1,-d); f.settle('C',1,-d)
def p2020_1(f):
    f.node('a',0,3); f.node('b',4,3); f.node('c',8,0); f.support('a'); f.support('c',1,0,0)
    f.member('ab','a','b'); f.member('bc','b','c'); f.mload('bc','pt',py=-68,a=2.5)
def p2020_2(f):
    for n,x,y in [('a',0,4),('b',4,4),('c',8,4),('d',12,4),('e',0,0),('f',4,0),('g',8,0),('h',12,0)]: f.node(n,x,y)
    for n in 'adeh': f.support(n)
    for m in ['ab','bc','cd','ef','fg','gh','fb','gc']: f.member(m,m[0],m[1],EI=20000)
    f.mload('bc','pt',py=-12,a=2); f.mload('fg','pt',py=-12,a=2)
def p2021_1(f):
    EI=10000
    for n,x in [('a',0),('b',4),('c',8),('d',10)]: f.node(n,x,0)
    f.node('s',4,-1); f.support('s'); f.support('a',0,1,0); f.support('d')
    f.member('ab','a','b',EI=EI,EA=1e12); f.member('bc','b','c',EI=EI,EA=1e12,hinge_j=True); f.member('cd','c','d',EI=EI,EA=1e12,hinge_i=True)
    f.member('spr','b','s',EI=1e-9,EA=15000,hinge_i=True,hinge_j=True)
    f.mload('ab','pt',py=-36,a=2); f.load('b',fy=-36)
def p2021_2(f):
    for n,x,y in [('a',0,3),('b',3,3),('e',9,3),('f',12,3),('c',3,0),('d',9,0)]: f.node(n,x,y)
    f.support('a',0,1,0); f.support('f',0,1,0); f.support('d',0,1,0); f.support('c',1,1,0)
    for m in ['ab','be','ef','cb','de','cd']: f.member(m,m[0],m[1],EI=20000,EA=1e12)
    f.load('f',fx=24)
def p2022_2(f):
    for n,x,y in [('a',0,0),('b',0,2),('c',0,4),('d',4,4),('p',4,6),('e',4,8)]: f.node(n,x,y)
    f.support('a',1,1,0); f.support('e',1,1,0)
    for m in ['ab','bc','cd','dp','pe']: f.member(m,m[0],m[1],EI=40000,EA=1e12)
    f.load('b',fx=30); f.load('p',fx=30)
def p2023_3(f):
    for n,x,y in [('A',0,0),('B',0,6),('C',4,6),('D',8,6)]: f.node(n,x,y)
    f.support('A',1,1,0); f.support('C',0,1,0); f.support('D')
    f.member('AB','A','B'); f.member('BC','B','C'); f.member('CD','C','D')
    f.mload('AB','udl',wx=-20); f.mload('BC','pt',py=50,a=2)
def p2024_3(f, r=1.5):
    f.node('A',0,0); f.node('B',0,1); f.node('C',r,1); f.node('D',r,0); f.support('A'); f.support('D')
    f.member('AB','A','B'); f.member('BC','B','C',hinge_j=True); f.member('DC','D','C',hinge_j=True); f.load('B',fx=1)
for k,v in list(globals().items()):
    if k.startswith('p20'):
        F = run(k, v); print({n: u for n, u in F.U.items()})
