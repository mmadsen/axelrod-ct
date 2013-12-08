#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log


def check_liveness(ax, model, args, simconfig, timestep):
    diff = timestep - model.get_time_last_interaction()
    num_links = model.model.number_of_edges()

    if (diff > (5 * num_links)):
        #log.debug("No interactions have occurred since %s - for %s ticks, which is 5 * %s network edges", model.get_time_last_interaction(), diff, num_links)
        if ax.get_fraction_links_active() == 0.0:
            log.debug("No active links found in the model, clear to finalize")
            return False
        else:
            return True
    else:
        return True




