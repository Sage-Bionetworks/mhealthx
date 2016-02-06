#!/usr/bin/env python
"""
This program stores select columns (features) from mhealthx's output.

The mhealthx command results in a one-row csv table for each recordId.
This recordId corresponds to a source row of mhealth data --
a given participant, for a given activity, at a given time.

The "mhealthy" command:
- Concatenates all one-row tables for each activity.
- Extracts specified columns from each activity table.
- Stores the resulting, reduced tables as Synapse tables.

Example:

    mhealthy

Note:

    First-time use on a given machine: include -u and -p for Synapse login.

For help in using mhealthy ::

        $ mhealthy --help

Authors:
    - Arno Klein, 2016  (arno@sagebase.org)  http://binarybottle.com

Copyright 2016,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""

import os
import argparse
from mhealthx.xio import concatenate_tables_vertically
from mhealthx.xio import write_columns_to_synapse_table

# ============================================================================
#
# Command-line arguments
#
# ============================================================================
parser = argparse.ArgumentParser(description="""
                    Extract features from mHealth data
                    stored on Sage Bionetwork's Synapse.org.
                    Example: mhealthx --voice syn4590865 -d /software
                    (-d: path to installed software dependencies; -u, -p:
                    Synapse login for first use on a given machine)
""",
                                 formatter_class = lambda prog:
                                 argparse.HelpFormatter(prog,
                                                        max_help_position=40))
parser.add_argument("-v", "--version", help="version number",
                    action='version', version='%(prog)s 0.1')
parser.add_argument("-u", "--username",
                         help="Synapse username", metavar='STR')
parser.add_argument("-p", "--password",
                         help="Synapse password", metavar='STR')
args = parser.parse_args()
username = args.username
password = args.password

# ============================================================================
#
# Login once to Synapse and cache credentials
#
# ============================================================================
import synapseclient
syn = synapseclient.Synapse()
syn.login(username, password, rememberMe=True)

# ============================================================================
#
# Concatenate one-row tables for each activity
#
# ============================================================================
outdir = '/Users/arno/mhealthx_output/feature_tables'
input_tables = os.listdir(outdir)
stems = []
stems_temp = []
collated_table_lists = []
for input_table in input_tables:
    stem = input_table.split('_row')[0]
    stem_temp = stem + '_row'
    if stem_temp not in stems_temp:
        stems.append(stem)
        stems_temp.append(stem_temp)
        tables_with_stem = [os.path.join(outdir, x) for x in input_tables
                            if stem_temp in x]
        collated_table_lists.append(tables_with_stem)

tables = []
for istem, collated_table_list in enumerate(collated_table_lists):
    output_table = os.path.join(outdir, stems[istem] + '.csv')
    table1, output_table = concatenate_tables_vertically(collated_table_list,
                                                         output_table)
    tables.append(output_table)

# ============================================================================
#
# Select columns from activity tables
#
# ============================================================================
# ----------------------------------------------------------------------------
# Voice columns
# ----------------------------------------------------------------------------
voice_openSMILE_columns = ['pcm_RMSenergy_sma_de_range',
                           'pcm_zcr_sma_de_upleveltime90',
                           'pcm_zcr_sma_de_risetime']
# ----------------------------------------------------------------------------
# Tap columns
# ----------------------------------------------------------------------------
tap_columns = ['intertap_mad', 'intertap_max', 'intertap_min']
tap_sdf_columns = ['SDF eigenvector 1',
                   'SDF eigenvector 2',
                   'SDF eigenvector 3']
# ----------------------------------------------------------------------------
# Walk columns
# ----------------------------------------------------------------------------
walk_pyGait_columns = ['avg_step_duration', 'cadence', 'number_of_steps']
walk_signals_columns = ['mad', 'max', 'min']
walk_sdf_columns = ['SDF eigenvector 1',
                    'SDF eigenvector 2',
                    'SDF eigenvector 3']
walk_openSMILE_columns = ['pcm_RMSenergy_sma_de_range',
                          'pcm_zcr_sma_de_upleveltime90',
                          'pcm_zcr_sma_de_risetime']
# ----------------------------------------------------------------------------
# Balance columns
# ----------------------------------------------------------------------------
balance_signals_columns = ['mad', 'max', 'min']
balance_sdf_columns = ['SDF eigenvector 1',
                       'SDF eigenvector 2',
                       'SDF eigenvector 3']
balance_openSMILE_columns = ['pcm_RMSenergy_sma_de_range',
                             'pcm_zcr_sma_de_upleveltime90',
                             'pcm_zcr_sma_de_risetime']



# DO YOUR THING, CHRIS!!!





# ----------------------------------------------------------------------------
# Dictionary of selection columns
# ----------------------------------------------------------------------------
select_columns_dict = {'walk':[walk_pyGait_columns,
                               walk_signals_columns,
                               walk_sdf_columns,
                               walk_openSMILE_columns],
                       'balance':[balance_signals_columns,
                                  balance_sdf_columns,
                                   balance_openSMILE_columns]}

# ----------------------------------------------------------------------------
# Loop through tables, select columns, write to Synapse tables
# ----------------------------------------------------------------------------
import os
from mhealthx.xio import write_columns_to_synapse_table
path = os.environ['MHEALTHX_OUTPUT']

for table in tables:

    table = os.path.join(path, 'feature_tables',
                         'tap_row0_v0_9d44a388-5d7e-4271-8705-2faa66204486.csv')
    column_headers = ['tapping_results.json.ButtonRectLeft',
                      'accel_tapping.json.items']
    username = ''
    password = ''
    synapse_project_id = 'syn4899451'
    table_name = 'Contents written to ' + synapse_table
    write_columns_to_synapse_table(table, column_headers, synapse_project_id,
                                   table_name, username, password)


    table_name = 'voice{0}'.format(smile_string1)
