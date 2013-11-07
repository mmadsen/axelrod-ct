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


class GraphModel:

    def initialize_population(self):
        """
        Given a graph and a simulation configuration, this method constructs
        an initial random population given the configuration for number of features
        and traits.
        """
        nf = self.simconfig.num_features
        nt = self.simconfig.num_traits
        for nodename in self.model.nodes():
            self.model.node[nodename]['traits'] = np.random.random_integers(0, nt - 1, size=nf)

    def get_agent_by_id(self, agent_id):
        return (agent_id, self.model.node[agent_id]['traits'])

    def get_random_agent(self):
        """
        Returns a random agent chosen from the population, in the form of a tuple of two elements
        (node_id, array_of_traits).  This allows operations on the agent and its traits without additional calls.

        To modify the traits, change one or more elements in the array, and then call set_agent_traits(agent_id, new_list)
        """
        rand_agent_id = np.random.randint(0, self.simconfig.popsize)
        return self.get_agent_by_id(rand_agent_id)

    def set_agent_traits(self, agent_id, trait_list):
        """
        Stores a modified version of the trait list for an agent.
        """
        self.model.node[agent_id]['traits'] = trait_list

    def get_random_neighbor_for_agent(self, agent_id):
        """
        Returns a random agent chosen from among the neighbors of agent_id.  The format is the same as
        get_random_agent -- a two element tuple with the neighbor's ID and their trait list.
        """
        neighbor_list = self.model.neighbors(agent_id)
        num_neighbors = len(neighbor_list)
        rand_neighbor_id = neighbor_list[np.random.randint(0,num_neighbors)]
        trait_list = self.model.node[rand_neighbor_id]['traits']
        return self.get_agent_by_id(rand_neighbor_id)