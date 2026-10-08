"""Bounded serial replay of the exact published Gappa goal files."""
from pathlib import Path
import subprocess,sys,shutil,time,json
R=Path(__file__).resolve().parent;g=sys.argv[1] if len(sys.argv)>1 else shutil.which('gappa');assert g
t=time.monotonic();results=[];output=R/'replay-logs';output.mkdir(exist_ok=True)
for p in sorted((R/'models').glob('*.g')):
 assert time.monotonic()-t<1800,'Overall30-minute replay cap'
 text=p.read_text();assert len([line for line in text.splitlines() if line.startswith('{')])==1
 assert not any(token in text for token in ['XMIN','XMAX','RND'])
 flags=['-Eprecision=200'] if p.stem.startswith('accurate-goal-') else []
 q=subprocess.run([g,*flags,str(p)],capture_output=True,text=True,timeout=180)
 log=q.stdout+'\n'+q.stderr;(output/(p.stem+'.log')).write_text(log)
 assert q.returncode==0 and not any(x in log.lower() for x in ['cannot prove','some enclosures were not satisfied','pointless','not trivially true']),p.name
 results.append(p.name);print('PASS',p.name,flush=True)
(output/'summary.json').write_text(json.dumps(dict(passed=True,goals=results,wall_seconds=time.monotonic()-t),indent=2)+'\n')
