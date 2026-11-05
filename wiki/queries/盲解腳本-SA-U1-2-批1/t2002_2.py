from truss import solve
nd={'A':(0,0),'B':(32,0),'D':(0,12),'F':(8,12),'C':(16,12),'H':(24,12),'I':(32,12),'E':(8,6),'G':(24,6)}
mem=[('D','A'),('I','B'),('D','F'),('F','C'),('C','H'),('H','I'),('D','E'),('F','E'),('E','C'),('A','E'),('C','G'),('H','G'),('G','I'),('G','B')]
sup=[('A',(1,0)),('A',(0,1)),('B',(1,0)),('B',(0,1))]
ld={k:(0,-20) for k in 'DFCHI'}; ld['D']=(16,-20)
f,R=solve(nd,mem,sup,ld)
for k,v in f.items(): print(k,round(v,3))
print('R Ax Ay Bx By',R.round(3))
print('a DF',f[('D','F')],'b DE',f[('D','E')],'c AE',f[('A','E')],'d CH',f[('C','H')],'e CG',f[('C','G')])
