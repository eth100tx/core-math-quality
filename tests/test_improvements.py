import copy
import json
from pathlib import Path
import unittest
from validate_queue import validate_queue

ROOT = Path(__file__).resolve().parents[1]

class ImprovementQueueTests(unittest.TestCase):
    def setUp(self):
        self.queue = json.loads((ROOT/'config/improvements.json').read_text(encoding='utf-8'))

    def test_current_queue_has_existing_context(self):
        validate_queue(self.queue, ROOT)

    def test_invalid_state_unknown_fields_and_duplicate_id_rejected(self):
        for mutate in [lambda d: d['priorities'][0].update(status='proved-everything'),
                       lambda d: d.update(extra=True),
                       lambda d: d['priorities'][1].update(id=d['priorities'][0]['id'])]:
            with self.subTest(mutate=mutate):
                d=copy.deepcopy(self.queue); mutate(d)
                with self.assertRaises(ValueError): validate_queue(d, ROOT)

    def test_budget_and_unsafe_evidence_rejected(self):
        for mutate in [lambda d: d['priorities'][0]['budget'].update(cpu_hours=100),
                       lambda d: d['weekly_budget'].update(cpu_hours=float('nan')),
                       lambda d: d['priorities'][0].update(evidence=['../outside']),
                       lambda d: d['priorities'][0].update(evidence=['missing-file'])]:
            with self.subTest(mutate=mutate):
                d=copy.deepcopy(self.queue); mutate(d)
                with self.assertRaises(ValueError): validate_queue(d, ROOT)
