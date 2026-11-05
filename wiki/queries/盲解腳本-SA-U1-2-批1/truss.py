import numpy as np
def solve(nodes, members, supports, loads):
    # supports: list of (node, (dx,dy)) reaction direction unit
    idx={n:i for i,n in enumerate(nodes)}; N=len(nodes)
    m=len(members); r=len(supports)
    A=np.zeros((2*N,m+r)); b=np.zeros(2*N)
    for k,(i,j) in enumerate(members):
        pi=np.array(nodes[i],float); pj=np.array(nodes[j],float); u=(pj-pi)/np.linalg.norm(pj-pi)
        A[2*idx[i]:2*idx[i]+2,k]+=u; A[2*idx[j]:2*idx[j]+2,k]-=u
    for k,(n,d) in enumerate(supports):
        A[2*idx[n]:2*idx[n]+2,m+k]+=np.array(d,float)
    for n,(fx,fy) in loads.items():
        b[2*idx[n]]-=fx; b[2*idx[n]+1]-=fy
    assert np.linalg.matrix_rank(A)==2*N==m+r, (np.linalg.matrix_rank(A),2*N,m+r)
    x=np.linalg.solve(A,b)
    return {members[k]:x[k] for k in range(m)}, x[m:]
