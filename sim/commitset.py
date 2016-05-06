import bitarray
import collections


Commit = collections.namedtuple(
    'Commit',
    ['parents', 'time',
     'ancestors', 'is_edit', 'ancestors_first_zero'])


class CommitSet(object):
    def __init__(self):
        self.all_commits = []

    def add_commit(self, parents, time):
        """ Returns the index of the new object """

        assert isinstance(parents, tuple)
        assert all(isinstance(p, int) for p in parents)

        ancestors = bitarray.bitarray(len(self.all_commits))
        ancestors.setall(False)
        for pidx in parents:
            ancestors[pidx] = True
            p_ancestors = self.all_commits[pidx].ancestors
            ancestors[:len(p_ancestors)] |= p_ancestors
        try:
            ancestors_first_zero = ancestors.index(False)
        except ValueError:
            ancestors_first_zero = len(ancestors)

        is_edit = len(parents) == 1

        commit = Commit(
            time=time,
            is_edit=is_edit,
            parents=parents,
            ancestors=ancestors,
            ancestors_first_zero=ancestors_first_zero)
        self.all_commits.append(commit)
        res = len(self.all_commits) - 1

        return res

    def has_ancestor(self, this_id, ancestor_id):
        if this_id < ancestor_id:
            return False
        this = self.all_commits[this_id]
        return this.ancestors[ancestor_id]

    def new_edits_between(self, c1_id, c2_id):
        c1 = self.all_commits[c1_id]
        c2 = self.all_commits[c2_id]
        c1_ancestors = c1.ancestors
        c2_ancestors = c2.ancestors

        if c1_id < c2_id:
            for i in range(c1_id + 1, c2_id):
                if c2_ancestors[i] and self.all_commits[i].is_edit:
                    return True
        elif c2_id < c1_id:
            for i in range(c2_id + 1, c1_id):
                if c1_ancestors[i] and self.all_commits[i].is_edit:
                    return True
        for i in range(min(c1.ancestors_first_zero, c2.ancestors_first_zero), min(c1_id, c2_id)):
            if (c1_ancestors[i] != c2_ancestors[i]) and self.all_commits[i].is_edit:
                return True
        return False

    def calc_merge_commit_count(self):
        return sum(1 for c in self.all_commits if len(c.parents) > 1)

    def calc_edit_count(self):
        return sum(1 for c in self.all_commits if len(c.parents) == 1)

    @property
    def commit_count(self):
        return len(self.all_commits)
