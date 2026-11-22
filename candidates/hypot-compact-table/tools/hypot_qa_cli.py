"""Portable finite-input hypot classification and exact-reference case export."""
import argparse,json
from hypot_finite_classifier import FiniteClassifier
from hypot_integer_reference import expected,MAX,INF

def encode(m,e):
    if e>=-1074:return ((e+1075)<<52)+(m-(1<<52))
    shift=-1074-e
    if m% (1<<shift):raise ValueError('inexact scale')
    return m>>shift

def variants(x,y):
    for swap in [False,True]:
        a,b=(y,x) if swap else (x,y)
        for sx,sy in [(0,0),(1<<63,0),(0,1<<63),(1<<63,1<<63)]:yield a|sx,b|sy

def hard_cases(c,all_scales=False):
    for a,b,g in sorted(c.families):
        lo=max(-1074-((a&-a).bit_length()-1)-g,-1074-((b&-b).bit_length()-1))
        hi=971-g
        for e in range(lo,hi+1) if all_scales else [0]:
            for x,y in variants(encode(a,e+g),encode(b,e)):yield x,y,'non_tie_midpoint_h100'

def boundary_cases():
    # Explicit finite edge cross-product, separate from hardness coverage.
    edge=[0,1,2,(1<<52)-1,1<<52,(1<<52)+1,0x3ff0000000000000,MAX-1,MAX]
    seen=set()
    for a in edge:
        for b in edge:
            for x,y in variants(a,b):
                if (x,y) not in seen:seen.add((x,y));yield x,y,'finite_format_boundary'

def parsebits(s):
    if len(s)!=16 or any(c not in '0123456789abcdefABCDEF' for c in s):raise argparse.ArgumentTypeError('16 hexadecimal digits required')
    return int(s,16)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('classify');q.add_argument('x',type=parsebits);q.add_argument('y',type=parsebits)
    q=sub.add_parser('cases');q.add_argument('--kind',choices=['hard','boundary'],required=True);q.add_argument('--all-scales',action='store_true');q.add_argument('--inputs-only',action='store_true')
    a=p.parse_args();c=FiniteClassifier()
    if a.cmd=='classify':print(json.dumps(c.classify(a.x,a.y)));return
    if a.all_scales and a.kind!='hard':p.error('--all-scales requires --kind hard')
    for x,y,kind in hard_cases(c,a.all_scales) if a.kind=='hard' else boundary_cases():
        if a.inputs_only:print(f'{x:016x} {y:016x}')
        else:print(json.dumps(dict(x=f'{x:016x}',y=f'{y:016x}',regime=kind,reference=dict(zip(['RN','RD','RU','RZ'],[f'{z:016x}' for z in expected(x,y)])))))

if __name__=='__main__':main()
