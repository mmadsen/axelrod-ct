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

    simconfig = utils.AxelrodConfiguration(args.configuration)

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
    log.info("Configuring Axelrod model with structure class: %s", structure_class_name)



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
    process = mp.Process(target=worker, args=(queue, simconfig, args))
    process.daemon = True
    process_list.append(process)
    process.start()


def create_processes(queue, worker):
    for i in range(0, int(args.parallelism)):
        process = mp.Process(target=worker, args=(queue, args))
        process.daemon = True
        process_list.append(process)
        process.start()


def queue_simulations(queue, simconfig, args):

    state_space = [
        simconfig.POPULATION_SIZES_STUDIED,
        simconfig.NUMBER_OF_DIMENSIONS_OR_FEATURES,
        simconfig.NUMBER_OF_TRAITS_PER_DIMENSION
    ]


    for param_combination in itertools.product(*state_space):
        # for each parameter combination, make a copy of the base configuration
        # set the specific param combo values, and queue the object
        for repl in range(0, simconfig.REPLICATIONS_PER_PARAM_SET):
            sc = copy.deepcopy(simconfig)
            sc.popsize = int(param_combination[0])
            sc.num_features = int(param_combination[1])
            sc.num_traits = int(param_combination[2])
            sc.periodic = 0

            queue.put(sc)


    log.info("All simulation configurations queued")



def run_simulation_worker(queue, args):

    # pull a simconfig object off the queue

    completed_count = 0
    while True:
        try:
            log.info("worker %s: starting simulation run", os.getpid())
            simconfig = queue.get()
            model_constructor = utils.load_class(simconfig.POPULATION_STRUCTURE_CLASS)
            model = model_constructor(simconfig)
            model.initialize_population()

            ax = rules.AxelrodRule(model)

            timestep = 0
            last_interaction = 0

            while(1):
                timestep += 1
                if timestep % 10000 == 0:
                    log.debug("time: %s active links: %s", timestep, ax.get_fraction_links_active())
                ax.step(timestep)
                if model.get_time_last_interaction() != timestep:
                    live = utils.check_liveness(ax, model, args, simconfig, timestep)
                    if live == False:
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


