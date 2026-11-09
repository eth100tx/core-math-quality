"""Verify the near-one table boundary on an independent, deliberately broken model."""
import hashlib, json, tempfile
from pathlib import Path
import sys
import verify_asin as model

def main(path):
    text=path.read_text(encoding='utf8')
    literal='__builtin_fabs(phi) * 0x1.45f306dc9c883p+4'
    assert text.count(literal)==1
    with tempfile.TemporaryDirectory() as tmp:
        bad=Path(tmp)/'fault.c'
        bad.write_bytes(text.replace(literal,literal[:-1]+'5').encode())
        try:
            model.prove(bad)
        except ValueError as e:
            assert str(e)=='source identity'
        else:
            raise RuntimeError('mutated pin accepted')
        # The mutation deliberately doubles the index scale. Authorize this one
        # synthetic source only within this throwaway interpreter, then require
        # the mathematical range gate itself to fail before a table read.
        model.SOURCE_SHA256=hashlib.sha256(bad.read_bytes()).hexdigest()
        try:
            model.prove(bad)
        except ValueError as e:
            assert str(e).startswith('refinement index'),str(e)
            print(json.dumps({'source_hash_control':'rejected','doubled_index_scale':'rejected by range gate','diagnostic':str(e)},indent=2))
        else:
            raise RuntimeError('invalid index missed')
if __name__=='__main__':
    main(Path(sys.argv[1]))
