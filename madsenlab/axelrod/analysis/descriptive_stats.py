#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log
from collections import defaultdict
import numpy as np
import math as m
import pprint as pp

def get_culture_count_map(pop):
    counts = defaultdict(int)
    graph = pop.agentgraph
    for nodename in graph.nodes():
        traits = graph.node[nodename]['traits']
        culture = pop.get_traits_packed(traits)
        counts[culture] += 1
    return counts

def get_culture_counts_dbformat(pop):
    """
    Takes an instance of a "population" and counts the distinct trait lists (i.e., cultures in the
    Axelrod model sense) in the population.  Cultures are represented by packing the feature/trait list
    into an integer which serves as an identifier for a unique combination of features and traits.

    The return value is a dict of culture id, count.
    """
    counts = defaultdict(int)
    graph = pop.agentgraph
    for nodename in graph.nodes():
        traits = graph.node[nodename]['traits']
        culture = pop.get_traits_packed(traits)
        counts[culture] += 1

    # transform into the list of dicts that's more convenient to stuff into mongodb
    stored_counts = []
    for key,val in counts.items():
        stored_counts.append(dict(cultureid=str(key),count=val))
    #log.debug("counts: %s", stored_counts)
    return stored_counts


def get_num_traits_per_individual_stats(pop):
    """
    Takes an instance of a population and returns a tuple with the mean and standard deviation of the
    number of traits per individual.  Only useful for the extensible and semantic models.

    """
    sizes = []
    for nodename in pop.agentgraph.nodes():
        sizes.append(len(pop.agentgraph.node[nodename]['traits']))
    mean = np.mean(np.asarray(sizes))
    sd = m.sqrt(np.var(np.asarray(sizes)))
    return (mean, sd)



def diversity_shannon_entropy(freq_list):
    k = len(freq_list)
    sw = 0.0
    for i in range(0, k):
        sw += freq_list[i] * m.log(freq_list[i])
    if sw == 0:
        return 0.0
    else:
        return sw * -1.0


def diversity_iqv(freq_list):
    k = len(freq_list)

    if k <= 1:
        return 0.0

    isum = 1.0 - _sum_squares(freq_list)
    factor = float(k) / (float(k) - 1.0)
    iqv = factor * isum

    #logger.debug("k: %s  isum: %s  factor: %s  iqv:  %s", k, isum, factor, iqv)
    return iqv


def _sum_squares(freq_list):
    ss = 0.0
    for p in freq_list:
        ss += p ** 2.0
    return ss


class PopulationTraitFrequencyAnalyzer(object):
    """
    Analyzer for trait frequencies across the entire population.  At each
    call to calculate_trait_frequencies(), the analyzer looks at the state
    of the agent population and stores frequencies.  Subsequent calls to
    get methods will return frequencies, richness, or the Shannon entropy
    measure of evenness for the frequencies.

    To use this over time, call calculate_trait_frequencies() when you
    want a sample, and then the various get_* methods to return the
    desired metrics.

    """

    def __init__(self, model):
        self.model = model
        self.total_traits = model.agentgraph.number_of_nodes()

    def get_trait_frequencies(self):
        return self.freq

    def get_trait_richness(self):
        """
        Returns the number of traits with non-zero frequencies
        """
        return len( [freq for freq in self.freq.values() if freq > 0] )

    def get_trait_evenness_entropy(self):
        return diversity_shannon_entropy(self.freq.values())


    def calculate_trait_frequencies(self):
        self.freq = None
        trait_counts = defaultdict(int)

        total = self.model.agentgraph.number_of_nodes()

        for agent_id in self.model.agentgraph.nodes():
            agent_traits = self.model.agentgraph.node[agent_id]['traits']
            for trait in agent_traits:
                trait_counts[trait] += 1

        #log.debug("counts: %s", pp.pformat(trait_counts))

        self.freq = {k : float(v)/float(total) for k,v in trait_counts.items()}
        #log.debug("freq: %s", pp.pformat(self.freq))


