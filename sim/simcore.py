from __future__ import unicode_literals, division

import collections

from commitset import CommitSet

Meeting = collections.namedtuple('Meeting', [
    'sender',
    'receiver',
    'time',
])

Edit = collections.namedtuple('Edit', [
    'node',
    'time',
])

Params = collections.namedtuple('Params', [
    'atom_count',  # number of atoms
    'node_count',  # number of nodes
    'edit_duration',  # in hours [but really arbitrary]
    'meeting_duration',
    'meeting_every_per_node',

    'edit_distribution',  # one of 'expo', 'uniform'
    'edit_every_per_node',  # negative for whole system
    'edit_every_global',  # If this is set, it takes precedence of edit_every_per_node

    'intelligent_merging',
    'bidi',  # 'push': unidirectional communication (default), 'doublepush': Both sides push to each other, 'merge': 1 side merges, this gets pushed
    'limit',  # abort when this cost is reached
    'runs',  # number of simulation runs
    'name',  # human-readable name of this simulation

    'merge_nocontent_percent',  # Merge only with this percentage when edit sets are identical
    'merge_nocontent_abort_after_total',  # TODO

    'accept_if_bored',  # probability of merging is base^bored; 0 means total apathy, 1 means merging every time
    'bored_base',  # probability of merging is base^bored; 0 means total apathy, 1 means merging every time
])


def sim_node_meetings(rng, params):
    # See R. Groenevelt, P. Nain, and G. Koole, The Message Delay in Mobile
    # Ad Hoc Networks
    next_time = 0
    while next_time < params.meeting_duration:
        next_time += rng.expovariate(1. / (params.meeting_every_per_node / params.node_count))
        node1 = rng.randint(0, params.node_count - 1)
        node2 = rng.randint(0, params.node_count - 2)
        if node2 >= node1:
            node2 += 1
        yield Meeting(node1, node2, next_time)


def sim_edits_expo(rng, params):
    next_time = 0
    if params.edit_every_global:
        expo = 1. / params.edit_every_global
    else:
        expo = 1. / (params.edit_every_per_node / params.node_count)
    while next_time < params.edit_duration:
        next_time += rng.expovariate(expo)
        node = rng.randint(0, params.node_count - 1)
        e = Edit(node, next_time)
        yield e


def sim_edits_uniform(rng, params):
    if params.edit_every_global:
        edit_freq = params.edit_every_global
    else:
        edit_freq = params.every_per_node * params.node_count
    edit_count = int(round(float(params.edit_duration) / edit_freq))
    times = [
        rng.random() * params.edit_duration
        for _ in range(edit_count)
    ]
    times.sort()

    for t in times:
        node = rng.randint(0, params.node_count - 1)
        yield Edit(node, t)


def sim_edits(rng, params):
    if params.edit_distribution == 'expo':
        yield from sim_edits_expo(rng, params)
    elif params.edit_distribution == 'uniform':
        yield from sim_edits_uniform(rng, params)
    else:
        assert False, 'Unsupported edit simulation distribution %s' % params.edit_distribution


def merge(rng, params, all_commits, newest_commit, merge_bored, time_now, sender, receiver):
    ours_id = newest_commit[receiver]
    theirs_id = newest_commit[sender]

    if ours_id == theirs_id:
        # Identical
        pass
    elif all_commits.has_ancestor(theirs_id, ours_id):
        # Their version is plain newer
        newest_commit[receiver] = theirs_id
        merge_bored[receiver] = 0
    elif all_commits.has_ancestor(ours_id, theirs_id):
        # Our version is plain newer, do nothing
        pass
    else:
        # We have a common ancestor, need to merge
        if params.intelligent_merging:
            if all_commits.new_edits_between(ours_id, theirs_id):
                merge_bored[receiver] = 0
            else:
                # Identical edits, but different merges on the way
                if params.merge_nocontent_percent is None:
                    if params.bored_base is None:
                        return
                    else:
                        r = rng.random()
                        bored_stats = merge_bored[receiver]
                        bored_base = params.bored_base
                        bored_probab = bored_base ** (1 + bored_stats)
                        merge_bored[receiver] += 1
                        if r >= bored_probab:
                            if params.accept_if_bored:
                                # Simply pick the bored value from the other side
                                newest_commit[receiver] = theirs_id
                            return
                else:
                    r = rng.random()
                    if r * 100 >= params.merge_nocontent_percent:
                        return

        newest_commit[receiver] = all_commits.add_commit((ours_id, theirs_id), time_now)


def run_sim(rng, params, events):
    all_commits = CommitSet()
    root_commit_id = all_commits.add_commit((), 0)
    newest_commits = [root_commit_id] * params.node_count
    merge_bored = [0] * params.node_count
    for e in events:
        if isinstance(e, Edit):
            edit_id = all_commits.add_commit((newest_commits[e.node],), e.time)
            newest_commits[e.node] = edit_id
            merge_bored[e.node] = 0
        elif isinstance(e, Meeting):
            if params.bidi == 'push':
                merge(rng, params, all_commits, newest_commits, merge_bored, e.time, e.sender, e.receiver)
            elif params.bidi == 'doublepush':
                sent_back_commit = newest_commits[e.receiver]
                merge(rng, params, all_commits, newest_commits, merge_bored, e.time, e.sender, e.receiver)
                new_commit = newest_commits[e.receiver]
                newest_commits[e.receiver] = sent_back_commit
                merge(rng, params, all_commits, newest_commits, merge_bored, e.time, e.receiver, e.sender)
                newest_commits[e.receiver] = new_commit
            elif params.bidi == 'merge':
                merge(rng, params, all_commits, newest_commits, merge_bored, e.time, e.sender, e.receiver)
                newest_commits[e.sender] = newest_commits[e.receiver]
            else:
                raise ValueError('Invalid bidi value %r' % params.bidi)
        else:
            raise NotImplementedError()

    return SimResult(params, all_commits, newest_commits, merge_bored)


class SimResult(object):
    def __init__(self, params, all_commits, newest_commits, merge_bored):
        self.params = params
        self.all_commits = all_commits
        self.newest_commits = newest_commits
        self.merge_bored = merge_bored

    @property
    def cost(self):
        return self.all_commits.calc_merge_commit_count()

    @property
    def time95_sunset(self):
        return self.time_quantil_sunset(95)

    @property
    def time_last(self):
        ac = self.all_commits.all_commits
        return ac[len(ac) - 1].time

    @property
    def edit_count(self):
        return self.all_commits.calc_edit_count()

    @property
    def commit_count(self):
        return len(self.all_commits.all_commits)

    def time_quantil_sunset(self, quantil):
        commit_count = len(self.all_commits.all_commits)
        final_idx = commit_count
        for idx, c in enumerate(self.all_commits.all_commits):
            if c.time >= self.params.edit_duration:
                final_idx = idx
                break

        remaining_commits = commit_count - final_idx
        idx = int(round(quantil * remaining_commits + final_idx))
        if idx >= commit_count:
            idx = commit_count - 1
        return self.all_commits.all_commits[idx].time


def combine_events(*streams):
    events = sum(map(list, streams), [])
    events.sort(key=lambda e: e.time)
    return events


def sim(rng, params):
    node_meetings = sim_node_meetings(rng, params)
    edits = sim_edits(rng, params)
    all_events = combine_events(node_meetings, edits)

    return run_sim(rng, params, all_events)
