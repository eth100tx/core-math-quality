"""Independent Python integer-sqrt reference for all finite binary64 inputs.

No float arithmetic in the reference. Integer units are 2^-1074.
"""
import math
MAX=0x7fefffffffffffff
INF=0x7ff0000000000000
def units(u):
    u&=0x7fffffffffffffff
    E=u>>52;m=u&((1<<52)-1)
    if E==2047:raise ValueError('Nonfinite input')
    return ((m|(1<<52))<<(E-1)) if E else m
def expected(x,y):
    S=units(x)**2+units(y)**2
    q=math.isqrt(S)
    if q==0:return [0]*4
    shift=max(0,q.bit_length()-53)
    sig=q>>shift
    lower=(sig if sig<(1<<52) else ((shift+1)<<52)+(sig-(1<<52)))
    lower=min(lower,MAX)
    L=units(lower)
    if L*L==S:return [lower]*4
    upper=lower+1
    U=(1<<2098) if upper==INF else units(upper)
    delta=4*S-(L+U)**2
    rn=lower if delta<0 or (delta==0 and not lower&1) else upper
    return [rn,lower,upper,lower]
