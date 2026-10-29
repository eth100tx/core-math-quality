"""Add the low-limb observation used by exceptions.c to a disposable source copy."""
from pathlib import Path
import sys
s=Path(sys.argv[1]).read_text(encoding='utf-8')
key='uint64_t d = (uint64_t) c1u + 5;'
assert s.count(key)==1
Path(sys.argv[2]).write_bytes(s.replace(key,'audit_low = (uint64_t)c1u; '+key).encode('utf-8'))
