from truss import solve
from fractions import Fraction as Fr
import numpy as np
print('=== 2003-3')
P={}
L=[(0,0),(8,0),(16,0),(24,0),(32,0),(4,4),(12,4),(20,4),(28,4),(8,8),(16,8),(24,8)]
nd={p:p for p in L}
mem=[((0,0),(4,4)),((4,4),(8,8)),((8,8),(12,4)),((12,4),(16,0)),((4,4),(12,4)),((4,4),(8,0)),((8,0),(12,4)),
     ((32,0),(28,4)),((28,4),(24,8)),((24,8),(20,4)),((20,4),(16,0)),((28,4),(20,4)),((28,4),(24,0)),((24,0),(20,4)),
     ((8,8),(16,8)),((16,8),(24,8)),((16,8),(16,0)),((0,0),(8,0)),((8,0),(16,0)),((16,0),(24,0)),((24,0),(32,0))]
f,R=solve(nd,mem,[((0,0),(1,0)),((0,0),(0,1)),((32,0),(0,1))],{(8,0):(0,-2),(16,0):(0,-2)})
for k,v in f.items(): print(k,round(v,4))
print('R',R.round(4)); print('a',f[((4,4),(12,4))],'b',f[((8,8),(12,4))])
print('=== 2010-1')
nd={'G':(0,0),'H':(4,0),'C':(0,2),'D':(2,2),'E':(4,2),'F':(6,2),'A':(2,4),'B':(6,4)}
mem=[('A','B'),('A','C'),('A','E'),('E','B'),('B','F'),('C','D'),('D','E'),('E','F'),('C','G'),('G','D'),('D','H'),('G','H'),('H','F')]
f,R=solve(nd,mem,[('B',(1,0)),('G',(1,0)),('G',(0,1))],{'H':(0,-30)})
for k,v in f.items(): print(k,round(v,4))
print('R Bx Gx Gy',R.round(4))
print('=== 2013-1')
nd={'a':(0,0),'l':(5,10),'b':(0,20),'k':(10,20),'c':(0,30),'d':(10,30),'e':(20,30),'f':(30,30),'j':(30,20),'g':(40,30),'h':(40,20),'i':(40,10)}
mem=[tuple(s) for s in 'cd de ef fg cb ba ck dk bk ke bl lk al ej fj jg jh gh hi ji'.split()]
f,R=solve(nd,mem,[('a',(1,0)),('a',(0,1)),('i',(1,0)),('i',(0,1))],{'c':(0,-5),'d':(0,-10),'e':(0,-10),'f':(0,-10),'g':(0,-5)})
for k,v in f.items(): print(k,round(v,4))
print('R ax ay ix iy',R.round(4))
print('=== 2014-1')
nd={'A':(0,0),'B':(12,0),'C':(24,0),'D':(36,0),'E':(48,0),'F':(60,0),'G':(72,0),'H':(12,12),'I':(24,17),'J':(36,22),'K':(48,17),'L':(60,12)}
mem=[tuple(s) for s in 'AH HI IJ JK KL LG AB BC CD DE EF FG BH CI DJ EK FL HC ID KD LE'.split()]
sup=[('A',(1,0)),('A',(0,1)),('G',(0,1))]
f,R=solve(nd,mem,sup,{'C':(0,-1)})
for k in [('C','D'),('I','D'),('I','J')]: print(k,f[k], Fr(f[k]).limit_denominator(2000))
for k,v in f.items(): print(' ',k,round(v,4))
for n in 'BCDEF':
    f,R=solve(nd,mem,sup,{n:(0,-1)}); print('P at',n,'CD=',round(f[('C','D')],5),Fr(f[('C','D')]).limit_denominator(2000))
