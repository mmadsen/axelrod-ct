#!/usr/bin/env python

# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

import ming
import csv
import os
import logging as log
import tempfile
import argparse
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data

# Prototype:
# mongoexport --db f-test_samples_postclassification --collection pergeneration_stats_postclassification --csv --out pgstats.csv --fieldFile fieldlist

mongoexport = "mongoexport "



## setup

def setup():
    global args, config, simconfig
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment, to be used as prefix for database collections")
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Path to configuration file")
    parser.add_argument("--model", choices=['axelrod', 'extensible', 'treestructured'], required=True)
    parser.add_argument("--finalized", help="Only export runs which finalized after convergence", action="store_true")

    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

    if args.model == 'axelrod':
        simconfig = utils.AxelrodConfiguration(args.configuration)
    elif args.model == 'extensible':
        simconfig = utils.AxelrodExtensibleConfiguration(args.configuration)
    elif args.model == 'treestructured':
        simconfig = utils.TreeStructuredConfiguration(args.configuration)
    else:
        log.error("This shouldn't happen - args.model = %s", args.model)

    if args.debug == 1:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')


    #### main program ####
    log.info("EXPORT DATA TO CSV - Experiment: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)



def export_collection_to_csv(database, collection_name, fieldlist):

    outputFileName = "data_"
    outputFileName += collection_name
    outputFileName += ".csv"

    fieldFile = tempfile.NamedTemporaryFile(mode="w+t",suffix=".txt",dir="/tmp",delete=False)
    fieldFileName = fieldFile.name
    log.debug("Saving field list to %s", fieldFileName)

    for field in fieldlist:
        fieldFile.write(field)
        fieldFile.write('\n')

    fieldFile.flush()

    args = []
    args.append(mongoexport)
    args.append("--db")
    args.append(database)
    args.append("--collection")
    args.append(collection_name)
    args.append("--csv")
    args.append("--fieldFile")
    args.append(fieldFileName)
    args.append("--out")
    args.append(outputFileName)

    log.debug("args: %s", args)
    retcode = os.system(" ".join(args))
    log.debug("return code: %s", retcode)




if __name__ == "__main__":
    setup()


    outputFileName = "data_"
    outputFileName += "axelrod_stats_treestructured"
    outputFileName += ".csv"

    fieldnames = data.axelrod_run_treestructured.columns_to_export_for_analysis()
    orig_fields = fieldnames[:]
    fieldnames.extend(["cultureid", "culture_count", "mean_radii", "sd_radii",
                       "orbit_number", "autgroupsize", "remaining_density",
                       "mean_degree", "sd_degree",
                       "mean_orbit_multiplicity", "sd_orbit_multiplicity",
                       "max_orbit_multiplicity"])
    ofile  = open(outputFileName, "wb")
    writer = csv.DictWriter(ofile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL)

    headers = dict((n,n) for n in fieldnames)
    writer.writerow(headers)

    if args.finalized == True:
        cursor = data.AxelrodStatsTreestructured.m.find(dict(run_finalized=1),dict(timeout=False))
    else:
        cursor = data.AxelrodStatsTreestructured.m.find(dict(),dict(timeout=False))



    for sample in cursor:
        row = dict()
        for field in sorted(orig_fields):
            row[field] = sample[field]

        # now pull apart the trait graph list - producing a row for each element of the trait graph list
        tg_stats = sample['trait_graph_stats']
        for tg in tg_stats:
            log.debug("tg: %s", tg)
            row['cultureid'] = tg['cultureid']
            row['culture_count'] = tg['culture_count']
            row['mean_radii'] = tg['mean_radii']
            row['sd_radii'] = tg['sd_radii']
            row['mean_degree'] = tg['mean_degree']
            row['sd_degree'] = tg['sd_degree']
            row['orbit_number'] = tg['orbit_number']
            row['autgroupsize'] = tg['autgroupsize']
            row['remaining_density'] = tg['remaining_density'],
            row['mean_orbit_multiplicity'] = tg['mean_orbit_multiplicity'],
            row['sd_orbit_multiplicity_orbit_multiplicity'] = tg['sd_orbit_multiplicity'],
            row['max_orbit_multiplicity'] = tg['max_orbit_multiplicity']

            writer.writerow(row)

    ofile.close()













