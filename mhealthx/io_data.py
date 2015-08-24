#!/usr/bin/env python
"""
Input/output functions to read and write Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def read_synapse_table(synapse_table_ID, synapse_email, synapse_password):
    """
    Read data from a Synapse table.

    Parameters
    ----------
    synapse_table_ID : string
        Synapse ID for table
    synapse_email : string
        email address to access Synapse project
    synapse_password : string
        password corresponding to email address to Synapse project

    Returns
    -------
    dataframe : Pandas DataFrame
        Synapse table contents

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table
    >>> synapse_table_ID = 'syn4590865'
    >>> synapse_email = 'arno.klein@sagebase.org'
    >>> synapse_password = '*****'
    >>> dataframe = read_synapse_table(synapse_table_ID, synapse_email, synapse_password)

    """
    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

    #schema = syn.get(synapse_table_ID)

    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()

    return dataframe


def read_synapse_table_files(synapse_table_ID,
                             synapse_email, synapse_password,
                             column_name='', select_rows=[], output_path='.'):
    """
    Read data from a Synapse table.

    Parameters
    ----------
    synapse_table_ID : string
        Synapse ID for table
    synapse_email : string
        email address to access Synapse project
    synapse_password : string
        password corresponding to email address to Synapse project
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
    >>> synapse_email = 'arno.klein@sagebase.org'
    >>> synapse_password = '*****'
    >>> column_name = 'audio_audio.m4a'
    >>> select_rows = range(3)
    >>> output_path = '.'
    >>> dataframe, files = read_synapse_table_files(synapse_table_ID, synapse_email, synapse_password, column_name, select_rows, output_path)

    """
    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

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


def write_synapse_table(dataframe, project_synID, synapse_email,
                        synapse_password, schema_name=''):
    """
    Write data to a Synapse table.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Synapse table contents
    project_synID : string
        Synapse ID for project within which table is to be written
    synapse_email : string
        email address to access Synapse project
    synapse_password : string
        password corresponding to email address to Synapse project
    schema_name : string
        schema name of table

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table, write_synapse_table
    >>> input_synapse_table_ID = 'syn4590865'
    >>> project_synID = 'syn4899451'
    >>> synapse_email = 'arno.klein@sagebase.org'
    >>> synapse_password = '*****'
    >>> dataframe = read_synapse_table(input_synapse_table_ID, synapse_email, synapse_password)
    >>> schema_name = 'Contents of ' + input_synapse_table_ID
    >>> write_synapse_table(dataframe, project_synID, synapse_email, synapse_password, schema_name)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

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


def m4a_to_wav(m4a_file):
    """
    Convert voice file from M4A (AAC) to WAV format.

    Calls python-audiotranscode (and faad2)

    Parameters
    ----------
    m4a_file : string
        M4A (AAC) file name
    output_wav_file : string
        WAV file name

    Returns
    -------
    wav_file : string
        WAV file name

    Examples
    --------
    >>> from mhealthx.io_data import m4a_to_wav
    >>> m4a_file = '/desk/test.tmp'
    >>> m4a_to_wav(m4a_file)

    """
    import os
    from mhealthx.thirdparty import audiotranscode

    wav_file = m4a_file + '.wav'

    at = audiotranscode.AudioTranscode()
    at.transcode(m4a_file, wav_file)

    if not os.path.exists(wav_file):
        raise(IOError(wav_file + " not found"))

    return wav_file
