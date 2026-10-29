#include <stdint.h>
#include <stdio.h>
#include <mpfr.h>
static uint64_t audit_low;
#include "cos-instrumented.c"
int main(void){
 double xs[]={0x1.8000000000009p-23,0x1.8000000000024p-22,0x1.800000000009p-21,0x1.20000000000f3p-20};
 int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};mpfr_rnd_t rms[]={MPFR_RNDN,MPFR_RNDZ,MPFR_RNDU,MPFR_RNDD};
 mpfr_t t;mpfr_init2(t,53);
 for(int i=0;i<4;i++)for(int m=0;m<4;m++){
  fesetround(modes[m]);double y=cos_large_accurate(xs[i]);mpfr_set_d(t,xs[i],MPFR_RNDN);mpfr_cos(t,t,rms[m]);double ref=mpfr_get_d(t,rms[m]);
  int guard=(audit_low+5<=3);printf("x=%a mode=%d low=%016lx guard=%d result=%a reference=%a\n",xs[i],m,audit_low,guard,y,ref);if(!guard||y!=ref)return 1;
 }return 0;}
