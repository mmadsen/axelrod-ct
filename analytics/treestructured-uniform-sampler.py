#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import logging as log
import argparse
import itertools
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data
import csv
import random
import ming
from bson import ObjectId




def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment", required=True)
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)
    parser.add_argument("--filename", help="path to file for export", required=True)


    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

    if args.debug == '1':
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    log.debug("experiment name: %s", args.experiment)

    #### main program ####

    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)



def main():

    fieldnames = data.axelrod_run_treestructured.columns_to_export_for_analysis()
    orig_fields = fieldnames[:]
    fieldnames.extend(["cultureid", "culture_count", "mean_radii", "sd_radii",
                       "orbit_number", "autgroupsize", "remaining_density",
                       "mean_degree", "sd_degree",
                       "mean_orbit_multiplicity", "sd_orbit_multiplicity",
                       "max_orbit_multiplicity","order", "msg_lambda", "msg_beta", "mem_beta"])
    ofile  = open(args.filename, "wb")
    writer = csv.DictWriter(ofile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL)

    headers = dict((n,n) for n in fieldnames)
    writer.writerow(headers)


    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring TreeStructured Axelrod model with structure class: %s", structure_class_name)




    basic_config = utils.TreeStructuredConfiguration(args.configuration)

    if basic_config.INTERACTION_RULE_CLASS == 'madsenlab.axelrod.rules.MultipleTreePrerequisitesLearningCopyingRule':
        state_space = [
            basic_config.POPULATION_SIZES_STUDIED,
            basic_config.TRAIT_LEARNING_RATE,
            basic_config.MAXIMUM_INITIAL_TRAITS,
            basic_config.NUM_TRAIT_TREES,
            basic_config.TREE_BRANCHING_FACTOR,
            basic_config.TREE_DEPTH_FACTOR,
            basic_config.TRAIT_LOSS_RATE,
            basic_config.INNOVATION_RATE,
        ]
    else:
        log.error("This analytics calss not compatible with rule class: %s", basic_config.INTERACTION_RULE_CLASS)
        exit(1)


    if basic_config.NETWORK_FACTORY_CLASS == 'madsenlab.axelrod.population.WattsStrogatzSmallWorldFactory':
        state_space.append(basic_config.WS_REWIRING_FACTOR)

    num_samples = basic_config.REPLICATIONS_PER_PARAM_SET

    fieldnames = data.axelrod_run_treestructured.columns_to_export_for_analysis()
    orig_fields = fieldnames[:]
    fieldnames.extend(["cultureid", "culture_count", "mean_radii", "sd_radii",
                       "orbit_number", "autgroupsize", "remaining_density",
                       "mean_degree", "sd_degree",
                       "mean_orbit_multiplicity", "sd_orbit_multiplicity",
                       "max_orbit_multiplicity","order", "msg_lambda", "msg_beta", "mem_beta"])
    ofile  = open(args.filename, "wb")
    writer = csv.DictWriter(ofile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL)

    headers = dict((n,n) for n in fieldnames)
    writer.writerow(headers)


    # The basic idea here is that we run through all parameter combinations
    # and for each one, we:
    #
    # 1.  Find all simulation_run_id's in the database with that parameter combination
    # 2.  Sample n = REPLICATIONS_PER_PARAM_SET from the sim run id list
    # 3.  For each of the sampled simulation run ID's:
    # 4.      Get all records for that simulation run ID from the database
    # 5.      Write those records to CSV
    #
    # The end result of this procedure should be a constant number of simulation run ID's per parameter set
    # This will not result in a constant number of ROWS, however, because a simulation run will have multiple
    # samples, and each of those samples may result in a different number of culture region solutions, each
    # of which will contribute a row to the result.


    for param_combination in itertools.product(*state_space):
            popsize = int(param_combination[0])
            lrate = float(param_combination[1])
            maxtraits = int(param_combination[2])
            num_trees = int(param_combination[3])
            branching_factor = float(param_combination[4])
            depth_factor = float(param_combination[5])
            loss_rate = float(param_combination[6])
            innov_rate = float(param_combination[7])

            # Find all simulation ID's with the combination of params...
            res = data.AxelrodStatsTreestructured.m.find(dict(population_size=popsize,
                                                        learning_rate=lrate,
                                                        max_init_traits=maxtraits,
                                                        num_trait_trees=num_trees,
                                                        branching_factor=branching_factor,
                                                        depth_factor=depth_factor,
                                                        loss_rate=loss_rate,
                                                        innovation_rate=innov_rate),
                                                         dict(simulation_run_id=1)).all()
            simruns = set([run.simulation_run_id for run in [x for x in res ]])

            if len(simruns) < num_samples:
                sample_simruns = simruns
                log.info("pc only has %s rows: LR: %s NT: %s BF: %s DF: %s IR: %s", len(simruns),
                         lrate, num_trees, branching_factor, depth_factor, innov_rate)
            else:
                sample_simruns = set(random.sample(simruns, num_samples))

            log.debug("num ids for param combo: %s ", len(simruns))
            id_count = 0
            for simid in sample_simruns:
                id_count += 1
                cursor = data.AxelrodStatsTreestructured.m.find(dict(simulation_run_id=simid))
                for sample in cursor:
                    row = dict()
                    for field in sorted(orig_fields):

                        row[field] = sample[field]

                    # now pull apart the trait graph list - producing a row for each element of the trait graph list
                    tg_stats = sample['trait_graph_stats']
                    for tg in tg_stats:
                        #log.info("tg: %s", tg)
                        row['cultureid'] = tg['cultureid']
                        row['culture_count'] = tg['culture_count']
                        row['mean_radii'] = tg['mean_radii']
                        row['sd_radii'] = tg['sd_radii']
                        row['mean_degree'] = tg['mean_degree']
                        row['sd_degree'] = tg['sd_degree']
                        row['orbit_number'] = tg['orbit_number']
                        row['autgroupsize'] = tg['autgroupsize']
                        row['remaining_density'] = tg['remaining_density']
                        row['mean_orbit_multiplicity'] = tg['mean_orbit_multiplicity']
                        row['sd_orbit_multiplicity'] = tg['sd_orbit_multiplicity']
                        row['max_orbit_multiplicity'] = tg['max_orbit_multiplicity']
                        row['order'] = tg['order']
                        row['msg_lambda'] = tg['msg_lambda']
                        row['msg_beta'] = tg['msg_beta']
                        row['mem_beta'] = tg['mem_beta']


                        #log.info("row: %s", row)
                        writer.writerow(row)

            log.debug("sampled %s rows from param combo", id_count)


if __name__ == "__main__":
    setup()
    main()


