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



class GraphModel(object):
    """
    Base class for all Axelrod models.  Specifies no specific graph, lattice, or network model,
    but defines operations usable on any specific model as long as the graph is represented by the
    NetworkX library and API.  Agents are given by nodes, and edges define "neighbors".

    Important operations on a model include choosing a random agent, finding a random neighbor,
    updating an agent's traits, and updating statistics such as the time the last interaction occurred
    (which is used to know when (or if) we've reached a fully absorbing state and can stop.

    Subclasses should ONLY implement an __init__ method, in which self.model is assigned an
    instance of a
    """

    def __init__(self):
        self.interactions = 0
        self.time_step_last_interaction = 0
        self.prng = RandomState()  # allow the library to choose a seed via OS specific mechanism


    # TODO:  initialization needs to be refactored before doing the structured model, so we can reuse the structure and part of the rules, but change the "traits"

    def draw_network_colored_by_culture(self):
        nodes, colors = zip(*nx.get_node_attributes(self.model, 'traits').items())
        nodes, pos = zip(*nx.get_node_attributes(self.model, 'pos').items())
        color_tupled_compressed = [int(''.join(str(i) for i in t)) for t in colors]
        nx.draw(self.model, pos=pos, nodelist=nodes, node_color=color_tupled_compressed)
        plt.show()

    def get_traits_packed(self,agent_traits):
        return ''.join(str(i) for i in agent_traits)

    def initialize_population(self):
        """
        Given a graph and a simulation configuration, this method constructs
        an initial random population given the configuration for number of features
        and traits.
        """
        nf = self.simconfig.num_features
        nt = self.simconfig.num_traits
        for nodename in self.model.nodes():
            self.model.node[nodename]['traits'] = self.prng.randint(0, nt, size=nf)

        #self.draw_network_colored_by_culture()

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

    def set_agent_traits(self, agent_id, trait_list):
        """
        Stores a modified version of the trait list for an agent.
        """
        #old_traits = self.model.node[agent_id]['traits']
        self.model.node[agent_id]['traits'] = trait_list
        #new_traits = self.model.node[agent_id]['traits']
        #log.debug("setting agent %s: target traits: %s  old: %s new: %s", agent_id, trait_list, old_traits, new_traits)

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


    def update_interactions(self, timestep):
        self.interactions += 1
        self.time_step_last_interaction = timestep

    def get_time_last_interaction(self):
        return self.time_step_last_interaction

    def get_interactions(self):
        return self.interactions