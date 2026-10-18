#include <stdio.h>
#include <mpfr.h>
#include "exp.c"
int main(void){
 mpfr_t z,w;mpfr_init2(z,256);mpfr_init2(w,256);
 for(int m=0;m<2;m++){
  volatile double a=1.,b=m?-0x1p-154:0x1p-154;fesetround(m?FE_DOWNWARD:FE_UPWARD);
  double low,high=fasttwosum(a,b,&low);
  mpfr_set_prec(z,256);mpfr_set_d(z,a,MPFR_RNDN);mpfr_add_d(z,z,b,MPFR_RNDN);
  mpfr_set_d(w,high,MPFR_RNDN);mpfr_sub(z,w,z,MPFR_RNDN);
  mpfr_prec_round(z,53,m?MPFR_RNDD:MPFR_RNDU);mpfr_neg(z,z,MPFR_RNDN);double model=mpfr_get_d(z,MPFR_RNDN);
  printf("mode=%s a=%a b=%a C_low=%a old_model_low=%a\n",m?"rndd":"rndu",a,b,low,model);
  if(low!=(m?0x1.fffffffffffffp-54:-0x1.fffffffffffffp-53)||model!=(m?0x1p-53:-0x1p-52))return 1;
 }
 mpfr_clear(z);mpfr_clear(w);return 0;
}
