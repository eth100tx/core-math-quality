/* Values on a compact dyadic grid and the neighbors of five branch inputs. */
#include <fenv.h>
#include <inttypes.h>
#include <math.h>
#include <mpfr.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern double cr_asin(double);
static uint64_t bits(double x) {
    uint64_t u;
    memcpy(&u, &x, sizeof u);
    return u;
}

int main(int argc, char **argv) {
    const int hw[] = {FE_TONEAREST, FE_TOWARDZERO, FE_UPWARD, FE_DOWNWARD};
    const mpfr_rnd_t mp[] = {MPFR_RNDN, MPFR_RNDZ, MPFR_RNDU, MPFR_RNDD};
    const double boundaries[] = {0x1.7137449123ef6p-26, 0.5, 1.0,
                                 0x1.76f45p-2, 0x1.d46p-1};
    double xs[600];
    size_t n = 0;
    for (int k = -256; k <= 256; ++k) xs[n++] = k / 256.;
    xs[n++] = -0.0;
    for (size_t i = 0; i < sizeof boundaries / sizeof boundaries[0]; ++i)
        for (int side = -1; side <= 1; ++side) {
            double x = boundaries[i];
            if (side) x = nextafter(x, side < 0 ? 0. : INFINITY);
            if (x <= 1.) { xs[n++] = x; xs[n++] = -x; }
        }
    mpfr_t x, y;
    mpfr_init2(x,53); mpfr_init2(y,53);
    int inject = argc == 2 && !strcmp(argv[1],"--negative-control");
    for (int m = 0; m < 4; ++m) {
        if (fesetround(hw[m])) return 2;
        for (size_t i = 0; i < n; ++i) {
            mpfr_set_d(x, xs[i], MPFR_RNDN);
            mpfr_asin(y,x,mp[m]);
            uint64_t expected = bits(mpfr_get_d(y,mp[m]));
            uint64_t actual = bits(cr_asin(xs[i]));
            if (inject && m == 0 && i == 0) actual ^= 1;
            if (actual != expected) {
                fprintf(stderr, "value mismatch x=%a mode=%d expected=%016" PRIx64 " actual=%016" PRIx64 "\n",
                        xs[i],m,expected,actual);
                return 1;
            }
        }
        printf("mode=%d calls=%zu PASS\n",m,n);
    }
    mpfr_clear(x); mpfr_clear(y);
    return 0;
}
