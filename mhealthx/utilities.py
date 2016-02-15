#!/usr/bin/env python
"""
Utility functions.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def run_command(command, flag1='', arg1='', flags='', args=[],
                flagn='', argn='', closing=''):
    """
    Run a generic command.

    Parameters
    ----------
    command : string
        name of command: "SMILExtract"
    flag1 : string
        optional first command line flag
    arg1 : string
        optional first argument, handy for iterating over in the pipeline
    flags : string or list of strings
        command line flags precede their respective args: ["-C", "-I", "-O"]
    args : string or list of strings
        command line arguments: ["config.conf", "input.wav", "output.csv"]
    flagn : string
        optional last command line flag
    argn : string
        optional last argument, handy for iterating over in the pipeline
    closing : string
        closing string in command

    Returns
    -------
    command_line : string
        full command line
    args : list of strings
        command line arguments
    arg1 : string
        optional first argument, handy for iterating over in the pipeline
    argn : string
        optional last argument, handy for iterating over in the pipeline

    Examples
    --------
    >>> from mhealthx.utilities import run_command
    >>> command = 'ls'
    >>> flag1 = ''
    >>> arg1 = ''
    >>> flags = ['-l', '']
    >>> args = ['/software', '/desk']
    >>> flagn = ''
    >>> argn = ''
    >>> closing = '' #'> test.txt'
    >>> command_line, args, arg1, argn = run_command(command, flag1, arg1, flags, args, flagn, argn, closing)

    """
    from nipype.interfaces.base import CommandLine

    # Join flags with args:
    if type(flags) == list and type(args) == list:
        flag_arg_tuples = zip(flags, args)
        flags_args = ''
        for flag_arg_tuple in flag_arg_tuples:
            flags_args = ' '.join([flags_args, ' '.join(flag_arg_tuple)])
    elif type(flags) == str and type(args) == str:
        flags_args = ' '.join([flags, args])
    else:
        raise IOError("-flags and -args should both be strings or lists")

    options = ' '.join([' '.join([flag1, arg1]), flags_args,
                        ' '.join([flagn, argn]), closing])
    command_line = ' '.join([command, options])

    # Nipype command line wrapper:
    try:
        cli = CommandLine(command=command)
        cli.inputs.args = options
        cli.cmdline
        cli.run()
    except:
        import traceback; traceback.print_exc()
        print("'{0}' unsuccessful".format(command_line))

    return command_line, args, arg1, argn


def plotxyz(x, y, z, t, title='', limits=[]):
    """
    Plot each accelerometer axis separately against relative time.

    Parameters
    ----------
    x : list or numpy array of floats
    y : list or numpy array of floats
    z : list or numpy array of floats
    t : list or numpy array of floats
        time points
    title : string
    limits : list of floats

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.utilities import plotxyz
    >>> plotxyz(ax, ay, az, t, title='', limits=[])

    """
    import numpy as np
    import matplotlib.pyplot as plt

    t -= np.min(t)

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(t, x)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('x-axis ' + title)
    plt.ylabel(title)

    plt.subplot(3, 1, 2)
    plt.plot(t, y)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('y-axis ' + title)
    plt.ylabel(title)

    plt.subplot(3, 1, 3)
    plt.plot(t, z)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('z-axis ' + title)
    plt.xlabel('Time (s)')
    plt.ylabel(title)
    plt.show()


def plotxyz3d(x, y, z, title=''):
    """
    Plot accelerometer readings in 3-D.

    (If trouble with "projection='3d'", try: ipython --pylab)

    Parameters
    ----------
    x : list or numpy array of floats
    y : list or numpy array of floats
    z : list or numpy array of floats
    title : string
        title

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> x, y, z = axyz
    >>> title = 'Test vectors'
    >>> from mhealthx.utilities import plotxyz3d
    >>> plotxyz3d(x, y, z, title)

    """
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #ax.plot(x, y, z) #, marker='o'
    ax.plot(x[1::], y[1::], z[1::], label='x, y, z') #, marker='o'
    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    #ax.set_xlim3d(0, 1)
    #ax.set_ylim3d(0, 1)
    #ax.set_zlim3d(0, 1)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.zlabel('z')
    plt.title(title)
    plt.show()


def plot_vectors(x, y, z, hx=[], hy=[], hz=[], title=''):
    """
    Plot vectors in 3-D from the origin [0,0,0].

    (If trouble with "projection='3d'", try: ipython --pylab)

    From: http://stackoverflow.com/questions/22867620/
                 putting-arrowheads-on-vectors-in-matplotlibs-3d-plot

    Parameters
    ----------
    x : list or numpy array of floats
        x-axis data for vectors
    y : list or numpy array of floats
        y-axis data for vectors
    z : list or numpy array of floats
        z-axis data for vectors
    hx : list or numpy array of floats
        x-axis data for vectors to highlight
    hy : list or numpy array of floats
        y-axis data for vectors to highlight
    hz : list or numpy array of floats
        z-axis data for vectors to highlight
    title : string
        title

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> x, y, z = axyz
    >>> hx, hy, hz = [[0,1],[0,1],[0,1]]
    >>> title = 'Test vectors'
    >>> from mhealthx.utilities import plot_vectors
    >>> plot_vectors(x, y, z, hx, hy, hz, title)

    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d

    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
            FancyArrowPatch.draw(self, renderer)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for i, x in enumerate(x):
        a = Arrow3D([0, x], [0, y[i]], [0, z[i]],
                    mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
        ax.add_artist(a)
    if hx:
        for i, hx in enumerate(hx):
            a = Arrow3D([0, hx], [0, hy[i]], [0, hz[i]],
                        mutation_scale=20, lw=1, arrowstyle="-|>", color="r")
            ax.add_artist(a)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    plt.title(title)
    plt.draw()
    plt.show()

def create_directory(path):
    import os
    if not os.path.exists(path):
        os.makedirs(path)
        print "Created directory: ", path


