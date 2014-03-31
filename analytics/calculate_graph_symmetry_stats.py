#!/usr/bin/env python

# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

import ming

import logging as log
import argparse
import madsenlab.axelrod.analysis as maa
import madsenlab.axelrod.data as data
import madsenlab.axelrod.utils as utils
import numpy as np
import scipy.misc as spm




## setup

def setup():
    global args, config, simconfig
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="provide name for experiment, to be used as prefix for database collections")
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--dryrun", help="Do the calculations but do not change the database (handiest with --debug 1 to see the results", action="store_true")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)

    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)


    if int(args.debug) == 1:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')


    #### main program ####
    log.info("CALCULATING GRAPH SYMMETRY STATS - Experiment: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)



if __name__ == "__main__":
    setup()

    # cache the values of the total automorphism group for a balanced forest, so we can avoid
    # calling nauty for each row once the cache is primed.
    forest_cache = dict()






    # get all simulation run id's
    num_processed = 0
    row_cursor = data.AxelrodStatsTreestructured.m.find()
    for row in row_cursor:
        row_id = row["_id"]

        r = row['branching_factor']
        h = row['depth_factor']
        n = row['num_trait_trees']

        t = (r,h,n)
        if t in forest_cache:
            forest_order = forest_cache[t]
        else:
            simconfig.branching_factor =  r
            simconfig.depth_factor = h
            simconfig.num_trees = n

            # hack - nauty takes *forever* to calculate the automorphism group size of a really large group
            #        so I did it once and we're caching the results.  r=6, h=6 is too big, nauty core dumps.
            manual = False
            if r == 4 and h == 6:
                forest_order = 4338.043478424945794
                manual = True
            elif r == 6 and h == 4:
                forest_order = 1704.026063910616259
                manual = True
            elif r == 6 and h == 6:
                forest_order = float("inf")
                manual = True
            else:
                sym = maa.BalancedTreeAutomorphismStatistics(simconfig)
                (forest,roots) = utils.generate_forest_balanced_trees(r,h,1)
                log.debug("asking nauty for the aut group size for r=%s, h=%s", r, h)
                res = sym.calculate_graph_symmetries(forest)
                forest_order = res["groupsize"]

            forest_cache[t] = forest_order

        trait_graph_stats_list = row["trait_graph_stats"]

        tgs_out = []

        for tgs in trait_graph_stats_list:
            # first calculate the number of remaining vertices in the forest and store it
            o_mult = tgs["orbit_multiplicities"]
            order = np.sum(np.asarray(o_mult))

            # calculate the size of the automorphism group relative to Kn (as a reference), and
            # relative to order N corolla (maximally symmetric tree)
            autgroupsize = tgs['autgroupsize']

            beta_g = maa.ratio_order_automorphism_to_symmetric_group(autgroupsize,order)
            if manual == False:
                beta_f = maa.ratio_log_order_automorphism_to_order_balanced_forest(autgroupsize,forest_order,n,order)
            else:
                beta_f = maa.ratio_log_order_automorphism_to_order_balanced_forest_large_forest(autgroupsize,forest_order,n,order)

            # calculate the fraction of vertices that belong to nontrivial orbits
            nontrivial_mult = [ mult for mult in o_mult if mult > 1 ]
            lambda_g = float(len(nontrivial_mult)) / float(order)

            tgs["order"] = order
            tgs["msg_beta"] = beta_g
            tgs["msg_lambda"] = lambda_g
            tgs["mem_beta"] = beta_f

            log.debug("order: %s  msg_lambda: %s  msg_beta: %s mem_beta: %s",
                      order, lambda_g, beta_g, beta_f)

            tgs_out.append(tgs)

            num_processed += 1

        #log.debug("tgs: %s", tgs_out)
        if  args.dryrun == False:
            data.updateFieldAxelrodStatsTreestructured(row_id, "trait_graph_stats", tgs_out)

    log.info("COMPLETE:  %s rows processed for additional graph symmetry statistics", num_processed)



