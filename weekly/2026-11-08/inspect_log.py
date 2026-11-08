"""Compile the unchanged log unit and expose the tiny-path source/assembly mapping.
Outputs are generated in a disposable directory; only -O3 Linux x86-64 profiles below.
"""
from pathlib import Path
import hashlib, subprocess, json, re, sys, tempfile
from shutil import copyfile
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def blob(d):return hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()
def main(root, variant):
    ids={'log.c':'7b57c0c8ac9a59ed1df1020bb304bab93385f2cb','dint.h':'31bfbbc07cf95548bf82ce020e2d687b091d06fd'}
    result=[]
    with tempfile.TemporaryDirectory() as tmp:
        td=Path(tmp)
        for f,h in ids.items():
            d=(root/f).read_bytes()
            if blob(d)!=h:raise ValueError(f)
            (td/f).write_bytes(d)
        for cc in ['gcc','clang-18']:
            flags=['-O3','-frounding-math','-fno-finite-math-only','-ffp-contract=off','-march=x86-64','-DCORE_MATH_SUPPORT_ERRNO','-DCORE_MATH_NO_OPENMP','-DCORE_MATH_CHECK_INEXACT']
            if variant=='v3-contract-fast':
                flags[flags.index('-ffp-contract=off')]='-ffp-contract=fast'
                flags[flags.index('-march=x86-64')]='-march=x86-64-v3'
            if cc=='gcc':flags+=['-fsignaling-nans']
            subprocess.run([cc,*flags,'-g','-c','log.c','-o','log.o'],cwd=td,check=True,timeout=30)
            out=subprocess.check_output(['objdump','-dl','-Mintel','--no-show-raw-insn','log.o'],cwd=td,text=True,timeout=30)
            # Restrict published assembly lines to the near-one function's source
            # and its fast_two_sum helper; a line table can be incomplete. No
            # automatic deduction of arbitrary compiler semantics from mnemonics.
            rows=[];line=None;func=None
            for s in out.splitlines():
                m=re.match(r'[0-9a-f]+ <([^>]+)>:',s)
                if m:func=m[1];line=None
                m=re.search(r'log\.c:(\d+)',s)
                if m:line=int(m[1])
                if func in ('cr_log','cr_log_tiny') and line is not None and (653<=line<=696 or 46<=line<=52) and re.match(r'\s*[0-9a-f]+:\s',s):
                    rows.append({'function':func,'source_line':line,'instruction':s.strip().split(':',1)[1].split('#')[0].strip()})
            if not rows:raise ValueError('missing line map')
            result.append({'cc':cc,'version':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],'flags':flags,'source_blobs':ids,'rows':rows})
    return result
if __name__=='__main__':print(json.dumps(main(Path(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else 'baseline'),indent=2))
