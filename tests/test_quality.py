import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quality', ROOT / 'quality.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class MeasurementTests(unittest.TestCase):
    def cell(self, name, lines, arcs, status='PASS'):
        return {'function': name, 'status': status, 'coverage_union': {
            'lines_total': 10, 'lines_hit': 10-lines, 'arcs_total': 20, 'arcs_hit': 20-arcs}}

    def test_ranking_zero_line_branch_gaps_and_partial(self):
        r = q.ranking([self.cell('a', 0, 0), self.cell('b', 1, 0),
                       self.cell('c', 0, 7), self.cell('d', 0, 1, 'INCOMPLETE')], list('abcd'))
        self.assertEqual([x['function'] for x in r['candidates']], ['c', 'b'])
        self.assertFalse(r['complete_population'])
        self.assertEqual(r['measured'], 3)

    def test_union_rejects_changed_denominator(self):
        with self.assertRaises(ValueError):
            q.add_union({('f', 1): 0}, {('f', 2): 4})

    def test_union_distinct_branch_identity(self):
        self.assertEqual(q.add_union({('f', 1, 0): 0, ('f', 1, 1): 3},
                                     {('f', 1, 0): 2, ('f', 1, 1): 0}),
                         {('f', 1, 0): 2, ('f', 1, 1): 3})

    def test_coverage_duplicate_identity_rejected(self):
        with self.assertRaises(ValueError):
            q.coverage_maps({'lines': [{'line_number': 1, 'count': 0}]*2})

    def test_checker_requires_success_count_and_exit(self):
        q.check_output({'returncode': 0, 'output': '8 tests passed, 0 failure(s)\n'}, 8)
        for rc, output in [(1, '8 tests passed, 0 failure(s)'), (0, '4 tests passed, 0 failure(s)'),
                           (0, ''), (0, '8 tests passed, 1 failure(s)')]:
            with self.assertRaises(RuntimeError):
                q.check_output({'returncode': rc, 'output': output}, 8)
        self.assertEqual(q.failed_status({'returncode':0,'output':'8 tests passed, 1 failure(s)'}),'FAIL')
        self.assertEqual(q.failed_status({'returncode':0,'output':'bad output'}),'INCOMPLETE')

    def test_sha_pins_and_selection(self):
        for pin in ['main', 'abc', '../path', 'A'*40]:
            with self.assertRaises(ValueError):
                q.pin_value(pin)
        for selection in ['sin,sin', 'hypot', '../sin', '']:
            with self.assertRaises(ValueError):
                q.targets(selection)
        self.assertEqual(len(q.targets('all')), 25)

    def test_expected_symmetry_and_comments(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/'test.wc').write_text('# note\n0x1p0\n0x1p-1\n')
            (p/'header.h').write_text('/* WORST_SYMMETRIC is documented */\n')
            self.assertEqual(q.expected_rows(p/'test.wc', p/'header.h'), (2, 2))
            (p/'header.h').write_text('#define WORST_SYMMETRIC\n')
            self.assertEqual(q.expected_rows(p/'test.wc', p/'header.h'), (2, 4))

    def test_timeout_reaps_child(self):
        import sys, os
        with tempfile.TemporaryDirectory() as d:
            pidfile = Path(d)/'pid'
            with self.assertRaises(RuntimeError):
                q.command([sys.executable, '-c',
                    'import time,os,pathlib,sys; pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(20)',
                    str(pidfile)], timeout=0.3)
            pid = int(pidfile.read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_retry_clears_stale_coverage_and_keeps_failure_modes(self):
        from unittest.mock import patch
        import time
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, runs = root/'source', root/'runs'
            files = {'src/binary64/rsqrt/rsqrt.c': 'double cr_rsqrt(double x){return x;}',
                     'src/binary64/rsqrt/rsqrt_mpfr.c': '',
                     'src/binary64/rsqrt/rsqrt.wc': '0x1p0\n',
                     'src/binary64/rsqrt/function_under_test.h': '',
                     'src/binary64/support/check_worst_uni.c':
                     '// CORE_MATH_CHECK_INEXACT CORE_MATH_SUPPORT_ERRNO CORE_MATH_NO_OPENMP\n'}
            for rel, contents in files.items():
                path = source/rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents)
            q.save(source/'manifest.json', {'files': {rel:q.sha(source/rel) for rel in files}})
            cell = runs/'rsqrt-toy-errno1'
            cell.mkdir(parents=True)
            (cell/'rndd-coverage.json').write_text('stale')
            def fake(args, **kwargs):
                fail = args == ['./plain', '--rndz']
                return {'returncode': int(fail), 'output': 'FAIL x=0x1p0' if fail else '1 tests passed, 0 failure(s)\n', 'wall_seconds': 0}
            p = {'cc':'fake', 'coverage':False, 'flags':[]}
            with patch.object(q,'profile',return_value=p), patch.object(q,'command',side_effect=fake):
                result = q.run_one(source,'rsqrt','toy',1,runs,{},time.monotonic()+10)
            self.assertEqual(result['status'], 'FAIL')
            self.assertEqual(len(result['modes']),4)
            self.assertEqual(result['modes'][1]['plain'],'FAIL')
            self.assertFalse((cell/'rndd-coverage.json').exists())

    def test_termination_reaps_detached_child(self):
        import sys, subprocess, os, signal
        with tempfile.TemporaryDirectory() as d:
            pidfile = Path(d)/'pid'
            child = 'import os,time,pathlib,sys; pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(20)'
            parent = 'import quality,sys; quality.command([sys.executable,"-c",sys.argv[1],sys.argv[2]],timeout=15)'
            proc = subprocess.Popen([sys.executable,'-c',parent,child,str(pidfile)],cwd=ROOT,
                                    stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    proc.communicate(timeout=0.7)
                pid = int(pidfile.read_text())
                proc.send_signal(signal.SIGTERM)
                proc.communicate(timeout=3)
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid,0)
            finally:
                if proc.poll() is None:
                    proc.kill(); proc.communicate()

    def test_lock_excludes_second_process(self):
        import sys
        with tempfile.TemporaryDirectory() as temp:
            lock = str(Path(temp) / 'test.lock')
            with q.locked(lock):
                r = q.command([sys.executable, '-c',
                               'import quality,sys;\nwith quality.locked(sys.argv[1]): print("bad")', lock], cwd=ROOT)
                self.assertNotEqual(r['returncode'], 0)
                self.assertIn('Another core-math-quality run', r['output'])

if __name__ == '__main__':
    unittest.main()
