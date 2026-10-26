"""Full-definition comparison with comments removed and whitespace collapsed.
Usage: python3 compare_components.py old-sin.c new-sin.c bindings.json output.json
Input source pins must be verified separately against the upstream Git blobs.
"""
from pathlib import Path
from fractions import Fraction as F
import re,json,sys,hashlib
NAMES=['_T','S1u','S2u','C2u','reduce_large_acc','u128_tod','mhUU']
def normalize(s):
    assert '"' not in s and "'" not in s
    return re.sub(r'\s+',' ',s).strip()

def body(s,name):
    s=re.sub(r'/\*.*?\*/|//[^\n]*',' ',s,flags=re.S)
    pattern=r'^static\b[^;{}#]*?\b'+name+(r'\s*\[\d+\]\s*=\s*\{' if name in NAMES[:4] else r'\s*\([^;{}]*\)\s*\{')
    matches=list(re.finditer(pattern,s,re.M));assert len(matches)==1,name
    m=matches[0]
    begin=m.end()-1;depth=1;end=begin+1
    while depth:
        depth+=(s[end]=='{')-(s[end]=='}');end+=1
    if name in NAMES[:4]:
        tail=re.match(r'\s*;',s[end:]);assert tail
        end+=tail.end()
    return normalize(s[m.start():end])

def support(source):
    s=re.sub(r'/\*.*?\*/|//[^\n]*',' ',source,flags=re.S);out={}
    m=re.search(r'^#if[^\n]*__BITINT_MAXWIDTH__[^\n]*\n.*?^#endif',s,re.M|re.S)
    assert m and m.group().count('typedef')==2
    out['u128-selection']=normalize(m.group())
    for name in ['u64','f64_u','b64u64_u']:
        pattern=(r'^typedef\s+uint64_t\s+u64\s*;' if name=='u64' else r'^typedef\s+union\s*\{[^}]*\}\s*'+name+r'\s*;')
        m=re.search(pattern,s,re.M);assert m,name
        out[name]=normalize(m.group())
    m=re.search(r'^#define U128[^\n]*',s,re.M);assert m and '\\' not in m.group()
    out['U128']=normalize(m.group())
    return out
def main():
    old,new=map(Path,sys.argv[1:3]);a=old.read_text();b=new.read_text();records=[]
    for name in NAMES:
        x,y=body(a,name),body(b,name);assert x==y,name
        records.append({'name':name,'full_definition_identical_after_comment_removal_and_whitespace_collapse':True,'definition_sha256':hashlib.sha256(x.encode()).hexdigest()})
    sa,sb=support(a),support(b);assert sa==sb
    for name,x in sa.items():
        records.append({'name':name,'supporting_definition_identical':True,'definition_sha256':hashlib.sha256(x.encode()).hexdigest()})
    assert normalize('a - -b')!=normalize('a-- b')
    altered=b.replace('static inline u128 mhUU','static inline u64 mhUU',1)
    assert body(altered,'mhUU')!=body(b,'mhUU')
    d=json.loads(Path(sys.argv[3]).read_text());assert F(d['aggregate_absolute_upper'])<F(30,1<<128)
    assert d['reduction_error']['output_units_verified']
    assert hashlib.sha256(new.read_bytes()).hexdigest() in d['source_hashes'].values()
    result={'old_pin':'74fcd1094a316164c94481f40f5c9658439bee63','new_pin':'336752ca18e1204321225ec90c1f43fcb90ada1b',
            'old_source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_source_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
            'components':records,'declaration_and_operator_controls_pass':True,'new_kernel_bound_below_previous_30_units':True,
            'reuse':'October8 reducer/table/distance and conversion-range arguments; historical all-input hardness completeness not regenerated'}
    Path(sys.argv[4]).write_text(json.dumps(result,indent=2)+'\n');print('Seven full definitions and five supporting type/macro definitions match; bound and controls pass')
if __name__=='__main__':main()
