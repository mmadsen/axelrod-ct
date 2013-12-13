#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.utils as utils
import logging as log


class MathFunctionsTest(unittest.TestCase):


    def test_num_nodes_balanced_tree(self):
        branching = 3
        height = 4
        expected = 121

        obs = utils.num_nodes_balanced_tree(branching,height)
        log.info("numnodes balanced tree: obs %s  exp: %s", obs, expected)
        self.assertEqual(obs,expected)

if __name__ == "__main__":
    unittest.main()