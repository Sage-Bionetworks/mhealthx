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

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def walking_direction(ax, ay, az, t, sample_rate, stride_fraction=1.0/8.0,
                      threshold=0.5, order=4, cutoff=5, plot_test=False):
    """
    Estimate local walking (not cardinal) direction.

    Inspired by Nirupam Roy's B.E. thesis: "WalkCompass:
    Finding Walking Direction Leveraging Smartphone's Inertial Sensors,"
    this program derives the local walking direction vector from the end
    of the primary leg's stride, when it is decelerating in its swing.
    While the WalkCompass relies on clear heel strike signals across the
    accelerometer axes, this program just uses the most prominent strikes,
    and estimates period from the real part of the FFT of the data.

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
        ratio to the maximum value of the summed acceleration across axes
    plot_test : Boolean
        plot most prominent heel strikes?

    Returns
    -------
    direction : numpy array of three floats
        unit vector of local walking (not cardinal) direction

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-d02455b6-2db5-4dd5-ab92-2ea8d959f2f46545544245760775418.tmp'
    >>> #device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.extractors.pyGait import walking_direction
    >>> threshold = 0.5
    >>> stride_fraction = 1.0/8.0
    >>> order = 4
    >>> cutoff = max([1, sample_rate/10])
    >>> plot_test = True
    >>> direction = walking_direction(ax, ay, az, t, sample_rate, stride_fraction, threshold, order, cutoff, plot_test)

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
        title = 'Average deceleration vectors + estimated walking direction'
        plot_vectors(dx, dy, dz, [hx], [hy], [hz], title)

    return direction


def project_axes(vectors, unit_vector):
    """
    Project vectors on a unit vector.

    Parameters
    ----------
    vectors : list of lists of x, y, z coordinates or numpy array equivalent
    unit_vector : numpy array or list of x, y, z coordinates
        unit vector to project vectors onto

    Returns
    -------
    projection_vectors : list of lists of x, y, z coordinates
        vectors projected onto unit vector

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.signals import compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-d02455b6-2db5-4dd5-ab92-2ea8d959f2f46545544245760775418.tmp'
    >>> #device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> vectors = zip(axyz[0], axyz[1], axyz[2])
    >>> from mhealthx.extractors.pyGait import project_axes
    >>> unit_vector = [1, 1, 1]
    >>> projection_vectors = project_axes(vectors, unit_vector)

    """
    import numpy as np

    projection_vectors = []
    for v in vectors:
        magnitude = np.asarray(v).dot(np.asarray(unit_vector))
        projection_vectors.append(magnitude * np.asarray(unit_vector))

    return projection_vectors


def heel_strikes(data, sample_rate, threshold=0.2, order=4, cutoff=5,
                 plot_test=False, t=None):
    """
    Estimate heel strike times from sign changes in accelerometer data.

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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-d02455b6-2db5-4dd5-ab92-2ea8d959f2f46545544245760775418.tmp'
    >>> device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #device_motion = True
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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #device_motion = True
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

        - cadence = number of steps divided by walking time
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
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #device_motion = True
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


def scratch(x, y, z, t, sample_rate, threshold=0.2,
                                    order=4, cutoff=5, plot_test=False):
    """
    Estimate heel strike times from autocorrelation in accelerometer data.

    Parameters
    ----------
    x : numpy array
        accelerometer data along x axis
    y : numpy array
        accelerometer data along y axis
    z : numpy array
        accelerometer data along z axis
    t : list or numpy array
        accelerometer time points
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    threshold : float
        ratio to the maximum value of the anterior-posterior acceleration
    plot_test : Boolean
        plot heel strikes?

    Returns
    -------
    strikes : numpy array of floats
        heel strike timings
    strike_indices : list of integers
        heel strike timing indices
    data : numpy array
        accelerometer data along selected axis

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-d02455b6-2db5-4dd5-ab92-2ea8d959f2f46545544245760775418.tmp'
    >>> #device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> ax, ay, az = axyz
    >>> from mhealthx.extractors.pyGait import heel_strikes_by_autocorrelation
    >>> threshold = 0.2
    >>> plot_test = True
    >>> heel_strikes, strike_indices, data = heel_strikes_by_autocorrelation(ax, ay, az, t, sample_rate, threshold, order, cutoff, plot_test)

    """
    import numpy as np
    from scipy.fftpack import rfft, fftfreq

    from mhealthx.signals import autocorrelate

    # Sum of absolute values across accelerometer axes:
    signal = np.abs(x) + np.abs(y) + np.abs(z)
    N = signal.size

    # Compute number of samples between peaks using the FFT:
    freqs = fftfreq(len(signal), d=1/sample_rate)
    f_signal = rfft(signal)
    imax_freq = np.argsort(f_signal)[-2]
    freq = freqs[imax_freq]
    interpeak = 2 * np.int(np.round(sample_rate / freq))

    # Find maximum peak:
    imax = np.argmax(signal)

    # Initialize peaks (below imax):
    ipeaks = [imax]
    go = True
    i = 0
    while go:
        i += 1
        ipeak = imax - i * interpeak
        if ipeak > 0:
            ipeaks.append(ipeak)
        else:
            go = False
    # Initialize peaks (above imax but within N):
    go = True
    i = 0
    while go:
        i += 1
        ipeak = imax + i * interpeak
        if ipeak <= N:
            ipeaks.append(ipeak)
        else:
            go = False


    # # Find all other peaks:
    # peaks = []
    # for ipeak in range(N/interpeak):
    #    window = coefficients[interpeak * (ipeak - 1) : interpeak * (ipeak + 1)]
    #    peaks.append(interpeak * (ipeak - 1) + np.argmax(window))

    # Plot results:
    if plot_test:
        from pylab import plt
        if isinstance(t, list):
            tplot = np.asarray(t) - t[0]
        else:
            tplot = np.linspace(0, np.size(x), np.size(x))

        # Plot autocorrelation:
        plt.subplot(2, 1, 1)
        plt.plot(tplot, signal, 'k-', tplot[ipeaks], signal[ipeaks], 'rs')
        plt.title('Estimated stride peaks')

        # Plot estimated heel strikes on accelerometer data:
        # plt.subplot(2, 1, 2)
        # plt.plot(t, xyz, 'k-', t[strike_indices], xyz[strike_indices], 'rs')
        # plt.title('estimated heel strikes')
        plt.show()


    # Autocorrelation of sum of absolute values across axes:
    unbias = 2
    normalize = 2
    coefficients, N = autocorrelate(xyz, unbias, normalize, False)

    #delta_peak_factor = 0.10
    #interpeak = np.argmax(coefficients[1::]) + 1
    #peaks = []
    #for ipeak in range(N/interpeak):
    #    window = coefficients[interpeak * (ipeak - 1) : interpeak * (ipeak + 1)]
    #    peaks.append(interpeak * (ipeak - 1) + np.argmax(window))

    from pylab import plt
    plt.subplot(311)
    plt.plot(signal, 'k-')
    plt.subplot(312)
    plt.plot(freqs, f_signal, 'k-')
    #plt.xlim(0, int(N/2))
    plt.subplot(313)
    tplot = np.asarray(t) - t[0]
    plt.plot(tplot, signal, 'k-',
             tplot[range(period, N, period)],
             signal[range(period, N, period)], 'rs')
    plt.show()

    plt.subplot(211)
    plt.plot(x, 'k-', y, 'b-', z, 'r-')
    plt.subplot(212)
    plt.plot(signal, 'k-')
    plt.show()




    idx = np.argsort(freqs)
    freq = freqs[idx[2]]

    plt.plot(freqs[idx], ps[idx]); plt.show()


    fourier = np.fft.fft(coefficients)
    fourier0 = fourier[0]
    fourier1 = np.abs(fourier[1::])
    iarg = np.argmax(fourier1)
    fourier_max = fourier1[iarg]
    # #freqs = np.fft.fftfreq(data.size, d=1/sample_rate)
    # #freq = np.abs(freqs[iarg])
    # itop = np.where(fourier1 > ffactor * fourier_max) + 1

    # Extract heel strikes along this axis:
    strikes, strike_indices = heel_strikes_by_sign_change(coefficients,
        sample_rate, threshold, order, cutoff, False, t)
    # Plot results:
    if plot_test:
        from pylab import plt
        if isinstance(t, list):
            t = np.asarray(t) - t[0]
        else:
            t = np.linspace(0, np.size(x), np.size(x))

        # Plot autocorrelation:
        plt.subplot(2, 1, 1)
        plt.plot(t, coefficients, 'k-', t[peaks], data[peaks], 'rs')
        plt.title('autocorrelation')

        # Plot estimated heel strikes on accelerometer data:
        plt.subplot(2, 1, 2)
        plt.plot(t, xyz, 'k-', t[strike_indices], xyz[strike_indices], 'rs')
        plt.title('estimated heel strikes')
        plt.show()

    return strikes, strike_indices, data
