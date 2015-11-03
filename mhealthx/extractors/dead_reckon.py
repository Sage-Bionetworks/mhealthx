#!/usr/bin/env python
"""
Attempt dead reckoning (estimating position) from accelerometer data.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def velocity_from_acceleration(Ax, Ay, Az, At):
    """
    Estimate velocity from accelerometer readings.

    Parameters
    ----------
    Ax : list or numpy array of floats
        accelerometer x-axis data
    Ay : list or numpy array of floats
        accelerometer y-axis data
    Az : list or numpy array of floats
        accelerometer z-axis data
    At : list or numpy array of floats
        accelerometer time points

    Returns
    -------
    Vx : list or numpy array of floats
        estimated velocity along x-axis
    Vy : list or numpy array of floats
        estimated velocity along y-axis
    Vz : list or numpy array of floats
        estimated velocity along z-axis

    Examples
    --------
    >>> from mhealthx.extractors.dead_reckon import velocity_from_acceleration
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-90f7096a-84ac-4f29-a4d1-236ef92c3d262549858224214804657.tmp'
    >>> start = 150
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start)
    >>> Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)

    """
    Vx = [0]
    Vy = [0]
    Vz = [0]
    for i in range(1, len(Ax)):
        dt = At[i] - At[i-1]
        Vx.append(Vx[i-1] + Ax[i] * dt)
        Vy.append(Vy[i-1] + Ay[i] * dt)
        Vz.append(Vz[i-1] + Az[i] * dt)

    return Vx, Vy, Vz


def position_from_velocity(Vx, Vy, Vz, Vt):
    """
    Estimate position from velocity.

    Parameters
    ----------
    Vx : list or numpy array of floats
        estimated velocity along x-axis
    Vy : list or numpy array of floats
        estimated velocity along y-axis
    Vz : list or numpy array of floats
        estimated velocity along z-axis
    Vt : list or numpy array of floats
        accelerometer time points

    Returns
    -------
    X : list or numpy array of floats
        estimated position along x-axis
    Y : list or numpy array of floats
        estimated position along y-axis
    Z : list or numpy array of floats
        estimated position along z-axis

    Examples
    --------
    >>> from mhealthx.extractors.dead_reckon import velocity_from_acceleration, distance_from_velocity
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-90f7096a-84ac-4f29-a4d1-236ef92c3d262549858224214804657.tmp'
    >>> start = 150
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start)
    >>> Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)
    >>> X, Y, Z = distance_from_velocity(Vx, Vy, Vz, At)

    """
    X = [0]
    Y = [0]
    Z = [0]
    for i in range(1, len(Vx)):
        dt = Vt[i] - Vt[i-1]
        X.append(X[i-1] + Vx[i] * dt)
        Y.append(Y[i-1] + Vy[i] * dt)
        Z.append(Z[i-1] + Vz[i] * dt)

    return X, Y, Z


def plotxyz(x, y, z, title='', limits=[]):
    """
    Plot each accelerometer axis separately.

    Parameters
    ----------
    x : list or numpy array of floats
    y : list or numpy array of floats
    z : list or numpy array of floats
    title : string
    limits : list of floats

    """
    import matplotlib.pyplot as plt

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(x)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('X-axis ' + title)
    #plt.xlabel('Time')
    plt.ylabel(title)

    plt.subplot(3, 1, 2)
    plt.plot(y)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('Y-axis ' + title)
    #plt.xlabel('Time')
    plt.ylabel(title)

    plt.subplot(3, 1, 3)
    plt.plot(z)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('Z-axis ' + title)
    plt.xlabel('Time')
    plt.ylabel(title)
    plt.show()


def plotxyz3d(x, y, z):
    """
    Plot accelerometer readings in 3-D.

    Parameters
    ----------
    x : list or numpy array of floats
    y : list or numpy array of floats
    z : list or numpy array of floats

    """
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #ax.plot(x, y, z) #, marker='o'
    ax.plot(x[1::], y[1::], z[1::], label='x, y, z') #, marker='o'
    ax.legend()
    #ax.xlabel('x')
    #ax.ylabel('y')
    #ax.zlabel('z')
    #ax.set_xlim3d(0, 1)
    #ax.set_ylim3d(0, 1)
    #ax.set_zlim3d(0, 1)
    plt.show()


# ============================================================================
if __name__ == '__main__':

    import numpy as np

    from mhealthx.xio import read_accel_json
    from mhealthx.extractors.dead_reckon import velocity_from_acceleration,\
        position_from_velocity, plotxyz, plotxyz3d

    #-------------------------------------------------------------------------
    # Load accelerometer x,y,z values (and clip beginning from start):
    #-------------------------------------------------------------------------
    #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-90f7096a-84ac-4f29-a4d1-236ef92c3d262549858224214804657.tmp'
    start = 150
    Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start)

    #-------------------------------------------------------------------------
    # De-mean accelerometer readings:
    #-------------------------------------------------------------------------
    Ax -= np.mean(Ax)
    Ay -= np.mean(Ay)
    Az -= np.mean(Az)
    
    plotxyz(Ax, Ay, Az, 'Acceleration')
    
    #-------------------------------------------------------------------------
    # Estimate velocity:
    #-------------------------------------------------------------------------
    Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)

    plotxyz(Vx, Vy, Vz, 'Velocity')
    
    #-------------------------------------------------------------------------
    # Estimate position (dead reckoning):
    #-------------------------------------------------------------------------
    X, Y, Z = position_from_velocity(Vx, Vy, Vz, At)
    
    plotxyz(X, Y, Z, 'Position')
    #plotxyz3d(X, Y, Z)




