"""Finite sanity check of an algebraic ABI argument; not a reachable-input search."""
import random,json,sys
from pathlib import Path
MASK=(1<<64)-1
def s32(x):return (x+(1<<31))%(1<<32)-(1<<31)
def predicates(tn,tl):
    assert 0<=tn<1<<63 and 0<=tl<1<<63 and tn%(1<<52)==0
    gap=(tn-tl)&MASK;dn=tl-tn;de=gap>>52
    lp64=(-2<=dn<=0) or de>47
    modulo32=(-2<=s32(tl)-s32(tn)<=0) or de>47
    portable=gap<=2 or de>47
    assert lp64==portable
    assert not portable or modulo32
    return lp64,modulo32

def main():
    n=0;r=random.Random(20261026)
    for e in range(53,2047):
        tn=(e-53)<<52
        for offset in [-2**52,-2**32,-3,-2,-1,0,1,2,3,2**32,2**52]:
            tl=tn+offset
            if 0<=tl<1<<63:predicates(tn,tl);n+=1
        predicates(tn,r.randrange(1<<63));n+=1
    tn=(1000-53)<<52;tl=tn-(1<<32)
    assert predicates(tn,tl)==(False,True)
    d={'tested_pairs':n,'lp64_equivalent':True,'no_modulo32_false_negative_in_test':True,
       'synthetic_extra_lookup':{'tn':hex(tn),'tl':hex(tl)},
       'scope':'Arithmetic encodings, not asserted reachable from cr_asin. LLP64 behavior is modeled with modulo conversion; no Windows qualification.'}
    Path(sys.argv[1]).write_text(json.dumps(d,indent=2)+'\n');print(n,'synthetic encoding pairs passed')

if __name__=='__main__':main()
