"""Verify the recorded assembly and optimized GCC graph, then replay the bounds and finite value checks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from contracted_asin import SOURCE, STRICT, evaluate

HERE = Path(__file__).resolve().parent
FLAGS = ["-O3", "-march=x86-64-v3", "-frounding-math", "-fno-finite-math-only",
         "-DCORE_MATH_SUPPORT_ERRNO"]
EXPECTED = "76ba970586b4d4ce33d1a3e354237aac0f7f63fe84eb68817b924c14207b7698"
GRAPH = "6d83579bab3bb4b6c3b854b3fe89b791550d66e545c9c2151c1223da80eaa231"


def assembly_digest(path):
    # Retain directives, constants, labels and operands, removing GCC commentary.
    lines = [s.partition("#")[0].rstrip() for s in path.read_text().splitlines()]
    return hashlib.sha256(("\n".join(s for s in lines if s)+"\n").encode()).hexdigest()


def run(source, library):
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE:
        raise ValueError("source identity")
    with tempfile.TemporaryDirectory() as name:
        td = Path(name)
        shutil.copyfile(source, td/"now-asin.c")
        def invoke(args, check=True):
            return subprocess.run(args,cwd=td,check=check,capture_output=True,text=True,timeout=90)
        digests = {}
        for mode in ("fast","off"):
            invoke(["gcc",*FLAGS,"-ffp-contract="+mode,"-fdump-tree-optimized-lineno=graph.txt",
                    "-S","-fverbose-asm","now-asin.c","-o",mode+".s"])
            digests[mode] = assembly_digest(td/(mode+".s"))
            if mode == "fast":
                graph = hashlib.sha256((td/"graph.txt").read_bytes()).hexdigest()
        if digests["fast"] != EXPECTED or graph != GRAPH or digests["off"] == EXPECTED:
            raise ValueError("build differs from reviewed graph")
        bounds = evaluate(source, library)
        try:
            evaluate(source, library, 2)
        except ValueError as err:
            if "refinement index out of range" not in str(err):
                raise
        else:
            raise ValueError("doubled index scale escaped the negative control")
        invoke(["gcc",*FLAGS,"-ffp-contract=fast",str(HERE/"probe_asin.c"),"fast.s",
                "-lmpfr","-lgmp","-lm","-o","probe"])
        values = invoke(["./probe"]).stdout.splitlines()
        if values != [f"mode={m} calls=542 PASS" for m in range(4)]:
            raise ValueError("missing mode or probe calls")
        control = invoke(["./probe","--negative-control"],False)
        if control.returncode != 1 or "value mismatch" not in control.stderr:
            raise ValueError("one-bit value control failed")
        return {"interval_library_sha256":STRICT, "flags":FLAGS+["-ffp-contract=fast"], "range":bounds, "assembly_sha256":digests,"optimized_graph_sha256":graph,
                "compiler":invoke(["gcc","--version"]).stdout.splitlines()[0],
                "value_probe":values, "negative_controls":["uncontracted assembly distinguished",
                "doubled index scale rejected","injected one-bit mismatch detected"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("interval_library",type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.source.resolve(), args.interval_library.resolve()),indent=2))
