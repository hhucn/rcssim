import unittest

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCommitSet(unittest.TestCase):
    def test_commitset(self):
        from commitset import CommitSet

        cs = CommitSet()
        self.assertEqual(cs.add_commit((), 1001), 0)
        self.assertEqual(len(cs.all_commits), 1)
        self.assertEqual(cs.calc_merge_commit_count(), 0)

        self.assertEqual(cs.add_commit((0,), 1002), 1)
        self.assertEqual(len(cs.all_commits), 2)
        self.assertEqual(cs.has_ancestor(1, 0), True)
        self.assertEqual(cs.has_ancestor(0, 1), False)
        self.assertEqual(cs.calc_merge_commit_count(), 0)

        self.assertEqual(cs.add_commit((0,), 1003), 2)
        self.assertEqual(len(cs.all_commits), 3)
        self.assertEqual(cs.has_ancestor(2, 0), True)
        self.assertEqual(cs.has_ancestor(0, 2), False)
        self.assertEqual(cs.has_ancestor(1, 2), False)
        self.assertEqual(cs.has_ancestor(2, 1), False)
        self.assertEqual(cs.calc_merge_commit_count(), 0)

        self.assertEqual(cs.add_commit((0,), 1004), 3)
        self.assertEqual(cs.has_ancestor(3, 0), True)
        self.assertEqual(cs.has_ancestor(0, 3), False)
        self.assertEqual(cs.has_ancestor(3, 1), False)
        self.assertEqual(cs.has_ancestor(1, 3), False)
        self.assertEqual(cs.has_ancestor(3, 2), False)
        self.assertEqual(cs.has_ancestor(2, 3), False)
        self.assertEqual(len(cs.all_commits), 4)
        self.assertEqual(cs.calc_merge_commit_count(), 0)

        self.assertEqual(cs.add_commit((1, 2), 1005), 4)
        self.assertEqual(len(cs.all_commits), 5)
        self.assertEqual(cs.calc_merge_commit_count(), 1)
        self.assertEqual(cs.has_ancestor(4, 0), True)
        self.assertEqual(cs.has_ancestor(0, 4), False)
        self.assertEqual(cs.has_ancestor(4, 1), True)
        self.assertEqual(cs.has_ancestor(1, 4), False)
        self.assertEqual(cs.has_ancestor(4, 2), True)
        self.assertEqual(cs.has_ancestor(2, 4), False)
        self.assertEqual(cs.has_ancestor(4, 3), False)
        self.assertEqual(cs.has_ancestor(3, 4), False)

        self.assertEqual(cs.add_commit((3, 4), 1006), 5)
        self.assertEqual(len(cs.all_commits), 6)
        self.assertEqual(cs.calc_merge_commit_count(), 2)
        self.assertEqual(cs.has_ancestor(5, 0), True)
        self.assertEqual(cs.has_ancestor(0, 5), False)
        self.assertEqual(cs.has_ancestor(5, 1), True)
        self.assertEqual(cs.has_ancestor(1, 5), False)
        self.assertEqual(cs.has_ancestor(5, 2), True)
        self.assertEqual(cs.has_ancestor(2, 5), False)
        self.assertEqual(cs.has_ancestor(5, 3), True)
        self.assertEqual(cs.has_ancestor(3, 5), False)
        self.assertEqual(cs.has_ancestor(5, 4), True)
        self.assertEqual(cs.has_ancestor(4, 5), False)

        self.assertEqual(cs.add_commit((3, 4), 1007), 6)
        self.assertEqual(len(cs.all_commits), 7)
        self.assertEqual(cs.calc_merge_commit_count(), 3)
        self.assertEqual(cs.has_ancestor(6, 0), True)
        self.assertEqual(cs.has_ancestor(0, 6), False)
        self.assertEqual(cs.has_ancestor(6, 1), True)
        self.assertEqual(cs.has_ancestor(1, 6), False)
        self.assertEqual(cs.has_ancestor(6, 2), True)
        self.assertEqual(cs.has_ancestor(2, 6), False)
        self.assertEqual(cs.has_ancestor(6, 3), True)
        self.assertEqual(cs.has_ancestor(3, 6), False)
        self.assertEqual(cs.has_ancestor(6, 4), True)
        self.assertEqual(cs.has_ancestor(4, 6), False)
        self.assertEqual(cs.has_ancestor(6, 5), False)
        self.assertEqual(cs.has_ancestor(5, 6), False)
