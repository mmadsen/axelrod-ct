#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.utils as utils
import networkx as nx
import logging as log


class NautyTest(unittest.TestCase):

    def test_dreadnaught_format(self):

        # build a simple example graph
        g = nx.petersen_graph()
        nauty_format = utils.get_dreadnaught_for_graph(g)

        log.info("%s", nauty_format)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()