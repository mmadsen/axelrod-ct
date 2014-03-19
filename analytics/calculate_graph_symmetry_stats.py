#!/usr/bin/env python

# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

import ming

import logging as log
import argparse
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data
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


    args = parser.parse_args()


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

    # get all simulation run id's
    num_processed = 0
    row_cursor = data.AxelrodStatsTreestructured.m.find()
    for row in row_cursor:
        row_id = row["_id"]

        trait_graph_stats_list = row["trait_graph_stats"]

        tgs_out = []

        for tgs in trait_graph_stats_list:
            # first calculate the number of remaining vertices in the forest and store it
            o_mult = tgs["orbit_multiplicities"]
            order = np.sum(np.asarray(o_mult))

            # calculate the size of the automorphism group relative to Kn (as a reference)
            autgroupsize = tgs['autgroupsize']
            size_sn = spm.factorial(order)
            ratio = float(autgroupsize) / float(size_sn)
            frac_order = float(1) / float(order)
            beta_g = np.power(ratio,frac_order)

            # calculate the fraction of vertices that belong to nontrivial orbits
            nontrivial_mult = [ mult for mult in o_mult if mult > 1 ]
            lambda_g = float(len(nontrivial_mult)) / float(order)

            tgs["order"] = order
            tgs["msg_beta"] = beta_g
            tgs["msg_lambda"] = lambda_g

            log.debug("order: %s  msg_lambda: %s  msg_beta: %s", order, lambda_g, beta_g)

            tgs_out.append(tgs)

            num_processed += 1

        #log.debug("tgs: %s", tgs_out)
        data.updateFieldAxelrodStatsTreestructured(row_id, "trait_graph_stats", tgs_out)

    log.info("COMPLETE:  %s rows processed for additional graph symmetry statistics", num_processed)



