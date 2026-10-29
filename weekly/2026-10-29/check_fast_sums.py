"""Verify printed aggregate fast-path inequalities with exact rational bounds.
This checks arithmetic implications, not the analytic premises individually.
"""
from fractions import Fraction as F
from pathlib import Path
import sys,json,time
from check_bindings_cos import power
start=time.process_time();checks=[]
def upper(e):return power(e,True)
def check(name,terms,target):
 v=sum(terms,F(0));assert v<target,name;checks.append({'name':name,'upper':str(v),'strict_target':str(target)})
check('moderate theoretical sum',[upper('103.342'),upper('77.708'),upper('63.699')],power('63.698'))
check('moderate rounding sum',[2*F(1,1<<80),2*F(1,1<<66),upper('66.912')],power('64.659'))
check('moderate final enclosure',[upper('63.698'),upper('64.659')],F(float.fromhex('0x1.dep-64')))
check('large theoretical sum',[upper('103.342'),upper('77.681'),upper('63.675')],power('63.674'))
check('large rounding sum',[2*F(1,1<<80),3*F(1,1<<66)],power('64.414'))
check('large final enclosure',[upper('63.674'),upper('64.414')],F(float.fromhex('0x1.01p-63')))
cases=0
for base in [0,1]:
 for quadrant in [0,1]:
  for neg in [0,1]:
   for w1,w2 in [(1,2),(2,1),(1,1)]:
    sign=base
    if quadrant^neg:c=w1+w2
    elif w1<=w2:c=w2-w1;sign^=1
    else:c=w1-w2
    got=(-1)**(sign^quadrant)*c
    expected=(-1)**base*((-1)**quadrant*w1-(-1)**neg*w2)
    assert got==expected;cases+=1
Path(sys.argv[1]).write_bytes((json.dumps({'inequalities':checks,'sign_assembly_cases':cases,'cpu_seconds':time.process_time()-start,'scope':'Exact aggregate inequalities conditional on stated component bounds; sign algebra including both orderings and equality, not a proof of all numeric premises.'},indent=2)+'\n').encode())
print('Six exact aggregate inequalities and 24 sign-assembly cases pass')
