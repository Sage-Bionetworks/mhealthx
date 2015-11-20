#!/usr/bin/env python
"""
This program implements some of the feature extraction equations from:

"iGAIT: An interactive accelerometer based gait analysis system"
Mingjing Yang, Huiru Zheng, Haiying Wang, Sally McClean, Dave Newell. 2012.
Computer methods and programs in biomedicine 108:715-723.
DOI:10.1016/j.cmpb.2012.04.004
http://www.ncbi.nlm.nih.gov/pubmed/22575802

iGait was written as a Matlab file and compiled as a Windows application.
It assumes a fixed accelerometer position, and derived heel strike timings
from an assumed anterior-posterior orientation along the y-axis.

iGAIT inputs ::
    - sample rate
    - threshold (anterior-posterior acceleration, to detect heel contact)
    - distance

iGAIT features ::
    - spatio-temporal features, from estimates of heel strikes:
        - cadence = number of steps divided by walking time
        - distance-based measures (mean step length, velocity)
    - regularity and symmetry (each direction):
        - step/stride regularity
        - symmetry
    - root mean square (each direction)
    - spectral features (each direction):
        - integral of the power spectral density (IPSD)
        - main frequency: frequency with the maximum value of PSD
        - frequencies when PSD is cumulated (CPSD)

pyGait functions compute all of iGAIT's features except spectral features::
    - gait_features() for all heel strike-based estimates:
        - cadence
        - mean step length and velocity (if distance supplied)
        - regularity and symmetry (each direction)
    - root_mean_square():
        - root mean square (each direction)

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com
    - Elias Chaibub-Neto, 2015 (neto@sagebase.org)

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def walk_direction_attitude(ax, ay, az, uw, ux, uy, uz, plot_test=False):
    """
    Estimate local walk (not cardinal) directions by rotation with attitudes.

    Translated by Arno Klein from Elias Chaibub-Neto's R code.

    Parameters
    ----------
    ax : list or numpy array
        x-axis accelerometer data
    ay : list or numpy array
        y-axis accelerometer data
    az : list or numpy array
        z-axis accelerometer data
    uw : list or numpy array
        w of attitude quaternion
    ux : list or numpy array
        x of attitude quaternion
    uy : list or numpy array
        y of attitude quaternion
    uz : list or numpy array
        z of attitude quaternion
    plot_test : Boolean
        plot rotated vectors?

    Returns
    -------
    directions : list of lists of three floats
        unit vector of local walk (not cardinal) direction at each time point

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 0
    >>> t, axyz, gxyz, wxyz, rxyz, sample_rate, duration = read_accel_json(input_file, device_motion, start)
    >>> ax, ay, az = axyz
    >>> uw, ux, uy, uz = wxyz
    >>> from mhealthx.extractors.pyGait import walk_direction_attitude
    >>> plot_test = True
    >>> directions = walk_direction_attitude(ax, ay, az, uw, ux, uy, uz, plot_test)
    """
    import numpy as np

    def quaternion_rotation_matrix(q):
        """Rotation matrix from a quaternion"""
        r11 = q[0]**2 + q[1]**2 - q[2]**2 - q[3]**2
        r12 = 2 * q[1] * q[2] + 2 * q[0] * q[3]
        r13 = 2 * q[1] * q[3] - 2 * q[0] * q[2]
        r21 = 2 * q[1] * q[2] - 2 * q[0] * q[3]
        r22 = q[0]**2 - q[1]**2 + q[2]**2 - q[3]**2
        r23 = 2 * q[2] * q[3] + 2 * q[0] * q[1]
        r31 = 2 * q[1] * q[3] + 2 * q[0] * q[2]
        r32 = 2 * q[2] * q[3] - 2 * q[0] * q[1]
        r33 = q[0]**2 - q[1]**2 - q[2]**2 + q[3]**2

        rot = np.array(((r11, r12, r13), (r21, r22, r23), (r31, r32, r33)))

        return rot

    def rotate_with_attitude(attitude, acceleration):
        """Rotate acceleration with attitude quaternion"""
        rot = quaternion_rotation_matrix(attitude)
        rotated = np.dot(rot, acceleration)

        return rotated

    directions = []
    for i, x in enumerate(ax):
        attitude = [uw[i], ux[i], uy[i], uz[i]]
        acceleration = [x, ay[i], az[i]]
        directions.append(rotate_with_attitude(attitude, acceleration))

    # Plot vectors:
    if plot_test:
        from mhealthx.utilities import plot_vectors
        dx = [x[0] for x in directions]
        dy = [x[1] for x in directions]
        dz = [x[2] for x in directions]
        title = 'Acceleration vectors + attitude-rotated vectors'
        plot_vectors(ax, ay, az, dx, dy, dz, title)

    return directions


def walk_direction_preheel(ax, ay, az, t, sample_rate, 
                           stride_fraction=1.0/8.0, threshold=0.5,
                           order=4, cutoff=5, plot_test=False):
    """
    Estimate local walk (not cardinal) direction with pre-heel strike phase.

    Inspired by Nirupam Roy's B.E. thesis: "WalkCompass:
    Finding Walking Direction Leveraging Smartphone's Inertial Sensors,"
    this program derives the local walk direction vector from the end
    of the primary leg's stride, when it is decelerating in its swing.
    While the WalkCompass relies on clear heel strike signals across the
    accelerometer axes, this program just uses the most prominent strikes,
    and estimates period from the real part of the FFT of the data.

    NOTE::
        This algorithm computes a single walk direction, and could compute
        multiple walk directions prior to detected heel strikes, but does
        NOT estimate walking direction for every time point, like
        walk_direction_attitude().

    Parameters
    ----------
    ax : list or numpy array
        x-axis accelerometer data
    ay : list or numpy array
        y-axis accelerometer data
    az : list or numpy array
        z-axis accelerometer data
    t : list or numpy array
        accelerometer time points
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    stride_fraction : float
        fraction of stride assumed to be deceleration phase of primary leg
    threshold : float
        ratio to the maximum value of the summed acceleration across axes
    plot_test : Boolean
        plot most prominent heel strikes?

    Returns
    -------
    direction : numpy array of three floats
        unit vector of local walk (not cardinal) direction

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.extractors.pyGait import walk_direction_preheel
    >>> threshold = 0.5
    >>> stride_fraction = 1.0/8.0
    >>> order = 4
    >>> cutoff = max([1, sample_rate/10])
    >>> plot_test = True
    >>> direction = walk_direction_preheel(ax, ay, az, t, sample_rate, stride_fraction, threshold, order, cutoff, plot_test)

    """
    import numpy as np

    from mhealthx.extractors.pyGait import heel_strikes
    from mhealthx.signals import compute_interpeak

    # Sum of absolute values across accelerometer axes:
    data = np.abs(ax) + np.abs(ay) + np.abs(az)

    # Find maximum peaks of smoothed data:
    plot_test2 = False
    dummy, ipeaks_smooth = heel_strikes(data, sample_rate, threshold,
                                        order, cutoff, plot_test2, t)

    # Compute number of samples between peaks using the real part of the FFT:
    interpeak = compute_interpeak(data, sample_rate)
    decel = np.int(np.round(stride_fraction * interpeak))

    # Find maximum peaks close to maximum peaks of smoothed data:
    ipeaks = []
    for ipeak_smooth in ipeaks_smooth:
        ipeak = np.argmax(data[ipeak_smooth - decel:ipeak_smooth + decel])
        ipeak += ipeak_smooth - decel
        ipeaks.append(ipeak)

    # Plot peaks and deceleration phase of stride:
    if plot_test:
        from pylab import plt
        if isinstance(t, list):
            tplot = np.asarray(t) - t[0]
        else:
            tplot = np.linspace(0, np.size(ax), np.size(ax))
        idecel = [x - decel for x in ipeaks]
        plt.plot(tplot, data, 'k-', tplot[ipeaks], data[ipeaks], 'rs')
        for id in idecel:
            plt.axvline(x=tplot[id])
        plt.title('Maximum stride peaks')
        plt.show()

    # Compute the average vector for each deceleration phase:
    vectors = []
    for ipeak in ipeaks:
        decel_vectors = np.asarray([[ax[i], ay[i], az[i]]
                                    for i in range(ipeak - decel, ipeak)])
        vectors.append(np.mean(decel_vectors, axis=0))

    # Compute the average deceleration vector and take the opposite direction:
    direction = -1 * np.mean(vectors, axis=0)

    # Return the unit vector in this direction:
    direction /= np.sqrt(direction.dot(direction))

    # Plot vectors:
    if plot_test:
        from mhealthx.utilities import plot_vectors
        dx = [x[0] for x in vectors]
        dy = [x[1] for x in vectors]
        dz = [x[2] for x in vectors]
        hx, hy, hz = direction
        title = 'Average deceleration vectors + estimated walk direction'
        plot_vectors(dx, dy, dz, [hx], [hy], [hz], title)

    return direction


def project_axes(vectors, unit_vectors):
    """
    Project vectors on unit vectors.

    Parameters
    ----------
    vectors : list of lists of x, y, z coordinates or numpy array equivalent
    unit_vectors : list of lists of x, y, z coordinates (or numpy arrays)
        unit vectors to project vectors onto

    Returns
    -------
    projection_vectors : list of lists of x, y, z coordinates
        vectors projected onto unit vectors

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> vectors = zip(axyz[0], axyz[1], axyz[2])
    >>> vectors = [vectors[0], vectors[1], vectors[2]]
    >>> from mhealthx.extractors.pyGait import project_axes
    >>> unit_vectors = [1, 1, 1]
    >>> projection_vectors = project_axes(vectors, unit_vectors)

    """
    import numpy as np

    projection_vectors = []
    for i, v in enumerate(vectors):
        unit_vector = np.asarray(unit_vectors[i])
        magnitude = np.asarray(v).dot(unit_vector)
        projection_vector = magnitude * unit_vector
        projection_vectors.append(projection_vector.tolist())

    return projection_vectors


def project_walk_direction_attitude(ax, ay, az, uw, ux, uy, uz):
    """
    Project accelerometer data on local walk direction by attitude rotation.

    Parameters
    ----------
    ax : list or numpy array
        x-axis accelerometer data
    ay : list or numpy array
        y-axis accelerometer data
    az : list or numpy array
        z-axis accelerometer data
    uw : list or numpy array
        w of attitude quaternion
    ux : list or numpy array
        x of attitude quaternion
    uy : list or numpy array
        y of attitude quaternion
    uz : list or numpy array
        z of attitude quaternion

    Returns
    -------
    px : numpy array
        accelerometer data along x axis projected on unit vector
    py : numpy array
        accelerometer data along y axis projected on unit vector
    pz : numpy array
        accelerometer data along z axis projected on unit vector

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 0
    >>> t, axyz, gxyz, wxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> uw, ux, uy, uz = wxyz
    >>> from mhealthx.extractors.pyGait import project_walk_direction_attitude
    >>> px, py, pz = project_walk_direction_attitude(ax, ay, az, uw, ux, uy, uz)

    """
    from mhealthx.extractors.pyGait import walk_direction_attitude, \
        project_axes

    directions = walk_direction_attitude(ax, ay, az, uw, ux, uy, uz)

    vectors = project_axes(zip(ax, ay, az), directions)

    px = [x[0] for x in vectors]
    py = [x[1] for x in vectors]
    pz = [x[2] for x in vectors]

    return px, py, pz


def project_walk_direction_preheel(ax, ay, az, t, sample_rate,
                                   stride_fraction, threshold, order, cutoff):
    """
    Project accelerometer data on local walk (not cardinal) direction.

    NOTE::
        This calls walk_direction_preheel(), which computes a single walk
        direction. It does NOT estimate walking direction for every time
        point, like walk_direction_attitude().

    Parameters
    ----------
    ax : numpy array
        accelerometer data along x axis
    ay : numpy array
        accelerometer data along y axis
    az : numpy array
        accelerometer data along z axis
    t : list or numpy array
        accelerometer time points
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    stride_fraction : float
        fraction of stride assumed to be deceleration phase of primary leg
    threshold : float
        ratio to the maximum summed acceleration to extract peaks
    order : integer
        order of the Butterworth filter
    cutoff : integer
        cutoff frequency of the Butterworth filter (Hz)

    Returns
    -------
    px : numpy array
        accelerometer data along x axis projected on unit vector
    py : numpy array
        accelerometer data along y axis projected on unit vector
    pz : numpy array
        accelerometer data along z axis projected on unit vector

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.extractors.pyGait import project_walk_direction_preheel
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> stride_fraction = 1.0/8.0
    >>> threshold = 0.5
    >>> order = 4
    >>> cutoff = max([1, sample_rate/10])
    >>> px, py, pz = project_walk_direction_preheel(ax, ay, az, t, sample_rate, stride_fraction, threshold, order, cutoff)

    """
    from mhealthx.extractors.pyGait import walk_direction_preheel, \
        project_axes

    directions = walk_direction_preheel(ax, ay, az, t, sample_rate,
                                       stride_fraction, threshold, order,
                                       cutoff, False)

    vectors = project_axes(zip(ax, ay, az), directions)

    px = [x[0] for x in vectors]
    py = [x[1] for x in vectors]
    pz = [x[2] for x in vectors]

    return px, py, pz


def heel_strikes(data, sample_rate, threshold=0.2, order=4, cutoff=5,
                 plot_test=False, t=None):
    """
    Estimate heel strike times between sign changes in accelerometer data.

    The iGAIT software assumes that the y-axis is anterior-posterior,
    and restricts some feature extraction to this orientation.
    In this program, we compute heel strikes for an arbitrary axis.

    Re: heel strikes (from Yang, et al., 2012):
    "The heel contacts are detected by peaks preceding the sign change of
    AP acceleration [3]. In order to automatically detect a heel contact
    event, firstly, the AP acceleration is low pass filtered by the 4th
    order zero lag Butterworth filter whose cut frequency is set to 5 Hz.
    After that, transitional positions where AP acceleration changes from
    positive to negative can be identified. Finally the peaks of AP
    acceleration preceding the transitional positions, and greater than
    the product of a threshold and the maximum value of the AP acceleration
    are denoted as heel contact events...
    This threshold is defined as the ratio to the maximum value
    of the AP acceleration, for example 0.5 indicates the threshold is set
    at 50% of the maximum AP acceleration. Its default value is set to 0.4
    as determined experimentally in this paper, where this value allowed
    correct detection of all gait events in control subjects. However,
    when a more irregular pattern is analysed, the threshold should be
    less than 0.4. The user can test different threshold values and find
    the best one according to the gait event detection results."

    Parameters
    ----------
    data : list or numpy array
        accelerometer data along one axis (preferably forward direction)
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    threshold : float
        ratio to the maximum value of the anterior-posterior acceleration
    order : integer
        order of the Butterworth filter
    cutoff : integer
        cutoff frequency of the Butterworth filter (Hz)
    plot_test : Boolean
        plot heel strikes?
    t : list or numpy array
        accelerometer time points

    Returns
    -------
    strikes : numpy array of floats
        heel strike timings
    strike_indices : list of integers
        heel strike timing indices

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.extractors.pyGait import heel_strikes
    >>> threshold = 0.4
    >>> order = 4
    >>> cutoff = max([1, sample_rate/10])
    >>> plot_test = True
    >>> data = np.abs(ax) + np.abs(ay) + np.abs(az)
    >>> strikes, strike_indices = heel_strikes(data, sample_rate, threshold, order, cutoff, plot_test, t)

    """
    import numpy as np

    from mhealthx.signals import compute_interpeak
    from mhealthx.signals import butter_lowpass_filter, \
                                 crossings_nonzero_pos2neg

    # Demean data (not in iGAIT):
    data -= np.mean(data)

    # Low-pass filter the AP accelerometer data by the 4th order zero lag
    # Butterworth filter whose cut frequency is set to 5 Hz:
    filtered = butter_lowpass_filter(data, sample_rate, cutoff, order)

    # Find transitional positions where AP accelerometer changes from
    # positive to negative.
    transitions = crossings_nonzero_pos2neg(filtered)

    # Find the peaks of AP acceleration preceding the transitional positions,
    # and greater than the product of a threshold and the maximum value of
    # the AP acceleration:
    strike_indices_smooth = []
    filter_threshold = np.abs(threshold * np.max(filtered))
    for i in range(1, np.size(transitions)):
        segment = range(transitions[i-1], transitions[i])
        imax = np.argmax(filtered[segment])
        if filtered[segment[imax]] > filter_threshold:
            strike_indices_smooth.append(segment[imax])

    # Compute number of samples between peaks using the real part of the FFT:
    interpeak = compute_interpeak(data, sample_rate)
    decel = np.int(interpeak / 2)

    # Find maximum peaks close to maximum peaks of smoothed data:
    strike_indices = []
    for ismooth in strike_indices_smooth:
        istrike = np.argmax(data[ismooth - decel:ismooth + decel])
        istrike = istrike + ismooth - decel
        strike_indices.append(istrike)

    if plot_test:
        from pylab import plt
        if t:
            tplot = np.asarray(t)
            tplot -= tplot[0]
        else:
            tplot = np.linspace(0, np.size(data), np.size(data))
        plt.plot(tplot, data, 'k-', linewidth=2, label='data')
        plt.plot(tplot, filtered, 'b-', linewidth=1, label='filtered data')
        plt.plot(tplot[transitions], filtered[transitions],
                 'ko', linewidth=1, label='transition points')
        plt.plot(tplot[strike_indices_smooth],
                 filtered[strike_indices_smooth],
                 'bs', linewidth=1, label='heel strikes')
        plt.plot(tplot[strike_indices], data[strike_indices],
                 'rs', linewidth=1, label='heel strikes')
        plt.xlabel('Time (s)')
        plt.grid()
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    strikes = np.asarray(strike_indices)
    strikes -= strikes[0]
    strikes = strikes / sample_rate

    return strikes, strike_indices


def gait_regularity_symmetry(data, step_period, stride_period):
    """
    Compute step and stride regularity and symmetry from accelerometer data.

    The iGAIT software assumes that the y-axis is anterior-posterior,
    and restricts some feature extraction to this orientation.
    In this program, we compute every measure for an arbitrary axis.

    From Yang, et al., 2012:

    "The peak value a1 = NFC(t1), which is found at the t1 lag time
    to be a step period, indicates the step regularity in a direction.
    The peak value a2 = NFC(t2), which was found at the t2 lag time
    to be a stride period, indicates the stride regularity in a direction.
    The variance of the stride regularity and step regularity D = |a2 - a1\,
    can be used as an indicator to measure gait asymmetry.
    A smaller value of D indicates a more symmetric gait.
    A larger value of D indicates a more asymmetric gait.
    In total, iGAIT extracts seven regularity and symmetry features
    from the acceleration data, namely ::

        - Step regularity: vertical (VT), anterior-posterior (AP) directions
        - Stride regularity: VT, AP, medial-lateral (ML) directions
        - Symmetry: VT, AP directions

    Parameters
    ----------
    data : list or numpy array
        accelerometer data for one (preferably forward) axis
    step_period : integer
        step period
    stride_period : integer
        stride period

    Returns
    -------
    step_regularity : float
        step regularity measure along axis
    stride_regularity : float
        stride regularity measure along axis
    symmetry : float
        symmetry measure along axis

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.extractors.pyGait import gait_regularity_symmetry
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> data = ay
    >>> step_period = 2
    >>> stride_period = 1
    >>> step_regularity, stride_regularity, symmetry = gait_regularity_symmetry(data, step_period, stride_period)

    """
    import numpy as np

    from mhealthx.signals import autocorrelate

    coefficients, N = autocorrelate(data, unbias=2, normalize=2,
                                    plot_test=False)

    step_regularity = coefficients[step_period]
    stride_regularity = coefficients[stride_period]
    symmetry = np.abs(stride_regularity - step_regularity)

    return step_regularity, stride_regularity, symmetry


def gait(strikes, data, duration, distance=None):
    """
    Extract gait features from estimated heel strikes and accelerometer data.

    This function extracts all of iGAIT's features
    that depend on the estimate of heel strikes::

        - cadence = number of steps divided by walk time
        - step/stride regularity
        - step/stride symmetry
        - mean step/stride length and velocity (if distance supplied)

    Parameters
    ----------
    strikes : numpy array
        heel strike timings
    data : list or numpy array
        accelerometer data along forward axis
    duration : float
        duration of accelerometer reading (s)
    distance : float
        distance traversed

    Returns
    -------
    number_of_steps : integer
        estimated number of steps based on heel strikes
    velocity : float
        velocity (if distance)
    avg_step_length : float
        average step length (if distance)
    avg_stride_length : float
        average stride length (if distance)
    cadence : float
        number of steps divided by duration
    step_durations : numpy array
        step durations
    avg_step_duration : float
        average step duration
    sd_step_durations : float
        standard deviation of step durations
    strides : list of two lists of floats
        stride timings for each side
    avg_number_of_strides : float
        estimated number of strides based on alternating heel strikes
    stride_durations : list of two lists of floats
        estimated stride durations
    avg_stride_duration : float
        average stride duration
    sd_step_durations : float
        standard deviation of stride durations
    step_regularity : float
        measure of step regularity along axis
    stride_regularity : float
        measure of stride regularity along axis
    symmetry : float
        measure of gait symmetry along axis

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.extractors.pyGait import heel_strikes
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> data = ay
    >>> plot_test = False
    >>> strikes, strike_indices = heel_strikes(data, sample_rate, threshold, order, cutoff, plot_test)
    >>> from mhealthx.extractors.pyGait import gait
    >>> distance = 90
    >>> a = gait(strikes, data, duration, distance)

    """
    import numpy as np

    step_durations = []
    for i in range(1, np.size(strikes)):
        step_durations.append(strikes[i] - strikes[i-1])

    avg_step_duration = np.mean(step_durations)
    sd_step_durations = np.std(step_durations)

    number_of_steps = np.size(strikes)
    cadence = number_of_steps / duration

    strides1 = strikes[0::2]
    strides2 = strikes[1::2]
    stride_durations1 = []
    for i in range(1, np.size(strides1)):
        stride_durations1.append(strides1[i] - strides1[i-1])
    stride_durations2 = []
    for i in range(1, np.size(strides2)):
        stride_durations2.append(strides2[i] - strides2[i-1])

    strides = [strides1, strides2]
    stride_durations = [stride_durations1, stride_durations2]

    avg_number_of_strides = np.mean([np.size(strides1), np.size(strides2)])
    avg_stride_duration = np.mean((np.mean(stride_durations1),
                                   np.mean(stride_durations2)))
    sd_stride_durations = np.mean((np.std(stride_durations1),
                                   np.std(stride_durations2)))

    step_period = 1 / avg_step_duration
    stride_period = 1 / avg_stride_duration

    step_regularity, stride_regularity, symmetry = \
        gait_regularity_symmetry(data, step_period, stride_period)

    # Set distance-based measures to None if distance not set:
    if distance:
        velocity = distance / duration
        avg_step_length = number_of_steps / distance
        avg_stride_length = avg_number_of_strides / distance
    else:
        velocity = None
        avg_step_length = None
        avg_stride_length = None

    return number_of_steps, cadence, velocity, \
        avg_step_length, avg_stride_length, step_durations, \
        avg_step_duration, sd_step_durations, strides, stride_durations, \
        avg_number_of_strides, avg_stride_duration, sd_stride_durations, \
        step_regularity, stride_regularity, symmetry
