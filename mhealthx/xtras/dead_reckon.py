#!/usr/bin/env python
"""
Attempt dead reckoning (estimating position) from accelerometer data.

The accelerometer data are too noisy!

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def velocity_from_acceleration(ax, ay, az, t):
    """
    Estimate velocity from accelerometer readings.

    Parameters
    ----------
    ax : list or numpy array of floats
        accelerometer x-axis data
    ay : list or numpy array of floats
        accelerometer y-axis data
    az : list or numpy array of floats
        accelerometer z-axis data
    t : list or numpy array of floats
        accelerometer time points

    Returns
    -------
    vx : list or numpy array of floats
        estimated velocity along x-axis
    vy : list or numpy array of floats
        estimated velocity along y-axis
    vz : list or numpy array of floats
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
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> vx, vy, vz = velocity_from_acceleration(ax, ay, az, t)

    """
    vx = [0]
    vy = [0]
    vz = [0]
    for i in range(1, len(ax)):
        dt = t[i] - t[i-1]
        vx.append(vx[i-1] + ax[i] * dt)
        vy.append(vy[i-1] + ay[i] * dt)
        vz.append(vz[i-1] + az[i] * dt)

    return vx, vy, vz


def position_from_velocity(vx, vy, vz, t):
    """
    Estimate position from velocity.

    Parameters
    ----------
    vx : list or numpy array of floats
        estimated velocity along x-axis
    vy : list or numpy array of floats
        estimated velocity along y-axis
    vz : list or numpy array of floats
        estimated velocity along z-axis
    t : list or numpy array of floats
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
    >>> from mhealthx.extractors.dead_reckon import velocity_from_acceleration, position_from_velocity
    >>> from mhealthx.xio import read_accel_json
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> start = 150
    >>> device_motion = True
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> vx, vy, vz = velocity_from_acceleration(ax, ay, az, t)
    >>> x, y, z, distance = position_from_velocity(vx, vy, vz, t)

    """
    import numpy as np

    x = [0]
    y = [0]
    z = [0]
    for i in range(1, len(vx)):
        dt = t[i] - t[i-1]
        x.append(x[i-1] + vx[i] * dt)
        y.append(y[i-1] + vy[i] * dt)
        z.append(z[i-1] + vz[i] * dt)

    dx = np.sum(x)
    dy = np.sum(y)
    dz = np.sum(z)
    distance = np.sqrt(dx**2 + dy**2 + dz**2)

    return x, y, z, distance


def dead_reckon(ax, ay, az, t):
    """
    Attempt dead reckoning (estimating position) from accelerometer data.

    The accelerometer data are too noisy!

    Parameters
    ----------
    ax : list or numpy array of floats
        accelerometer x-axis data
    ay : list or numpy array of floats
        accelerometer y-axis data
    az : list or numpy array of floats
        accelerometer z-axis data
    t : list or numpy array of floats
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
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> x, y, z, distance = dead_reckon(ax, ay, az, t)

    """
    import numpy as np

    from mhealthx.extractors.dead_reckon import velocity_from_acceleration,\
        position_from_velocity

    #-------------------------------------------------------------------------
    # De-mean accelerometer readings:
    #-------------------------------------------------------------------------
    ax -= np.mean(ax)
    ay -= np.mean(ay)
    az -= np.mean(az)

    #-------------------------------------------------------------------------
    # Estimate velocity:
    #-------------------------------------------------------------------------
    vx, vy, vz = velocity_from_acceleration(ax, ay, az, t)

    #-------------------------------------------------------------------------
    # Estimate position (dead reckoning):
    #-------------------------------------------------------------------------
    x, y, z, distance = position_from_velocity(vx, vy, vz, t)

    print('distance = {0}'.format(distance))

    return x, y, z, distance


# ============================================================================
if __name__ == '__main__':

    import numpy as np

    from mhealthx.xio import read_accel_json
    from mhealthx.extractors.dead_reckon import velocity_from_acceleration,\
        position_from_velocity
    from mhealthx.utilities import plotxyz

    #-------------------------------------------------------------------------
    # Load accelerometer x,y,z values (and clip beginning from start):
    #-------------------------------------------------------------------------
    #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    #device_motion = False
    input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    device_motion = True
    start = 150
    t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    ax, ay, az = axyz

    #-------------------------------------------------------------------------
    # De-mean accelerometer readings:
    #-------------------------------------------------------------------------
    ax -= np.mean(ax)
    ay -= np.mean(ay)
    az -= np.mean(az)
    
    plotxyz(ax, ay, az, t, 'Acceleration')
    
    #-------------------------------------------------------------------------
    # Estimate velocity:
    #-------------------------------------------------------------------------
    vx, vy, vz = velocity_from_acceleration(ax, ay, az, t)

    plotxyz(vx, vy, vz, t, 'Velocity')
    
    #-------------------------------------------------------------------------
    # Estimate position (dead reckoning):
    #-------------------------------------------------------------------------
    x, y, z, distance = position_from_velocity(vx, vy, vz, t)

    print('distance = {0}'.format(distance))

    plotxyz(x, y, z, t, 'Position')
    #plotxyz3d(x, y, z)




