#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import base as b
import logging as log
import math as m
import networkx as nx


class SquareLatticeModel(b.GraphModel):
    """
    Defines a population of agents, each of which is represented by an array of integers.
    Position in the array represents the locus or feature, and the integer at the array
    position represents the trait at that feature.

    Agents in this model are positioned at the nodes of a square lattice, given by
    a NetworkX graph generated by the regular grid generator.

    The SquareLatticeModel has, by default, periodic boundary conditions (thus, the lattice is
    a torus), but this can be overridden in configuration.

    Inherits generic methods for

    """

    def __init__(self, simconfig):

        super(SquareLatticeModel, self).__init__()

        self.simconfig = simconfig
        self.lattice_dimension = 0


        # The lattice size should be a perfect square, ideally, and is sqrt(population size)
        l = m.sqrt(self.simconfig.popsize)
        # get the fractional part of the result, because sqrt always returns a float, even if the number is technically an integer
        # so we have to test the fractional part, not check python types
        frac, integral = m.modf(l)
        if frac == 0.0:
            log.info("Lattice model:  popsize %s, lattice will be %s by %s", simconfig.popsize, l, l)
            self.lattice_dimension = int(l)
        else:
            log.error("Lattice model: population size %s is not a perfect square", simconfig.popsize)
            exit(1)

        self.model = nx.grid_2d_graph(self.lattice_dimension, self.lattice_dimension, periodic=False)
        # now convert the resulting graph to have simple nodenames to use as keys
        g = nx.convert_node_labels_to_integers(self.model)
        self.model = g








