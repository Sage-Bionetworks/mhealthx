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
    schema : synapseclient.table.Schema
        Synapse table schema

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table
    >>> synapse_table_ID = 'syn4590865'
    >>> synapse_email = 'arno.klein@sagebase.org'
    >>> synapse_password = '*****'
    >>> dataframe, schema = read_synapse_table(synapse_table_ID, synapse_email, synapse_password)

    """
    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

    schema = syn.get(synapse_table_ID)

    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()

    return dataframe, schema


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


def get_synapse_file(dataframe, schema, synapse_table_ID, synapse_email, synapse_password):
    """
    Retrieve file in Synapse table.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Synapse table contents
    schema : synapseclient.table.Schema
        Synapse table schema
    synapse_email : string
        email address to access Synapse project
    synapse_password : string
        password corresponding to email address to Synapse project

    Returns
    -------
    #fileinfo : string
    #    name of file from Synapse table

    Examples
    --------
    >>> from mhealthx.io_data import read_synapse_table, get_synapse_file
    >>> input_synapse_table_ID = 'syn4590865'
    >>> synapse_email = 'arno.klein@sagebase.org'
    >>> synapse_password = '*****'
    >>> dataframe, schema = read_synapse_table(input_synapse_table_ID, synapse_email, synapse_password)
    >>> file = get_synapse_file(dataframe, schema, synapse_table_ID, synapse_email, synapse_password)

    """
    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(synapse_email, synapse_password)

    fileinfo = syn.downloadTableFile(schema, rowId=0, versionNumber=0, column='audio_audio.m4a', downloadLocation='.')

    return fileinfo


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
