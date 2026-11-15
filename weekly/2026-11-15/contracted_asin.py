"""Enclose the pinned GCC 13.3 v3 graph with the previously published interval primitives."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct

SOURCE = "d9cc7c44922ac3caef5a25d0eb3d9e1e2aa94a0fea761737416d68d6f3a2a8e9"
STRICT = "985b41f0dda6404a102401a9e4c36b744738a1777ff304f81298504848712a1e"


def evaluate(source, library, scale_factor=1):
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE:
        raise ValueError("source identity")
    if hashlib.sha256(library.read_bytes()).hexdigest() != STRICT:
        raise ValueError("interval library identity")
    spec = importlib.util.spec_from_file_location("asin_intervals", library)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    I, fma, twosum = lib.I, lib.fma, lib.twosum
    text = source.read_text()
    cc, s, c, ct = (lib.table(text, name) for name in
                    ("double cc[][8]", "double s[33][2]", "double c[][2]", "double ct[]"))
    lib.require(tuple(map(len, (cc, s, c, ct))) == (33, 33, 5, 3), "table dimensions")
    offsets = lib.table(text, "double off[][2]")
    scale = float.fromhex(re.search(r"__builtin_fabs\(phi\) \* (0x[\da-f.p+-]+)", text)[1])
    word = int(re.search(r"ax<(0x[0-9a-f]+)ull", text)[1], 16)
    cuts = [F(struct.unpack(">d", (word // 2).to_bytes(8, "big"))[0])]
    lib.require(word % 2 == 0 and 0 < cuts[0] < F(1, 256), "tiny cutoff")
    cuts += [F(i, 256) for i in range(1, 256)] + [1-F(1, 2**53)]
    pih, pil, pis = [I(float.fromhex(re.search(
        rf"static const double {name} = ([^;]+);", text)[1]))
        for name in ("pih", "pil", "pis")]
    for jt in range(-32, 33):
        for const in (pih, pil):
            exact = const.lo*jt
            lib.require(F(float(exact)) == exact, "angle product exact")

    def product_parts(x, xl, y, yl):
        h = x*y
        l = fma(x, yl, xl*y) + lib.sym(lib.ulp(h))
        return h, l

    def caller(ax, sign, large):
        x = sign*ax
        if large:
            a = fma(-ax, 2, 2)
            jd_arg = a*32
            mag = lib.root(a)
            z = -sign*mag
            zl = lib.root_residual(z)*((-0.5/a)*z)
            off, tail = offsets[int(sign < 0)]
        else:
            jd_arg = (x*x)*128
            z, zl, off, tail = x, I(0), I(0), I(0)
        for index in lib.ints(jd_arg):
            lib.require(0 <= index <= 32, "caller index")
            k = -F(index,128)
            t = fma(a, 0.25, k) if large else fma(x, x, k)
            eps_source = mag if large else x
            eps = (eps_source*t).absolute()*float.fromhex("0x1.99p-52" if large else "0x1.77p-52")
            coeff = cc[index]
            t2 = t*t
            p = [fma(coeff[i+1], t, coeff[i]) for i in (2,4,6)]
            poly = fma(fma(p[2], t2, p[1]), t2, p[0])
            h, l = product_parts(z, zl, coeff[0], fma(poly, t, coeff[1]))
            h, l = lib.fastsum(off, tail, h, l)
            yield h + (l-eps)

    def refine(ax, sign, j, ch, cl):
        sl, sh = s[j]
        cltab, chtab = s[32-j]
        dsh, dch = ax-sh, ch-chtab
        # cosine_parts rounds the product hull outwards, so cl also
        # contains the exact multiplier product used in GCC's fused subtract.
        dcl = cl-cltab
        sc, dsc = lib.magic_product(sh,dch)
        cs, dcs = lib.magic_product(chtab,dsh)
        dv = (fma(-chtab,sl,cltab*dsh)-fma(sh,dcl,sl*dch))-(dsc-dcs)
        v, dv = twosum(cs-sc,dv)
        v2 = v*v
        dv2 = fma(v*dv, 2, lib.sym(lib.ulp(v2)))
        v, dv = sign*v, sign*dv
        u = fma(fma(v2,ct[2],ct[1]),v2,ct[0])
        h = fma(u,v2,c[4][0])
        z = h-c[4][0]
        # Exact product minus z is minus the sum of the two preceding
        # rounding errors; final FMS rounds that residual once.
        bound = lib.outward(lib.ulp(h)+lib.ulp(z), True)
        l = c[4][1] + fma(u,v2,-z).intersect(lib.sym(bound))
        for row in (3,2,1,0):
            h,l = product_parts(v2,dv2,h,l)
            h,l = lib.fastsum(c[row][0],c[row][1],h,l)
        fh,fl = product_parts(v,dv,h,l)
        jt = sign*j
        # Exact high and middle angle products make these two fused
        # FastTwoSum steps equivalent to their ordinary rounded sums.
        mid, residual = twosum(fh, pil*jt)
        tail = residual + fma(jt,pis,fl)
        high, low = twosum(pih*jt,mid)
        low, _ = twosum(low,tail)
        return high+low

    indices, cells = set(), 0
    min_ph, max_ph, max_arg = F(2), F(0), F(0)
    for lo,hi in zip(cuts,cuts[1:]):
        ax = I(lo,hi)
        ch,cl = lib.cosine_parts(ax)
        for sign in (-1,1):
            for phi in caller(ax,sign,lo>=F(1,2)):
                arg = phi.absolute()*(scale*scale_factor)
                max_arg = max(max_arg,arg.hi)
                for j in lib.ints(arg):
                    lib.require(0<=j<=32, "refinement index out of range")
                    ph = refine(ax,sign,j,ch,cl).absolute()
                    lib.require(ph.lo >= F(1,2**970) and ph.hi <= 2,"predicate exponent")
                    min_ph,max_ph = min(min_ph,ph.lo),max(max_ph,ph.hi)
                    indices.add(j)
                    cells += 1
    return {"source_sha256":SOURCE, "intervals":len(cuts)-1, "branch_boxes":cells,
            "indices":sorted(indices), "index_argument_upper":float(max_arg).hex(),
            "abs_ph_lower":float(min_ph).hex(),"abs_ph_upper":float(max_ph).hex(),
            "biased_exponent_lower":math.frexp(float(min_ph))[1]-1+1023}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("interval_library",type=Path)
    parser.add_argument("--negative-control",action="store_true")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.source,args.interval_library,2 if args.negative_control else 1),indent=2))
