#!/usr/bin/env python
"""
Input/output functions to read, write, and modify files and Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def read_synapse_table(synapse_table_ID, username='', password=''):
    """
    Read data from a Synapse table.

    Parameters
    ----------
    synapse_table_ID : string
        Synapse ID for table
    username : string
        Synapse username
    password : string
        Synapse password

    Returns
    -------
    dataframe : Pandas DataFrame
        Synapse table contents

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table
    >>> synapse_table_ID = 'syn4590865'
    >>> username = ''
    >>> password = ''
    >>> dataframe = read_synapse_table(synapse_table_ID, username, password)

    """
    import synapseclient

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()

    return dataframe


def read_synapse_table_files(synapse_table_ID, username='', password='',
                             column_name='', select_rows=[], output_path='.'):
    """
    Read data from a Synapse table.

    Parameters
    ----------
    synapse_table_ID : string
        Synapse ID for table
    username : string
        Synapse username
    password : string
        Synapse password
    column_name : string
        column header for fileIDs in Synapse table (if wish to download files)
    select_rows : list
        row indices, if retrieving column_name files (empty means all rows)
    output_path : string
        output path to store column_name files

    Returns
    -------
    dataframe : Pandas DataFrame
        Synapse table contents
    files : list of strings
        files from Synapse table (full paths to downloaded files)

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table_files
    >>> synapse_table_ID = 'syn4590865'
    >>> username = ''
    >>> password = ''
    >>> column_name = 'audio_audio.m4a'
    >>> select_rows = range(3)
    >>> output_path = '.'
    >>> dataframe, files = read_synapse_table_files(synapse_table_ID, username, password, column_name, select_rows, output_path)

    """
    import synapseclient

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Download Synapse table schema and dataframe:
    schema = syn.get(synapse_table_ID)
    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()
    files = []

    # Download Synapse files for fileIDs in specified table column:
    if column_name:
        if not select_rows:
            select_rows = range(dataframe.shape[0])
        for rowID in select_rows:
            fileinfo = syn.downloadTableFile(schema,
                                             rowId=rowID,
                                             versionNumber=0,
                                             column=column_name,
                                             downloadLocation=output_path)
            if fileinfo:
                files.append(fileinfo['path'])
            else:
                files.append('')

    return dataframe, files


def write_synapse_table(dataframe, project_synID, schema_name='',
                        username='', password=''):
    """
    Write data to a Synapse table.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Synapse table contents
    project_synID : string
        Synapse ID for project within which table is to be written
    schema_name : string
        schema name of table
    username : string
        Synapse username
    password : string
        Synapse password

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table, write_synapse_table
    >>> input_synapse_table_ID = 'syn4590865'
    >>> project_synID = 'syn4899451'
    >>> dataframe = read_synapse_table(input_synapse_table_ID, username, password)
    >>> schema_name = 'Contents of ' + input_synapse_table_ID
    >>> username = ''
    >>> password = ''
    >>> write_synapse_table(dataframe, project_synID, schema_name, username, password)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    dataframe.index = range(dataframe.shape[0])

    schema = Schema(name=schema_name, columns=as_table_columns(dataframe),
                    parent=project_synID, includeRowIdAndRowVersion=False)

    syn.store(Table(schema, dataframe))


def append_file_names(input_files, file_append):
    """
    Copy each file with an append to its file name.

    Parameters
    ----------
    input_files : list of strings
        full path to the input files
    file_append : string
        append to each file name

    Returns
    -------
    output_files : list of strings
        each string is the full path to a renamed file

    Examples
    --------
    >>> from mhealthx.io_data import append_file_names
    >>> input_files = ['/Users/arno/mhealthx_working/mHealthX/phonation_files/test.tmp']
    >>> file_append = '.m4a'
    >>> output_files = append_file_names(input_files, file_append)

    """
    import os
    from shutil import copyfile

    output_files = []

    # Loop through input files:
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise(IOError(input_file + " not found"))
        else:
            # Don't copy file if file already has correct append:
            if input_file.endswith(file_append):
                output_files.append(input_file)
            # Copy to a new file with appended file name:
            else:
                output_file = input_file + file_append
                copyfile(input_file, output_file)
                if not os.path.exists(output_file):
                    raise(IOError(output_file + " not found"))
                else:
                    output_files.append(output_file)

    return output_files


def convert_audio_files(input_files, file_append, command='avconv'):
    """
    Convert audio files to new format.

    Calls python-audiotranscode (and faad2)

    Parameters
    ----------
    input_files : list of strings
        full path to the input files
    file_append : string
        append to each file name to indicate output file format (e.g., '.wav')
    command : string
        executable command without arguments

    Returns
    -------
    output_files : list of strings
        each string is the full path to a renamed file

    Examples
    --------
    >>> from mhealthx.io_data import convert_audio_files
    >>> input_files = ['/Users/arno/mhealthx_working/mHealthX/phonation_files/test.m4a']
    >>> file_append = '.wav'
    >>> command = '/home/arno/software/audio/libav/avconv'
    >>> output_files = convert_audio_files(input_files, file_append)

    """
    import os
    from nipype.interfaces.base import CommandLine

    output_files = []

    # Loop through input files:
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise(IOError(input_file + " not found"))
        else:
            # Don't convert file if file already has correct append:
            if input_file.endswith(file_append):
                output_files.append(input_file)
            # Convert file to new format:
            else:
                output_file = input_file + file_append

                # Nipype command line wrapper over ffmpeg:
                cli = CommandLine(command = command)
                cli.inputs.args = ' '.join(['-i', input_file, output_file])
                cli.cmdline
                cli.run()

                if not os.path.exists(output_file):
                    raise(IOError(output_file + " not found"))
                else:
                    output_files.append(output_file)

    return output_files
