#!/usr/bin/env python
"""Run feature extraction software.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def opensmile(wav_file, config_file, file_append='.csv',
              command='SMILExtract'):
    """
    Run openSMILE's SMILExtract on input file to extract audio features.

    SMILExtract -C config/my_configfile.conf -I input.wav -O output.csv

    Parameters
    ----------
    wav_file : string
        full path to the input file
    command : string
        command without arguments
    config_file : string
        path to openSMILE configuration file
    file_append : string
        append to each file name to indicate output file format (e.g., '.csv')
    command : string
        executable command without arguments

    Returns
    -------
    feature_file : string
        output table of features (full path)

    Examples
    --------
    >>> from mhealthx.features import opensmile
    >>> wav_file = ['/home/arno/mhealthx_working/mHealthX/phonation_files/test.wav']
    >>> config_file = '/home/arno/software/audio/openSMILE/config/IS13_ComParE.conf'
    >>> file_append = '.csv'
    >>> command = '/home/arno/software/audio/openSMILE/SMILExtract'
    >>> feature_file = opensmile(wav_file, config_file, file_append, command)

    """
    import os
    from nipype.interfaces.base import CommandLine

    if not os.path.exists(wav_file):
        raise(IOError(wav_file + " not found"))
    else:
        feature_file = wav_file + file_append

        # Nipype command line wrapper over openSMILE:
        cli = CommandLine(command = command)
        cli.inputs.args = ' '.join(['-C', config_file,
                                    '-I', wav_file,
                                    '-O', feature_file])
        cli.cmdline
        cli.run()

        if not os.path.exists(feature_file):
            raise(IOError(feature_file + " not found"))

    return feature_file


def opensmile_features_to_synapse(in_files, synapse_project_id,
                                  table_name, username, password):
    """
    Save openSMILE's SMILExtract audio features to a Synapse table.

    Parameters
    ----------
    in_files : list of strings
        full path to the input files
    synapse_project_id : string
        Synapse ID for project to which table is to be written
    table_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    table_data : Pandas DataFrame
        output table
    table_name : string
        schema name of table
    synapse_table_id : string
        Synapse table ID

    Examples
    --------
    >>> from mhealthx.features import opensmile_features_to_synapse
    >>> in_files = []
    >>> synapse_project_id = 'syn4899451'
    >>> table_name = 'Phonation openSMILE feature table'
    >>> username = ''
    >>> password = ''
    >>> table_data, table_name, synapse_table_id = opensmile_features_to_synapse(in_files, synapse_project_id, table_name)

    """
    import pandas as pd
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    from mhealthx.io_data import concatenate_tables_to_synapse_table as cat

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Store each file as a row in a Synapse table:
    first = True
    for in_file in in_files:
        if first:
            df_data = pd.read_csv(in_file)
            first = False
        else:
            df_data = pd.read_csv(in_file)

    table_data, project_id = cat(frames, synapse_project_id, table_name,
                                 username, password)

    # Create table schema:
    schema = Schema(name=table_name, columns=as_table_columns(table_data),
                    parent=synapse_project_id)

    # Store as Synapse table:
    table = syn.store(Table(schema, table_data))
    synapse_table_id = str(table.tableId)

    return table_data, table_name, synapse_table_id
