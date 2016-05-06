import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def _get_fn(key):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    return os.path.join(DATA_DIR, key + '.json')


def save(res):
    key = res[0]['params']['name']
    fn = _get_fn(key)
    with open(fn, 'w') as f:
        json.dump(res, f, sort_keys=True, indent=2)


def load(key):
    fn = _get_fn(key)
    with open(fn, 'r') as f:
        return json.load(f)


def load_all():
    ls = os.listdir(DATA_DIR)
    for f in ls:
        m = re.match(r'^([^/]*)\.json$', f)
        key = m.group(1)
        yield (key, load(key))
