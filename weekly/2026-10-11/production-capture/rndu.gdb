set pagination off
set confirm off
set disable-randomization off
python
import gdb,json
class Probe(gdb.Breakpoint):
 def stop(self):
  x=int(gdb.parse_and_eval('(unsigned long long)$xmm0.v2_int64[0]'))
  f=int(gdb.parse_and_eval('(unsigned long long)$xmm1.v2_int64[0]'))
  mx=int(gdb.parse_and_eval('$mxcsr'))
  print('PROBE '+json.dumps({'x_bits':format(x,'016x'),'f_bits':format(f,'016x'),'mxcsr':mx}))
  return False
Probe('*as_exp_database')
end
run --rndu < database.wc
