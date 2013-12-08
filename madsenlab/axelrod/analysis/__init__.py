#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
from descriptive_stats import get_culture_counts, get_culture_size_statistics
from overlap import calc_probability_interaction_axelrod, get_different_feature_positions_axelrod, calc_overlap_axelrod, calc_overlap_extensible, calc_probability_interaction_extensible, \
    get_traits_differing_from_focal_extensible
from order_parameters import klemm_normalized_L_axelrod, klemm_normalized_L_extensible