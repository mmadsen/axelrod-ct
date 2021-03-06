#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import json
from operator import itemgetter
from numpy.random import RandomState
import sys

##########################################################################

class BaseConfiguration(object):
    """
    Common behavior for all configuration classes.

    An object of this class also has property getter/setters for specific instances of the configuration, which would
    characterize a specific simulation run.  These must be set by a simulation model's script, for consumption by
    underlying classes and modules.

    The class also contains two methods for constructing document-ready representations of a set of configuration
    parameters, as a LaTeX table or a Pandoc-formatted Markdown table.  With a wrapper script, these methods
    allow direct incorporation of simulation configurations into publications and reports, for accuracy and
    reproducibility.
    """

    INTERACTION_RULE_CLASS = 'madsenlab.axelrod.rules.AxelrodRule'

    POPULATION_STRUCTURE_CLASS = 'madsenlab.axelrod.population.SquareLatticeFixedTraitModel'

    NETWORK_FACTORY_CLASS = 'madsenlab.axelrod.population.SquareLatticeFactory'

    TRAIT_FACTORY_CLASS = 'madsenlab.axelrod.traits.AxelrodTraitFactory'
    """
    The fully qualified import path for a class which implements the population model.
    """

    STRUCTURE_PERIODIC_BOUNDARY = [True, False]

    SIMULATION_CUTOFF_TIME = 2000000
    """
    The time at which we terminate a simulation which is cycling endlessly with active links.
    """

    REPLICATIONS_PER_PARAM_SET = 10
    """
    For each combination of simulation parameters, CTPy and simuPOP will run this many replicate
    populations, saving samples identically for each, but initializing each replicate with a
    different population and random seed.
    """

    POPULATION_SIZES_STUDIED = [1000,2000]
    """
    In most of the CT models we study, the absolute amount of variation we might expect to see is
    partially a function of the number of individuals doing the transmitting.  This is *total* population
    size, either for a single population, or the metapopulation as a whole in a spatial model.  Because we are
    going to model this on a grid, these numbers should be perfect squares, so that if the population size is N,
    the lattice size (on a side) is SQRT(N).
    """

    base_parameter_labels = {
        'POPULATION_SIZES_STUDIED' : 'Population sizes',
        'STRUCTURE_PERIODIC_BOUNDARY' : 'Does the population structure have a periodic boundary condition?',
        'REPLICATIONS_PER_PARAM_SET' : 'Replicate simulation runs at each parameter combination',
        'NUMBER_OF_TRAITS_PER_DIMENSION': 'Number of traits per locus/dimension/feature',
        'NUMBER_OF_DIMENSIONS_OR_FEATURES': 'Number of loci/dimensions/features each individual holds',
        'SIMULATION_CUTOFF_TIME' : 'Maximum time after which a simulation is sampled and terminated if it does not converge',
    }


    def __init__(self, config_file):
        # if we don't give a configuration file on the command line, then we
        # just return a Configuration object, which has the default values specified above.
        if config_file is None:
            return

        # otherwise, we load the config file and override the default values with anything in
        # the config file
        try:
            json_data = open(config_file)
            self.config = json.load(json_data)
        except ValueError:
            print "Problem parsing json configuration file - probably malformed syntax"
            exit(1)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            exit(1)

        # we succeeded in loading the configuration, now override the default values of variables
        # given the contents of the configuration file
        for variable,value in self.config.iteritems():
            setattr(self, variable, value)

        # finalize the list of derived values
        self._calc_derived_values()


        # run-specific values common to all models
        self._popsize = None
        self._sim_id = None
        self._periodic = None
        self._script = None
        self._max_time = None

        # set up a global RNG everything can use
        self._prng = RandomState()

    @property
    def prng(self):
        return self._prng


    @property
    def script(self):
        return self._script

    @script.setter
    def script(self,s):
        self._script = s

    @property
    def periodic(self):
        return self._periodic

    @periodic.setter
    def periodic(self,p):
        self._periodic = p

    @property
    def sim_id(self):
        return self._sim_id

    @sim_id.setter
    def sim_id(self,id):
        self._sim_id = id


    @property
    def popsize(self):
        return self._popsize

    @popsize.setter
    def popsize(self, val):
        self._popsize = val

    @property
    def maxtime(self):
        return self._max_time

    @maxtime.setter
    def maxtime(self,val):
        self._max_time = val


    def __repr__(self):
        attrs = vars(self)
        rep = '\n'.join("%s: %s" % item for item in attrs.items() if item[0] != "config")
        return rep

    def to_latex_table(self, experiment, **kwargs):
        """
        Constructs a LaTeX table and tabular environment for the simulation parameters and
        control variable settings.  A list of "internal" or unimplemented variables are
        filtered out of this list, and actual variable names are translated to human-readable
        phrases with a lookup table.

        Takes an optional named argument:  caption=String.  This parameter will replace
        the caption automatically generated by this method.

        :return: A string comprising the LaTeX representation for the parameters.

        """
        if 'caption' not in kwargs or kwargs['caption'] is None:
            caption_text = "\\caption{Parameters for Semantic Axelrod simulations for Experiment Name: "
            caption_text += experiment
            caption_text += '}\n'
        else:
            caption_text = '\\caption{'
            caption_text += kwargs['caption']
            caption_text += '}\n'


        #if kwargs['caption'] is not None:
        #    caption_text = '\\caption{'
        #    caption_text += kwargs['caption']
        #    caption_text += '}\n'
        #else:
        #    caption_text = "\\caption{Parameters for Axelrod Simulations for Experiment Name: "
        #    caption_text += experiment
        #    caption_text += '}\n'


        t = []
        t.append('\\begin{table}[h]\n')
        t.append('\\begin{tabular}{|p{0.6\\textwidth}|p{0.4\\textwidth}|}\n')
        t.append('\\hline\n')
        t.append('\\textbf{Simulation Parameter} & \\textbf{Value or Values} \\\\ \n')
        t.append('\\hline\n')

        for var in self._get_public_variables():
            s = self.parameter_labels[var[0]]
            s += ' & '


            # need to know if var[1] is a single integer, or a list
            if hasattr(var[1], '__iter__'):
                s += ', '.join(map(str, var[1]))
            else:
                s += str(var[1])

            s += '\\\\ \n \\hline \n'
            t.append(s)


        t.append('\\hline\n')
        t.append('\\end{tabular}\n')
        t.append(caption_text)
        t.append('\\label{tab:axelrodct-sim-parameters}\n')
        t.append('\\end{table}\n')

        return ''.join(t)

    def to_pandoc_table(self, experiment, **kwargs):
        """
        Constructs a Markdown table (in pandoc format) for the simulation parameters and
        control variable settings.  A list of "internal" or unimplemented variables are
        filtered out of this list, and actual variable names are translated to human-readable
        phrases with a lookup table.

        :return: Text string representing a Pandoc table
        """
        t = []

        t.append('| Simulation Parameter                   | Value or Values                                   |\n')
        t.append('|:---------------------------------------|:--------------------------------------------------|\n')

        for var in self._get_public_variables():
            s = '|    '
            s += self.parameter_labels[var[0]]
            s += '   |   '


            # need to know if var[1] is a single integer, or a list
            if hasattr(var[1], '__iter__'):
                s += ', '.join(map(str, var[1]))
            else:
                s += str(var[1])

            s += '  | \n'
            t.append(s)

        return ''.join(t)

    def _get_public_variables(self):
        attrs = vars(self)
        filtered = [item for item in attrs.items() if item[0] not in self.vars_to_filter]
        filtered.sort(key=itemgetter(0))
        return filtered

##########################################################################

class AxelrodConfiguration(BaseConfiguration):
    """
    Defines a number of class level constants which serve as configuration for a set of simulation models.
    Each constant can be overriden by a JSON configuration file, which this class is responsible for
    parsing.  Given a JSON configuration file, the values for any constants defined in that file replace
    the default values given here -- but the names must match.

    This class also contains any logic required by a simulation model to calculate derived parameters -- i.e.,
    those values which the simulation model may treat as configuration but which are derived by calculation from
    user supplied parameter values.


    """

    NUMBER_OF_DIMENSIONS_OR_FEATURES = [100,200]
    """
    This is the number of "loci" or "features" in Axelrod's original terminology.  By analogy with classifications,
    these are also "dimensions".
    """

    NUMBER_OF_TRAITS_PER_DIMENSION = [500,1000]
    """
    The Axelrod model dynamics are strongly affected by the number of possible traits per locus or feature.  We
    model a range of values to capture the full phase diagram of the process.
    """

    DRIFT_RATES = [0.001,0.005]



    parameter_labels = {
        'POPULATION_SIZES_STUDIED' : 'Population sizes',
        'STRUCTURE_PERIODIC_BOUNDARY' : 'Does the population structure have a periodic boundary condition?',
        'REPLICATIONS_PER_PARAM_SET' : 'Replicate simulation runs at each parameter combination',
        'NUMBER_OF_TRAITS_PER_DIMENSION': 'Number of traits per locus/dimension/feature',
        'NUMBER_OF_DIMENSIONS_OR_FEATURES': 'Number of loci/dimensions/features each individual holds'
    }


    # For Latex or Pandoc output, we also filter out any object instance variables, and output only the class-level variables.
    vars_to_filter = ['config', '_prng', "_popsize", "_num_features", "_num_traits", "_sim_id", "_periodic", "_script", "_drift_rate", "_max_time", "_num_features", "_num_traits"]
    """
    List of variables which are never (or at least currently) pretty-printed into summary tables using the latex or markdown/pandoc methods

    Some variables might be here because they're currently unused or unimplemented....
    """

    def __init__(self, config_file):

        super(AxelrodConfiguration, self).__init__(config_file)

        # object properties for each specific run

        self._num_features = None
        self._num_traits = None
        self._drift_rate = None


    @property
    def drift_rate(self):
        return self._drift_rate

    @drift_rate.setter
    def drift_rate(self, r):
        self._drift_rate = r

    @property
    def num_features(self):
        return self._num_features

    @num_features.setter
    def num_features(self,val):
        self._num_features = val

    @property
    def num_traits(self):
        return self._num_traits

    @num_traits.setter
    def num_traits(self,val):
        self._num_traits = val



    def _calc_derived_values(self):
        """
        No known derived values right now....
        """
        pass


##########################################################################

class AxelrodExtensibleConfiguration(BaseConfiguration):

    TRAIT_ADDITION_RATE = [0.01, 0.05, 0.1, 0.25]
    """
    When an interaction occurs, some models may allow the trait list to grow by adding a neighbor's trait
    to the list, instead of replacing an existing trait with it.  This isn't very interesting in a basic
    extensible model, but it's the foundation for models where addition happens for a *reason* -- i.e.,
    learning prerequisites, etc.
    """

    MAXIMUM_INITIAL_TRAITS = [4,8,16,32]
    """
    Individual agents will receive a random number of initial traits, distributed between 1 and this MAX value.
    The distribution used to generate each agent's initial trait endowment may vary by rule.
    """

    DRIFT_RATES = [0.001,0.005]
    """
    Rates at which random mutations occur within the population.
    """

    MAX_TRAIT_TOKEN = 100
    """
    Traits can be any token from 0 to this value.
    """
    # For Latex or Pandoc output, we also filter out any object instance variables, and output only the class-level variables.
    vars_to_filter = ['config', '_prng', "_popsize", "_num_features", "_num_traits", "_sim_id", "_periodic", "_script", "_drift_rate"]
    """
    List of variables which are never (or at least currently) pretty-printed into summary tables using the latex or markdown/pandoc methods

    Some variables might be here because they're currently unused or unimplemented....
    """




    def __init__(self, config_file):
        super(AxelrodExtensibleConfiguration, self).__init__(config_file)

        self._maxtraits = None
        self._drift_rate = None
        self._addition_rate = None

    @property
    def maxtraits(self):
        return self._maxtraits

    @maxtraits.setter
    def maxtraits(self,val):
        self._maxtraits = val

    @property
    def drift_rate(self):
        return self._drift_rate

    @drift_rate.setter
    def drift_rate(self, r):
        self._drift_rate = r

    @property
    def addition_rate(self):
        return self._addition_rate

    @addition_rate.setter
    def addition_rate(self,val):
        self._addition_rate = val

    def _calc_derived_values(self):
        """
        No known derived values right now....
        """
        pass

##########################################################################

class TreeStructuredConfiguration(BaseConfiguration):

    INNOVATION_RATE = [0.01, 0.05, 0.005, 0.001]
    """
    The population-level innovation rate, whereby a random individual adds a trait they don't have (and any prerequisites
    needed.
    """

    TRAIT_LEARNING_RATE = [0.01, 0.05, 0.1, 0.25]
    """
    When an interaction occurs, some models may allow the trait list to grow by adding a neighbor's trait
    to the list, instead of replacing an existing trait with it.  This isn't very interesting in a basic
    extensible model, but it's the foundation for models where addition happens for a *reason* -- i.e.,
    learning prerequisites, etc.
    """

    TRAIT_LOSS_RATE = [0.0, 0.05, 0.1, 0.2]
    """
    Occasionally, individuals may forget or lose a skill.  This crudely models that process through a loss rate,
    where the traits lost are chosen uniformly at random.  When the rate is 0.0, no losses occur during that
    simulation run
    """

    MAXIMUM_INITIAL_TRAITS = [4,8,16,32]
    """
    Individual agents will receive a random number of initial traits, distributed between 1 and this MAX value.
    The distribution used to generate each agent's initial trait endowment may vary by rule.
    """

    NUM_TRAIT_TREES = [1,4,8,16,32]
    """
    The number of independent trait trees created to serve as the trait universe.
    """

    TREE_BRANCHING_FACTOR = [2,3,4,8]
    """
    Interpretable either as the fixed branching factor for regular trees, or the mean branching factor for
    random trees.
    """

    TREE_DEPTH_FACTOR = [4,5,6,8]
    """
    Interpretable either as the fixed depth for regular trees (e.g., balanced trees), or the mean depth for
    random trees.
    """

    WS_REWIRING_FACTOR = [0.05,0.075,0.1,0.2]
    """
    When using the Watts-Strogatz small-world lattice, this represents the probability of rewiring a vertex
    """

    parameter_labels = {
        'INNOVATION_RATE' : 'Population rate at which new traits arise by individual learning',
        'TRAIT_LEARNING_RATE' : 'Individual rate at which a missing prerequisite is learned during an interaction',
        'TRAIT_LOSS_RATE' : 'Population rate at which existing traits are lost, perhaps by disuse',
        'MAXIMUM_INITIAL_TRAITS': 'Maximum number of initial traits (not including their prerequisites) each individual is endowed with',
        'NUM_TRAIT_TREES': 'Number of distinct trees of traits and prerequisites',
        'TREE_BRANCHING_FACTOR' : 'Number of branches at each level of a trait tree',
        'TREE_DEPTH_FACTOR' : 'Depth of traits/prerequisites in each trait tree',
        'WS_REWIRING_FACTOR' : 'Rewiring probability for Watts-Strogatz small world lattices',
    }


    # For Latex or Pandoc output, we also filter out any object instance variables, and output only the class-level variables.
    vars_to_filter = ['config', '_prng', "_popsize", "_num_features", "_num_traits", "_sim_id", "_periodic", "_script", "_drift_rate", "_maxtraits",
                      "_learning_rate", "_num_trees", "_branching_factor", "_depth_factor", "_loss_rate", "_innov_rate", "_max_time", "_wsrewiring",
                      "_save_graphs", "INTERACTION_RULE_CLASS", "POPULATION_STRUCTURE_CLASS", "NETWORK_FACTORY_CLASS", "TRAIT_FACTORY_CLASS"]


    """
    List of variables which are never (or at least currently) pretty-printed into summary tables using the latex or markdown/pandoc methods

    Some variables might be here because they're currently unused or unimplemented....
    """



    def __init__(self, config_file):
        super(TreeStructuredConfiguration, self).__init__(config_file)

        # unify the base configuration labels with the specific parameters from this class
        self.parameter_labels.update(self.base_parameter_labels)

        self._maxtraits = None
        self._learning_rate = None
        self._num_trees = None
        self._branching_factor = None
        self._depth_factor = None
        self._loss_rate = None
        self._innov_rate = None
        self._save_graphs = False
        self._wsrewiring = None


    @property
    def ws_rewiring(self):
        return self._wsrewiring

    @ws_rewiring.setter
    def ws_rewiring(self,val):
        self._wsrewiring = val

    @property
    def save_graphs(self):
        return self._save_graphs

    @save_graphs.setter
    def save_graphs(self, val):
        self._save_graphs = val

    @property
    def innov_rate(self):
        return self._innov_rate

    @innov_rate.setter
    def innov_rate(self, val):
        self._innov_rate = val


    @property
    def loss_rate(self):
        return self._loss_rate

    @loss_rate.setter
    def loss_rate(self,val):
        self._loss_rate = val

    @property
    def maxtraits(self):
        return self._maxtraits

    @maxtraits.setter
    def maxtraits(self,val):
        self._maxtraits = val

    @property
    def learning_rate(self):
        return self._learning_rate

    @learning_rate.setter
    def learning_rate(self,val):
        self._learning_rate = val

    @property
    def num_trees(self):
        return self._num_trees

    @num_trees.setter
    def num_trees(self,val):
        self._num_trees = val

    @property
    def branching_factor(self):
        return self._branching_factor

    @branching_factor.setter
    def branching_factor(self,val):
        self._branching_factor = val

    @property
    def depth_factor(self):
        return self._depth_factor

    @depth_factor.setter
    def depth_factor(self,val):
        self._depth_factor = val



    def _calc_derived_values(self):
        """
        No known derived values right now....
        """
        pass