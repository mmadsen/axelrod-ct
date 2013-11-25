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


class SquareLatticeFactory(object):
    """
    Defines a population of agents, each of which is represented by an array of integers.
    Position in the array represents the locus or feature, and the integer at the array
    position represents the trait at that feature.

    Agents in this model are positioned at the nodes of a square lattice, given by
    a NetworkX graph generated by the regular grid generator.

    The SquareLatticeFixedTraitModel has, by default, periodic boundary conditions (thus, the lattice is
    a torus), but this can be overridden in configuration.

    Inherits generic methods for

    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.lattice_dimension = 0
        self.lattice_coordination_number = 4

    def get_lattice_coordination_number(self):
        return self.lattice_coordination_number

    def get_graph(self):
        lattice_coord_num = 4
        side_length = 0

        # The lattice size should be a perfect square, ideally, and is sqrt(population size)
        l = m.sqrt(self.simconfig.popsize)
        # get the fractional part of the result, because sqrt always returns a float, even if the number is technically an integer
        # so we have to test the fractional part, not check python types
        frac, integral = m.modf(l)
        if frac == 0.0:
            log.debug("Lattice model:  popsize %s, lattice will be %s by %s", self.simconfig.popsize, l, l)
            side_length = int(l)
        else:
            log.error("Lattice model: population size %s is not a perfect square", self.simconfig.popsize)
            exit(1)

        if self.simconfig.periodic == 1:
            p = True
            log.debug("periodic boundary condition selected")
        else:
            p = False

        model = nx.grid_2d_graph(side_length, side_length, periodic=p)
        # now convert the resulting graph to have simple nodenames to use as keys
        # We need to retain the original nodenames, because they're tuples which represent the position
        # of the node in the lattice.  So we first store them as attribution 'pos' and then convert
        for nodename in model.nodes():
            model.node[nodename]['pos'] = nodename

        g = nx.convert_node_labels_to_integers(model)
        return g








