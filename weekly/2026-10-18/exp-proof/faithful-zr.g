# This file has been generated automatically and will be overwritten

@rnd = float<ieee_64,zr>;
@roundeven = int<ne>;

c0h=0x1p+0;
c0l=0;
c0=c0h+c0l;

c1h=0x1p-1;
c1l=0x1.712f72ecec2cfp-99;
c1=c1h+c1l;

c2h=0x1.5555555555555p-3;
c2l=0x1.5555555554d07p-57;
c2=c2h+c2l;

c3h=0x1.5555555555555p-5;
c3l=0x1.55194d28275dap-59;
c3=c3h+c3l;

c4h=0x1.1111111111111p-7;
c4l=0x1.12faa0e1c0f7bp-63;
c4=c4h+c4l;

c5h=0x1.6c16c16da6973p-10;
c5l=-0x1.4ba45ab25d2a3p-64;
c5=c5h+c5l;

c6h=0x1.a01a019eb7f31p-13;
c6l=-0x1.9091d845ecd36p-67;
c6=c6h+c6l;

# Defining real values 
dx_real = dxh+dxl;
y0_real = (c0 + dx_real * (c1 + dx_real * (c2 + dx_real * (c3 + dx_real * (c4 + dx_real * (c5 + dx_real * (c6)))))));
y1_real = dx_real*y0_real;
th = rnd(th_);
tl = rnd(tl_);
## fh, fl <- opolydd(dxh, dxl, 7, c)
v_ch = c6h;
v_cl = c6l;
rC = c6;

# v_ch1, v_cl1 <- fastFMA_dw(dxh, dxl, v_ch, v_cl, c5h, c5l)
v_ch1 = rnd (dxh * v_ch + c5h);
fma_t = c5h - v_ch1;
fma_e = rnd (-(v_ch1 - (dxh * v_ch + c5h)));
fma_f rnd = fma_e + c5l;
fma_g rnd = (dxh * v_cl + fma_f);
v_cl1 rnd = (dxl * v_ch + fma_g);
rC1 = dx_real*rC + c5;

# v_ch2, v_cl2 <- fastFMA_dw(dxh, dxl, v_ch1, v_cl1, c4h, c4l)
v_ch2 = rnd (dxh * v_ch1 + c4h);
fma_t1 = c4h - v_ch2;
fma_e1 = rnd (-(v_ch2 - (dxh * v_ch1 + c4h)));
fma_f1 rnd = fma_e1 + c4l;
fma_g1 rnd = (dxh * v_cl1 + fma_f1);
v_cl2 rnd = (dxl * v_ch1 + fma_g1);
rC2 = dx_real*rC1 + c4;

# v_ch3, v_cl3 <- fastFMA_dw(dxh, dxl, v_ch2, v_cl2, c3h, c3l)
v_ch3 = rnd (dxh * v_ch2 + c3h);
fma_t2 = c3h - v_ch3;
fma_e2 = rnd (-(v_ch3 - (dxh * v_ch2 + c3h)));
fma_f2 rnd = fma_e2 + c3l;
fma_g2 rnd = (dxh * v_cl2 + fma_f2);
v_cl3 rnd = (dxl * v_ch2 + fma_g2);
rC3 = dx_real*rC2 + c3;

# v_ch4, v_cl4 <- fastFMA_dw(dxh, dxl, v_ch3, v_cl3, c2h, c2l)
v_ch4 = rnd (dxh * v_ch3 + c2h);
fma_t3 = c2h - v_ch4;
fma_e3 = rnd (-(v_ch4 - (dxh * v_ch3 + c2h)));
fma_f3 rnd = fma_e3 + c2l;
fma_g3 rnd = (dxh * v_cl3 + fma_f3);
v_cl4 rnd = (dxl * v_ch3 + fma_g3);
rC4 = dx_real*rC3 + c2;

# v_ch5, v_cl5 <- fastFMA_dw(dxh, dxl, v_ch4, v_cl4, c1h, c1l)
v_ch5 = rnd (dxh * v_ch4 + c1h);
fma_t4 = c1h - v_ch5;
fma_e4 = rnd (-(v_ch5 - (dxh * v_ch4 + c1h)));
fma_f4 rnd = fma_e4 + c1l;
fma_g4 rnd = (dxh * v_cl4 + fma_f4);
v_cl5 rnd = (dxl * v_ch4 + fma_g4);
rC5 = dx_real*rC4 + c1;

# v_ch6, v_cl6 <- fastFMA_dw(dxh, dxl, v_ch5, v_cl5, c0h, c0l)
v_ch6 = rnd (dxh * v_ch5 + c0h);
fma_t5 = c0h - v_ch6;
fma_e5 = rnd (-(v_ch6 - (dxh * v_ch5 + c0h)));
fma_f5 rnd = fma_e5 + c0l;
fma_g5 rnd = (dxh * v_cl5 + fma_f5);
v_cl6 rnd = (dxl * v_ch5 + fma_g5);
rC6 = dx_real*rC5 + c0;
fh = v_ch6;
fl = v_cl6;

# fh_1, fl_1 <- muldd(dxh, dxl, fh, fl)
low_high rnd = dxl * fh;
high_low rnd = dxh * fl;
fh_1 rnd = dxh * fh;
high_high_rest = fh * dxh - fh_1;
t1 rnd = high_low + low_high;
fl_1 rnd = t1 + high_high_rest;
y0 = fh + fl;
y1 = fh_1 + fl_1;

# fh_2, fl_2 <- muldd(fh_1, fl_1, th, tl)
low_high1 rnd = fl_1 * th;
high_low1 rnd = fh_1 * tl;
fh_2 rnd = fh_1 * th;
high_high_rest2 = th * fh_1 - fh_2;
t2 rnd = high_low1 + low_high1;
fl_2 rnd = t2 + high_high_rest2;

# yh,yl <- fast_sum(th,tl,fh_2,fl_2)
yh=rnd(th + fh_2);
sl=rnd((th + fh_2) - yh);
yl rnd = (tl + fl_2) + sl;

y = yh + yl;
y_real = (y1_real*(th+tl) + (th+tl));

{ (dxh in [1b-154, 90901b-30] \/ dxh in [0,0] \/ dxh in [-90901b-30,-1b-154]) /\ @FIX(dxh,-154) /\ (dxl in [-16396b-80, -1b-154] \/ dxl in [0,0] \/ dxl in [1b-154, 16396b-80]) /\ @FIX(dxl,-154) /\ th in [1,2] /\ tl in [-598b-60,598b-60] ->  c5h // v_ch1 in [0.5, 2] /\  c4h // v_ch2 in [0.5, 2] /\  c3h // v_ch3 in [0.5, 2] /\  c2h // v_ch4 in [0.5, 2] /\  c1h // v_ch5 in [0.5, 2] /\  c0h // v_ch6 in [0.5, 2] /\ @FIX(dxh*fh, -1074) /\ @FIX(fh_1*th, -1074) /\ fh_2 // th in [-1,1] /\ |y - y_real| in ? /\ |yl| in ?}


(v_ch+v_cl) - rC -> (c6h+c6l) - c6;
(v_ch1 + v_cl1) - ((dxh + dxl)*(v_ch + v_cl) + (c5h + c5l)) -> (fma_e - (-(v_ch1 - (dxh * v_ch + c5h)))) + (fma_f - (fma_e + c5l)) + (fma_g - (dxh * v_cl + fma_f)) + (v_cl1 - (dxl * v_ch + fma_g)) - dxl*v_cl;
(v_ch1 + v_cl1) - rC1 -> ((v_ch1 + v_cl1) - ((dxh + dxl)*(v_ch + v_cl)+(c5h + c5l))) + (dxh + dxl)*((v_ch + v_cl) - rC) + ((dxh + dxl) - dx_real)*rC + ((c5h + c5l) - c5);
(v_ch2 + v_cl2) - ((dxh + dxl)*(v_ch1 + v_cl1) + (c4h + c4l)) -> (fma_e1 - (-(v_ch2 - (dxh * v_ch1 + c4h)))) + (fma_f1 - (fma_e1 + c4l)) + (fma_g1 - (dxh * v_cl1 + fma_f1)) + (v_cl2 - (dxl * v_ch1 + fma_g1)) - dxl*v_cl1;
(v_ch2 + v_cl2) - rC2 -> ((v_ch2 + v_cl2) - ((dxh + dxl)*(v_ch1 + v_cl1)+(c4h + c4l))) + (dxh + dxl)*((v_ch1 + v_cl1) - rC1) + ((dxh + dxl) - dx_real)*rC1 + ((c4h + c4l) - c4);
(v_ch3 + v_cl3) - ((dxh + dxl)*(v_ch2 + v_cl2) + (c3h + c3l)) -> (fma_e2 - (-(v_ch3 - (dxh * v_ch2 + c3h)))) + (fma_f2 - (fma_e2 + c3l)) + (fma_g2 - (dxh * v_cl2 + fma_f2)) + (v_cl3 - (dxl * v_ch2 + fma_g2)) - dxl*v_cl2;
(v_ch3 + v_cl3) - rC3 -> ((v_ch3 + v_cl3) - ((dxh + dxl)*(v_ch2 + v_cl2)+(c3h + c3l))) + (dxh + dxl)*((v_ch2 + v_cl2) - rC2) + ((dxh + dxl) - dx_real)*rC2 + ((c3h + c3l) - c3);
(v_ch4 + v_cl4) - ((dxh + dxl)*(v_ch3 + v_cl3) + (c2h + c2l)) -> (fma_e3 - (-(v_ch4 - (dxh * v_ch3 + c2h)))) + (fma_f3 - (fma_e3 + c2l)) + (fma_g3 - (dxh * v_cl3 + fma_f3)) + (v_cl4 - (dxl * v_ch3 + fma_g3)) - dxl*v_cl3;
(v_ch4 + v_cl4) - rC4 -> ((v_ch4 + v_cl4) - ((dxh + dxl)*(v_ch3 + v_cl3)+(c2h + c2l))) + (dxh + dxl)*((v_ch3 + v_cl3) - rC3) + ((dxh + dxl) - dx_real)*rC3 + ((c2h + c2l) - c2);
(v_ch5 + v_cl5) - ((dxh + dxl)*(v_ch4 + v_cl4) + (c1h + c1l)) -> (fma_e4 - (-(v_ch5 - (dxh * v_ch4 + c1h)))) + (fma_f4 - (fma_e4 + c1l)) + (fma_g4 - (dxh * v_cl4 + fma_f4)) + (v_cl5 - (dxl * v_ch4 + fma_g4)) - dxl*v_cl4;
(v_ch5 + v_cl5) - rC5 -> ((v_ch5 + v_cl5) - ((dxh + dxl)*(v_ch4 + v_cl4)+(c1h + c1l))) + (dxh + dxl)*((v_ch4 + v_cl4) - rC4) + ((dxh + dxl) - dx_real)*rC4 + ((c1h + c1l) - c1);
(v_ch6 + v_cl6) - ((dxh + dxl)*(v_ch5 + v_cl5) + (c0h + c0l)) -> (fma_e5 - (-(v_ch6 - (dxh * v_ch5 + c0h)))) + (fma_f5 - (fma_e5 + c0l)) + (fma_g5 - (dxh * v_cl5 + fma_f5)) + (v_cl6 - (dxl * v_ch5 + fma_g5)) - dxl*v_cl5;
(v_ch6 + v_cl6) - rC6 -> ((v_ch6 + v_cl6) - ((dxh + dxl)*(v_ch5 + v_cl5)+(c0h + c0l))) + (dxh + dxl)*((v_ch5 + v_cl5) - rC5) + ((dxh + dxl) - dx_real)*rC5 + ((c0h + c0l) - c0);
(fh+fl) -> (v_ch6+v_cl6);
(fh_1 + fl_1) - (dxh + dxl)*(fh + fl) ->(high_low - (dxh*fl)) + (low_high - (dxl * fh)) + (t1 - (high_low + low_high)) + (fl_1 - (t1 + high_high_rest)) - (fl*dxl);
(fh_2 + fl_2) - (fh_1 + fl_1)*(th + tl) ->(high_low1 - (fh_1*tl)) + (low_high1 - (fl_1 * th)) + (t2 - (high_low1 + low_high1)) + (fl_2 - (t2 + high_high_rest2)) - (tl*fl_1);
(yh + sl) - (th + fh_2) -> sl - ((th + fh_2) - yh);
(yh + yl) - ((th+tl)+(fh_2+fl_2)) -> ((yh + sl) - (th + fh_2)) + (yl - ((tl + fl_2) + sl));
y0 - y0_real -> (v_ch6 + v_cl6) - rC6;
(dxh + dxl) - dx_real -> dxl - (-(dxh - dx_real));
y1 - y1_real -> ((fh_1 + fl_1) - (dxh + dxl)*(fh + fl)) + ((dxh + dxl) - dx_real)*(fh + fl) + dx_real*((fh+fl) - y0_real);
(yh + yl) - y_real -> ((yh + yl) - ((th + tl) + (fh_2 + fl_2))) + ((fh_2 + fl_2) - ((fh_1 + fl_1)*(th + tl))) + ((fh_1 + fl_1)- y1_real)*(th + tl);
