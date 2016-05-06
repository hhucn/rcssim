#!/usr/bin/env python3

import functools
import io
import json
import multiprocessing
import random
import subprocess
import sys

import simplot
import simstore
import simcore


def plot_graph(current_nodes):
    out = 'digraph G {'
    visited = set()
    to_visit = list(set(current_nodes))
    while to_visit:
        n = to_visit.pop()
        visited.add(n)
        for p in n.parents:
            out += 'node_%s -> node_%s;\n' % (id(p), id(n))
            if p not in visited:
                to_visit.append(p)

    merges = 0
    for v in visited:
        out += 'node_%s [label = "%s"]' % (id(v), v.id)
        if 'merge' in v.id:
            merges += 1
    print('%s merges' % merges)
    out += '}'

    img_fn = 'tmp.svg'
    dot_fn = 'tmp.dot'
    with io.open(dot_fn, 'w', encoding='utf-8') as dotf:
        dotf.write(out)
    subprocess.check_call(['dot', '-Tsvg', dot_fn, '-o', img_fn])

    subprocess.check_call(['display', img_fn])

    import sys
    sys.exit(1)


def get_default_params_dict():
    with open('default_params.json') as jsonf:
        res = json.load(jsonf)

    try:
        with open('local_params.json') as localf:
            local_params = json.load(localf)
            res.update(local_params)
    except FileNotFoundError:
        pass

    return res


def one_sim_run(params, rng_seed):
    rng = random.Random(rng_seed)
    simres = simcore.sim(rng, params)
    return simres


def one_sim(ex):
    name = ex['name']
    changes = ex['changes']
    base_params = ex['base_params']

    crit = ex.get('crit')
    if crit is None:
        crit = 'cost'
    assert isinstance(crit, str)

    def critfunc(res):
        return getattr(res, crit)

    print(name)

    param_dict = get_default_params_dict()
    param_dict['name'] = name
    if base_params:
        param_dict.update(base_params)

    common_params = simcore.Params(**param_dict)

    pool = multiprocessing.Pool()
    res = []
    for change_idx, c in enumerate(changes):
        print(' ' + ','.join('%s = %r' % item for item in c.items()))
        xkey = c.get('_label')
        if not xkey:
            assert len(c) == 1
            xkey = list(c.values())[0]
        cvals = {
            ckey: cval
            for ckey, cval in c.items()
            if not ckey.startswith('_')
        }
        params = common_params._replace(**cvals)

        rng_seeds = [
            run + change_idx * params.runs
            for run in range(params.runs)]
        called_func = functools.partial(one_sim_run, params)

        simresults = pool.map(called_func, rng_seeds)

        results = []
        edit_counts = []
        commit_counts = []
        for simres in simresults:
            edit_counts.append(simres.edit_count)
            commit_counts.append(simres.commit_count)
            cost = critfunc(simres)
            results.append(cost)

        sres = {
            'params': params._asdict(),
            'crit': crit,
            'results': results,
            'xkey': '%s' % xkey,
        }
        xlabel = ex.get('xlabel')
        if xlabel:
            sres['xlabel'] = xlabel

        res.append(sres)
        print(' -> min %s, avg %s, max %s, edits: %s/%s, commits: %s/%s' % (
            min(results),
            round(sum(results) / len(results)),
            max(results),
            min(edit_counts), max(edit_counts),
            min(commit_counts), max(commit_counts),
        ))

    pool.close()
    pool.join()

    simstore.save(res)


def sim_json(name):
    with open('experiments.json') as exf:
        experiments = json.load(exf)

    ex = next(e for e in experiments if e['name'] == name)
    return one_sim(ex)


def simall_json(names=None):
    def on_error(e):
        raise e

    with open('experiments.json') as exf:
        experiments = json.load(exf)

    if names:
        experiments = [e for e in experiments if e['name'] in names]
    else:
        experiments = [e for e in experiments if e['active']]

    for ex in experiments:
        one_sim(ex)


def run_all_sims():
    simall_json()


def help():
    print('Usage: %s CMD' % sys.argv[0])
    print('Available commands (CMD):')
    print(' sim   Run simulations and store results')
    print(' plot  Plot results')


def main():
    if (len(sys.argv) < 2):
        help()
        return 11
    cmd = sys.argv[1]

    if cmd == 'sim':
        run_all_sims()
    elif cmd == 'plot':
        names = sys.argv[2:]
        if names:
            simplot.plot_only(names)
        else:
            simplot.plot_all()
    else:
        help()
        return 12

    return 0


if __name__ == '__main__':
    sys.exit(main())
