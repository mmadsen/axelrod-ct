#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log
import unittest
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.population as pop
import os
import tempfile
import pprint as pp
import networkx as nx

class SquareLatticeTest(unittest.TestCase):


    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
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
        config = utils.AxelrodConfiguration(self.tf.name)

        config.popsize = 25
        config.num_features = 8
        config.num_traits = 16

        self.pop = pop.SquareLatticeFixedTraitModel(config)
        self.pop.initialize_population()


    def tearDown(self):
        os.remove(self.tf.name)


    def test_lattice_initialization(self):
        for nodename in self.pop.model.nodes(data=True):
            pp.pprint(nodename)

        for nodename in self.pop.model.nodes():
            log.info("neighbors of %s: %s  traits: %s", nodename, pp.pformat(self.pop.model.neighbors(nodename)), pp.pformat(self.pop.model.node[nodename]['traits']))

        log.info("testing random agent selection")
        agent_tuple = self.pop.get_random_agent()
        log.info("agent %s", pp.pformat(agent_tuple))

        log.info("testing random neighbor for selected agent")
        neighbor_tuple = self.pop.get_random_neighbor_for_agent(agent_tuple[0])
        log.info("neighbor: %s", pp.pformat(neighbor_tuple))

        log.info("testing changing a trait list")
        (id, traits) = self.pop.get_random_agent()
        log.info("agent %s traits: %s", id, traits)
        traits[0] = 100000   # easily recognizable value
        self.pop.set_agent_traits(id, traits)

        (new_id, new_traits) = self.pop.get_agent_by_id(id)
        log.info("post-save agent %s traits: %s", new_id, new_traits)



if __name__ == "__main__":
    unittest.main()