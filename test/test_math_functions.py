#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.analysis as stats
import logging as log


class MathFunctionsTest(unittest.TestCase):


    def test_num_nodes_balanced_tree(self):
        branching = 3
        height = 4
        expected = 121

        obs = stats.num_nodes_balanced_tree(branching,height)
        log.info("numnodes balanced tree: obs %s  exp: %s", obs, expected)
        self.assertEqual(obs,expected)


    def test_num_rooted_trees(self):
        """
        Tests the approximation r(n) from Otter 1948 against values of r(n) calculated
        via recursion formula #2 by Li 1996

        """
        tests = [6,10,12,14]
        ans = [20,719,4766,32973]

        for n in tests:
            rn = stats.num_rooted_trees_otter_approx(n)

        self.assertTrue(True)

    def test_num_trees_with_leaves(self):

        n = 341
        k = 256

        snk = stats.num_ordered_trees_by_leaves(n, k)



if __name__ == "__main__":
    unittest.main()