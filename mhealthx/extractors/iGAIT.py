#!/usr/bin/env python
"""
This program implements some of the feature extraction equations from:

"iGAIT: An interactive accelerometer based gait analysis system"
Mingjing Yang, Huiru Zheng, Haiying Wang, Sally McClean, Dave Newell. 2012.
Computer methods and programs in biomedicine 108:715-723.
DOI:10.1016/j.cmpb.2012.04.004
http://www.ncbi.nlm.nih.gov/pubmed/22575802

iGAIT inputs ::
    - sample rate
    - distance (not included here)
    - threshold (anterior-posterior acceleration, to detect heel contact)

iGait was written as a Matlab file and compiled as a Windows application.

Features ::
    - cadence (step/min)
    - distance-related (not included here): velocity, mean step length
    - RMS (each direction)
    - integral of the power spectral density (PSD, each direction)
    - main frequency: frequency with the maximum value of PSD
    - frequency of cumulated IPSD at 50/75/90/99% energy (each direction)
    - autocorrelation coefficients-derived:
        - symmetry (vertical and anterior-posterior directions)
        - regularity of stride/step (each direction)

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License
"""


def gait(data, sample_rate=100.0, threshold=0.20, order=4, cutoff=5):
    """
    Estimate heel strike times from time series (accelerometer) data.

    From Yang, et al., 2012:

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
    data : numpy array
        y-axis (anterior-posterior) accelerometer data
    sample_rate : integer
        sample rate of accelerometer reading (Hz)
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
    step_durations : numpy array
        step durations
    avg_step_duration : float
        average step duration
    std_step_duration : float
        standard deviation of step duration

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> x, y, z, t = read_accel_json(input_file)
    >>> sample_rate = compute_sample_rate(t)
    >>> from mhealthx.extractors.iGAIT import gait
    >>> threshold = 0.2
    >>> order = 4
    >>> cutoff = 5
    >>> data = y
    >>> heel_strikes, step_durations, avg_step_duration, std_step_duration = gait(data, sample_rate, threshold, order, cutoff)

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
    for i in range(1, len(transitions)):
        segment = range(transitions[i-1], transitions[i])
        imax = np.argmax(filtered[segment])
        if filtered[segment[imax]] > filter_threshold:
            strikes.append(segment[imax])

    plot_test = False
    if plot_test:
        from pylab import plt
        t = np.linspace(0, len(data), len(data))
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
    heel_strikes = [x/sample_rate for x in heel_strikes]

    step_durations = []
    for i in range(1, len(heel_strikes)):
        step_durations.append(heel_strikes[i] - heel_strikes[i-1])

    avg_step_duration = np.mean(step_durations)
    std_step_duration = np.std(step_durations)

    return heel_strikes, step_durations, avg_step_duration, std_step_duration


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

    N = len(data)
    fvi = np.fft.fft(data, n=2*N)
    coefficients = np.real(np.fft.ifft(fvi * np.conjugate(fvi))[:N])
    if unbiased:
        coefficients /= (N - np.arange(N))
    else:
        coefficients /= N

    if normalized:
        coefficients /= coefficients[0]

    return coefficients


def gait_regularity_symmetry(data, step_period, stride_period):
    """
    Compute the step and stride regularity and symmetry from time series data
    (accelerometer data in a given direction).

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
    data : numpy array
        time series data
    step_period : integer
        step period
    stride_period : integer
        stride period

    Returns
    -------
    step_regularity : float
        step regularity measure in a given direction
    stride_regularity : float
        stride regularity measure in given direction
    symmetry : float
        symmetry measure in given direction

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json, compute_sample_rate
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/accel_walking_outbound.json.items-6dc4a144-55c3-4e6d-982c-19c7a701ca243282023468470322798.tmp'
    >>> x, y, z, t = read_accel_json(input_file)
    >>> sample_rate = compute_sample_rate(t)
    >>> from mhealthx.extractors.iGAIT import gait
    >>> threshold = 0.1
    >>> order = 4
    >>> cutoff = 5
    >>> data = y
    >>> heel_strikes, step_durations, avg_step_duration, std_step_duration = gait(data, sample_rate, threshold, order, cutoff)
    >>>
    >>> import numpy as np
    >>> from mhealthx.extractors.iGAIT import gait_regularity_symmetry
    >>> data = np.random.random(1000)
    >>> step_period = 2
    >>> stride_period = 10
    >>> gait_regularity_symmetry(data, step_period, stride_period)

    From "Efficient computation of autocorrelations; demonstration in MatLab
    and Python" (Dec. 29, 2013) by Jesper Toft Kristensen:
    http://jespertoftkristensen.com/JTK/Blog/Entries/2013/12/29_Efficient_
    computation_of_autocorrelations%3B_demonstration_in_MatLab_and_Python.html
    """
    import numpy as np

    from mhealthx.extractors.iGAIT import autocorrelation

    coefficients = autocorrelation(data, unbiased=True, normalized=True)

    plot_test = False
    if plot_test:
        from pylab import plt
        t = np.linspace(0, len(coefficients), len(coefficients))
        plt.plot(t, coefficients, 'b-', label='coefficients')
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend(loc='lower left', shadow=True)
        plt.show()

    step_regularity = coefficients(step_period)
    stride_regularity = coefficients(stride_period)
    symmetry = np.abs(stride_regularity - step_regularity)

    return step_regularity, stride_regularity, symmetry


def rms(data):
    """
    The root mean square of acceleration indicates the intensity of motion.
    The RMS values of the three acceleration directions (VT, AP and ML)
    are calculated as: RMS_d = sqrt( (sum[i=0:N-1](xdi - [xd])^2 / N) )
    where xdi (i = 1,2,...,N; d = VT,AP,ML) is the acceleration in either
    the VT, AP or ML axis, N is the length of the acceleration signal,
    [xd] is the mean value of acceleration in any axis.
    """
    pass

