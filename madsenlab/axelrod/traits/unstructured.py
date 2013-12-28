#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import networkx as nx
from numpy.random import RandomState
import logging as log

class ExtensibleTraitFactory(object):
    """
    In the "extensible" model, agents have no "loci" but are capable of carrying any number
    of traits (alternatively, it's a single locus model with multiple occupancy).  Individuals
    are initialized by selecting a random block of integers of random size, between 1 and
    the "initial maximum traits" value, where the specific integers are chosen between 0 and
    a maximum trait value variable, set in configuration.  The resulting block of integers
    is given as a Python set object, which is stored as an agent's initial trait set.

    This factory is dynamically loaded from its fully qualified name in a configuration file,
     and passed the simulation configuration object in its constructor.  The instantiating
     code then calls initialize_population(graph), passing it a NetworkX graph of nodes, previously
     constructed.

    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.prng = self.simconfig.prng  # allow the library to choose a seed via OS specific mechanism

    def initialize_population(self,graph):
        mt = self.simconfig.maxtraits
        mv = self.simconfig.max_trait_value
        log.debug("max trait value: %s", mv)
        for nodename in graph.nodes():
            # get a random number of initial traits between 1 and mt
            trait_set = set()
            init_trait_num = self.prng.random_integers(1, mt)

            for i in range(0, init_trait_num):
                trait = self.prng.random_integers(0, mv)
                trait_set.add(trait)

            #log.debug("traits: %s", pp.pformat(trait_set))
            graph.node[nodename]['traits'] = trait_set



class AxelrodTraitFactory(object):
    """
    In the original Axelrod model, agents have F loci and T possible traits per locus.
    Individuals are initialized with a list of F random integers, each chosen from 0 to T-1.
    The result is given as a Python list, and stored as the individual's initial trait set.


    This factory is dynamically loaded from its fully qualified name in a configuration file,
     and passed the simulation configuration object in its constructor.  The instantiating
     code then calls initialize_population(graph), passing it a NetworkX graph of nodes, previously
     constructed
    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.prng = RandomState()  # allow the library to choose a seed via OS specific mechanism

    def initialize_population(self,graph):
        nf = self.simconfig.num_features
        nt = self.simconfig.num_traits
        for nodename in graph.nodes():
            graph.node[nodename]['traits'] = self.prng.randint(0, nt, size=nf)


