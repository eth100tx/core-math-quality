# u = 8r
R = 8*r;
U = R;
u = R;
# u2 = mhUU(u,u)
ah2 = fixed<-64,dn>(u);
al2 = -(ah2 - u);
ahbh2 = ah2*ah2;
ahbl2 = ah2*al2;
albh2 = al2*ah2;
U2 = U*U; # U2 = (2*pi*r)^2
u2 = ahbh2 + (fixed<-128,dn>(ahbl2) + fixed<-128,dn>(albh2));
# u4 = mhUU(u2,u2)
ah3 = fixed<-64,dn>(u2);
al3 = -(ah3 - u2);
ahbh3 = ah3*ah3;
ahbl3 = ah3*al3;
albh3 = al3*ah3;
U4 = U2*U2; # U4 = (2*pi*r)^4
u4 = ahbh3 + (fixed<-128,dn>(ahbl3) + fixed<-128,dn>(albh3));

# evalPS
c1 = 0xc90fdaa22168c234c4c6628b80dbed80p-128;
c3 = 0x14abbce625be52beabb8e5506ca45b03p-128;
c5 = 0x00a335e33bad570e044c54995bb97635p-128;
c7 = 0x000265a5999d06c4p-64;
u2h = fixed<-64,dn>(u2);
u2l = -(u2h-u2);
S5 = c5-c7*U2;
s5 = c5-c7*u2h;
# s_1 \leftarrow c_1 - \mhUU(c_3, u_2)
ah4 = fixed<-64,dn>(c3);
al4 = -(ah4 - c3);
# bh4 = ah3
# bl4 = al3
ahbh4 = ah4*ah3;
ahbl4 = ah4*al3;
albh4 = al4*ah3;
T1 = c3*U2;
t1 = ahbh4 + (fixed<-128,dn>(ahbl4) + fixed<-128,dn>(albh4));
S1 = c1-T1;
s1 = c1-t1;
# s_2 = s_1 + \mhUU(s_5, u_4)
ah5 = fixed<-64,dn>(s5);
al5 = -(ah5 - s5);
bh5 = fixed<-64,dn>(u4);
bl5 = -(bh5 - u4);
ahbh5 = ah5*bh5;
ahbl5 = ah5*bl5;
albh5 = al5*bh5;
T2 = S5*U4;
t2 = ahbh5 + (fixed<-128,dn>(ahbl5) + fixed<-128,dn>(albh5));
S2 = S1 + T2;
s2 = s1 + t2;
# s = mhUU(s2,u)
ah6 = fixed<-64,dn>(s2);
al6 = -(ah6 - s2);
# bh6 = ah2
# bl6 = al2
ahbh6 = ah6*ah2;
ahbl6 = ah6*al2;
albh6 = al6*ah2;
Sr = S2*U; # Sr represents S(2piR)
SR = Sr + eps5; # SR represents sin(2piR) and |eps5|<=2^-128.601 the Sollya error
sr = ahbh6 + (fixed<-128,dn>(ahbl6) + fixed<-128,dn>(albh6));

# evalPC
v0 = 0xffffffffffffffffffffffffffffffffp-128;
v2 = 0x4ef4f326f91779692b71366cbcf0b096p-128;
v4 = 0x040f07c206d6b0ecd4c9076e3db78fedp-128;
v6 = 0x00155d3c7e3cbef9eec6962368fb7c41p-128;
v8 = 0x00003c3e845b5510p-64;
# c_6 \leftarrow v_6 - v_8 u_{2h}
C6 = v6-v8*U2;
c6 = v6-v8*u2h;
# c_4 \leftarrow v_4 - \mhUU(c_6, u_2)
ah7 = fixed<-64,dn>(c6);
al7 = -(ah7 - c6);
# bh7 = ah3
# bl7 = al3
ahbh7 = ah7*ah3;
ahbl7 = ah7*al3;
albh7 = al7*ah3;
T3 = C6*U2;
t3 = ahbh7 + (fixed<-128,dn>(ahbl7) + fixed<-128,dn>(albh7));
C4 = v4-T3;
c4 = v4-t3;
# c_0 \leftarrow v_0 - \mhUU(v_2, u_2)
ah8 = fixed<-64,dn>(v2);
al8 = -(ah8 - v2);
# bh8 = ah3
# bl8 = al3
ahbh8 = ah8*ah3;
ahbl8 = ah8*al3;
albh8 = al8*ah3;
T4 = v2*U2;
t4 = ahbh8 + (fixed<-128,dn>(ahbl8) + fixed<-128,dn>(albh8));
C0 = v0-T4;
c0 = v0-t4;
# c_r \leftarrow c_0 + \mhUU(c_4, u_4)
ah9 = fixed<-64,dn>(c4);
al9 = -(ah9 - c4);
# bh9 = bh5
# bl9 = bl5
ahbh9 = ah9*bh5;
ahbl9 = ah9*bl5;
albh9 = al9*bh5;
T5 = C4*U4;
t5 = ahbh9 + (fixed<-128,dn>(ahbl9) + fixed<-128,dn>(albh9));
Cr = C0+T5; # Cr represents C(2piR)
CR = Cr + eps4; # CR represents cos(2piR) and |eps4|<=2^-128 the Sollya error
cr = c0+t5;

# w_1 \leftarrow \mhUU(c_z,c_r)
ah10 = fixed<-64,dn>(cz);
al10 = -(ah10 - cz);
bh10 = fixed<-64,dn>(cr);
bl10 = -(bh10 - cr);
ahbh10 = ah10*bh10;
ahbl10 = ah10*bl10;
albh10 = al10*bh10;
Cz = cz - eps2;
W1 = Cz*CR;
w1 = ahbh10 + (fixed<-128,dn>(ahbl10) + fixed<-128,dn>(albh10));
# w_2 \leftarrow \mhUU(s_z,s_r)
ah11 = fixed<-64,dn>(sz);
al11 = -(ah11 - sz);
bh11 = fixed<-64,dn>(sr);
bl11 = -(bh11 - sr);
ahbh11 = ah11*bh11;
ahbl11 = ah11*bl11;
albh11 = al11*bh11;
Sz = sz - eps3;
W2 = Sz*SR;
w2 = ahbh11 + (fixed<-128,dn>(ahbl11) + fixed<-128,dn>(albh11));

#@-Eprecision=200

# { r in [0,1b-14] -> s5 in ? } # [2^(-8.649415),2^(-8.649398)]
# { r in [0,1b-14] -> s1 in ? } # [0.785398,0.785399]
# { r in [0,1b-14] -> s2 in ? } # [0.785398,0.785399]
# { r in [0,1b-14] -> |sr-Sr| in ? } # 2^(-126.414306)
# 2^-128.605 < 2694b-140
# { r in [0,1b-14] /\ eps5 in [-2694b-140,2694b-140] -> |sr-SR| in ? } # 2^(-126.128417) [Lemma evalPS]
# { r in [0,1b-14] -> c6 in ? } # [2^(-11.582886),2^(-11.582870)]
# { r in [0,1b-14] -> c4 in ? } # [2^(-5.978982),2^(-5.978973)]
# { r in [0,1b-14] -> c0 in ? } # [0.999999,1]
# { r in [0,1b-14] -> c0 >= 0 /\ c0 <= 0xffffffffffffffffffffffffffffffffp-128 }
# { r in [0,1b-14] -> cr >= 0.999999 /\ cr <= 0xffffffffffffffffffffffffffffffffp-128 }
# { r in [0,1b-14] -> |cr-Cr| in ? } # 2^(-126.369995)
# { r in [0,1b-14] /\ eps4 in [-1b-128,1b-128] -> |cr-CR| in ? } # 2^(-125.966064) [Lemma evalPC]
# { r in [0,1b-14] /\ sz in [0,1] -> |w1-cz*cr| in ? } # 2^(-126.414916)
# 2^-125.691 < 20298b-140
# { r in [0,1b-14] /\ cz in [0,1] /\ eps2 in [-20298b-140,20298b-140] /\ eps4 in [-1b-128,1b-128] -> |w1-W1| in ? } # 2^(-124.414550)
# { r in [0,1b-14] /\ sz in [0,1] -> |w2-sz*sr| in ? } # 2^(-126.414916)
{ r in [0,1b-14] -> cr >= 0.999999 /\ cr <= 0xffffffffffffffffffffffffffffffffp-128 }

u2 - u*u ->
  (fixed<-128,dn>(ahbl2) - ahbl2) +
  (fixed<-128,dn>(albh2) - albh2) -
  al2*al2;
u4 - u2*u2 ->
  (fixed<-128,dn>(ahbl3) - ahbl3) +
  (fixed<-128,dn>(albh3) - albh3) -
  al3*al3;
t1 - c3*u2 ->
  (fixed<-128,dn>(ahbl4) - ahbl4) +
  (fixed<-128,dn>(albh4) - albh4) -
  al4*al3;
t2 - s5*u4 ->
  (fixed<-128,dn>(ahbl5) - ahbl5) +
  (fixed<-128,dn>(albh5) - albh5) -
  al5*bl5;
sr - s2*u ->
  (fixed<-128,dn>(ahbl6) - ahbl6) +
  (fixed<-128,dn>(albh6) - albh6) -
  al6*al2;
t3 - c6*u2 ->
  (fixed<-128,dn>(ahbl7) - ahbl7) +
  (fixed<-128,dn>(albh7) - albh7) -
  al7*al3;
t4 - v2*u2 ->
  (fixed<-128,dn>(ahbl8) - ahbl8) +
  (fixed<-128,dn>(albh8) - albh8) -
  al8*al3;
t5 - c4*u4 ->
  (fixed<-128,dn>(ahbl9) - ahbl9) +
  (fixed<-128,dn>(albh9) - albh9) -
  al9*bl5;
w1 - cz*cr ->
  (fixed<-128,dn>(ahbl10) - ahbl10) +
  (fixed<-128,dn>(albh10) - albh10) -
  al10*bl10;
w1-W1 -> (w1-cz*cr) + cz*(cr-Cr) + eps2*Cr + eps4*eps2 - eps4 * cz;
w2 - sz*sr ->
  (fixed<-128,dn>(ahbl11) - ahbl11) +
  (fixed<-128,dn>(albh11) - albh11) -
  al11*bl11;
w2-W2 -> (w2-sz*sr) + sz*(sr-Sr) + eps3*Sr + eps5*eps3 - eps5*sz;
cr-CR -> (cr-Cr) - eps4;
sr-SR -> (sr-Sr) - eps5;
