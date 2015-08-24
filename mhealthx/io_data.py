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
                files.append(fileinfo['files'][0])
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
    >>> dataframe, schema = read_synapse_table(input_synapse_table_ID, synapse_email, synapse_password)
    >>> schema_name = 'Contents of ' + input_synapse_table_ID
    >>> write_synapse_table(dataframe, project_synID, synapse_email, synapse_password, schema_name)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

    schema = Schema(name=schema_name, columns=as_table_columns(dataframe),
                    parent=project_synID)
    syn.store(Table(schema, dataframe))


def m4a_to_wav(m4a_file, output_wav_file):
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
    >>> wav_file = '/desk/test.wav'
    >>> m4a_to_wav(m4a_file, wav_file)

    """
    import os
    from shutil import copyfile
    from mhealthx.thirdparty import audiotranscode

    if not m4a_file.endswith('m4a'):
        m4a_new = m4a_file + '.m4a'
        copyfile(m4a_file, m4a_new)
        m4a_file = m4a_new

    wav_file = m4a_file + '.wav'

    at = audiotranscode.AudioTranscode()
    at.transcode(m4a_file, wav_file)

    if not os.path.exists(wav_file):
        raise(IOError(wav_file + " not found"))

    return wav_file
