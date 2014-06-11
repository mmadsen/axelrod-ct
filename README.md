axelrod-ct
==========

[![Build Status](https://travis-ci.org/mmadsen/axelrod-ct.svg?branch=master)](https://travis-ci.org/mmadsen/axelrod-ct)


Cultural Transmission Models based upon Robert Axelrod's (1997) model of homophily and culture


## Installation ##

First, see dependencies below.  Have a working python 2.7 distribution and the required modules installed.  Also, a working instance of MongoDB.  

Then, clone the Github repository, or download one of the zip or tar.gz distributions for the latest release version.  Then, run `python setup.py install` (possibly with sudo if you need root permissions to install software, but Anaconda should be a user-directory install).

You can run simulations directly from the source directory, or install the scripts wherever you like once the python modules are on the path.  


## Admin Programs ##

**NOTE**:  all executable scripts have help for the command line options they require.  


The `admin` directory contains scripts which allow you to export data from MongoDB to CSV files, to generate LaTeX or Markdown tables from simulation configuration files, suitable for embedding in your paper (so you don't transcribe them wrong!), scoping the size of a potential simulation configuration, and building parallelized simulation runs (the "builder") scripts.  

## Analytical Programs ##


The `analytics` directory contains scripts for post-processing simulation runs.  The principal ones are:

`calculate_graph_symmetry_stats.py` -- run after a simulation run completes, to add additional graph algebraic metrics using the `nauty` program.  

`treestructured-uniform-sampler.py` -- an alternative to `admin/export-data-to-csv.py` which takes even-sized samples of each parameter combination and exports to CSV.  This allows one to run many instances of a simulation configuration across many cluster instances, combine their data output, and "trim" their overlapping output to ensure that each parameter combination has the same number of replicates.  This allows one great flexibility in planning and executing large parallel batches.  

`export-traitgraph-to-graphviz.py` -- takes samples of trait graphs from a simulation run database, and exports that sample to DOT files for processing by AT&T `graphviz`.  This is useful for visualization.  

## Simulation Driver Programs ##

The `simulations` directory contains:

`sim-axelrod-{single|parallel}.py`:  implements the original Axelrod model as a single simulation, and performing a batch in parallel across N cores.  

`sim-extensible-{single|parallel}.py`:  implements an Axelrod-style model with traits given by a mathematical set, instead of Q discrete features with F alleles or traits.  This is the bridge between the original model and semantic models.  

`sim-treestructured-{single|parallel}.py`:  implements the tree-structured "prerequisites" model currently.  The single version is used for everything, and the `admin/treestructured-parallel-builder.py` constructs scripts which run large parallel batches, given inefficiencies and performance problems with the Python multiprocessing approach used in the original Axelrod model scripts.  Thus, the "parallel" version here is deprecated.

`sim-treestructured-longrun.py`:  treestructured "prerequisites" model, but run for a fixed length rather than until convergence.  THIS MODEL WAS USED EXCLUSIVELY FOR OUR 2014 PAPER.  



## Dependencies ##

### MongoDB Database ###

You will need an instance of [MongoDB](http://www.mongodb.org/) installed on a computer, with the ability to create databases and grant access if the database and simulations are run on different systems.  For a basic installation, simply install MongoDB on the same machine you are using for simulation; all programs contained herein will default to using the local instance of the database.  You can run MongoDB on any size system or laptop.  

MongoDB is a "NoSQL" database, which means it has no fixed schema, and performs database operations using JSON objects for inserts and query results.  This makes it very flexible for research purposes, although the tradeoff is that databases can require a fair amount of disk space (which is cheap!).  MongoDB is mainly used as a flexible means of storing and operating on the raw data, prior to its export to R and other analytics systems.  Scripts are provided by adding derived metrics to the database, sampling it, and exporting it to CSV files for direct import to R.  

### Nauty+Traces ###

You will need Brendan MacKay's `nauty+Traces` software for certain calculations of graph symmetry statistics, whether or not you are concerned about those metrics (or you can disable this in the code fairly easily).  

Download from (http://pallini.di.uniroma1.it/index.html), compile it with any C compiler on your system, and install the `dreadnaut` program on your system's default executable path.  Note that in parallel runs, you may be running the simulations without your full user environment (i.e., detached from a user session), so this does not mean in your own user's executable path, but somewhere on the system where a system program can also run it.  On a Mac or Linux system, an excellent choice is `/usr/local/bin`.


### Python ###

You will need a Python 2.7 interpreter.  I very strongly recommend the [Anaconda](https://store.continuum.io/cshop/anaconda/) python distribution, which is packaged for scientific computing and data science.  It already has some of the modules you will need, but here is the complete list.  

In particular, you'll need to use "pip" or "easy_install" from Anaconda to install things like Ming and parts of matplotlib if you want to make images of trait graphs.   

Actively used modules:

   * argparse
   * copy
   * csv
   * importlib
   * itertools
   * json
   * logging
   * math
   * matplotlib
   * ming
   * networkx
   * numpy
   * os
   * pprint
   * random
   * re
   * scipy
   * sys
   * tempfile
   * time
   * unittest
   * uuid

   Deprecated, but still imported by several unused scripts (need cleanup)

   * subprocess
   * multiprocessing
