#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2019--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Str, Plugin, Choices, List, Citations)
from .merge import merge_taxa
from .dereplicate import dereplicate
from q2_types.feature_data import FeatureData, Taxonomy, Sequence

import rescript


citations = Citations.load('citations.bib', package='q2_vsearch')

plugin = Plugin(
    name='rescript',
    version=rescript.__version__,
    website="https://github.com/nbokulich/RESCRIPt",
    package='rescript',
    description=('Reference sequence annotation and curation pipeline.'),
    short_description=(
        'Pipeline for reference sequence annotation and curation.'),
)


plugin.methods.register_function(
    function=merge_taxa,
    inputs={'data': List[FeatureData[Taxonomy]]},
    parameters={
        'mode': Str % Choices(['len', 'lca', 'score']),
        'rank_handle': Str,
        'new_rank_handle': Str},
    outputs=[('merged_data', FeatureData[Taxonomy])],
    input_descriptions={
        'data': 'Two or more feature taxonomies to be merged.'},
    parameter_descriptions={
        'mode': 'How to merge feature taxonomies: "len" will select the '
                'taxonomy with the most elements (e.g., species level will '
                'beat genus level); "lca" will find the least common ancestor '
                'and report this consensus taxonomy; "score" will select the '
                'taxonomy with the highest score (e.g., confidence or '
                'consensus score). Note that "score" assumes that this score '
                'is always contained as the second column in a feature '
                'taxonomy dataframe.',
        'rank_handle': 'Text handle indicating which taxonomic rank a label '
                       'belongs to; this handle is stripped from the label '
                       'prior to taxonomy comparisons and merging. The net '
                       'effect is that ambiguous or empty levels can be '
                       'removed prior to comparison, enabling selection of '
                       'taxonomies with more complete taxonomic information. '
                       'Regular expressions may be used for this parameter; '
                       'e.g., "^[kpcofgs]__" will recognize greengenes rank '
                       'handles. Note that rank_handles are removed but not '
                       'replaced; use the new_rank_handle parameter to '
                       'replace the rank handles.',
        'new_rank_handle': 'A semicolon-delimited string of rank handles to '
                           'prepend to taxonomic labels at each rank. For '
                           'example, "k__;p__;c__;o__;f__;g__;s__" will '
                           'prepend greengenes-style rank handles. Note that '
                           'merged taxonomies will only contain as many '
                           'levels as there are handles if this parameter is '
                           'used. So "k__;p__" will trim all taxonomies to '
                           'phylum level, even if longer annotations exist.'},
    name='Compare taxonomies and select the longest, highest scoring, or find '
         'the least common ancestor.',
    description='Compare taxonomy annotations and choose the best one. Can '
                'select the longest taxonomy annotation, the highest scoring, '
                'or the least common ancestor. Note: when a tie occurs, the '
                'last taxonomy added takes precedent.',
)


plugin.methods.register_function(
    function=dereplicate,
    inputs={'sequences': FeatureData[Sequence],
            'taxa': FeatureData[Taxonomy]},
    parameters={
        'mode': Str % Choices(['uniq', 'lca', 'majority'])},
    outputs=[('dereplicated-sequences', FeatureData[Sequence]),
             ('dereplicated-taxa', FeatureData[Taxonomy])],
    input_descriptions={
        'sequences': 'Sequences to be dereplicated',
        'taxa': 'Taxonomic classifications of sequences to be dereplicated'},
    parameter_descriptions={
        'mode': 'How to handle dereplication when sequences map to distinct '
                'taxonomies. "uniq" will retain all sequences with unique '
                'taxonomic affiliations. "lca" will find the least common '
                'ancestor among all taxa sharing a sequence. "majority" will '
                'find the most common taxonomic label associated with that '
                'sequence; note that in the event of a tie, "majority" will '
                'pick the winner arbitrarily.'
    },
    name='Dereplicate features with matching sequences and taxonomies.',
    description=(
        'Dereplicate FASTA format sequences and taxonomies wherever '
        'sequences and taxonomies match; duplicated sequences and taxonomies '
        'are dereplicated using the "mode" parameter to either: retain all '
        'sequences that have unique taxonomic annotations even if the '
        'sequences are duplicates (uniq); or return only dereplicated '
        'sequences labeled by either the least common ancestor (lca) or the '
        'most common taxonomic label associated with sequences in that '
        'cluster (majority).'),
    citations=[citations['rognes2016vsearch']]
)
