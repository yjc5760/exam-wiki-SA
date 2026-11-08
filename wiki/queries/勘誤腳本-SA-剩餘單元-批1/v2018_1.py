# SA-2018-1 independent check (interpretation B shape). Path1: discrete 8-DOF wall flexibility + shear frame.
# Path2: continuum EI y'''' - GA y'' = w via FD, frame force density = -GA y''.
import numpy as np
n=8
def disc(EI,k=1.0):
    z=np.arange(1,n+1.); f=np.array([[min(a,b)**2*(3*max(a,b)-min(a,b))/(6*EI) for b in z] for a in z]); Kw=np.linalg.inv(f)
    Kf=np.zeros((n,n))
    for s in range(n):
        Kf[s,s]+=k
        if s>0: Kf[s-1,s-1]+=k; Kf[s,s-1]-=k; Kf[s-1,s]-=k
    u=np.linalg.solve(Kw+Kf,np.ones(n)); return Kf@u, Kw@u
def cont(EI,GA=1.0,H=8.0,m=801):
    x=np.linspace(0,H,m); d=x[1]-x[0]; N=m
    A=np.zeros((N,N)); b=np.full(N,1.0)  # w=1 per unit height (F per floor, h=1)
    for i in range(2,N-2):
        A[i,i-2:i+3]+=EI*np.array([1,-4,6,-4,1])/d**4; A[i,i-1:i+2]+=-GA*np.array([1,-2,1])/d**2
    A[0]=0;A[0,0]=1;b[0]=0                         # y(0)=0
    A[1]=0;A[1,0:3]=[-1,0,1];b[1]=0                 # y'(0)=0 (wall fixed)  (centered approx using ghost-free one-sided)
    A[1]=0;A[1,0]=-3;A[1,1]=4;A[1,2]=-1;b[1]=0
    A[N-1]=0;A[N-1,N-3:N]=[1,-2,1];b[N-1]=0          # M=0 top: y''=0
    A[N-2]=0;A[N-2,N-4:N]=EI*np.array([-1,3,-3,1])/d**3;A[N-2,N-2:N]+=-GA*np.array([-1,1])/d;b[N-2]=0  # total shear 0 at top
    y=np.linalg.solve(A,b); ypp=np.gradient(np.gradient(y,d),d); wf=-GA*ypp  # frame distributed load
    return x,wf
mm=0
for EI in [5/12,5/3,1.0,3.0]:
    ff,fw=disc(EI)
    print("EI=%.3f frame:"%EI,np.round(ff,2)," wall:",np.round(fw,2))
    c1=ff[0]<0; c2=ff[-1]>1; c3=fw[-1]<0; c4=fw[0]>1
    if not(c1 and c2 and c3 and c4): mm+=1; print("  shape check fail",c1,c2,c3,c4)
    x,wf=cont(EI)
    zc=x[np.where(np.diff(np.sign(wf[50:-50])))[0]+50]
    print("  continuum: frame load at base %.2f, top region %.2f, sign change at x="%(wf[20],wf[-60]),np.round(zc,2))
    if not(wf[20]<0 and wf[-60]>0): mm+=1
# interpretation A
print("Interpretation A: frame F/6=%.3f wall 5F/6=%.3f each floor"%(1/6,5/6))
print("MISMATCHES:",mm)
