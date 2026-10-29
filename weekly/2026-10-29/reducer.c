/* Bounded MPFR check of newly stated small-input reducer domain. */
#include <stdio.h>
#include <mpfr.h>
#include "cos.c"
int main(void){
 mpfr_t pi,x,truth,got,err,bound,t;mpfr_inits2(512,pi,x,truth,got,err,bound,t,(mpfr_ptr)0);
 mpfr_const_pi(pi,MPFR_RNDN);mpfr_mul_2ui(pi,pi,1,MPFR_RNDN);
 mpfr_set_ui_2exp(bound,1,-128,MPFR_RNDN);mpfr_set_ui_2exp(t,1,-139,MPFR_RNDN);mpfr_add(bound,bound,t,MPFR_RNDN);
 uint64_t rng=1234567;int count=0;
 for(int e=996;e<=1006;e++)for(int n=0;n<1026;n++){
  rng=rng*6364136223846793005ULL+1;
  uint64_t m=n==0?0:n==1?0xfffffffffffffULL:rng&0xfffffffffffffULL;
  b64u64_u v={.u=((uint64_t)e<<52)|m};u128 r;int neg;uint64_t k=reduce_large_acc(&r,&neg,v.f);
  mpfr_set_d(x,v.f,MPFR_RNDN);mpfr_div(truth,x,pi,MPFR_RNDN);
  mpfr_set_ui(got,(uint64_t)(r>>64),MPFR_RNDN);mpfr_mul_2ui(got,got,64,MPFR_RNDN);mpfr_add_ui(got,got,(uint64_t)r,MPFR_RNDN);mpfr_div_2ui(got,got,128,MPFR_RNDN);
  mpfr_sub(err,truth,got,MPFR_RNDN);
  if(k||neg||mpfr_sgn(err)<0||mpfr_cmp(err,bound)>=0){printf("FAIL reducer x=%a k=%lu neg=%d\n",v.f,k,neg);return 1;}count++;
 }
 printf("PASS small-domain reducer samples=%d exponents=11; sampled, not exhaustive mantissas\n",count);return 0;
}
