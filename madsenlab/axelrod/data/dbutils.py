#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

def getMingConfiguration(modules):
    config = {}
    for module in modules:
        urlstring = 'mongodb://'
        urlstring += dbhost
        urlstring += ":"
        urlstring += dbport
        urlstring += "/"

        key = ''
        key += 'ming.'
        key += module._get_dataobj_id()
        key += '.uri'
        collection = module._get_collection_id()
        urlstring += collection
        #log.debug("Configuring %s module as %s", module, urlstring)
        config[key] = urlstring
    return config


def set_database_hostname(name):
    global dbhost
    dbhost = name

def set_database_port(port):
    global dbport
    dbport = port

def set_experiment_name(name):
    """
    Takes the name of the experiment currently being run, for use as a prefix to database collection names

    :param name:
    :return: none
    """
    global experiment_name
    experiment_name = name


def generate_collection_id(suffix):
    collection_id = experiment_name
    collection_id += suffix
    return collection_id