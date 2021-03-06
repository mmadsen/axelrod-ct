#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import base_population_classes as b
import logging as log
import math as m
import networkx as nx


class WattsStrogatzSmallWorldFactory(object):
    """
    Defines a population of agents, each of which is represented by an array of integers.
    Position in the array represents the locus or feature, and the integer at the array
    position represents the trait at that feature.

    Agents in this model are positioned at the nodes of a square lattice, given by
    a NetworkX graph generated by the regular grid generator.

    The SquareLatticeFixedTraitModel has, by default, periodic boundary conditions (thus, the lattice is
    a torus), but this can be overridden in configuration.


    This factory is dynamically loaded from its fully qualified name in a configuration file,
     and passed the simulation configuration object in its constructor.  The instantiating
     code then calls get_graph()

    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.lattice_dimension = 0
        self.lattice_coordination_number = 4
        self.rewiring = self.simconfig.ws_rewiring

    def get_lattice_coordination_number(self):
        return self.lattice_coordination_number


    def get_graph(self):

        log.debug("Constructing Watts-Strogatz SW lattice with k=%s and rewiring %s", self.lattice_coordination_number, self.rewiring)
        graph = nx.connected_watts_strogatz_graph(self.simconfig.popsize, self.lattice_coordination_number, self.rewiring)

        # now convert the resulting graph to have simple nodenames to use as keys
        # We need to retain the original nodenames, because they're tuples which represent the position
        # of the node in the lattice.  So we first store them as attribution 'pos' and then convert
        for nodename in graph.nodes():
            graph.node[nodename]['pos'] = nodename

        g = nx.convert_node_labels_to_integers(graph)
        return g








