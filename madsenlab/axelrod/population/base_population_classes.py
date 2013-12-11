#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log
import networkx as nx
import madsenlab.axelrod.utils.configuration
import numpy as np
import math as m
import pprint as pp
import matplotlib.pyplot as plt
from numpy.random import RandomState

###################################################################################

class BaseGraphPopulation(object):
    """
    Base class for all Axelrod model populations that use a graph (NetworkX) representation to
    store the relations between agents.  Methods here need to be independent of the trait representation,
    but can assume that the agents are nodes in a Graph.  Thus, most of the "agent selection" and
    "neighbor" methods are concentrated here.
    """

    def __init__(self,simconfig,graph_factory,trait_factory):
        self.simconfig = simconfig
        self.interactions = 0
        self.time_step_last_interaction = 0
        self.prng = RandomState()  # allow the library to choose a seed via OS specific mechanism
        self.graph_factory = graph_factory
        self.trait_factory = trait_factory

        # initialize the graph structure via the factory object
        self.model = self.graph_factory.get_graph()


    def get_agent_by_id(self, agent_id):
        return (agent_id, self.model.node[agent_id]['traits'])

    def get_random_agent(self):
        """
        Returns a random agent chosen from the population, in the form of a tuple of two elements
        (node_id, array_of_traits).  This allows operations on the agent and its traits without additional calls.

        To modify the traits, change one or more elements in the array, and then call set_agent_traits(agent_id, new_list)
        """
        rand_agent_id = self.prng.randint(0, self.simconfig.popsize)
        return self.get_agent_by_id(rand_agent_id)

    def get_random_neighbor_for_agent(self, agent_id):
        """
        Returns a random agent chosen from among the neighbors of agent_id.  The format is the same as
        get_random_agent -- a two element tuple with the neighbor's ID and their trait list.
        """
        neighbor_list = self.model.neighbors(agent_id)
        num_neighbors = len(neighbor_list)
        rand_neighbor_id = neighbor_list[self.prng.randint(0,num_neighbors)]
        trait_list = self.model.node[rand_neighbor_id]['traits']
        return self.get_agent_by_id(rand_neighbor_id)


    def get_coordination_number(self):
        return self.graph_factory.get_lattice_coordination_number()

    def update_interactions(self, timestep):
        self.interactions += 1
        self.time_step_last_interaction = timestep

    def get_time_last_interaction(self):
        return self.time_step_last_interaction

    def get_interactions(self):
        return self.interactions

    def initialize_population(self):
        self.trait_factory.initialize_population(self.model)

    ### Abstract methods - derived classes need to override
    def draw_network_colored_by_culture(self):
        raise NotImplementedError

    def get_traits_packed(self,agent_traits):
        raise NotImplementedError

    def set_agent_traits(self, agent_id, trait_list):
        raise NotImplementedError


###################################################################################

class TreeTraitStructurePopulation(BaseGraphPopulation):
    """
    Base class for all Axelrod models which feature a non-fixed number of features/traits per individual.
    """
    def __init__(self, simconfig,graph_factory,trait_factory):
        super(TreeTraitStructurePopulation, self).__init__(simconfig,graph_factory, trait_factory)


    def set_agent_traits(self, agent_id, trait_set):
        # TODO:  rewrite set traits for tree structured traits - or not?
        self.model.node[agent_id]['traits'] = trait_set

    def get_traits_packed(self,agent_traits):
        # TODO:  rewrite packed traits network for tree structured traits
        hashable_set = frozenset(agent_traits)
        return hash(hashable_set)

    def draw_network_colored_by_culture(self):
        # TODO:  rewrite draw network for tree structured traits
        nodes, traits = zip(*nx.get_node_attributes(self.model, 'traits').items())
        nodes, pos = zip(*nx.get_node_attributes(self.model, 'pos').items())
        color_tupled_compressed = [self.get_traits_packed(t) for t in traits]
        nx.draw(self.model, pos=pos, nodelist=nodes, node_color=color_tupled_compressed)
        plt.show()

    # EXPLICIT OVERRIDE OF BASE CLASS METHOD!

    def initialize_population(self):
        """
        For semantically structured traits, since the traits are not just random integers,
        we need to have a copy of the trait "universe" -- i.e., all possible traits and their
        relations.  So we initialize the trait universe first, and then allow the trait factory
        to initialize our starting population on the chosen population structure.
        """
        self.trait_universe = self.trait_factory.initialize_traits()
        self.trait_factory.initialize_population(self.model)




###################################################################################

class ExtensibleTraitStructurePopulation(BaseGraphPopulation):
    """
    Base class for all Axelrod models which feature a non-fixed number of features/traits per individual.
    """
    def __init__(self, simconfig,graph_factory,trait_factory):
        super(ExtensibleTraitStructurePopulation, self).__init__(simconfig,graph_factory, trait_factory)

    def set_agent_traits(self, agent_id, trait_set):
        self.model.node[agent_id]['traits'] = trait_set

    def get_traits_packed(self,agent_traits):
        hashable_set = frozenset(agent_traits)
        return hash(hashable_set)

    def draw_network_colored_by_culture(self):
        nodes, traits = zip(*nx.get_node_attributes(self.model, 'traits').items())
        nodes, pos = zip(*nx.get_node_attributes(self.model, 'pos').items())
        color_tupled_compressed = [self.get_traits_packed(t) for t in traits]
        nx.draw(self.model, pos=pos, nodelist=nodes, node_color=color_tupled_compressed)
        plt.show()



###################################################################################

class FixedTraitStructurePopulation(BaseGraphPopulation):
    """
    Base class for all Axelrod models with a fixed number of features and number of traits per feature.
    Specifies no specific graph, lattice, or network model,
    but defines operations usable on any specific model as long as the graph is represented by the
    NetworkX library and API.  Agents are given by nodes, and edges define "neighbors".

    Important operations on a model include choosing a random agent, finding a random neighbor,
    updating an agent's traits, and updating statistics such as the time the last interaction occurred
    (which is used to know when (or if) we've reached a fully absorbing state and can stop.

    Subclasses should ONLY implement an __init__ method, in which self.model is assigned an
    instance of a
    """

    def __init__(self, simconfig,graph_factory, trait_factory):
        super(FixedTraitStructurePopulation, self).__init__(simconfig, graph_factory, trait_factory)

    # TODO:  initialization needs to be refactored before doing the structured model, so we can reuse the structure and part of the rules, but change the "traits"

    def draw_network_colored_by_culture(self):
        nodes, colors = zip(*nx.get_node_attributes(self.model, 'traits').items())
        nodes, pos = zip(*nx.get_node_attributes(self.model, 'pos').items())
        color_tupled_compressed = [int(''.join(str(i) for i in t)) for t in colors]
        nx.draw(self.model, pos=pos, nodelist=nodes, node_color=color_tupled_compressed)
        plt.show()

    def get_traits_packed(self,agent_traits):
        return ''.join(str(i) for i in agent_traits)


    def set_agent_traits(self, agent_id, trait_list):
        """
        Stores a modified version of the trait list for an agent.
        """
        #old_traits = self.model.node[agent_id]['traits']
        self.model.node[agent_id]['traits'] = trait_list
        #new_traits = self.model.node[agent_id]['traits']
        #log.debug("setting agent %s: target traits: %s  old: %s new: %s", agent_id, trait_list, old_traits, new_traits)








