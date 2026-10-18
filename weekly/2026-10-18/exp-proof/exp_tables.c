#include <stdio.h>
#include <math.h>
#include <mpfr.h>
#include "exp.c"
int main(void){
 int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
 mpfr_t z,lo,hi,sum,a,b,maxerr,eb,tb,tmp;mpfr_inits2(256,z,lo,hi,sum,a,b,maxerr,eb,tb,tmp,(mpfr_ptr)0);
 mpfr_set_str(eb,"-102.491",10,MPFR_RNDD);mpfr_exp2(eb,eb,MPFR_RNDD);
 mpfr_set_str(tb,"-50.776",10,MPFR_RNDD);mpfr_exp2(tb,tb,MPFR_RNDD);mpfr_set_zero(maxerr,0);
 unsigned failures=0;int mi=0,mj=0,mm=0;
 for(int mode=0;mode<4;mode++)for(int i=0;i<64;i++)for(int j=0;j<64;j++){
  fesetround(modes[mode]);double tl,th=muldd(t0[i][1],t0[i][0],t1[j][1],t1[j][0],&tl);
  mpfr_set_ui(z,64*i+j,MPFR_RNDN);mpfr_div_2ui(z,z,12,MPFR_RNDN);
  mpfr_exp2(lo,z,MPFR_RNDD);mpfr_exp2(hi,z,MPFR_RNDU);
  mpfr_set_d(sum,th,MPFR_RNDN);mpfr_add_d(sum,sum,tl,MPFR_RNDN);
  mpfr_sub(a,sum,lo,MPFR_RNDU);mpfr_sub(b,hi,sum,MPFR_RNDU);mpfr_max(tmp,a,b,MPFR_RNDU);
  if(mpfr_cmp(tmp,maxerr)>0){mpfr_set(maxerr,tmp,MPFR_RNDU);mi=i;mj=j;mm=mode;}
  mpfr_set_d(a,fabs(tl),MPFR_RNDN);
  if(mpfr_cmp(tmp,eb)>=0||mpfr_cmp(a,tb)>=0||th<1.||th>=1.9997)failures++;
 }
 fesetround(FE_TONEAREST);mpfr_printf("cells=16384 failures=%u max_error_upper=%.80Rg at i=%d j=%d mode=%d\n",failures,maxerr,mi,mj,mm);
 double edges[]={-0x1.6232bdd7abcd2p+9,nextafter(-0x1.6232bdd7abcd2p+9,-INFINITY),nextafter(-0x1.74910d52d3052p+9,INFINITY)};
 for(int j=0;j<3;j++){
  int exponent=j<2?1022:1075;
  mpfr_const_log2(lo,MPFR_RNDD);mpfr_mul_ui(lo,lo,exponent,MPFR_RNDD);mpfr_add_d(lo,lo,edges[j],MPFR_RNDD);
  mpfr_const_log2(hi,MPFR_RNDU);mpfr_mul_ui(hi,hi,exponent,MPFR_RNDU);mpfr_add_d(hi,hi,edges[j],MPFR_RNDU);
  mpfr_printf("endpoint=%a r_lower=%.80Rg r_upper=%.80Rg\n",edges[j],lo,hi);
  if(j==1 && mpfr_cmp_d(hi,-0x1p-44)>=0)failures++;
  if(j==2 && mpfr_cmp_d(lo,0x1p-49)<=0)failures++;
  for(int mode=0;mode<4;mode++){
   fesetround(modes[mode]);volatile double x=edges[j];double t=roundeven_finite(x*0x1.71547652b82fep+12);i64 jt=t;
   double value=as_exp_accurate(x);printf("edge=%a mode=%d t=%.0f ie=%lld accurate=%a\n",x,mode,t,(long long)(jt>>12),value);
  }
 }
 printf("ENDPOINT_SUMMARY failures=%u\n",failures);
 mpfr_clears(z,lo,hi,sum,a,b,maxerr,eb,tb,tmp,(mpfr_ptr)0);return failures?1:0;
}
