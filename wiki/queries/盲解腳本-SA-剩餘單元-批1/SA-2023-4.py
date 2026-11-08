"""SA-2023-4 偏心斜撐連梁端旋轉角推估
路徑1：剛性三角區機構 γ = θ·L/e，樓層側移比 θ_i ∝ 樓層剪力（各層連梁同 EI、同幾何 → 樓層勁度相同）
路徑2：以座標把左右剛性三角區繞其下角剛體旋轉，數值求連梁兩端相對轉角；並以虛功求樓層勁度驗證 θ ∝ V"""
import numpy as np, sympy as sp
h=4.0; a=4.0; e=0.6; L=2*a+e; top=0.06
P=[300,450,600]                      # 由下而上（每端或合計，比例同）
V=[sum(P[i:]) for i in range(3)]     # 樓層剪力 1F,2F,3F
dr=[top*v/sum(V) for v in V]; th=[d/h for d in dr]
g1=[t*L/e for t in th]
print('層剪力',V,' 層間側移(cm)',[round(d*100,4) for d in dr])
print('θ',th); print('路徑1 γ (rad)',g1)
# 路徑2 幾何
def link_rot(t):
    R=lambda ang: np.array([[np.cos(ang),np.sin(ang)],[-np.sin(ang),np.cos(ang)]])  # 順時針旋轉
    pL=np.array([a,h]); pR=np.array([a+e,h])        # 左三角繞 (0,0)、右三角繞 (L,0)
    qL=R(t)@pL; qR=np.array([L,0])+R(t)@(pR-np.array([L,0]))
    chord=np.arctan2(-(qR[1]-qL[1]),qR[0]-qL[0])   # 弦轉角（順時針正）
    return t-chord                                  # 端部切線（隨三角區轉 t）相對弦
g2=[link_rot(t) for t in th]; print('路徑2 γ (rad, 有限轉角)',g2)
# 虛功：V h θ = 2·(6EIγ/e)·γ，γ=θL/e → K_story = 12EI L^2/(h^2 e^3) 與層無關
EI,t=sp.symbols('EI theta',positive=True)
gam=t*L/e; Vst=sp.simplify(2*6*EI*gam/e*gam/(h*t)); print('V(θ)=',Vst,'→ θ ∝ V')
print('替代（均勻側移比 θ=6/1200）γ=',top/12*L/e)
