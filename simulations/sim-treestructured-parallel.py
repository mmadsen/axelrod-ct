#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import logging as log
import ming
import argparse
import time
import itertools
import copy
import os
import uuid
import pprint as pp
import multiprocessing as mp
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data
import madsenlab.axelrod.rules as rules



def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment", required=True)
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)
    parser.add_argument("--parallelism", help="Number of concurrent processes to run", default="4")
    parser.add_argument("--diagram", help="Draw a diagram when complete", default=False)

    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

    if args.debug == '1':
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    log.debug("experiment name: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)




def main():
    global work_queue, process_list
    process_list = []

    work_queue = mp.JoinableQueue()

    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring TreeStructured Axelrod model with structure class: %s", structure_class_name)



    create_queueing_process(work_queue, queue_simulations)
    time.sleep(1)
    create_processes(work_queue, run_simulation_worker)
    try:
        work_queue.join()
    except KeyboardInterrupt:
        log.info("simulations interrupted by ctrl-c")
        for proc in process_list:
            proc.terminate()
        exit(1)

# End of main


def create_queueing_process(queue, worker):
    process = mp.Process(target=worker, args=(queue, args))
    process.daemon = True
    process_list.append(process)
    process.start()


def create_processes(queue, worker):
    for i in range(0, int(args.parallelism)):
        process = mp.Process(target=worker, args=(queue, args))
        process.daemon = True
        process_list.append(process)
        process.start()


def queue_simulations(queue, args):
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
        log.error("This parallel sim runner not compatible with rule class: %s", basic_config.INTERACTION_RULE_CLASS)
        exit(1)

    for param_combination in itertools.product(*state_space):
        # for each parameter combination, make a copy of the base configuration
        # set the specific param combo values, and queue the object
        for repl in range(0, basic_config.REPLICATIONS_PER_PARAM_SET):
            #log.debug("param combination: %s", param_combination)
            sc = copy.deepcopy(basic_config)
            sc.popsize = int(param_combination[0])
            sc.add_rate = float(param_combination[1])
            sc.maxtraits = int(param_combination[2])
            sc.num_trees = int(param_combination[3])
            sc.branching_factor = float(param_combination[4])
            sc.depth_factor = float(param_combination[5])
            sc.loss_rate = float(param_combination[6])
            sc.innov_rate = float(param_combination[7])
            sc.sim_id = uuid.uuid4().urn
            sc.script = __file__
            sc.periodic = 0

            queue.put(sc)


    log.info("All simulation configurations queued")



def run_simulation_worker(queue, args):

    # pull a simconfig object off the queue

    completed_count = 0
    while True:
        try:
            simconfig = queue.get()

            log.info("worker %s: starting run for popsize: %s add_rate: %s maxtraits: %s",
                     os.getpid(), simconfig.popsize, simconfig.add_rate, simconfig.maxtraits)
            gf_constructor = utils.load_class(simconfig.NETWORK_FACTORY_CLASS)
            model_constructor = utils.load_class(simconfig.POPULATION_STRUCTURE_CLASS)
            rule_constructor = utils.load_class(simconfig.INTERACTION_RULE_CLASS)
            trait_factory_constructor = utils.load_class(simconfig.TRAIT_FACTORY_CLASS)
            trait_factory = trait_factory_constructor(simconfig)
            graph_factory = gf_constructor(simconfig)
            model = model_constructor(simconfig, graph_factory, trait_factory)
            model.initialize_population()

            ax = rule_constructor(model)

            timestep = 0
            last_interaction = 0

            while(1):
                timestep += 1
                if timestep % 250000 == 0:
                    log.debug("worker %s: time: %s active links: %s", os.getpid(), timestep, ax.get_fraction_links_active())
                ax.step(timestep)
                if model.get_time_last_interaction() != timestep:
                    live = utils.check_liveness(ax, model, args, simconfig, timestep)
                    if live == False:
                        utils.finalize_treestructured_model(model, args, simconfig)
                        break

            # clean up before moving to next queue item
            simconfig = None
            model = None
            completed_count += 1
            if(completed_count % 100 == 0):
                log.info("trait worker %s: completed %s samples", os.getpid(), completed_count )

        finally:
            queue.task_done()


if __name__ == "__main__":
    setup()
    main()


