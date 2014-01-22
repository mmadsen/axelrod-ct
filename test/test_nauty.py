#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.analysis as stats
import madsenlab.axelrod.utils as utils
import networkx as nx
import logging as log
import os
import tempfile
import re

class NautyTest(unittest.TestCase):

    filename = "test"

    def setUp(self):
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
        {
    "REPLICATIONS_PER_PARAM_SET" : 5,
    "POPULATION_SIZES_STUDIED" : [500,1000],
    "NUMBER_OF_DIMENSIONS_OR_FEATURES" : [1,2,4,8,16],
    "NUMBER_OF_TRAITS_PER_DIMENSION" :  [2,3,4,6,8,12,16,32]
}
        """)
        self.tf.flush()
        self.sc = utils.TreeStructuredConfiguration(self.tf.name)
        self.sc.branching_factor = 4
        self.sc.depth_factor = 4

    def tearDown(self):
        os.remove(self.tf.name)

    def test_dreadnaught_format(self):

        # build a simple example graph
        g = nx.petersen_graph()
        sym = stats.BalancedTreeAutomorphismStatistics(self.sc)
        dg = sym._get_dreadnaught_for_graph(g)
        nauty_format = sym._get_raw_nauty_output(dg)
        log.info("%s", nauty_format)

        o = re.compile('(\d+) orbit;')
        m = o.search(nauty_format)
        if m:
            num_orbits = m.group(1)
            #log.debug("num_orbits match: %s", num_orbits)

            log.info("orbits in petersen graph: %s", num_orbits)
            self.assertEqual(1, int(num_orbits))
        else:
            self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()