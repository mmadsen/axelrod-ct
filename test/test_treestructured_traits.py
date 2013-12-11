#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import unittest
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.traits as traits
import networkx as nx
import matplotlib.pyplot as plt
import logging as log
import pprint as pp
import tempfile

class TreeStructuredTraitTest(unittest.TestCase):

    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
        {
    "REPLICATIONS_PER_PARAM_SET" : 10,
    "POPULATION_SIZES_STUDIED" : [64,100],
    "TRAIT_ADDITION_RATE" : [0.01, 0.05, 0.1, 0.25],
    "MAXIMUM_INITIAL_TRAITS" : [4,8,16,32],
    "NUM_TRAIT_TREES" : [1,4,8,16],
    "TREE_BRANCHING_FACTOR" : [2,3,4,8],
    "TREE_DEPTH_FACTOR" : [4,5,6,8],
    "POPULATION_STRUCTURE_CLASS" : "madsenlab.axelrod.population.ExtensibleTraitStructurePopulation",
    "INTERACTION_RULE_CLASS" : "madsenlab.axelrod.rules.ExtensibleAxelrodRule",
    "NETWORK_FACTORY_CLASS" : "madsenlab.axelrod.population.SquareLatticeFactory",
    "TRAIT_FACTORY_CLASS" : "madsenlab.axelrod.traits.BalancedTreeStructuredTraitFactory"
}
        """)
        self.tf.flush()
        self.config = utils.TreeStructuredConfiguration(self.tf.name)

    @unittest.skip("Skipping test_tree_construction: this creates a graph and blocks - run manually")
    def test_tree_construction(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()

        pos=nx.graphviz_layout(trait_univ.graph,prog='dot')
        nx.draw(trait_univ.graph,pos,with_labels=True,arrows=False)
        plt.show()
        self.assertTrue(True)


    def test_path(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        expected = [0, 3, 12, 39]
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        path = trait_univ.get_parents_for_node(120)
        log.info("path for trait 120: %s", pp.pformat(path))
        self.assertEqual(expected, path)

    def test_has_prerequisites(self):
        agent_traits = set([0, 3, 12, 39])
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        self.assertTrue(trait_univ.has_prereq_for_trait(120, agent_traits))



    def test_nothave_prerequisites(self):
        agent_traits = set([0, 3])
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        self.assertFalse(trait_univ.has_prereq_for_trait(120, agent_traits))




if __name__ == "__main__":
    unittest.main