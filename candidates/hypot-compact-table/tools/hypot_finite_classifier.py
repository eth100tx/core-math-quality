"""Full finite-input non-tie midpoint-H100 predicate, including RN overflow.

Only the single real binary64 RN overflow boundary is considered, not any
unbounded-format midpoint above it. False does not exclude exact ties.
"""
from fractions import Fraction as Q
from hypot_family_classifier import Classifier,A

def boundary_certificate(families):
    eps=Q(1,1<<100)
    bound=eps*(2*A+eps)
    if not bound<Q(1,4):raise ValueError('subnormal residual certificate')
    checks=[]
    for a,b,g in sorted(families):
        S=(a<<g)**2+b*b
        for step,t2 in [(1,4*A-1),(2,8*A-2)]:
            T=t2<<(g-1);spacing=step<<g
            lower=(T<<100)-spacing;upper=(T<<100)+spacing
            scaled=S<<200
            hit=lower*lower<=scaled<=upper*upper
            if hit:raise ValueError('overflow last-midpoint candidate')
            checks.append(dict(a=a,b=b,g=g,output_step=step,near_last_midpoint=False))
    return dict(subnormal_bound=[str(bound.numerator),str(bound.denominator)],
                nonzero_residual_quantum=['1','4'],last_midpoint_checks=checks,
                overflow_definition='Distance to2^1024-2^970 normalized by2^971; no abstract midpoint beyond2^1024')

class FiniteClassifier(Classifier):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.boundary_certificate=boundary_certificate(self.families)
    def classify(self,x,y):
        result=super().classify(x,y)
        if result['status']=='outside_subnormal_norm':return dict(status='subnormal_norm_excluded',hit=False)
        if result['status']=='outside_overflow_norm':return dict(status='overflow_norm_excluded',hit=False)
        return result
