"""Replay the changed accurate-path obligations, one named goal per file.
Usage: python3 check_gappa.py acclarge.g output_directory [gappa executable]
"""
from pathlib import Path
import subprocess,sys,json,resource,time,hashlib

def main():
    source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
    tool=sys.argv[3] if len(sys.argv)>3 else 'gappa'
    start=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()
    txt=source.read_text();active=next(x for x in txt.splitlines() if x.startswith('{'))
    names=['s5 in ?','s1 in ?','s2 in ?','|sr-Sr|','|sr-SR|','c6 in ?','c4 in ?',
           'c0 >=','cr >=','|cr-Cr|','|cr-CR|','|w1-W1|']
    goals=[]
    for name in names:
        matches=[x[2:] for x in txt.splitlines() if x.startswith('# {') and name in x]
        assert len(matches)==1,(name,matches)
        goals.append((name,matches[0]))
    goals.append(('|w2-W2|',active))
    results=[]
    for i,(name,goal) in enumerate(goals):
        p=out/('%02d.g'%i);p.write_text(txt.replace(active,goal))
        print('Gappa',i,name,flush=True)
        r=subprocess.run([tool,str(p)],capture_output=True,text=True,timeout=45)
        log=r.stdout+r.stderr;(out/('%02d.log'%i)).write_text(log)
        results.append({'name':name,'goal':goal,'returncode':r.returncode,'output':log,
                        'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        assert r.returncode==0,log
    end=resource.getrusage(resource.RUSAGE_CHILDREN)
    d={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
       'tool_version':subprocess.check_output([tool,'--version'],text=True).splitlines()[0],
       'results':results,'complete':True,'child_cpu_seconds':end.ru_utime+end.ru_stime-start.ru_utime-start.ru_stime,
       'wall_seconds':time.monotonic()-wall}
    (out/'gappa.json').write_text(json.dumps(d,indent=2)+'\n')

if __name__=='__main__':main()
