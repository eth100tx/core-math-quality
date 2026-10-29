/* Independent finite-table check. Compile with -frounding-math -ffp-contract=off.
   The pinned upstream source is included from a disposable build directory. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <fenv.h>
#include <mpfr.h>
#include "cos.c"
static double md(double a,double b,double c,double d,double *l,int variant) {
 double h=a*c, e=fma(a,c,-h), l2=a*d, l3=b*c;
 if(variant==0)*l=(l2+l3)+e;
 else if(variant==1)*l=fma(b,c,l2)+e;
 else *l=fma(a,d,l3)+e;
 return h;
}
int main(void) {
 int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
 mpfr_t pi,z,cr,sr,a,b,err,mc,ms,boundc,bounds,pad;
 mpfr_inits2(256,pi,z,cr,sr,a,b,err,mc,ms,boundc,bounds,pad,(mpfr_ptr)0);
 mpfr_const_pi(pi,MPFR_RNDN); mpfr_set_zero(mc,1);mpfr_set_zero(ms,1);
 mpfr_set_ui_2exp(pad,1,-240,MPFR_RNDN);
 mpfr_set_str(a,"-103.342",10,MPFR_RNDD);mpfr_exp2(boundc,a,MPFR_RNDD);
 mpfr_set_str(a,"-51.569",10,MPFR_RNDD);mpfr_exp2(bounds,a,MPFR_RNDD);
 unsigned long combos=0,shcombos=0;int violations=0;double maxCh=0,maxCl=0,maxSh=0;
 for(int i=0;i<128;i++)for(int j=0;j<128;j++) {
  mpfr_mul_ui(z,pi,128*i+j,MPFR_RNDN);mpfr_div_2ui(z,z,14,MPFR_RNDN);
  mpfr_sin_cos(sr,cr,z,MPFR_RNDN);
  /* pi, angle and sin/cos round-to-nearest errors together < 2^-240.
     |angle| < pi and sin/cos are 1-Lipschitz. All subsequent errors rounded up. */
  for(int m=0;m<4;m++) {
   if(fesetround(modes[m]))return 2;
   for(int u=0;u<3;u++)for(int v=0;v<3;v++) {
    double l1,l2,cl;
    double h1=md(U1[i][2],U1[i][3],U2[j][2],U2[j][3],&l1,u);
    double h2=md(U2[j][0],U2[j][1],U1[i][0],U1[i][1],&l2,v);
    if(h1!=0 && fabs(h1)<fabs(h2))violations++;
    double ch=fastsum(h1,l1,-h2,-l2,&cl);
    mpfr_set_d(a,ch,MPFR_RNDN);mpfr_set_d(b,cl,MPFR_RNDN);mpfr_add(a,a,b,MPFR_RNDN);
    mpfr_sub(a,a,cr,MPFR_RNDN);mpfr_abs(err,a,MPFR_RNDU);mpfr_add(err,err,pad,MPFR_RNDU);
    if(mpfr_greater_p(err,mc)){mpfr_set(mc,err,MPFR_RNDN);printf("Cmax %d %d mode%d variant%d%d %.17g\n",i,j,m,u,v,mpfr_get_d(mc,MPFR_RNDU));}
    if(fabs(ch)>maxCh)maxCh=fabs(ch);if(fabs(cl)>maxCl)maxCl=fabs(cl);combos++;
   }
   double t1=U1[i][0],t2=U2[j][2],t3=U1[i][2],t4=U2[j][0];
   double sh[3]={t1*t2+t3*t4,fma(t1,t2,t3*t4),fma(t3,t4,t1*t2)};
   for(int v=0;v<3;v++) {
    mpfr_set_d(a,sh[v],MPFR_RNDN);mpfr_sub(a,a,sr,MPFR_RNDN);mpfr_abs(err,a,MPFR_RNDU);mpfr_add(err,err,pad,MPFR_RNDU);
    if(mpfr_greater_p(err,ms)){mpfr_set(ms,err,MPFR_RNDN);printf("Smax %d %d mode%d variant%d %.17g\n",i,j,m,v,mpfr_get_d(ms,MPFR_RNDU));}
    if(fabs(sh[v])>maxSh)maxSh=fabs(sh[v]);shcombos++;
   }
  }
 }
 fesetround(FE_TONEAREST);
 int ok=mpfr_less_p(mc,boundc)&&mpfr_less_p(ms,bounds)&&!violations&&maxCh<=1&&maxSh<=1&&maxCl<mpfr_get_d(bounds,MPFR_RNDD);
 printf("SUMMARY C=%lu S=%lu fasttwosum_violations=%d maxCh=%a maxCl=%a maxSh=%a PASS=%d\n",combos,shcombos,violations,maxCh,maxCl,maxSh,ok);
 mpfr_printf("C_error_upper=%Ra S_error_upper=%Ra\n",mc,ms);
 return !ok;
}
