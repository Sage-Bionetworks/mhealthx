#!/usr/bin/env python
"""
This program implements the symbolic dynamic filtering (SDF) algorithm
as a time series feature extraction method, presented in the following paper:

Bahrampour, Soheil, Asok Ray, Soumalya Sarkar,
Thyagaraju Damarla, and Nasser M. Nasrabadi.
"Performance comparison of feature extraction algorithms for target detection
and classification." Pattern Recognition Letters 34, no. 16 (2013): 2126-2134.

Written by Soheil Bahrampour, August 2012
Rewritten in Python by Arno Klein, November 2015

Authors:
    - Soheil Bahrampour, August 2012
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com
"""


def max_entropy_partition(data, number_of_symbols):
    """
    Perform maximum entropy partitioning on given data.

    Parameters
    ----------
    data : numpy array
    number_of_symbols : integer
        number of symbols for symbolic dynamic filtering method

    Returns
    -------
    partition : numpy array

    Examples
    --------
    >>> # Example checked against original Matlab code:
    >>> import numpy as np
    >>> from mhealthx.extractors.symbolic_dynamic_filtering import max_entropy_partition
    >>> data = np.array([0.82487374,  0.21834812,  0.60166418,  0.76465689, 0.44819955,  0.72335342,  0.8710113,  0.73258881, 0.97047932,  0.5975058,  0.02474567,  0.38093561]) #np.random.random((3,4))
    >>> number_of_symbols = 4
    >>> partition = max_entropy_partition(data, number_of_symbols)
    array([ 0.38093561,  0.60166418,  0.76465689])

    """
    import numpy as np

    if isinstance(data, np.ndarray):
        pass
    elif isinstance(data, list):
        data = np.asarray(data)
    else:
        raise IOError("data should be a numpy array")

    # Change into long vector:
    data = data.flatten()

    # Sort and partition data:
    data = np.sort(data)
    len_data = np.float(len(data))

    #-------------------------------------------------------------------------
    # This code follows the article, resulting in K+1 partitions
    #-------------------------------------------------------------------------
    #npartitions = number_of_symbols + 1
    #partition = np.zeros(npartitions)
    #partition[0] = data[0]
    #partition[-1] = data[-1]
    #
    #for isymbol in range(1, number_of_symbols):
    #    partition[isymbol] = data[np.ceil(isymbol * len_data /
    #                                      number_of_symbols)]

    #-------------------------------------------------------------------------
    # This code matches the Matlab code output, resulting in K-1 partitions
    #-------------------------------------------------------------------------
    npartitions = number_of_symbols - 1
    partition = np.zeros(npartitions)

    for ipart in range(1, npartitions + 1):
        partition[ipart - 1] = data[np.floor(ipart * len_data /
                                             number_of_symbols) - 1]

    return partition


def generate_symbol_sequence(data, partition):
    """
    Generate symbol sequence of a given time series using given partition.

    Parameters
    ----------
    data : numpy array
    partition : numpy array

    Returns
    -------
    symbols : numpy array

    Examples
    --------
    >>> # Example checked against original Matlab code:
    >>> import numpy as np
    >>> from mhealthx.extractors.symbolic_dynamic_filtering import generate_symbol_sequence, max_entropy_partition
    >>> data = np.array([0.82487374,  0.21834812,  0.60166418,  0.76465689, 0.44819955,  0.72335342,  0.8710113,  0.73258881, 0.97047932,  0.5975058,  0.02474567,  0.38093561]) #np.random.random((3,4))
    >>> number_of_symbols = 4
    >>> partition = max_entropy_partition(data, number_of_symbols)
    >>> symbols = generate_symbol_sequence(data, partition)
    array([ 4.,  1.,  3.,  4.,  2.,  3.,  4.,  3.,  4.,  2.,  1.,  2.])

    """
    import numpy as np

    partition = np.hstack((partition, np.Inf))
    symbols = np.zeros(len(data))
    for i1 in range(len(data)):
        for i2 in range(len(partition)):
            if partition[i2] > data[i1]:
                symbols[i1] = i2 + 1
                break

    return symbols


def analyze_symbol_sequence(symbols, number_of_states, morph_matrix_flag):
    """
    Estimate the state transition probability ("morph") matrix of the
    probabilistic finite state automata, and its eigenvector
    corresponding to eigenvalue 1 by counting.

    NOTE: Currently the number of states is set to the number of symbols.

    Parameters
    ----------
    symbol_sequence : numpy array
    number_of_states : integer
    morph_matrix_flag : Boolean

    Returns
    -------
    morph_matrix : numpy array
    pvec : numpy array

    Examples
    --------
    >>> # Example checked against original Matlab code:
    >>> import numpy as np
    >>> from mhealthx.extractors.symbolic_dynamic_filtering import analyze_symbol_sequence, generate_symbol_sequence, max_entropy_partition
    >>> data = np.array([0.82487374,  0.21834812,  0.60166418,  0.76465689, 0.44819955,  0.72335342,  0.8710113,  0.73258881, 0.97047932,  0.5975058,  0.02474567,  0.38093561]) #np.random.random((3,4))
    >>> number_of_symbols = 4
    >>> partition = max_entropy_partition(data, number_of_symbols)
    >>> symbols = generate_symbol_sequence(data, partition)
    >>> number_of_states = number_of_symbols
    >>> morph_matrix_flag = True
    >>> morph_matrix, pvec = analyze_symbol_sequence(symbols, number_of_states, morph_matrix_flag)
    array([[ 0.        ,  0.5       ,  0.        ,  0.5       ],
           [ 0.33333333,  0.        ,  0.        ,  0.66666667],
           [ 0.33333333,  0.33333333,  0.        ,  0.33333333],
           [ 0.        ,  0.        ,  1.        ,  0.        ]])
    array([ 0.18181818,  0.18181818,  0.27272727,  0.36363636])
    """
    import numpy as np

    morph_matrix = np.zeros((number_of_states, number_of_states))
    pvec = np.zeros(number_of_states)

    for isymbol in range(1, len(symbols)):
        index1 = symbols[isymbol - 1] - 1
        index2 = symbols[isymbol] - 1
        pvec[index1] += 1
        if morph_matrix_flag:
            morph_matrix[index2, index1] += 1

    # Normalize the computed vector:
    pvec = pvec / np.sum(pvec)

    # Normalize each row of Matrix to make it a stochastic matrix:
    if morph_matrix_flag:
        for istate in range(number_of_states):
            row_sum = np.sum(morph_matrix[istate, :])
            if row_sum == 0:
                morph_matrix[istate, :] = pvec
            else:
                morph_matrix[istate, :] /= row_sum

    return morph_matrix, pvec


def sdf_features(data, number_of_symbols, pi_matrix_flag=False):
    """
    Extract symbolic dynamic filtering features from time series data.

    NOTE: Currently the number of states is set to the number of symbols.

    Parameters
    ----------
    data : numpy array
    number_of_symbols : integer
        number of symbols for symbolic dynamic filtering method
    pi_matrix_flag : Boolean
        feature as vectorized morph matrix (default: False)?

    Returns
    -------
    feature : numpy array

    Examples
    --------
    >>> # Example checked against original Matlab code:
    >>> import numpy as np
    >>> from mhealthx.extractors.symbolic_dynamic_filtering import sdf_features
    >>> data = np.array([0.82487374,  0.21834812,  0.60166418,  0.76465689, 0.44819955,  0.72335342,  0.8710113,  0.73258881, 0.97047932,  0.5975058,  0.02474567,  0.38093561]) #np.random.random((3,4))
    >>> number_of_symbols = 4
    >>> pi_matrix_flag = False
    >>> feature = sdf_features(data, number_of_symbols, pi_matrix_flag)
    array([ 0.18181818,  0.18181818,  0.27272727,  0.36363636])
    """
    import numpy as np

    from mhealthx.extractors.symbolic_dynamic_filtering import \
        max_entropy_partition, generate_symbol_sequence, \
        analyze_symbol_sequence

    # Generate partitions:
    partition = max_entropy_partition(data, number_of_symbols)

    # Generate symbols:
    symbols = generate_symbol_sequence(data, partition)

    # morph_matrix is the estimated Morph Matrix, and
    # pvec is the eigenvector corresponding to the eigenvalue 1:
    morph_matrix, pvec = analyze_symbol_sequence(symbols, number_of_symbols,
                                                 pi_matrix_flag)

    # Feature as vectorized morph matrix:
    if pi_matrix_flag:
        b = np.transpose(morph_matrix)
        feature = b.flatten()
    # Feature as state transition probability vector store:
    else:
        feature = pvec

    return feature
