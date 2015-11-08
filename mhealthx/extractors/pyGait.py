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
    - distance
    - threshold (anterior-posterior acceleration, to detect heel contact)

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


def butter_lowpass_filter(data, cutoff, sample_rate, order=4):
    """
    Low-pass filter data by the [order]th order zero lag Butterworth filter
    whose cut frequency is set to [cutoff] Hz.

    After http://stackoverflow.com/questions/25191620/
    creating-lowpass-filter-in-scipy-understanding-methods-and-units
    """
    from scipy.signal import butter, lfilter

    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    y = lfilter(b, a, data)

    return y


def crossings_nonzero_pos2neg(data):
    """
    Find indices of zero crossings from positive to negative values.

    http://stackoverflow.com/questions/3843017/
    efficiently-detect-sign-changes-in-python
    """
    import numpy as np

    if isinstance(data, np.ndarray):
        pass
    elif isinstance(data, list):
        data = np.asarray(data)
    else:
        raise IOError('data should be a numpy array')

    pos = data > 0

    return (pos[:-1] & ~pos[1:]).nonzero()[0]


def autocorrelate(data, unbiased=True, normalize_1st=True,
                  normalize_max=True, plot_test=False):
    """
    Compute the autocorrelation coefficients for time series data.

    Here we use scipy.signal.correlate, but the results are the same as in
    Yang, et al., 2012:
    "The autocorrelation coefficient refers to the correlation of a time
    series with its own past or future values. iGAIT uses unbiased
    autocorrelation coefficients of acceleration data to scale the regularity
    and symmetry of gait.
    The autocorrelation coefficients are divided by fc(0) in Eq. (6),
    so that the autocorrelation coefficient is equal to 1 when t=0 ::
        NFC(t) = fc(t) / fc(0)
    Here NFC(t) is the normalised autocorrelation coefficient, and fc(t) are
    autocorrelation coefficients."

    Parameters
    ----------
    data : numpy array
        time series data
    unbiased : Boolean
        compute unbiased autocorrelation?
    normalize_1st : Boolean
        normalize by 1st coefficient?
    normalize_max : Boolean
        normalize by maximum absolute value?
    plot_test : Boolean
        plot?

    Returns
    -------
    coefficients : numpy array
        [normalized, unbiased] autocorrelation coefficients

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.pyGait import autocorrelate
    >>> data = np.random.random(100)
    >>> unbiased = True
    >>> normalize_1st = True
    >>> normalize_max = True
    >>> plot_test = True
    >>> coefficients = autocorrelate(data, unbiased, normalize_1st, normalize_max, plot_test)

    """
    import numpy as np
    from scipy.signal import correlate

    coefficients = correlate(data, data, 'full')

    N = np.size(data)

    if plot_test:
        from pylab import plt
        t = np.linspace(0, np.size(coefficients), np.size(coefficients))
        plt.figure()
        plt.subplot(3, 1, 1)
        plt.plot(t, coefficients, 'k-', label='coefficients')
        plt.title('coefficients')

    if unbiased:
        coefficients /= np.hstack([np.arange(1, N), N - np.arange(N)])

        if plot_test:
            plt.subplot(3, 1, 2)
            plt.plot(t, coefficients, 'k-', label='coefficients')
            plt.title('unbiased coefficients')

    if normalize_1st:
        coefficients /= np.abs(coefficients[0])

    if normalize_max:
        coefficients /= np.max(coefficients)

    if normalize_1st or normalize_max:
        if plot_test:
            plt.subplot(3, 1, 3)
            plt.plot(t, coefficients, 'k-', label='coefficients')
            plt.title('normalized coefficients')

    if plot_test:
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    return coefficients


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
        accelerometer data for one axis
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
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> data = y
    >>> step_period = 2
    >>> stride_period = 1
    >>> step_regularity, stride_regularity, symmetry = gait_regularity_symmetry(data, step_period, stride_period)

    """
    import numpy as np

    from mhealthx.extractors.pyGait import autocorrelate

    coefficients = autocorrelate(data, unbiased=True, normalize_1st=True,
                                 normalize_max=False, plot_test=False)

    step_regularity = coefficients[step_period]
    stride_regularity = coefficients[stride_period]
    symmetry = np.abs(stride_regularity - step_regularity)

    return step_regularity, stride_regularity, symmetry


def extract_heel_strikes(data, sample_rate, threshold=0.2, order=4, cutoff=5,
                         plot_test=False, t=None):
    """
    Estimate heel strike times from accelerometer data.

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
        accelerometer data along one axis
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
    heel_strikes : numpy array of floats
        heel strike timings
    strike_indices : list of integers
        heel strike timing indices

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #device_motion = True
    >>> start = 150
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> from mhealthx.extractors.pyGait import extract_heel_strikes
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> plot_test = True
    >>> data = x
    >>> heel_strikes, strike_indices = extract_heel_strikes(data, sample_rate, threshold, order, cutoff, plot_test, t)

    """
    import numpy as np

    from mhealthx.extractors.pyGait import butter_lowpass_filter, \
                                           crossings_nonzero_pos2neg

    # Demean data (not in iGAIT):
    data -= np.mean(data)

    # Low-pass filter the AP accelerometer data by the 4th order zero lag
    # Butterworth filter whose cut frequency is set to 5 Hz:
    filtered = butter_lowpass_filter(data, cutoff, sample_rate, order)

    # Find transitional positions where AP accelerometer changes from
    # positive to negative.
    transitions = crossings_nonzero_pos2neg(filtered)

    # Find the peaks of AP acceleration preceding the transitional positions,
    # and greater than the product of a threshold and the maximum value of
    # the AP acceleration:
    strike_indices = []
    filter_threshold = np.abs(threshold * np.max(filtered))
    for i in range(1, np.size(transitions)):
        segment = range(transitions[i-1], transitions[i])
        imax = np.argmax(filtered[segment])
        if filtered[segment[imax]] > filter_threshold:
            strike_indices.append(segment[imax])

    if plot_test:
        from pylab import plt
        if t:
            t = np.asarray(t)
            t -= t[0]
        else:
            t = np.linspace(0, np.size(data), np.size(data))
        plt.plot(t, data, 'b-', label='data')
        plt.plot(t, filtered, 'g-', linewidth=2, label='filtered data')
        plt.plot(t[transitions], filtered[transitions],
                 'ko', linewidth=2, label='transition points')
        plt.plot(t[strike_indices], filtered[strike_indices],
                 'rs', linewidth=2, label='heel strikes')
        plt.xlabel('Time (s)')
        plt.grid()
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    heel_strikes = np.asarray(strike_indices)
    heel_strikes -= heel_strikes[0]
    heel_strikes = heel_strikes / sample_rate

    return heel_strikes, strike_indices


def select_heel_strikes(x, y, z, sample_rate, threshold=0.2,
                        order=4, cutoff=5, plot_test=False, t=None):
    """
    Run extract_heel_strikes() for each accelerometer axis, and select the
    axis with the greatest periodicity based on a normalized autocorrelation.

    Parameters
    ----------
    x : numpy array
        accelerometer data along x axis
    y : numpy array
        accelerometer data along y axis
    z : numpy array
        accelerometer data along z axis
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
    heel_strikes : numpy array of floats
        heel strike timings
    strike_indices : list of integers
        heel strike timing indices

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> device_motion = False
    >>> #input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-5981e0a8-6481-41c8-b589-fa207bfd2ab38771455825726024828.tmp'
    >>> #device_motion = True
    >>> start = 150
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> from mhealthx.extractors.pyGait import select_heel_strikes
    >>> threshold = 0.2
    >>> order = 1
    >>> cutoff = 5
    >>> plot_test = True
    >>> heel_strikes, strike_indices = select_heel_strikes(x, y, z, sample_rate, threshold, order, cutoff, plot_test, t)

    """
    import numpy as np

    from mhealthx.extractors.pyGait import extract_heel_strikes, autocorrelate

    # De-mean data for each axis:
    xm = x - np.mean(x)
    ym = y - np.mean(y)
    zm = z - np.mean(z)

    # Autocorrelation of de-meaned data for each axis:
    unbiased = True
    normalize_1st = True
    normalize_max = True
    xc = autocorrelate(xm, unbiased, normalize_1st, normalize_max, False)
    yc = autocorrelate(ym, unbiased, normalize_1st, normalize_max, False)
    zc = autocorrelate(zm, unbiased, normalize_1st, normalize_max, False)

    # Find axis with the largest second autocorrelation coefficient:
    N2 = len(xc)/2
    xyz2 = np.asarray((xc[N2+1], yc[N2+1], zc[N2+1]))
    imax = xyz2.argmax()

    # Extract heel strikes along this axis:
    xyz = [x, y, z]
    data = np.asarray(xyz[imax])
    heel_strikes, strike_indices = extract_heel_strikes(data, sample_rate,
                                                        threshold, order,
                                                        cutoff, False, t)
    # Plot results:
    if plot_test:
        from pylab import plt
        if isinstance(t, list):
            t = np.asarray(t)
            t -= t[0]
        else:
            t = np.linspace(0, np.size(x), np.size(x))
        xyz_strings = ['x', 'y', 'z']

        # Plot autocorrelations for all three axes:
        plt.subplot(2, 1, 1)
        xyzc = [xc, yc, zc]
        datac = xyzc[imax]
        xyzc.pop(imax)
        plt.plot(t, xyzc[0][N2:], 'k-',
                 t, xyzc[1][N2:], 'b-',
                 t, datac[N2:], 'r-')
        plt.title('x,y,z autocorrelations (red: {0}-axis)'.
                  format(xyz_strings[imax]))

        # Plot estimated heel strikes on accelerometer data for selected axis:
        plt.subplot(2, 1, 2)
        plt.plot(t, data, 'k-',
                 t[strike_indices], data[strike_indices], 'rs')
        plt.title('estimated heel strikes')
        plt.show()

    # xdf = pd.DataFrame(xc)
    # ydf = pd.DataFrame(yc)
    # zdf = pd.DataFrame(zc)
    # dx = xdf.diff() #compute the difference between each point
    # dy = ydf.diff() #compute the difference between each point
    # dz = zdf.diff() #compute the difference between each point
    #
    # xdf = pd.DataFrame(x - np.mean(x))
    # ydf = pd.DataFrame(y - np.mean(y))
    # zdf = pd.DataFrame(z - np.mean(z))
    # dx = xdf.diff() #compute the difference between each point!
    # dy = ydf.diff() #compute the difference between each point!
    # dz = zdf.diff() #compute the difference between each point!

    return heel_strikes, strike_indices


def gait(heel_strikes, data, duration, distance=None):
    """
    Extract gait features from estimated heel strikes from accelerometer data.

    This function extracts all of iGAIT's features
    that depend on the estimate of heel strikes::

        - cadence = number of steps divided by walking time
        - step/stride regularity
        - step/stride symmetry
        - mean step/stride length and velocity (if distance supplied)

    Parameters
    ----------
    heel_strikes : numpy array
        heel strike timings
    data : list or numpy array
        accelerometer data along one axis
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
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> from mhealthx.extractors.pyGait import extract_heel_strikes
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> data = y
    >>> plot_test = False
    >>> heel_strikes = extract_heel_strikes(data, sample_rate, threshold, order, cutoff, plot_test)
    >>> from mhealthx.extractors.pyGait import gait
    >>> distance = 90
    >>> a = gait(heel_strikes, data, duration, distance)

    """
    import numpy as np

    step_durations = []
    for i in range(1, np.size(heel_strikes)):
        step_durations.append(heel_strikes[i] - heel_strikes[i-1])

    avg_step_duration = np.mean(step_durations)
    sd_step_durations = np.std(step_durations)

    number_of_steps = np.size(heel_strikes)
    cadence = number_of_steps / duration

    strides1 = heel_strikes[0::2]
    strides2 = heel_strikes[1::2]
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


def root_mean_square(data):
    """
    Compute root mean square of data.

    from Yang, et al., 2012:
    "The root mean square of acceleration indicates the intensity of motion.
    The RMS values of the three acceleration directions (VT, AP and ML)
    are calculated as: RMS_d = sqrt( (sum[i=1:N](xdi - [xd])^2 / N) )
    where xdi (i = 1,2,...,N; d = VT,AP,ML) is the acceleration in either
    the VT, AP or ML axis, N is the length of the acceleration signal,
    [xd] is the mean value of acceleration in any axis."

    Parameters
    ----------
    data : numpy array of floats

    Returns
    -------
    rms : float
        root mean square

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.pyGait import root_mean_square
    >>> data = np.random.random(100)
    >>> rms = root_mean_square(data)

    """
    import numpy as np

    N = np.size(data)
    demeaned_data = data - np.mean(data)
    rms = np.sqrt(np.sum(demeaned_data**2 / N))

    return rms