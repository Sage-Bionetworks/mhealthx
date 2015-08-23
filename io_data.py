#!/usr/bin/env python
"""
Input/output functions to read and write Synapse tables.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def read_synapse_table(table_synID, email, password):
    """
    Read data from a Synapse table.

    Parameters
    ----------
    table_synID : string
        Synapse ID for table
    email : string
        email address to access Synapse project
    password : string
        password corresponding to email address to Synapse project

    Returns
    -------
    dataframe : Pandas DataFrame
        Synapse table contents

    Examples
    --------
    >>> from extract.io_data import read_synapse_table
    >>> table_synID = 'syn4590865'
    >>> email = 'arno.klein@sagebase.org'
    >>> password = '*****'
    >>> dataframe = read_synapse_table(table_synID, email, password)

    """
    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(email, password)

    results = syn.tableQuery("select * from {0}".format(table_synID))
    dataframe = results.asDataFrame()

    return dataframe

def write_synapse_table(dataframe, project_synID, email, password,
                        schema_name=''):
    """
    Write data to a Synapse table.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Synapse table contents
    project_synID : string
        Synapse ID for project within which table is to be written
    email : string
        email address to access Synapse project
    password : string
        password corresponding to email address to Synapse project
    schema_name : string
        schema name of table

    Examples
    --------
    >>> from extract.io_data import read_synapse_table, write_synapse_table
    >>> input_table_synID = 'syn4590865'
    >>> project_synID = 'syn4899451'
    >>> email = 'arno.klein@sagebase.org'
    >>> password = '*****'
    >>> dataframe = read_synapse_table(input_table_synID, email, password)
    >>> schema_name = 'Contents of ' + input_table_synID
    >>> write_synapse_table(dataframe, project_synID, email, password, schema_name)

    """
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()
    syn.login(email, password)

    schema = Schema(name=schema_name, columns=as_table_columns(dataframe),
                    parent=project_synID)
    syn.store(Table(schema, dataframe))
