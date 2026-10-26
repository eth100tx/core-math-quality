/* Bounded throughput observation, not exhaustive qualification or a census. */
#include <stdint.h>
#include <stdio.h>
#include <math.h>
#include <fenv.h>
#include <errno.h>
#include <time.h>
#include <mpfr.h>
double cr_hypot(double,double);
typedef union { double d; uint64_t u; } bits;
static uint64_t state=0x763ba99541bdc832ULL;
static uint64_t next(void){state^=state<<13;state^=state>>7;state^=state<<17;return state;}
int main(void){
  const int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
  const mpfr_rnd_t rnd[]={MPFR_RNDN,MPFR_RNDZ,MPFR_RNDU,MPFR_RNDD};
  mpfr_t a,b,y;mpfr_inits2(53,a,b,y,(mpfr_ptr)0);
  unsigned bad=0,flags_bad=0,errno_bad=0;uint64_t checksum=0;
  clock_t begin=clock();
  for(unsigned i=0;i<100000;i++){
    bits x={.u=0x3ff8000000000000ULL|(next()&0x7ffffffffffffULL)};
    bits z={.u=0x3ff8000000000000ULL|(next()&0x7ffffffffffffULL)};
    mpfr_set_d(a,x.d,MPFR_RNDN);mpfr_set_d(b,z.d,MPFR_RNDN);
    for(int m=0;m<4;m++){
      int inexact=mpfr_hypot(y,a,b,rnd[m]);bits ref={.d=mpfr_get_d(y,rnd[m])};
      fesetround(modes[m]);feclearexcept(FE_ALL_EXCEPT);errno=0;
      bits actual={.d=cr_hypot(x.d,z.d)};
      int flags=fetestexcept(FE_ALL_EXCEPT),err=errno;
      bad+=actual.u!=ref.u;flags_bad+=flags!=(inexact?FE_INEXACT:0);errno_bad+=err!=0;
      checksum^=actual.u+(uint64_t)i*0x9e3779b97f4a7c15ULL+(uint64_t)m;
    }
  }
  fesetround(FE_TONEAREST);
  double cpu=(double)(clock()-begin)/CLOCKS_PER_SEC;
  printf("pairs=100000 modes=4 comparisons=400000 value_failures=%u flag_failures=%u errno_failures=%u cpu_seconds=%.9f checksum=%016llx\n",bad,flags_bad,errno_bad,cpu,(unsigned long long)checksum);
  mpfr_clears(a,b,y,(mpfr_ptr)0);return bad||flags_bad||errno_bad;
}
