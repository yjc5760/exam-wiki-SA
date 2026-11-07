import numpy as np
W=[20,40,40,40]; OFF=[0,2.4,3.9,5.4]   # ① 在最左（車頭向左）
def maxeff(f, x0, x1, step=0.005, both=False):
    """f(x)：影響線函數（結構外回傳 0）；以車頭位置掃描。回傳 (max, 車頭位置, min, 位置)"""
    best=(-1e9,None); worst=(1e9,None)
    for xh in np.arange(x0-6,x1+0.001,step):
        v=sum(w*f(xh+o) for w,o in zip(W,OFF))
        if v>best[0]: best=(v,xh)
        if v<worst[0]: worst=(v,xh)
    return best,worst
