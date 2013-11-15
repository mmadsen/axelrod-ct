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

def check_liveness(ax, model, args, simconfig, timestep):
    diff = timestep - model.get_time_last_interaction()
    num_links = model.model.number_of_edges()

    if (diff > (5 * num_links)):
        log.debug("No interactions have occurred for %s ticks, which is 5 * %s network edges", diff, num_links)
        if ax.get_fraction_links_active() == 0.0:
            log.debug("No active links found in the model, finalizing")
            finalize_model(model, simconfig)
            if args.diagram == True:
                model.draw_network_colored_by_culture()
            return False
        else:
            True
    else:
        True


def finalize_model(model,simconfig):
    counts = stats.get_culture_counts(model)
    data.store_stats_axelrod_original(simconfig.popsize,None,simconfig.sim_id,simconfig.num_features,simconfig.num_traits,simconfig.script,len(counts),model.get_time_last_interaction(),counts)

