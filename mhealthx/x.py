#!/usr/bin/env python
"""Currently unused functions.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def concatenate_dataframes_to_synapse_table(tables, synapse_project_id,
                                            table_name, username='',
                                            password=''):
    """
    Concatenate multiple pandas DataFrames with the same column names,
    and store as a Synapse table.

    Parameters
    ----------
    tables : list of pandas DataFrames
        each dataframe has the same column names
    synapse_project_id : string
        Synapse ID for project to which output is to be written
    table_name : string
        schema name of table
    username : string
        Synapse username (only needed once on a given machine)
    password : string
        Synapse password (only needed once on a given machine)

    Returns
    -------
    table_data : Pandas DataFrame
        output table data
    table_name : string
        schema name of table
    synapse_table_id : string
        Synapse ID for table
    synapse_project_id : string
        Synapse ID for project

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.x import concatenate_dataframes_to_synapse_table
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3'],
    >>>                     'D': ['D0', 'D1', 'D2', 'D3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7'],
    >>>                     'D': ['D4', 'D5', 'D6', 'D7']},
    >>>                     index=[0, 1, 2, 3])
    >>> tables = [df1, df2]
    >>> synapse_project_id = 'syn4899451'
    >>> table_name = 'Test to join tables'
    >>> username = ''
    >>> password = ''
    >>> table_data, table_name, synapse_table_id, synapse_project_id = concatenate_dataframes_to_synapse_table(tables, synapse_project_id, table_name, username, password)
    """
    import pandas as pd
    import synapseclient
    from synapseclient import Schema, Table, as_table_columns

    syn = synapseclient.Synapse()

    # Log in to Synapse:
    if username and password:
        syn.login(username, password)
    else:
        syn.login()

    # Raise an error if tables are not pandas DataFrames:
    if not type(tables[0]) == pd.DataFrame:
        raise IOError("'tables' should contain pandas DataFrames.")

    # Concatenate DataFrames, increasing the number of rows:
    table_data = pd.concat(tables, ignore_index=True)

    # Create table schema:
    schema = Schema(name=table_name, columns=as_table_columns(table_data),
                    parent=synapse_project_id)

    # Store as Synapse table:
    table = syn.store(Table(schema, table_data))
    synapse_table_id = table.tableId

    return table_data, table_name, synapse_table_id, synapse_project_id
