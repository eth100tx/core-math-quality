#!/bin/python

import re # regular expressions

file = open("generated.g","w")

header = """# This file has been generated automatically and will be overwritten

@rnd = float<ieee_64,RND>;
@roundeven = int<ne>;

"""
#
# The coefficients are extracted from the copy-pasted code using regular expressions
#
coeff_code_ch = """
    { {0x1p+0, 0}, {0x1p-1, 0x1.712f72ecec2cfp-99}, {0x1.5555555555555p-3, 0x1.5555555554d07p-57},
     {0x1.5555555555555p-5, 0x1.55194d28275dap-59}, {0x1.1111111111111p-7, 0x1.12faa0e1c0f7bp-63},
     {0x1.6c16c16da6973p-10, -0x1.4ba45ab25d2a3p-64}, {0x1.a01a019eb7f31p-13, -0x1.9091d845ecd36p-67} };

"""

def extract_double(source):
    words=re.split(r"[{},;\n ]",source)
    return [s for s in words if re.search(r".*[0-9].*",s) != None]

def write_coefficients_double_double():
    coeffs = extract_double(coeff_code_ch)
    assert (len(coeffs) % 2 == 0)
    for i in range(0,len(coeffs)//2):
        file.write(f"c{i}h={coeffs[2*i]};\nc{i}l={coeffs[2*i+1]};\nc{i}=c{i}h+c{i}l;\n\n")

def horner_rec(n,i,variable,tab):
    if i==n-1:
        return f"{tab}{i}" 
    return f"{tab}{i} + {variable} * ({horner_rec(n,i+1,variable,tab)})"

def horner(n,variable,tab):
    """
    Writes a generic horner scheme
    """
    return horner_rec(n,0,variable,tab)

goal_list = []
hint_list = []
variables= {'x':0, 't':0} # x is already taken

def get_var(s):
    if not (s in variables):
        variables[s]=0
        return s
    variables[s]+=1
    return f"{s}{variables[s]}"

def wdeclare(varname,expression):
    file.write(f"{varname} = {expression};\n")

def fasttwosum(h,l,a,b):
    """
    takes identifiers in input, h and l should not be already defined
    writes h,l <- f2s(a,b), and adds the goal |b|<=|a| to the goal list
    """
    res=[f"# {h},{l} <- fasttwosum({a},{b})"]
    goal_list.append(f"{b} // {a} in [-1,1]")
    # add hint (h+l) - (a+b) -> l - (-(h-(a+b)));
    hint_list.append(f"({h} + {l}) - ({a} + {b}) -> {l} - (({a} + {b}) - {h})")
    return f"{h}=rnd({a} + {b});\n{l}=rnd(({a} + {b}) - {h});"

def fast_sum(h,l,ah,al,bh,bl):
    """
    writes h,l <- fast_sum(ah,al,bh,bl)
    """
    res=[f"# {h},{l} <- fast_sum({ah},{al},{bh},{bl})"]
    sl=get_var("sl")
    res.append(fasttwosum(h,sl,ah,bh))
    res.append(f"{l} rnd = ({al} + {bl}) + {sl};")
    hint_list.append(f"({h} + {l}) - (({ah}+{al})+({bh}+{bl})) -> (({h} + {sl}) - ({ah} + {bh})) + ({l} - (({al} + {bl}) + {sl}))")
    res.append("")
    return '\n'.join(res)

# static inline double
# FastFMA_DW (double ah, double al, double bh, double bl, double ch, double cl,
#             double *l)
# {
#   double dh = __builtin_fma (ah, bh, ch);
#   double t = ch - dh;
#   double e = __builtin_fma (ah, bh, t);
#   double f = e + cl;
#   double g = __builtin_fma (ah, bl, f);
#   *l = __builtin_fma (al, bh, g); // this is dl in the paper
#   return dh;
# }
# we define e as rnd(-(dh-(ah*bh+ch))) instead as rnd(ah*bh+t) but the two formulations
# are equivalent. Indeed, assume dh = ah*bh+ch+eps, then t = -ah*bh-eps, thus
# rnd(ah*bh+t) = rnd(-eps). On the other hand, dh-(ah*bh+ch) = eps.
def fastFMA_dw(h,l,ah,al,bh,bl,ch,cl):
    res=["",f"# {h}, {l} <- fastFMA_dw({ah}, {al}, {bh}, {bl}, {ch}, {cl})"]
    
    res.append(f"{h} = rnd ({ah} * {bh} + {ch});")
    t = get_var("fma_t")
    goal_list.append(f" {ch} // {h} in [0.5, 2]")
    res.append(f"{t} = {ch} - {h};") # exact thanks to Sterbenz
    e = get_var("fma_e")
    res.append(f"{e} = rnd (-({h} - ({ah} * {bh} + {ch})));")
    f = get_var("fma_f")
    res.append(f"{f} rnd = {e} + {cl};")
    g = get_var("fma_g")
    res.append(f"{g} rnd = ({ah} * {bl} + {f});")
    res.append(f"{l} rnd = ({al} * {bh} + {g});")
    hint_list.append(f"({h} + {l}) - (({ah} + {al})*({bh} + {bl}) + ({ch} + {cl})) -> ({e} - (-({h} - ({ah} * {bh} + {ch})))) + ({f} - ({e} + {cl})) + ({g} - ({ah} * {bl} + {f})) + ({l} - ({al} * {bh} + {g})) - {al}*{bl}")
    return '\n'.join(res)
    
# static inline double muldd(double xh, double xl, double ch, double cl, double *l){
#   double ahhh = ch*xh;
#   *l = (ch*xl + cl*xh) + __builtin_fma(ch, xh, -ahhh);
#   return ahhh;
# }
def muldd(result,l,xh,xl,ch,cl):
    """
    takes identifiers in input, writes
    result,l <- muldd(...)
    result and l should not be already defined
    """
    res=["",f"# {result}, {l} <- muldd({xh}, {xl}, {ch}, {cl})"]
    low_high=get_var("low_high")
    high_low=get_var("high_low")
    high_high_rest=get_var("high_high_rest")
    res.append(f"{low_high} rnd = {xl} * {ch};")
    res.append(f"{high_low} rnd = {xh} * {cl};")
    res.append(f"{result} rnd = {xh} * {ch};")
    res.append(f"{high_high_rest} = {ch} * {xh} - {result};")
    goal_list.append(f"@FIX({xh}*{ch}, -1074)")
    high_high_rest2=get_var("high_high_rest")
    t=get_var("t")
    res.append(f"{t} rnd = {high_low} + {low_high};")
    res.append(f"{l} rnd = {t} + {high_high_rest};")
    # hint (result+l) - (xh+xl)*(ch+cl) -> (high_low - (xh*cl)) + (low_high - (xl*ch)) + (t - (high_low+low_high)) + (l - (t+high_high_rest)) - xl*cl;
    hint_list.append(f"({result} + {l}) - ({xh} + {xl})*({ch} + {cl}) ->({high_low} - ({xh}*{cl})) + ({low_high} - ({xl} * {ch})) + ({t} - ({high_low} + {low_high})) + ({l} - ({t} + {high_high_rest})) - ({cl}*{xl})")
    res.append("")
    return '\n'.join(res)

# static inline double opolydd(double xh, double xl, int n, const double c[][2], double *l){
#   int i = n-1;
#   double ch = c[i][0], cl = c[i][1];
#   while(--i>=0)
#     ch = FastFMA_DW (xh, xl, ch, cl, c[i][0], c[i][1], &cl);
#   *l = cl;
#   return ch;
# }
def opolydd(h,l,xh,xl,n,tab,real_x):
    """
    writes h,l <- opolydd(x,n,array) 
    """
    res = [f"## {h}, {l} <- opolydd({xh}, {xl}, {n}, {tab})"]
    cl = get_var("v_cl")
    ch = get_var("v_ch")
    res.append(f"{ch} = {tab}{n-1}h;")
    res.append(f"{cl} = {tab}{n-1}l;")
    rC = get_var("rC")
    res.append(f"{rC} = {tab}{n-1};")
    hint_list.append(f"({ch}+{cl}) - {rC} -> ({tab}{n-1}h+{tab}{n-1}l) - {tab}{n-1}")
    for i in range(n-2,-1,-1):
        ch_new = get_var("v_ch")
        cl_new = get_var("v_cl")
        res.append(fastFMA_dw(ch_new,cl_new,xh,xl,ch,cl,f"{tab}{i}h",f"{tab}{i}l"))
        rC_new = get_var("rC")
        res.append(f"{rC_new} = {real_x}*{rC} + {tab}{i};")
        hint_list.append(f"({ch_new} + {cl_new}) - {rC_new} -> (({ch_new} + {cl_new}) - (({xh} + {xl})*({ch} + {cl})+({tab}{i}h + {tab}{i}l))) + ({xh} + {xl})*(({ch} + {cl}) - {rC}) + (({xh} + {xl}) - {real_x})*{rC} + (({tab}{i}h + {tab}{i}l) - {tab}{i})")
        ch = ch_new
        cl = cl_new
        rC = rC_new
    res.append(f"{h} = {ch_new};")
    res.append(f"{l} = {cl_new};")
    hint_list.append(f"({h}+{l}) -> ({ch_new}+{cl_new})")
    return '\n'.join(res)  
    
###########################################################
## Create file
file.write(header)
write_coefficients_double_double()
# file.write("x = rnd(x_);\n")

# ## RANGE REDUCTION
#file.write("s = 0x1.71547652b82fep+12;\n")
#file.write("t = roundeven(rnd(x*s));\n")

# wdeclare("l2h", "0x1.62e42ffp-13")
# wdeclare("l2l", "0x1.718432a1b0e26p-47")
# wdeclare("l2ll", "0x1.9ff0342542fc3p-102")

file.write("# Defining real values \n")
# wdeclare("l2_real", "l2h - l2l - l2ll")
# wdeclare("dx_real", "x - l2_real*t")
# wdeclare("dxh", "rnd(dx_real)")
# wdeclare("dxl", "rnd(-(dxh - dx_real))")
wdeclare("dx_real", "dxh+dxl")
wdeclare("y0_real", f"({horner(7,'dx_real','c')})")
wdeclare("y1_real", f"dx_real*y0_real")

wdeclare("th", "rnd(th_)")
wdeclare("tl", "rnd(tl_)")

file.write(opolydd("fh","fl","dxh","dxl",7,"c","dx_real")+"\n")
file.write(muldd("fh_1", "fl_1", "dxh", "dxl", "fh", "fl"))

wdeclare("y0", "fh + fl")
wdeclare("y1", "fh_1 + fl_1")

file.write(muldd("fh_2","fl_2","fh_1","fl_1","th","tl")+ "\n")
file.write(fast_sum("yh","yl","th","tl","fh_2","fl_2")+ "\n")

wdeclare("y","yh + yl")
wdeclare("y_real","(y1_real*(th+tl) + (th+tl))")


hint_list.append("y0 - y0_real -> (v_ch6 + v_cl6) - rC6")
hint_list.append("(dxh + dxl) - dx_real -> dxl - (-(dxh - dx_real))")
hint_list.append("y1 - y1_real -> ((fh_1 + fl_1) - (dxh + dxl)*(fh + fl)) + ((dxh + dxl) - dx_real)*(fh + fl) + dx_real*((fh+fl) - y0_real)")
hint_list.append("(yh + yl) - y_real -> ((yh + yl) - ((th + tl) + (fh_2 + fl_2))) + ((fh_2 + fl_2) - ((fh_1 + fl_1)*(th + tl))) + ((fh_1 + fl_1)- y1_real)*(th + tl)")

# Goal
dxh_min = "1b-154"
dxh_max = "90901b-30" # 2^-13.528 < 90901b-30
dxl_min = "1b-154"
dxl_max = "16396b-80" # 2^-65.999 < 16396b-80
tl_max = "598b-60" # 2^-50.776 < 598b-60

goal_list.append("|y - y_real| in ? /\\ |yl| in ?") 
#goal_list.append("|y - y_real| <= 0x1.40278036009p-101") 
# <= 2^(-100.677368)
## Print goals

s1 = f"\n{{ (dxh in [{dxh_min}, {dxh_max}] \\/ dxh in [0,0] \\/ dxh in [-{dxh_max},-{dxh_min}]) /\\ @FIX(dxh,-154) /\\ (dxl in [-{dxl_max}, -{dxl_min}] \\/ dxl in [0,0] \\/ dxl in [{dxl_min}, {dxl_max}]) /\\ @FIX(dxl,-154) /\\ th in [1,2] /\\ tl in [-{tl_max},{tl_max}] -> "
s2 = r' /\ '.join(goal_list)
s3 = "}\n"
file.writelines([s1,s2,s3,"\n\n"])

# Hints
hint_list.append("")
file.write(';\n'.join(hint_list))

## Finished
file.close()
