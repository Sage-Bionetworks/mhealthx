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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start, device_motion)
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
    distance : float
        estimated change in position

    Examples
    --------
    >>> from mhealthx.extractors.dead_reckon import velocity_from_acceleration, position_from_velocity
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)
    >>> X, Y, Z, distance = position_from_velocity(Vx, Vy, Vz, At)

    """
    import numpy as np

    X = [0]
    Y = [0]
    Z = [0]
    for i in range(1, len(Vx)):
        dt = Vt[i] - Vt[i-1]
        X.append(X[i-1] + Vx[i] * dt)
        Y.append(Y[i-1] + Vy[i] * dt)
        Z.append(Z[i-1] + Vz[i] * dt)

    dX = np.sum(X)
    dY = np.sum(Y)
    dZ = np.sum(Z)
    distance = np.sqrt(dX**2 + dY**2 + dZ**2)

    return X, Y, Z, distance


def dead_reckon(Ax, Ay, Az, At):
    """
    Attempt dead reckoning (estimating position) from accelerometer data.

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
    x : list or numpy array of floats
        estimated position along x-axis
    y : list or numpy array of floats
        estimated position along y-axis
    z : list or numpy array of floats
        estimated position along z-axis
    distance : float
        estimated change in position

    Examples
    --------
    >>> from mhealthx.extractors.dead_reckon import dead_reckon
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> x, y, z, distance = dead_reckon(Ax, Ay, Az, At)

    """
    import numpy as np

    from mhealthx.extractors.dead_reckon import velocity_from_acceleration,\
        position_from_velocity

    #-------------------------------------------------------------------------
    # De-mean accelerometer readings:
    #-------------------------------------------------------------------------
    Ax -= np.mean(Ax)
    Ay -= np.mean(Ay)
    Az -= np.mean(Az)

    #-------------------------------------------------------------------------
    # Estimate velocity:
    #-------------------------------------------------------------------------
    Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)

    #-------------------------------------------------------------------------
    # Estimate position (dead reckoning):
    #-------------------------------------------------------------------------
    x, y, z, distance = position_from_velocity(Vx, Vy, Vz, At)

    print('distance = {0}'.format(distance))

    return x, y, z, distance


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
    >>> from mhealthx.extractors.dead_reckon import velocity_from_acceleration, position_from_velocity
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)
    >>> x, y, z, distance = position_from_velocity(Vx, Vy, Vz, At)
    >>> plotxyz(x, y, z, At, title='', limits=[])

    """
    import numpy as np
    import matplotlib.pyplot as plt

    t -= np.min(t)

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(t, x)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('X-axis ' + title)
    plt.ylabel(title)

    plt.subplot(3, 1, 2)
    plt.plot(t, y)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('Y-axis ' + title)
    plt.ylabel(title)

    plt.subplot(3, 1, 3)
    plt.plot(t, z)
    if limits:
        plt.ylim((limits[0], limits[1]))
    plt.title('Z-axis ' + title)
    plt.xlabel('Time (s)')
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
        position_from_velocity, plotxyz

    #-------------------------------------------------------------------------
    # Load accelerometer x,y,z values (and clip beginning from start):
    #-------------------------------------------------------------------------
    #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    #device_motion = False
    input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    device_motion = True
    start = 150
    Ax, Ay, Az, At, sample_rate, duration = read_accel_json(input_file, start, device_motion)

    #-------------------------------------------------------------------------
    # De-mean accelerometer readings:
    #-------------------------------------------------------------------------
    Ax -= np.mean(Ax)
    Ay -= np.mean(Ay)
    Az -= np.mean(Az)
    
    plotxyz(Ax, Ay, Az, At, 'Acceleration')
    
    #-------------------------------------------------------------------------
    # Estimate velocity:
    #-------------------------------------------------------------------------
    Vx, Vy, Vz = velocity_from_acceleration(Ax, Ay, Az, At)

    plotxyz(Vx, Vy, Vz, At, 'Velocity')
    
    #-------------------------------------------------------------------------
    # Estimate position (dead reckoning):
    #-------------------------------------------------------------------------
    X, Y, Z, distance = position_from_velocity(Vx, Vy, Vz, At)

    print('distance = {0}'.format(distance))

    plotxyz(X, Y, Z, At, 'Position')
    #plotxyz3d(X, Y, Z)




