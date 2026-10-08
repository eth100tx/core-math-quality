#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <mpfr.h>
#include "source/src/binary64/sin/sin.c"
static void setu(mpfr_t v,u128 u){mpfr_set_ui(v,(uint64_t)(u>>64),MPFR_RNDN);mpfr_mul_2ui(v,v,64,MPFR_RNDN);mpfr_add_ui(v,v,(uint64_t)u,MPFR_RNDN);mpfr_div_2ui(v,v,128,MPFR_RNDN);}
int main(void){
 mpfr_t pl,pu,al,au,sl,su,cl,cu,delta,v,lo,hi,err;mpfr_inits2(256,pl,pu,al,au,sl,su,cl,cu,delta,v,lo,hi,err,(mpfr_ptr)0);mpfr_const_pi(pl,MPFR_RNDD);mpfr_const_pi(pu,MPFR_RNDU);
 int modes[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};int condfail=0;double maxs[4]={0},maxc[4]={0},maxl[4]={0},maxsh[4]={0},maxch[4]={0};
 for(unsigned j=0;j<16384;j++){
  mpfr_mul_ui(al,pl,j,MPFR_RNDD);mpfr_div_2ui(al,al,14,MPFR_RNDD);mpfr_mul_ui(au,pu,j,MPFR_RNDU);mpfr_div_2ui(au,au,14,MPFR_RNDU);mpfr_sub(delta,au,al,MPFR_RNDU);
  mpfr_sin(sl,al,MPFR_RNDD);mpfr_sin(su,al,MPFR_RNDU);mpfr_sub(sl,sl,delta,MPFR_RNDD);mpfr_add(su,su,delta,MPFR_RNDU);mpfr_cos(cl,al,MPFR_RNDD);mpfr_cos(cu,al,MPFR_RNDU);mpfr_sub(cl,cl,delta,MPFR_RNDD);mpfr_add(cu,cu,delta,MPFR_RNDU);
  int a=j>>7,b=j&127;
  for(int m=0;m<4;m++){
   fesetround(modes[m]);double l1,l2,s1=muldd(U1[a][0],U1[a][1],U2[b][2],U2[b][3],&l1),s2=muldd(U2[b][0],U2[b][1],U1[a][2],U1[a][3],&l2),l,s=fastsum(s1,l1,s2,l2,&l),c=U1[a][2]*U2[b][2]-U1[a][0]*U2[b][0];
   if(s1!=0 && fabs(s1)<fabs(s2))condfail++;
   mpfr_set_d(v,s,MPFR_RNDN);mpfr_add_d(v,v,l,MPFR_RNDN);mpfr_sub(lo,v,su,MPFR_RNDD);mpfr_sub(hi,v,sl,MPFR_RNDU);mpfr_abs(lo,lo,MPFR_RNDU);mpfr_abs(hi,hi,MPFR_RNDU);double se=fmax(mpfr_get_d(lo,MPFR_RNDU),mpfr_get_d(hi,MPFR_RNDU));
   mpfr_set_d(v,c,MPFR_RNDN);mpfr_sub(lo,v,cu,MPFR_RNDD);mpfr_sub(hi,v,cl,MPFR_RNDU);mpfr_abs(lo,lo,MPFR_RNDU);mpfr_abs(hi,hi,MPFR_RNDU);double ce=fmax(mpfr_get_d(lo,MPFR_RNDU),mpfr_get_d(hi,MPFR_RNDU));
   maxs[m]=fmax(maxs[m],se);maxc[m]=fmax(maxc[m],ce);maxl[m]=fmax(maxl[m],fabs(l));maxsh[m]=fmax(maxsh[m],fabs(s));maxch[m]=fmax(maxch[m],fabs(c));
  }
 }
 fesetround(FE_TONEAREST);for(int m=0;m<4;m++)printf("fast_table mode=%d pairs=16384 sin_error_upper=%a cos_error_upper=%a low_abs_max=%a high_abs_max=%a cos_abs_max=%a\n",m,maxs[m],maxc[m],maxl[m],maxsh[m],maxch[m]);printf("simple_magnitude_condition_failures=%d (not necessarily failure of the broader FastTwoSum theorem)\n",condfail);
 double maxas=0,maxac=0;u128 largestS=0,largestC=0;
 for(int a=0;a<64;a++)for(int b=0;b<64;b++){
  u128 s1=a<=32?S1u[a]:S1u[64-a],c1=a<=32?S1u[32-a]:S1u[a-32];u128 s=mhUU(s1,C2u[b]),t=mhUU(c1,S2u[b]);assert(a<32 ? s<=~(u128)0-t : s>=t);s=a<32?s+t:s-t;u128 c=mhUU(c1,C2u[b]);t=mhUU(s1,S2u[b]);assert(a<32 ? c>=t : c<=~(u128)0-t);c=a<32?c-t:c+t;if(s>largestS)largestS=s;if(c>largestC)largestC=c;
  unsigned j=64*a+b;mpfr_mul_ui(al,pl,j,MPFR_RNDD);mpfr_div_2ui(al,al,12,MPFR_RNDD);mpfr_mul_ui(au,pu,j,MPFR_RNDU);mpfr_div_2ui(au,au,12,MPFR_RNDU);mpfr_sub(delta,au,al,MPFR_RNDU);
  mpfr_sin(sl,al,MPFR_RNDD);mpfr_sin(su,al,MPFR_RNDU);mpfr_sub(sl,sl,delta,MPFR_RNDD);mpfr_add(su,su,delta,MPFR_RNDU);mpfr_cos(cl,al,MPFR_RNDD);mpfr_cos(cu,al,MPFR_RNDU);mpfr_sub(cl,cl,delta,MPFR_RNDD);mpfr_add(cu,cu,delta,MPFR_RNDU);
  setu(v,s);mpfr_sub(lo,v,su,MPFR_RNDD);mpfr_sub(hi,v,sl,MPFR_RNDU);mpfr_abs(lo,lo,MPFR_RNDU);mpfr_abs(hi,hi,MPFR_RNDU);maxas=fmax(maxas,fmax(mpfr_get_d(lo,MPFR_RNDU),mpfr_get_d(hi,MPFR_RNDU)));
  setu(v,c);if(a>=32)mpfr_neg(v,v,MPFR_RNDN);mpfr_sub(lo,v,cu,MPFR_RNDD);mpfr_sub(hi,v,cl,MPFR_RNDU);mpfr_abs(lo,lo,MPFR_RNDU);mpfr_abs(hi,hi,MPFR_RNDU);maxac=fmax(maxac,fmax(mpfr_get_d(lo,MPFR_RNDU),mpfr_get_d(hi,MPFR_RNDU)));
 }
 printf("accurate_table pairs=4096 sin_error_upper=%a cos_error_upper=%a S_below_2p128=%llu C_below_2p128=%llu\n",maxas,maxac,(unsigned long long)(-largestS),(unsigned long long)(-largestC));
 assert(maxas<=ldexp(20298.,-140) && maxac<=ldexp(20298.,-140));
 assert(largestS<=~(u128)0-2 && largestC<=~(u128)0-2);
 return 0;
}

