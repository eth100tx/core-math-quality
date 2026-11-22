"""Compare contraction settings on one source-bound Clang asin build."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = "d9cc7c44922ac3caef5a25d0eb3d9e1e2aa94a0fea761737416d68d6f3a2a8e9"
FLAGS = ["-O3", "-march=x86-64-v3", "-frounding-math", "-fno-finite-math-only",
         "-DCORE_MATH_SUPPORT_ERRNO"]


def compare(source, listing):
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE:
        raise ValueError("source identity")
    compiler = shutil.which("clang-18")
    if not compiler:
        raise ValueError("Clang 18 required")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root/"now-asin.c").write_bytes(source.read_bytes())
        def invoke(command):
            return subprocess.run(command, cwd=root, capture_output=True, text=True,
                                  check=True, timeout=60).stdout
        for mode in ("fast", "off"):
            invoke([compiler, *FLAGS, "-ffp-contract="+mode, "-c", "now-asin.c", "-o", mode+".o"])
        objects = [(root/(mode+".o")).read_bytes() for mode in ("fast", "off")]
        if objects[0] != objects[1]:
            raise ValueError("contraction settings produced different objects; review required")
        assembly = invoke(["objdump", "-dr", "fast.o"])
        listing.write_text(assembly)
        return {"source_sha256": SOURCE, "compiler": invoke([compiler, "--version"]).splitlines()[0],
                "compiler_binary_sha256": hashlib.sha256(Path(compiler).resolve().read_bytes()).hexdigest(),
                "flags": FLAGS, "compared_contraction_settings": ["fast", "off"],
                "object_sha256": hashlib.sha256(objects[0]).hexdigest(), "objects_byte_identical": True,
                "listing_sha256": hashlib.sha256(assembly.encode()).hexdigest(),
                "range_certificate_replayed": False, "function_value_tests_run": False,
                "flags_checked": False, "errno_checked": False,
                "scope": "Object equivalence for the named compiler, source and flags only."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("listing", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.source.resolve(), args.listing.resolve()), indent=2))
