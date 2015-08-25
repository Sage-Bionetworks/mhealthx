#!/usr/bin/env python
"""Run feature extraction software.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def opensmile(input_files, config_file, output_append):
    """
    Run openSMILE's SMILExtract on input files to extract audio features.

    SMILExtract -C config/my_configfile.conf -I input_file.wav -O output_file

    Parameters
    ----------
    input_files : list of strings
        full path to the input files
    config_file : string
        path to openSMILE configuration file
    output_append : string
        append to each file name to indicate output file format (e.g., '.csv')

    Returns
    -------
    output_files : list of strings
        each string is the full path to a renamed file

    Examples
    --------
    >>> from mhealthx.features import opensmile
    >>> input_files = ['/home/arno/mhealthx_working/mHealthX/phonation_files/test.wav']
    >>> config_file = '/home/arno/software/audio/openSMILE/config/IS13_ComParE.conf'
    >>> output_append = '.csv'
    >>> output_files = opensmile(input_files, config_file)

    """
    import os
    from nipype.interfaces.base import CommandLine

    output_files = []

    # Loop through input files:
    for input_file in input_files:
        if not os.path.exists(input_file):
            raise(IOError(input_file + " not found"))
        else:

            output_file = input_file + output_append

            # Nipype command line wrapper over openSMILE:
            cli = CommandLine(command = 'SMILExtract')
            cli.inputs.args = ' '.join(['-C', config_file,
                                        '-I', input_file,
                                        '-O', output_file])
            cli.cmdline
            cli.run()

            if not os.path.exists(output_file):
                raise(IOError(output_file + " not found"))
            else:
                output_files.append(output_file)

    return output_files
