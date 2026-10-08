@rnd = float<ieee_64,zr>;
# capital letters Hxxx are exact values
x = rnd(x_);
c3h = -0x1.5555555555555p-3;
c3l = -0x1.55554b00de7e8p-57;
c5 = 0x1.111111110848p-7;
x2 = x*x;
x2h = rnd(x2);
x2l = x2-x2h; # exact
h0 = rnd(c5*x2h);
H0 = c5*x2;
h1 = rnd(c3l+h0);
H1 = c3l+H0;
# h_2, \ell_2 \leftarrow \fasttwosum(c_{3h}, h_1)
H2 = c3h+H1;
s2 = c3h+h1;
h2 = rnd(s2);
l2 = s2-h2+eps2;
# from Theorem 9-11 from "FastTwoSum revisited", |eps2| < ulp_106(s2)
# h_3, \ell_3 \leftarrow \muldd(h_2, \ell_2, x_{2h}, x_{2\ell})
H3 = H2*x2;
h3 = rnd(h2*x2h);
l3_1 = h2*x2h-h3;
l3_2 = rnd(h2*x2l);
l3_3 = rnd(l2*x2h);
l3_4 = rnd(l3_2+l3_3);
l3 = rnd(l3_4+l3_1);
# h_4, \ell_4 \leftarrow \muldd(h_3, \ell_3, x, 0)
H4 = H3*x;
h4 = rnd(h3*x);
l4_1 = h3*x-h4;
# l4_2 = rnd(h3*0) = 0
l4_3 = rnd(l3*x);
# l4_4 = rnd(l4_2+l4_3) = l4_3
l4 = rnd(l4_3+l4_1);
# h, t \leftarrow \fasttwosum(x, h_4)
s5 = x+h4;
h = rnd(s5);
t = s5-h+eps5;
# from Theorem 9-11 from "FastTwoSum revisited", |eps5| < ulp_106(s5)
H5 = x+H4; # H5 = S(x)
l = rnd(l4+t);

# { x in [-0x1p-16,-0x1p-26] -> x2h+x2l-x2 in ? }
# { x in [-0x1p-16,-0x1p-26] -> |h0-H0| in ? } # 2^(-90.383300)
# { x in [-0x1p-16,-0x1p-26] -> |h1-H1| in ? } # 2^(-89.658935)
# { x in [-0x1p-16,-0x1p-26] -> h1 // c3h in [-1,1] } # 1st fasttwosum condition
# { x in [-0x1p-16,-0x1p-26] -> h4 // x in [-1,1] } # 2nd fasttwosum condition
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // s2 in [-1b-105,1b-105] -> |(h2+l2)-s2| in ? } # 2^(-107.584960)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // s2 in [-1b-105,1b-105] -> |(h2+l2)-H2| in ? } # 2^(-89.658935)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] -> |h3+l3-(h2+l2)*(x2h+x2l)| in ? } # 2^(-136.677978)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] -> |h3+l3-H3| in ? } # 2^(-121.658813)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] -> |h4+l4-(h3+l3)*x| in ? } # 2^(-153.000000)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] -> |h4+l4-H4| in ? } # 2^(-137.658691)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] -> h4 // x in [-1,1] } # 2nd fasttwosum condition
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] /\ eps5 // s5 in [-1b-105,1b-105] -> |h+t-s5| in ? } # 2^(-121.000000)
# { x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] /\ eps5 // s5 in [-1b-105,1b-105] -> |h+l-H5| in ? } # 2^(-119.999877)}
{ x in [-0x1p-16,-0x1p-26] /\ eps2 // H2 in [-1b-105,1b-105] /\ eps5 // s5 in [-1b-105,1b-105] -> |h+l-H5|/|H5| <= 1b-103 }

x2h+x2l -> x2;
(h2+l2)-s2 -> eps2;
h3+l3-(h2+l2)*(x2h+x2l) -> (l3_2-h2*x2l) + (l3_3-l2*x2h) + (l3_4-(l3_2+l3_3)) + (l3-(l3_4+l3_1)) - l2*x2l;
h4+l4-(h3+l3)*x -> (l4_3-l3*x) + (l4-(l4_3+l4_1));
h+t-s5 -> eps5;
h+l-H5 -> (h4+l4-H4) + eps5 + (l-(l4+t));
