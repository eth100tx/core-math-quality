@rnd = float<ieee_64,dn>;
r2 = r*r;
r2r rnd= r2;
s1 = 1;
s3 = -0x1.55555553068fp-3;
sh = r*(s1+s3*r2);
shr rnd= r*(s1+s3*r2r);
c2 = -0.5;
c4 = 0x1.55555553bfd3p-5;
ch = r2*(c2+c4*r2);
chr rnd= r2r*(c2+c4*r2r);
# 2^-13.339 < 0x1.94dp-14
{ r in [-0x1.94dp-14,0x1.94dp-14] -> |shr-sh| in ? /\ |chr-ch| in ? }

