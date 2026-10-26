/* Restricted exact-bit qualification adapter, not a general libm tester. */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fenv.h>
#include <errno.h>
#include <float.h>
#include <unistd.h>
#include <signal.h>
#ifdef ORACLE
#include <mpfr.h>
#endif
#pragma STDC FENV_ACCESS ON
#ifndef FAULT
#define FAULT 0
#endif
double cr_hypot(double, double);
static int decode(const char *s, uint64_t *u) {
  if (strlen(s)!=16) return 0;
  *u=0;
  for(int i=0;i<16;i++) {
    int c=s[i],v=(c>='0'&&c<='9')?c-'0':(c>='a'&&c<='f')?c-'a'+10:-1;
    if(v<0) return 0;
    *u=(*u<<4)|(unsigned)v;
  }
  return (*u>>52)==0x3ff;
}
int main(int argc, char **argv) {
  const char *names[]={"rndn","rndz","rndu","rndd"};
  const int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
  uint64_t ux,uy,uz; double x,y,z;
  if(argc!=4 || sizeof(double)!=8 || DBL_MANT_DIG!=53 || FLT_RADIX!=2 || FLT_EVAL_METHOD!=0) return 2;
  if(!decode(argv[1],&ux)||!decode(argv[2],&uy)) return 2;
  int index=-1;
  for(int i=0;i<4;i++) if(!strcmp(argv[3],names[i])) index=i;
  if(index<0) return 2;
  if(FAULT==6) { signal(SIGTERM,SIG_IGN); for(;;) pause(); }
  if(FAULT==3) ux^=1;
  memcpy(&x,&ux,8); memcpy(&y,&uy,8);
  if(fesetround(modes[FAULT==2?0:index])) return 3;
  int observed=-1;
  for(int i=0;i<4;i++) if(fegetround()==modes[i]) observed=i;
  if(feclearexcept(FE_ALL_EXCEPT)) return 3;
  errno=0;
#ifdef ORACLE
  mpfr_t a,b,c; mpfr_inits2(53,a,b,c,(mpfr_ptr)0);
  mpfr_set_d(a,x,MPFR_RNDN); mpfr_set_d(b,y,MPFR_RNDN);
  const mpfr_rnd_t rounds[]={MPFR_RNDN,MPFR_RNDZ,MPFR_RNDU,MPFR_RNDD};
  int inex=mpfr_hypot(c,a,b,rounds[index]);
  z=mpfr_get_d(c,MPFR_RNDN);
  mpfr_clears(a,b,c,(mpfr_ptr)0);
  mpfr_t aa,bb,ss,low,high; mpfr_inits2(256,aa,bb,ss,low,high,(mpfr_ptr)0);
  mpfr_set_d(aa,x,MPFR_RNDN);mpfr_set_d(bb,y,MPFR_RNDN);
  mpfr_sqr(aa,aa,MPFR_RNDN);mpfr_sqr(bb,bb,MPFR_RNDN);mpfr_add(ss,aa,bb,MPFR_RNDN);
  mpfr_sqrt(low,ss,MPFR_RNDD);mpfr_sqrt(high,ss,MPFR_RNDU);
  double dl=mpfr_get_d(low,MPFR_RNDD),du=mpfr_get_d(high,MPFR_RNDU);
  uint64_t bl,bu;memcpy(&bl,&dl,8);memcpy(&bu,&du,8);
  mpfr_clears(aa,bb,ss,low,high,(mpfr_ptr)0);
  int error=0,flags=inex?FE_INEXACT:0;
#else
  double (*volatile fn)(double,double)=cr_hypot;
  volatile double result=fn(x,y);
  int error=errno,flags=fetestexcept(FE_ALL_EXCEPT);
  z=result;
#endif
  int post=fegetround();
  memcpy(&uz,&z,8);
  if(FAULT==1) uz^=1;
  if(FAULT==4) flags^=FE_INEXACT;
  if(FAULT==5) error=EDOM;
  printf("{\"x_bits\":\"%016" PRIx64 "\",\"y_bits\":\"%016" PRIx64 "\",\"value\":\"%016" PRIx64 "\",\"mode_index\":%d,\"mode_preserved\":%d,\"flags\":{\"inexact\":%d,\"invalid\":%d,\"divbyzero\":%d,\"underflow\":%d,\"overflow\":%d},\"errno\":%d,\"raw_flags\":%d",
         ux,uy,uz,observed,post==modes[index],!!(flags&FE_INEXACT),!!(flags&FE_INVALID),!!(flags&FE_DIVBYZERO),!!(flags&FE_UNDERFLOW),!!(flags&FE_OVERFLOW),error,flags);
#ifdef ORACLE
  printf(",\"bound_lo\":\"%016" PRIx64 "\",\"bound_hi\":\"%016" PRIx64 "\"",bl,bu);
#endif
  puts("}");
  return 0;
}
