@rnd = float<ieee_64,dn>;
r2 = r*r;
r2r rnd= r2;
s1 = 0x1.921fb54442d18p2;
s3 = -0x1.4abbcdb6b26d1p5;
sh = r*(s1+s3*r2);
shr rnd= r*(s1+s3*r2r);
c2 = -0x1.3bd3cc9be45dep4;
c4 = 0x1.03c1eee483083p6;
ch = r2*(c2+c4*r2);
chr rnd= r2r*(c2+c4*r2r);
{ r in [-1b-16,1b-16] -> |shr-sh| in ? /\ |chr-ch| in ? }

