#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import unittest
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.rules as rules
import madsenlab.axelrod.population as pop
import madsenlab.axelrod.analysis as analysis
import logging as log
import pprint as pp
import tempfile


class ExtensibleTraitTest(unittest.TestCase):


    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
       {
    "REPLICATIONS_PER_PARAM_SET" : 10,
    "POPULATION_SIZES_STUDIED" : [64,100],
    "TRAIT_ADDITION_RATE" : [0.01, 0.05, 0.1, 0.25],
    "MAXIMUM_INITIAL_TRAITS" : [4,8,16,32],
    "POPULATION_STRUCTURE_CLASS" : "madsenlab.axelrod.population.ExtensibleTraitStructurePopulationBase",
    "INTERACTION_RULE_CLASS" : "madsenlab.axelrod.rules.AxelrodRule",
    "NETWORK_FACTORY_CLASS" : "madsenlab.axelrod.population.SquareLatticeFactory"
}
        """)
        self.tf.flush()
        config = utils.AxelrodExtensibleConfiguration(self.tf.name)

        config.popsize = 25
        config.maxtraits = 16
        config.add_rate = 0.1

        graph_factory = pop.SquareLatticeFactory(config)
        self.pop = pop.ExtensibleTraitStructurePopulationBase(config, graph_factory)
        self.pop.initialize_population()


    def test_node_coloring(self):

        node0_traits = self.pop.model.node[0]['traits']
        pack = self.pop.get_traits_packed(node0_traits)
        log.info("node0_traits: %s packed: %s", pp.pformat(node0_traits), pack)
        self.assertTrue(isinstance(pack, (int, long)))


    def test_diagram(self):
        self.pop.draw_network_colored_by_culture()

if __name__ == "__main__":
    unittest.main