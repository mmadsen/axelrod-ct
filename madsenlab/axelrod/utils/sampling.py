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
    trait_spectrum = trait_analyzer.get_trait_spectrum()

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
                                      trait_spectrum,
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
    radii = []

    symstats = stats.BalancedTreeAutomorphismStatistics(simconfig)
    subgraph_set = model.trait_universe.get_trait_graph_components(traitset)
    trait_subgraph = model.trait_universe.get_trait_forest_from_traits(traitset)
    results = symstats.calculate_graph_symmetries(trait_subgraph)

    for subgraph in subgraph_set:
        radii.append( nx.radius(subgraph))

    mean_radii = np.mean(np.asarray(radii))
    sd_radii = np.sqrt(np.var(np.asarray(radii)))
    degrees = nx.degree(trait_subgraph).values()
    mean_degree = np.mean(np.asarray(degrees))
    sd_degree = np.sqrt(np.var(np.asarray(degrees)))
    mean_orbit_mult = np.mean(np.asarray(results['orbitcounts']))
    sd_orbit_mult = np.sqrt(np.var(np.asarray(results['orbitcounts'])))
    max_orbit_mult = np.nanmax(np.asarray(results['orbitcounts']))

    r = dict(cultureid=str(cultureid), culture_count=culture_count_map[cultureid],
             orbit_multiplicities=results['orbitcounts'],
             orbit_number=results['orbits'],
             autgroupsize=results['groupsize'],
             remaining_density=results['remainingdensity'],
             mean_radii=mean_radii,
             sd_radii=sd_radii,
             mean_degree=mean_degree,
             sd_degree=sd_degree,
             mean_orbit_multiplicity=mean_orbit_mult,
             sd_orbit_multiplicity=sd_orbit_mult,
             max_orbit_multiplicity=max_orbit_mult
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




