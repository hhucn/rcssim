import multiprocessing
import os

import matplotlib.pyplot as plt

import simstore

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plots')


def _get_fn(key):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    return os.path.join(DATA_DIR, key + '.svg')


YLABELS = {
    'cost': '# merges',
    'time_last': 'time of last commit',
}


def plot(key, data):
    # Random test data
    all_data = [run['results'] for run in data]

    fig, axis = plt.subplots(nrows=1, ncols=1, figsize=(10, 5))

    # rectangular box plot
    axis.boxplot(all_data, vert=True)
    maxval = max(max(results) for results in all_data)
    plt.ylim([0, int(round(maxval * 1.05))])

    # adding horizontal grid lines
    axis.yaxis.grid(True)
    axis.set_xticks([y + 1 for y in range(len(all_data))], )
    axis.set_xlabel(data[0].get('xlabel', key))
    ylabel = YLABELS[data[0].get('crit', 'cost')]
    axis.set_ylabel(ylabel)

    # add x-tick labels
    vals = [run['xkey'] for run in data]
    plt.setp(axis, xticks=[y + 1 for y in range(len(all_data))],
             xticklabels=vals)

    plt.savefig(_get_fn(key))
    plt.close()


def on_error(e):
    raise e


def plot_all():
    pool = multiprocessing.Pool()
    tasks = simstore.load_all()
    for task in tasks:
        pool.apply_async(plot, task, error_callback=on_error)
    pool.close()
    pool.join()


def plot_only(lst):
    for key in lst:
        data = simstore.load(key)
        plot(key, data)
