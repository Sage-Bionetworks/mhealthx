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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
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


def gravity_compensate(q, acc):
    """
    Compensate the accelerometer readings from gravity.

    http://www.varesano.net/blog/fabio/simple-gravity-compensation-9-dom-imus

    #-------------------------------------------------------------------------
    # Compensate the accelerometer readings from gravity:
    #-------------------------------------------------------------------------
    # for i in range(len(data)):
    #     a = [data[i]['userAcceleration']['x'],
    #          data[i]['userAcceleration']['y'],
    #          data[i]['userAcceleration']['z']]
    #     g = [data[i]['gravity']['x'],
    #          data[i]['gravity']['y'],
    #          data[i]['gravity']['z']]
    #     q = [data[i]['attitude']['x'],
    #          data[i]['attitude']['y'],
    #          data[i]['attitude']['z'],
    #          data[i]['attitude']['w']]
    #     a = gravity_compensate(q, a) # rotate a into Earth frame of reference

    Parameters
    ----------
    q : list or numpy array of floats
        quaternion representing orientation
    acc : list or numpy array of floats
        readings coming from an accelerometer expressed in g

    Returns
    -------
    dyn_acc : list of floats
        3d vector representing dynamic acceleration expressed in g

    Examples
    --------
    >>> from mhealthx.extractors.dead_reckon import gravity_compensate
    >>> q = 
    >>> acc = 
    >>> dyn_acc = gravity_compensate(q, acc)

    """
    g = [0.0, 0.0, 0.0]
    
    # Get expected direction of gravity:
    g[0] = 2 * (q[1] * q[3] - q[0] * q[2])
    g[1] = 2 * (q[0] * q[1] + q[2] * q[3])
    g[2] = q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]
    
    # Compensate accelerometer readings with expected direction of gravity:
    dyn_acc = [acc[0] - g[0], acc[1] - g[1], acc[2] - g[2]]

    return dyn_acc


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
    input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
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




