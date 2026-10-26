"""Strict structural checks for the improvement queue; not scientific review."""
from pathlib import Path
import datetime
import math
import re

TOP = {'schema_version', 'updated', 'implementation_pin', 'proof_pin', 'weekly_budget', 'execution_policy', 'priorities'}
CARD = {'id', 'rank', 'title', 'status', 'owner', 'reason', 'next_action', 'deliverable', 'acceptance', 'budget', 'stop', 'dependency', 'last_substantive_change', 'change', 'next_checkpoint', 'evidence'}

def exact(obj, fields, label):
    if not isinstance(obj, dict) or set(obj) != fields:
        raise ValueError('Incomplete/unknown improvement '+label+' fields')

def budget(d):
    exact(d, {'cpu_hours', 'wall_minutes'}, 'budget')
    if any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in d.values()):
        raise ValueError('Invalid improvement budget')

def validate_queue(d, root):
    exact(d, TOP, 'top-level')
    if type(d['schema_version']) is not int or d['schema_version'] != 1:
        raise ValueError('Unsupported improvement schema')
    datetime.date.fromisoformat(d['updated'])
    for key in ['implementation_pin', 'proof_pin']:
        if not isinstance(d[key], str) or not re.fullmatch('[0-9a-f]{40}', d[key]):
            raise ValueError('Invalid improvement pin')
    if not isinstance(d['execution_policy'], str) or not d['execution_policy'].strip():
        raise ValueError('Missing improvement execution policy')
    budget(d['weekly_budget'])
    cards = d['priorities']
    if not isinstance(cards, list) or not 1 <= len(cards) <= 3:
        raise ValueError('Queue must contain one to three genuine priorities')
    ids = set()
    for rank, card in enumerate(cards, 1):
        exact(card, CARD, 'card')
        if type(card['rank']) is not int or card['rank'] != rank:
            raise ValueError('Priority ranks must be consecutive')
        for key in CARD - {'rank', 'budget', 'evidence'}:
            if not isinstance(card[key], str) or not card[key].strip():
                raise ValueError('Missing improvement '+key)
        if not re.fullmatch('P[1-9][0-9]*', card['id']) or card['id'] in ids:
            raise ValueError('Invalid/duplicate improvement ID')
        ids.add(card['id'])
        if card['status'] not in {'planned', 'in_progress', 'blocked', 'tested', 'closed'}:
            raise ValueError('Unknown improvement status')
        for key in ['last_substantive_change', 'next_checkpoint']:
            datetime.date.fromisoformat(card[key])
        budget(card['budget'])
        evidence = card['evidence']
        if not isinstance(evidence, list) or not evidence:
            raise ValueError('Missing improvement evidence/context')
        for rel in evidence:
            if not isinstance(rel, str) or '\\' in rel or ':' in rel or rel.startswith('/') or '..' in Path(rel).parts:
                raise ValueError('Unsafe improvement evidence path')
            target = (root/rel).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise ValueError('Missing improvement evidence file')
    if any(sum(c['budget'][k] for c in cards) > d['weekly_budget'][k] for k in ['cpu_hours', 'wall_minutes']):
        raise ValueError('Card budgets exceed weekly envelope')
