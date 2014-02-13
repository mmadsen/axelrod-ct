#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
import madsenlab.axelrod.analysis as stats
import madsenlab.axelrod.data as data
import logging as log
import pprint as pp
import numpy as np
import math as m
import networkx as nx

def sample_axelrod_model(model,args,simconfig):
    counts = stats.get_culture_counts_dbformat(model)
    klemm = stats.klemm_normalized_L_axelrod(model,simconfig)
    data.store_stats_axelrod_original(simconfig.popsize,
                                      simconfig.sim_id,
                                      simconfig.num_features,
                                      simconfig.num_traits,
                                      simconfig.drift_rate,
                                      simconfig.INTERACTION_RULE_CLASS,
                                      simconfig.POPULATION_STRUCTURE_CLASS,
                                      simconfig.script,
                                      len(counts),
                                      model.get_time_last_interaction(),
                                      counts,
                                      klemm)
    if args.diagram == True:
        model.draw_network_colored_by_culture()

def sample_extensible_model(model, args, simconfig):
    counts = stats.get_culture_counts_dbformat(model)
    (mean_traits,sd_traits) = stats.get_num_traits_per_individual_stats(model)
    log.debug("culture size - mean: %s sd: %s", mean_traits, sd_traits)
    klemm = stats.klemm_normalized_L_extensible(model, simconfig)
    data.store_stats_axelrod_extensible(simconfig.popsize,
                                      simconfig.sim_id,
                                      simconfig.maxtraits,
                                      simconfig.add_rate,
                                      simconfig.drift_rate,
                                      simconfig.INTERACTION_RULE_CLASS,
                                      simconfig.POPULATION_STRUCTURE_CLASS,
                                      simconfig.script,
                                      len(counts),
                                      model.get_time_last_interaction(),
                                      counts,
                                      klemm,
                                      mean_traits,
                                      sd_traits)
    if args.diagram == True:
        model.draw_network_colored_by_culture()


def sample_treestructured_model(model, args, simconfig, finalized):
    log.debug("sampling tree structured model")
    trait_analyzer = stats.PopulationTraitFrequencyAnalyzer(model)
    trait_analyzer.calculate_trait_frequencies()

    culture_counts_dbformat = stats.get_culture_counts_dbformat(model)
    culture_count_map = stats.get_culture_count_map(model)
    (mean_traits,sd_traits) = stats.get_num_traits_per_individual_stats(model)
    #log.debug("culture size - mean: %s sd: %s", mean_traits, sd_traits)
    klemm = stats.klemm_normalized_L_extensible(model, simconfig)

    graphml_blobs = []
    trait_tree_stats = []
    traitset_map = get_traitset_map(model)
    for culture, traits in traitset_map.items():
        g = dict(cultureid=str(culture), content=model.trait_universe.get_graphml_for_culture(traits))
        if simconfig.save_graphs == True:
            graphml_blobs.append(g)
        trait_tree_stats.append( get_tree_symmetries_for_traitset(model, simconfig, culture, traits, culture_count_map))


    #log.debug("graphml: %s", pp.pformat(graphml_blobs))

    sample_time = model.get_time_last_interaction()
    if finalized == 1:
        convergence_time = model.get_time_last_interaction()
    else:
        convergence_time = 0

    # Not recording the entropy yet, it doesn't mean anything given the way frequencies work.

    data.store_stats_axelrod_treestructured(simconfig.popsize,
                                      simconfig.sim_id,
                                      simconfig.maxtraits,
                                      simconfig.learning_rate,
                                      simconfig.loss_rate,
                                      simconfig.innov_rate,
                                      simconfig.num_trees,
                                      simconfig.branching_factor,
                                      simconfig.depth_factor,
                                      simconfig.INTERACTION_RULE_CLASS,
                                      simconfig.POPULATION_STRUCTURE_CLASS,
                                      simconfig.NETWORK_FACTORY_CLASS,
                                      simconfig.script,
                                      len(culture_counts_dbformat),
                                      convergence_time,
                                      sample_time,
                                      culture_counts_dbformat,
                                      klemm,
                                      mean_traits,
                                      sd_traits,
                                      graphml_blobs,
                                      trait_tree_stats,
                                      trait_analyzer.get_trait_richness(),
                                      None,
                                      finalized,
                                      simconfig.ws_rewiring)

    if args.diagram == True and finalized == 1:
        for culture, traits in traitset_map.items():
            model.trait_universe.draw_trait_network_for_culture(culture, traits)




def get_tree_symmetries_for_traitset(model, simconfig, cultureid, traitset, culture_count_map):
    order = []
    groupsizes = []
    densities = []
    radii = []
    mean_degree = []

    symstats = stats.BalancedTreeAutomorphismStatistics(simconfig)
    subgraph_set = model.trait_universe.get_trait_graph_components(traitset)
    for subgraph in subgraph_set:
        results = symstats.calculate_graph_symmetries(subgraph)
        order.append( results['orbits'])
        groupsizes.append( results[ 'groupsize'])
        densities.append( results['remainingdensity'])
        radii.append( results['radius'])
        mean_degree.append( np.mean(np.asarray(nx.degree(subgraph).values())))

    mean_orbit = np.mean(np.asarray(order))
    sd_orbit = m.sqrt(np.var(np.asarray(order)))
    mean_groupsize = np.mean(np.asarray(groupsizes))
    sd_groupsize = m.sqrt(np.var(np.asarray(groupsizes)))
    mean_densities = np.mean(np.asarray(densities))
    sd_densities = np.sqrt(np.var(np.asarray(densities)))
    mean_radii = np.mean(np.asarray(radii))
    sd_radii = np.sqrt(np.var(np.asarray(radii)))
    mean_degree = np.mean(np.asarray(mean_degree))

    r = dict(cultureid=str(cultureid), culture_count=culture_count_map[cultureid], orbit_number=order, group_size=groupsizes,
             remaining_density=densities, mean_orbits=mean_orbit, sd_orbits=sd_orbit,
             mean_groupsize=mean_groupsize, sd_groupsize=sd_groupsize,mean_density=mean_densities,
             sd_density=sd_densities,mean_radii=mean_radii,sd_radii=sd_radii, mean_degree=mean_degree
             )
    #log.debug("groupstats: %s", r)
    return r


def get_traitset_map(pop):
    """
    Utility method which returns a map of culture ID's (hashes) and the trait set
     corresponding to a random individual of that culture (actually, the first one
     we encounter).
    """
    traitsets = {}
    graph = pop.agentgraph
    for nodename in graph.nodes():
        traits = graph.node[nodename]['traits']
        culture = pop.get_traits_packed(traits)
        if culture not in traitsets:
            traitsets[culture] = traits
    return traitsets




