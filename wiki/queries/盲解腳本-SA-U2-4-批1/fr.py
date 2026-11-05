"""共用：2D 剛架（只取彎曲項，軸向以運動約束處理）。sympy。
符號：全域 x 右、y 上、轉角逆時針為正；桿端力以局部座標回報 (N1,V1,M1,N2,V2,M2)，
M 為作用在桿端、逆時針為正。總位能法組 K 與 R：K d = P - FEF。"""
import sympy as sp


def k_beam_local(EI, L):
    k = sp.zeros(6, 6)
    a, b, c, d = 12*EI/L**3, 6*EI/L**2, 4*EI/L, 2*EI/L
    idx = [1, 2, 4, 5]
    m = sp.Matrix([[a, b, -a, b], [b, c, -b, d], [-a, -b, a, -b], [b, d, -b, c]])
    for i in range(4):
        for j in range(4):
            k[idx[i], idx[j]] = m[i, j]
    return k


def rot(c, s):
    T = sp.zeros(6, 6)
    r = sp.Matrix([[c, s, 0], [-s, c, 0], [0, 0, 1]])
    T[:3, :3] = r; T[3:, 3:] = r
    return T


class Frame:
    def __init__(s, red):
        s.red = list(red); s.mem = []; s.nodes = {}

    def node(s, n, x, y, u=0, v=0, t=0):
        s.nodes[n] = (x, y, sp.Matrix([u, v, t]))

    def member(s, n1, n2, EI, fef_local=None, t1=None, t2=None):
        s.mem.append((n1, n2, EI, fef_local if fef_local is not None else sp.zeros(6, 1), t1, t2))

    def _d(s, m):
        n1, n2, EI, fef, t1, t2 = m
        x1, y1, d1 = s.nodes[n1]; x2, y2, d2 = s.nodes[n2]
        L = sp.sqrt((x2-x1)**2+(y2-y1)**2); c = (x2-x1)/L; sn = (y2-y1)/L
        d = sp.Matrix([d1[0], d1[1], d1[2] if t1 is None else t1,
                       d2[0], d2[1], d2[2] if t2 is None else t2])
        return L, rot(c, sn), d, EI, fef

    def solve(s, extra_PE=0, P=0):
        q = sp.Matrix(s.red)
        PE = extra_PE - P
        for m in s.mem:
            L, T, d, EI, fef = s._d(m)
            kg = T.T*k_beam_local(EI, L)*T
            PE += (d.T*kg*d)[0]/2 + (d.T*(T.T*fef))[0]
        eqs = [sp.expand(sp.diff(PE, x)) for x in q]
        K = sp.Matrix([[sp.simplify(sp.diff(e, y)) for y in q] for e in eqs])
        R = -sp.Matrix([sp.simplify(e.subs({x: 0 for x in q})) for e in eqs])
        sol = K.LUsolve(R)
        s.K, s.R = K, R
        s.sol = dict(zip(list(q), [sp.simplify(v) for v in sol]))
        return s.K, s.R, s.sol

    def end_forces(s):
        out = []
        for m in s.mem:
            L, T, d, EI, fef = s._d(m)
            f = k_beam_local(EI, L)*T*d + fef
            out.append((m[0], m[1], sp.simplify(f.subs(s.sol))))
        return out


def fef_udl(wy, L):
    """局部 y 正向的均佈 wy（向下載重在水平桿給 wy=-w）"""
    return sp.Matrix([0, -wy*L/2, -wy*L**2/12, 0, -wy*L/2, wy*L**2/12])


def fef_point_mid(Py, L):
    return sp.Matrix([0, -Py/2, -Py*L/8, 0, -Py/2, Py*L/8])


def show(F):
    for n1, n2, f in F:
        print(f"  {n1}{n2}: M{n1}={sp.factor(f[2])}, M{n2}={sp.factor(f[5])}, V{n1}={sp.factor(f[1])}, V{n2}={sp.factor(f[4])}")
