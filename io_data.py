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

    results = syn.tableQuery("select * from {0}".format(synapse_table_ID))
    dataframe = results.asDataFrame()

    return dataframe

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

    schema = Schema(name=schema_name, columns=as_table_columns(dataframe),
                    parent=project_synID)
    syn.store(Table(schema, dataframe))
