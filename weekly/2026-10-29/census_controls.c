/* Finite algorithm controls; not regeneration of the binary64 completeness census. */
#define main supplied_main
#include "check_k0.c"
#undef main
int main(void) {
 mpfr_t a,b,d,t;mpfr_inits2(256,a,b,d,t,(mpfr_ptr)0);
 uint64_t state=0x93481230u;int cases=0;
 for(int c=0;c<1024;c++) {
  state=state*6364136223846793005ULL+1;unsigned av=(state>>32)%65535+1;
  state=state*6364136223846793005ULL+1;unsigned bv=(state>>32)%65536;
  state=state*6364136223846793005ULL+1;unsigned dv=(state>>32)%1024+1;
  uint64_t N=4096,expected=N;
  mpfr_set_ui_2exp(a,av,-16,MPFR_RNDN);mpfr_set_ui_2exp(b,bv,-16,MPFR_RNDN);mpfr_set_ui_2exp(d,dv,-16,MPFR_RNDN);
  for(uint64_t i=0;i<N;i++)if(((bv-i*av)&65535)<dv){expected=i;break;}
  uint64_t got=lefevre(a,b,d,N);
  /* Caller treats any return >=N as no hit, rather than requiring exactly N. */
  if((got<N?got:N)!=expected){printf("FAIL %u %u %u expected%lu got%lu\n",av,bv,dv,expected,got);return 1;}cases++;
 }
 printf("PASS exact-dyadic first-hit controls %d (not pi census completeness)\n",cases);
 double x=0x1.6ac5b262ca1ffp+850;mpfr_set_d(a,x,MPFR_RNDN);mpfr_cos(a,a,MPFR_RNDN);
 mpfr_set_prec(b,54);mpfr_set(b,a,MPFR_RNDN);mpfr_sub(t,a,b,MPFR_RNDN);mpfr_abs(t,t,MPFR_RNDN);
 mpfr_printf("hard_input=%a cosine=%Ra nearest54_boundary=%Ra distance=%Ra\n",x,a,b,t);
 mpfr_log2(t,t,MPFR_RNDN);mpfr_printf("log2_distance=%.20Rf (numerical 256-bit check)\n",t);
 return 0;
}
