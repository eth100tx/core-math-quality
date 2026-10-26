#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <fenv.h>
#include <errno.h>
#include <mpfr.h>
double cr_rsqrt(double);
int main(void) {
  int rounds[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
  mpfr_rnd_t mr[]={MPFR_RNDN,MPFR_RNDZ,MPFR_RNDU,MPFR_RNDD};
  const char *names[]={"rndn","rndz","rndu","rndd"};
  double xs[]={0x1.fffffffffffffp+1021,0x1p+1022,0x1.0000000000001p+1022,0x1.8p+1022,0x1.fffffffffffffp+1022,0x1p+1023,0x1.0000000000001p+1023,0x1.fffffffffffffp+1023};
  mpfr_t a,b;mpfr_init2(a,53);mpfr_init2(b,53);
  unsigned fail=0;
  for(unsigned mode=0;mode<4;mode++)for(unsigned j=0;j<sizeof(xs)/sizeof(xs[0]);j++){
    mpfr_set_d(a,xs[j],MPFR_RNDN);int inex=mpfr_rec_sqrt(b,a,mr[mode]);double expected=mpfr_get_d(b,MPFR_RNDN);
    fesetround(rounds[mode]);feclearexcept(FE_ALL_EXCEPT);errno=0;
    volatile double actual=cr_rsqrt(xs[j]);int flags=fetestexcept(FE_ALL_EXCEPT);int err=errno;
    int bad=(actual!=expected)||(flags&FE_UNDERFLOW)||(flags&FE_OVERFLOW)||(flags&FE_INVALID)||(flags&FE_DIVBYZERO)||((!!(flags&FE_INEXACT))!=(!!inex))||err;
    fail+=bad;
    printf("mode=%s x=%a actual=%a expected=%a underflow=%d inexact=%d expected_inexact=%d errno=%d bad=%d\n",names[mode],xs[j],actual,expected,!!(flags&FE_UNDERFLOW),!!(flags&FE_INEXACT),!!inex,err,bad);
  }
  mpfr_clear(a);mpfr_clear(b);printf("SUMMARY cases=32 failures=%u\n",fail);return fail?1:0;
}
