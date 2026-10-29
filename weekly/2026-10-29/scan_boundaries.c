/* Membership/classification of supplied corpus, not completeness regeneration. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpfr.h>
#ifndef PRECISION
#define PRECISION 256
#endif
int main(int argc,char**argv){
 FILE*f=fopen(argv[1],"r");if(!f)return 2;
 mpfr_t x,y,z,d,mn;mpfr_inits2(PRECISION,x,y,d,mn,(mpfr_ptr)0);mpfr_init2(z,54);mpfr_set_ui(mn,1,MPFR_RNDN);
 char line[256];long rows=0,small=0,near=0,nearone=0,other=0;double witness=0;
 while(fgets(line,sizeof(line),f)){
  if(line[0]=='#')continue;char*end;double v=strtod(line,&end);if(end==line||!isfinite(v))continue;rows++;
  mpfr_set_d(x,v,MPFR_RNDN);mpfr_cos(y,x,MPFR_RNDN);mpfr_abs(d,y,MPFR_RNDN);
  if(mpfr_cmp_d(d,0x1p-27)>=0){if(mpfr_cmp_d(d,0x1.fffffffffffffp-1)>0)nearone++;else other++;continue;}small++;
  mpfr_set(z,y,MPFR_RNDN);mpfr_sub(d,y,z,MPFR_RNDN);mpfr_abs(d,d,MPFR_RNDN);
  if(mpfr_cmp_d(d,0x1p-106)<0)near++;
  if(mpfr_less_p(d,mn)){mpfr_set(mn,d,MPFR_RNDN);witness=v;}
 }
 mpfr_log2(d,mn,MPFR_RNDN);printf("rows=%ld small_cos=%ld small_cos_near_boundary=%ld near_unity=%ld other=%ld min_witness=%a precision=%d\n",rows,small,near,nearone,other,witness,PRECISION);mpfr_printf("minimum_distance=%Ra log2=%.20Rf\n",mn,d);
 double vs[]={0x1.6ac5b262ca1ffp+849,0x1.6ac5b262ca1ffp+850};
 for(int i=0;i<2;i++){mpfr_set_d(x,vs[i],MPFR_RNDN);mpfr_cos(y,x,MPFR_RNDN);mpfr_set(z,y,MPFR_RNDN);mpfr_sub(d,y,z,MPFR_RNDN);mpfr_abs(d,d,MPFR_RNDN);mpfr_log2(mn,d,MPFR_RNDN);printf("example=%a ",vs[i]);mpfr_printf("cos=%Ra distance=%Ra log2=%.20Rf\n",y,d,mn);}
 return 0;
}
