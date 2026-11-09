"""Verify adopted pickup rows and the source/PDF sign checkpoint. Supply the
pinned hypot.wc, cos.tex and the downloaded cos.pdf as positional arguments.
Requires Python 3 and pdftotext. Prints a receipt without private machine paths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PICKUPS = (
    ('above', 'candidates/hypot-midpoint-plus-one/hypot-midpoint-plus-one.wc',
     'candidates/hypot-midpoint-plus-one/README.md'),
    ('below', 'weekly/2026-11-08/hypot-below.wc', 'weekly/2026-11-08/REPORT.md'),
)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify(corpus, tex, pdf):
    data = corpus.read_bytes()
    require(digest(data) == '0ccf8be8b70eac41c87749928a1e2d8bf74b714812a4cb2dcdcd3e4f11b5dfec', 'corpus identity')
    lines = data.decode('utf-8').splitlines()
    groups = {}
    all_rows = set()
    for name, pickup, citation in PICKUPS:
        rows = [line for line in (ROOT / pickup).read_text(encoding='utf8').splitlines()
                if line and not line.startswith('#')]
        require(len(rows) == len(set(rows)) == 16 and not all_rows.intersection(rows), 'pickup population')
        all_rows.update(rows)
        positions = []
        for row in rows:
            require(lines.count(row) == 1, 'exact ordered row must appear once')
            positions.append(lines.index(row) + 1)
        require(positions == list(range(positions[0], positions[0] + 16)), 'contiguous pickup order')
        url = 'https://github.com/eth100tx/core-math-quality/blob/main/' + citation
        anchor = lines.index('# ' + url) + 1
        require(anchor < positions[0] and all(x.startswith('#') for x in lines[anchor:positions[0]-1]), 'citation before data')
        groups[name] = dict(first_line=positions[0], last_line=positions[-1], exact_ordered_rows=len(rows),
                            citation_line=anchor, citation=url, pickup_sha256=digest((ROOT/pickup).read_bytes()))
    require(digest(tex.read_bytes()) == 'd71a522222641fd36418afa6aa17e2f85108a896a021dca8f4192dd68bdf2adf', 'TeX identity')
    require(digest(pdf.read_bytes()) == '4fac541e7372737b18f7a663957676d8df46e95b4a4848c599e2cc3abcd90de4', 'PDF identity')
    require(r'q+\sigma_r=0' in tex.read_text(encoding='utf8'), 'older TeX sign paragraph')
    layout = subprocess.check_output(['pdftotext','-enc','UTF-8','-layout',str(pdf),'-'],timeout=30).decode('utf8')
    for fragment in ['Before applying the half-turn factor', 'Define d = 1 if q = σr and w1 ≤ w2',
                     'σ = (b + q + d) mod 2', '(−1)σ C = (−1)b D']:
        require(fragment in layout, 'published PDF sign text')
    # Independently follow Algorithm AccurateLarge's unsigned branches without
    # introducing d. Representatives cover the two strict comparisons and equality.
    cases = 0
    for b in (0, 1):
        for q in (0, 1):
            for sr in (0, 1):
                for w1, w2 in ((1, 2), (2, 1), (1, 1)):
                    sign = b ^ q
                    if q != sr:
                        magnitude = w1 + w2
                    elif w1 <= w2:
                        magnitude = w2 - w1
                        sign ^= 1
                    else:
                        magnitude = w1 - w2
                    signed_difference = (-1)**q * w1 - (-1)**sr * w2
                    require((-1)**sign * magnitude == (-1)**b * signed_difference, 'signed identity')
                    cases += 1
    return dict(implementation='185b7dec645407a4ded6ee01d6af14a784a17514',
                proof_repository='d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b',
                published_pdf='https://core-math.gitlabpages.inria.fr/cos.pdf',
                pdf_sha256=digest(pdf.read_bytes()), tex_sha256=digest(tex.read_bytes()),
                corpus_sha256=digest(data), groups=groups, representative_sign_cases=cases)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','tex','pdf'):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.corpus,args.tex,args.pdf),indent=2))
