#!/usr/bin/env python
"""
This program implements some of the feature extraction equations from:

"iGAIT: An interactive accelerometer based gait analysis system"
Mingjing Yang, Huiru Zheng, Haiying Wang, Sally McClean, Dave Newell. 2012.
Computer methods and programs in biomedicine 108:715-723.
DOI:10.1016/j.cmpb.2012.04.004
http://www.ncbi.nlm.nih.gov/pubmed/22575802

iGait was written as a Matlab file and compiled as a Windows application.

iGAIT inputs ::
    - sample rate
    - distance (not included here)
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

pyGait functions compute all of iGAIT's features except
those that require an input distance (mean step length, velocity)
and the spectral features::
    - gait_features() for all heel strike-based estimates:
        - cadence
        - regularity and symmetry (each direction)
    - root_mean_square():
        - root mean square (each direction)

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def autocorrelation(data, unbiased=True, normalized=True):
    """
    Compute the autocorrelation coefficients for time series data.

    From Yang, et al., 2012:

    "The autocorrelation coefficient refers to the correlation of a time
    series with its own past or future values. iGAIT uses unbiased
    autocorrelation coefficients of acceleration data to scale the regularity
    and symmetry of gait [30]. The unbiased estimate of autocorrelation
    coefficients of acceleration data can be calculated by Eq. (5) ::

        fc(t) = 1/(N-|t|)  *  SUM[i=1:N-|t|](xi * x_i+t)

    where xi (i=1,2,...,N) is the acceleration data,
    fc(t) are autocorrelation coefficients,
    t is the time lag (t=-N,-N+1,...,0,1,2,...,N).

    When the time lag t is equal to the periodicity of the acceleration xi,
    a peak will be found in the fc(t) series.
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
    normalized : Boolean
        compute normalized autocorrelation?

    Returns
    -------
    coefficients : numpy array
        [normalized, unbiased] autocorrelation coefficients

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.iGAIT import autocorrelation
    >>> data = np.random.random(100)
    >>> unbiased = True
    >>> normalized = True
    >>> coefficients = autocorrelation(data, unbiased, normalized)

    From "Efficient computation of autocorrelations; demonstration in MatLab
    and Python" (Dec. 29, 2013) by Jesper Toft Kristensen:
    http://jespertoftkristensen.com/JTK/Blog/Entries/2013/12/29_Efficient_
    computation_of_autocorrelations%3B_demonstration_in_MatLab_and_Python.html
    """
    import numpy as np

    N = np.size(data)
    fvi = np.fft.fft(data, n=2*N)
    coefficients = np.real(np.fft.ifft(fvi * np.conjugate(fvi))[:N])
    if unbiased:
        coefficients /= (N - np.arange(N))
    else:
        coefficients /= N

    if normalized:
        coefficients /= coefficients[0]

    return coefficients


def gait_regularity_symmetry(x, y, z, step_period, stride_period):
    """
    Compute step and stride regularity and symmetry from accelerometer data.

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
    x : list
        x-axis accelerometer data
    y : list
        y-axis accelerometer data
    z : list
        z-axis accelerometer data
    step_period : integer
        step period
    stride_period : integer
        stride period

    Returns
    -------
    step_regularity_x : float
        step regularity measure in medial-lateral direction
    step_regularity_y : float
        step regularity measure in anterior-posterior direction
    step_regularity_z : float
        step regularity measure in vertical direction
    stride_regularity_x : float
        stride regularity measure in medial-lateral direction
    stride_regularity_y : float
        stride regularity measure in anterior-posterior direction
    stride_regularity_z : float
        stride regularity measure in vertical direction
    symmetry_x : float
        symmetry measure in medial-lateral direction
    symmetry_y : float
        symmetry measure in anterior-posterior direction
    symmetry_z : float
        symmetry measure in vertical direction

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> from mhealthx.extractors.iGAIT import gait_regularity_symmetry
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file)
    >>> step_period = 2
    >>> stride_period = 1
    >>> a = gait_regularity_symmetry(x, y, z, step_period, stride_period)

    """
    import numpy as np

    from mhealthx.extractors.iGAIT import autocorrelation

    coefficients_x = autocorrelation(x, unbiased=True, normalized=True)
    coefficients_y = autocorrelation(y, unbiased=True, normalized=True)
    coefficients_z = autocorrelation(z, unbiased=True, normalized=True)

    plot_test = False
    if plot_test:
        from pylab import plt
        t = np.linspace(0, np.size(coefficients_y), np.size(coefficients_y))
        plt.plot(t, coefficients_y, 'b-', label='coefficients')
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    step_regularity_x = coefficients_x[step_period]
    step_regularity_y = coefficients_y[step_period]
    step_regularity_z = coefficients_z[step_period]
    stride_regularity_x = coefficients_x[stride_period]
    stride_regularity_y = coefficients_y[stride_period]
    stride_regularity_z = coefficients_z[stride_period]
    symmetry_x = np.abs(stride_regularity_x - step_regularity_x)
    symmetry_y = np.abs(stride_regularity_y - step_regularity_y)
    symmetry_z = np.abs(stride_regularity_z - step_regularity_z)

    return step_regularity_x, step_regularity_y, step_regularity_z, \
           stride_regularity_x, stride_regularity_y, stride_regularity_z, \
           symmetry_x, symmetry_y, symmetry_z


def gait(x, y, z, t, sample_rate, duration,
         threshold=0.20, order=4, cutoff=5):
    """
    Extract gait features from estimated heel strikes from accelerometer data.

    This function extracts all of iGAIT's features that depend on the estimate
    of heel strikes, but do not require an input distance::

        - cadence = number of steps divided by walking time
        - step/stride regularity
        - step/stride symmetry

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
    x : list
        x-axis accelerometer data
    y : list
        y-axis accelerometer data
    z : list
        z-axis accelerometer data
    t : list
        time points for accelerometer data
    sample_rate : float
        sample rate of accelerometer reading (Hz)
    duration : float
        duration of accelerometer reading (s)
    threshold : float
        ratio to the maximum value of the anterior-posterior acceleration
    order : integer
        order of the Butterworth filter
    cutoff : integer
        cutoff frequency of the Butterworth filter (Hz)

    Returns
    -------
    heel_strikes : numpy array
        heel strike timings
    number_of_steps : integer
        estimated number of steps based on heel strikes
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
    step_regularity_x : float
        measure of step regularity in x-axis
    step_regularity_y : float
        measure of step regularity in y-axis
    step_regularity_z : float
        measure of step regularity in z-axis
    stride_regularity_x : float
        measure of stride regularity in x-axis
    stride_regularity_y : float
        measure of stride regularity in y-axis
    stride_regularity_z : float
        measure of stride regularity in z-axis
    symmetry_x : float
        measure of gait symmetry in x-axis
    symmetry_y : float
        measure of gait symmetry in y-axis
    symmetry_z : float
        measure of gait symmetry in z-axis

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> x, y, z, t, sample_rate, duration = read_accel_json(input_file)
    >>> from mhealthx.extractors.iGAIT import gait
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> data = y
    >>> a = gait(x, y, z, t, sample_rate, duration, threshold, order, cutoff)

    """
    import numpy as np
    from scipy.signal import butter, lfilter

    def butter_lowpass(cutoff, sample_rate, order=4):
        """
        After http://stackoverflow.com/questions/25191620/
        creating-lowpass-filter-in-scipy-understanding-methods-and-units
        """
        nyquist = 0.5 * sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(data, cutoff, sample_rate, order=4):
        """
        After http://stackoverflow.com/questions/25191620/
        creating-lowpass-filter-in-scipy-understanding-methods-and-units
        """
        b, a = butter_lowpass(cutoff, sample_rate, order=order)
        y = lfilter(b, a, data)
        return y

    def crossings_nonzero_pos2neg(data):
        """http://stackoverflow.com/questions/3843017/
        efficiently-detect-sign-changes-in-python"""
        pos = data > 0
        return (pos[:-1] & ~pos[1:]).nonzero()[0]

    # Demean data (not in iGAIT):
    data = y
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
    strikes = []
    filter_threshold = np.abs(threshold * np.max(filtered))
    for i in range(1, np.size(transitions)):
        segment = range(transitions[i-1], transitions[i])
        imax = np.argmax(filtered[segment])
        if filtered[segment[imax]] > filter_threshold:
            strikes.append(segment[imax])

    plot_test = False
    if plot_test:
        from pylab import plt
        t = np.linspace(0, np.size(data), np.size(data))
        plt.plot(t, data, 'b-', label='data')
        plt.plot(t, filtered, 'g-', linewidth=2, label='filtered data')
        plt.plot(t[transitions], filtered[transitions],
                 'ko', linewidth=2, label='transition points')
        plt.plot(t[strikes], filtered[strikes],
                 'rs', linewidth=2, label='heel strikes')
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    heel_strikes = np.asarray(strikes)
    heel_strikes -= strikes[0]
    heel_strikes = [hs/sample_rate for hs in heel_strikes]

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

    step_regularity_x, step_regularity_y, step_regularity_z, \
           stride_regularity_x, stride_regularity_y, stride_regularity_z, \
           symmetry_x, symmetry_y, symmetry_z = \
        gait_regularity_symmetry(x, y, z, step_period, stride_period)

    return heel_strikes, number_of_steps, cadence, step_durations, \
           avg_step_duration, sd_step_durations, strides, stride_durations, \
           avg_number_of_strides, avg_stride_duration, sd_stride_durations, \
           step_regularity_x, step_regularity_y, step_regularity_z, \
           stride_regularity_x, stride_regularity_y, stride_regularity_z, \
           symmetry_x, symmetry_y, symmetry_z


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
    >>> from mhealthx.extractors.iGAIT import root_mean_square
    >>> data = np.random.random(100)
    >>> rms = root_mean_square(data)

    """
    import numpy as np

    N = np.size(data)
    demeaned_data = data - np.mean(data)
    rms = np.sqrt(np.sum(demeaned_data**2 / N))

    return rms