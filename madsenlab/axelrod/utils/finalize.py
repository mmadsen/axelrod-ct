#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
from madsenlab.axelrod import analysis as stats
import madsenlab.axelrod.data as data
import logging as log

def finalize_axelrod_model(model,args,simconfig):
    counts = stats.get_culture_counts(model)
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

def finalize_extensible_model(model, args, simconfig):
    counts = stats.get_culture_counts(model)
    (mean_traits,sd_traits) = stats.get_culture_size_statistics(model)
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


