# Gappa proof of Lemma lemma4bis for t >= 2

@rnd = float<ieee_64,ne>;
@round = int<ne>;

x = rnd(x_);
s = 0x1.71547652b82fep+12;
tmp0=rnd(x*s);
t = round(tmp0);
l2h = 0x1.62e42ffp-13;
l2l = 0x1.718432a1b0e26p-47;
l2s = 0x1.9ff0342542fc3p-102;
dx = x - l2h*t; # exact (see proof of Lemma lemma3)
dxl = rnd(l2l*t);
inter0 = l2l*t - dxl; # fma(l2l,t,-dxl) in the code, exact
inter1 = rnd(l2s*t);
dxll = rnd (l2s*t + inter0);
# Dh,Tl <- fast2sum(dx, dxl)
Dh = rnd(dx + dxl);
Tl = -(Dh -(dx + dxl)); # exact
Dl = rnd(Tl + dxll); 
dxr = Dh + Dl;

l2_real = l2h - l2l - l2s;
dx_real = x - l2_real*t;

# { x in [-746,710] /\ (t>=1 \/ t<=-1) -> dx in ? } # [-2^(-13.528030), 2^(-13.527984)]
# { x in [-746,710] /\ (t>=1 \/ t<=-1) -> dxl in ? } # [2^(-24.398681). 2^(-24.470062)]
{ x in [-746,710] /\ (t>=1 \/ t<=-1) -> |dxr - dx_real| <= 1025b-128} # 2^(-117.999145)

dxr - dx_real -> (Dl - (Tl + dxll)) + (dxll - (l2s*t + inter0));
dx_real -> -(l2_real*(t-tmp0) + l2_real*(tmp0 - x*s) + (l2_real*s - 1)*x);
