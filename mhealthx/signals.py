#!/usr/bin/env python
"""
Signal processing functions from different sources.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com
    - Elias Chaibub-Neto, 2015 (neto@sagebase.org)

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def compute_sample_rate(t):
    """
    Compute sample rate.

    Parameters
    ----------
    t : list
        time points

    Returns
    -------
    sample_rate : float
        sample rate
    duration : float
        duration of time series

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import compute_sample_rate
    >>> t = np.linspace(.1, 1000, 10000)
    >>> sample_rate, duration = compute_sample_rate(t)
    """
    import numpy as np

    deltas = []
    tprev = t[0]
    for tnext in t[1::]:
        deltas.append(tnext - tprev)
        tprev = tnext
    sample_rate = 1 / np.mean(deltas)

    duration = t[-1] - t[0]

    return sample_rate, duration


def butter_lowpass_filter(data, sample_rate, cutoff=10, order=4):
    """
    Low-pass filter data by the [order]th order zero lag Butterworth filter
    whose cut frequency is set to [cutoff] Hz.

    After http://stackoverflow.com/questions/25191620/
    creating-lowpass-filter-in-scipy-understanding-methods-and-units

    Parameters
    ----------
    data : numpy array of floats
        time-series data
    sample_rate : integer
        data sample rate
    cutoff : float
        filter cutoff
    order : integer
        order

    Returns
    -------
    y : numpy array of floats
        low-pass-filtered data

    Examples
    --------
    >>> from mhealthx.signals import butter_lowpass_filter
    >>> data = np.random.random(100)
    >>> sample_rate = 10
    >>> cutoff = 5
    >>> order = 4
    >>> y = butter_lowpass_filter(data, sample_rate, cutoff, order)

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

    From: http://stackoverflow.com/questions/3843017/
                 efficiently-detect-sign-changes-in-python

    Parameters
    ----------
    data : numpy array of floats

    Returns
    -------
    crossings : numpy array of integers
        crossing indices to data

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import crossings_nonzero_pos2neg
    >>> data = np.random.random(100)
    >>> crossings = crossings_nonzero_pos2neg(data)

    """
    import numpy as np

    if isinstance(data, np.ndarray):
        pass
    elif isinstance(data, list):
        data = np.asarray(data)
    else:
        raise IOError('data should be a numpy array')

    pos = data > 0

    crossings = (pos[:-1] & ~pos[1:]).nonzero()[0]

    return crossings


def autocorrelate(data, unbias=2, normalize=2, plot_test=False):
    """
    Compute the autocorrelation coefficients for time series data.

    Here we use scipy.signal.correlate, but the results are the same as in
    Yang, et al., 2012 for unbias=1:
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
    unbias : integer or None
        unbiased autocorrelation: divide by range (1) or by weighted range (2)
    normalize : integer or None
        normalize: divide by 1st coefficient (1) or by maximum abs. value (2)
    plot_test : Boolean
        plot?

    Returns
    -------
    coefficients : numpy array
        [normalized, unbiased] autocorrelation coefficients
    N : integer
        number of coefficients

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import autocorrelate
    >>> data = np.random.random(100)
    >>> unbias = 2
    >>> normalize = 2
    >>> plot_test = True
    >>> coefficients, N = autocorrelate(data, unbias, normalize, plot_test)

    """
    import numpy as np
    from scipy.signal import correlate

    # Autocorrelation:
    coefficients = correlate(data, data, 'full')
    coefficients = coefficients[coefficients.size/2:]
    N = coefficients.size

    # Plot:
    if plot_test:
        from pylab import plt
        t = np.linspace(0, N, N)
        plt.figure()
        plt.subplot(3, 1, 1)
        plt.plot(t, coefficients, 'k-', label='coefficients')
        plt.title('coefficients')

    # Unbiased:
    if unbias:
        if unbias == 1:
            coefficients /= (N - np.arange(N))
        elif unbias == 2:
            coefficient_ratio = coefficients[0]/coefficients[-1]
            coefficients /= np.linspace(coefficient_ratio, 1, N)
        else:
            raise IOError("unbias should be set to 1, 2, or None")
        # Plot:
        if plot_test:
            plt.subplot(3, 1, 2)
            plt.plot(t, coefficients, 'k-', label='coefficients')
            plt.title('unbiased coefficients')

    # Normalize:
    if normalize:
        if normalize == 1:
            coefficients /= np.abs(coefficients[0])
        elif normalize == 2:
            coefficients /= np.max(np.abs(coefficients))
        else:
            raise IOError("normalize should be set to 1, 2, or None")
        # Plot:
        if plot_test:
            plt.subplot(3, 1, 3)
            plt.plot(t, coefficients, 'k-', label='coefficients')
            plt.title('normalized coefficients')

    # Plot:
    if plot_test:
        plt.show()

    return coefficients, N


def parabolic(f, x):
    """
    Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    From: https://gist.github.com/endolith/255291 and
          https://github.com/endolith/waveform-analyzer

    Parameters
    ----------
    f : list or array
        vector
    x : integer
        index for vector f

    Returns
    -------
    (vx, vy) : floats
        coordinates of the vertex of a parabola that goes through point x
        and its two neighbors

    Examples
    --------
    >>> from mhealthx.signals import parabolic
    >>> # Define a vector f with a local maximum at index 3 (= 6); find local
    >>> # maximum if points 2, 3, and 4 actually defined a parabola.
    >>> f = [2, 3, 1, 6, 4, 2, 3, 1]
    >>> parabolic(f, argmax(f))
    >>> # Out[4]: (3.2142857142857144, 6.1607142857142856)

    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)

    return xv, yv


def compute_interpeak(data, sample_rate):
    """
    Compute number of samples between signal peaks using the real part of FFT.

    Parameters
    ----------
    data : list or numpy array
        time series data
    sample_rate : float
        sample rate of accelerometer reading (Hz)

    Returns
    -------
    interpeak : integer
        number of samples between peaks

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import compute_interpeak
    >>> data = np.random.random(10000)
    >>> sample_rate = 100
    >>> interpeak = compute_interpeak(data, sample_rate)
    """
    import numpy as np
    from scipy.fftpack import rfft, fftfreq

    # Real part of FFT:
    freqs = fftfreq(data.size, d=1.0/sample_rate)
    f_signal = rfft(data)

    # Maximum non-zero frequency:
    imax_freq = np.argsort(f_signal)[-2]
    freq = np.abs(freqs[imax_freq])

    # Inter-peak samples:
    interpeak = np.int(np.round(sample_rate / freq))

    return interpeak


def compute_mean_teagerkaiser_energy(x):
    """
    Mean Teager-Kaiser energy operator

    (from TKEO function in R library(seewave) using f = 1, m = 1, M = 1)

    Parameters
    ----------
    x : numpy array of floats

    Return
    ------
    tk_energy : float

    Examples
    --------
    >>> from mhealthx.signals import compute_mean_teagerkaiser_energy
    >>> x = np.array([1,  3, 12, 25, 10])
    >>> tk_energy = compute_mean_teagerkaiser_energy(x)

    """
    import numpy as np

    if isinstance(x, list):
        x = np.asarray(x)

    tk_energy = np.mean((x**2)[1:-1] - x[2:] * x[:-2])

    return tk_energy


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
    >>> from mhealthx.signals import root_mean_square
    >>> data = np.random.random(100)
    >>> rms = root_mean_square(data)

    """
    import numpy as np

    N = np.size(data)
    demeaned_data = data - np.mean(data)
    rms = np.sqrt(np.sum(demeaned_data**2 / N))

    return rms


def weighted_to_repeated_values(X, W=[], precision=1):
    """
    Create a list of repeated values from weighted values.

    This is useful for computing weighted statistics (ex: weighted median).

    Adapted to allow for fractional weights from
        http://stackoverflow.com/questions/966896/
               code-golf-shortest-code-to-find-a-weighted-median

    Parameters
    ----------
    X : numpy array of floats or integers
        values
    W : numpy array of floats or integers
        weights
    precision : integer
        number of decimal places to consider weights

    Returns
    -------
    repeat_values : numpy array of floats or integers
        repeated values according to their weight

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import weighted_to_repeated_values
    >>> X = np.array([1,2,4,7,8])
    >>> W = np.array([.1,.1,.3,.2,.3])
    >>> precision = 1
    >>> weighted_to_repeated_values(X, W, precision)
        [1, 2, 4, 4, 4, 7, 7, 8, 8, 8]

    """
    import numpy as np

    # Make sure arguments have the correct type:
    if not isinstance(X, np.ndarray):
        X = np.array(X)
    if not isinstance(W, np.ndarray):
        W = np.array(W)
    if not isinstance(precision, int):
        precision = int(precision)

    if np.size(W):
        # If weights are decimals, multiply by 10 until they are whole.
        # If after multiplying precision times they are not whole, round them:
        whole = True
        if any(np.mod(W,1)):
            whole = False
            for i in range(precision):
                if any(np.mod(W,1)):
                    W *= 10
                else:
                    whole = True
                    break

        if not whole:
             W = [int(np.round(x)) for x in W]

        repeat_values = sum([[x]*w for x,w in zip(X,W)],[])

    else:
        repeat_values = X

    return repeat_values


def compute_median_abs_dev(X, W=[], precision=1, c=1.0):
    """
    Compute the (weighted) median absolute deviation.

    mad = median(abs(x - median(x))) / c

    Parameters
    ----------
    X : numpy array of floats or integers
        values
    W : numpy array of floats or integers
        weights
    precision : integer
        number of decimal places to consider weights
    c : float
        constant used as divisor for mad computation;
        c = 0.6745 is used to convert from mad to standard deviation

    Returns
    -------
    mad : float
        (weighted) median absolute deviation

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import compute_median_abs_dev
    >>> X = np.array([1,2,4,7,8])
    >>> W = np.array([.1,.1,.3,.2,.3])
    >>> precision = 1
    >>> # [1, 2, 4, 4, 4, 7, 7, 8, 8, 8]
    >>> compute_median_abs_dev(X, W, precision)
        2.0

    """
    import numpy as np

    from mhealthx.signals import weighted_to_repeated_values

    # Make sure arguments have the correct type:
    if not isinstance(X, np.ndarray):
        X = np.array(X)
    if not isinstance(W, np.ndarray):
        W = np.array(W)
    if not isinstance(precision, int):
        precision = int(precision)

    if np.size(W):
        X = weighted_to_repeated_values(X, W, precision)

    mad = np.median(np.abs(X - np.median(X))) / c

    return mad


def compute_cv(x):
    """
    cv = 100 * np.std(x) / np.mean(x)

    Parameters
    ----------
    x : list or array of floats

    Return
    ------
    cv : float

    Examples
    --------
    >>> from mhealthx.signals import compute_cv
    >>> x = [1,  3, 10]
    >>> cv = compute_cv(x)

    """
    import numpy as np

    cv = 100 * np.std(x) / np.mean(x)

    return cv


def compute_stats(x):
    """
    Compute statistical summaries of data.

    Parameters
    ----------
    x : list or array of floats

    Return
    ------
    num : integer
        number of elements
    min : integer
        minimum
    max : integer
        maximum
    rng : integer
        range
    avg : float
        mean
    std : float
        standard deviation
    med : float
        median
    mad : float
        median absolute deviation
    kurt : float
        kurtosis
    skew : float
        skewness
    cvar : float
        coefficient of variation
    lower25 : float
        lower quartile
    upper25 : float
        upper quartile
    inter50 : float
        interquartile range

    Examples
    --------
    >>> from mhealthx.signals import compute_stats
    >>> x = [1,  3, 10]
    >>> num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, lower25, upper25, inter50 = compute_stats(x)

    """
    import numpy as np
    from scipy import stats

    from mhealthx.signals import compute_median_abs_dev, compute_cv

    num = np.size(x)
    min = np.min(x)
    max = np.max(x)
    rng = max - min
    avg = np.mean(x)
    std = np.std(x)
    med = np.median(x)
    mad = compute_median_abs_dev(x, W=[], precision=1, c=1.0)

    # Kurtosis and skew:
    #xdiff = x - np.mean(x)
    #kurtosis = np.mean(xdiff**4)/(np.mean(xdiff**2))**2
    kurt = stats.kurtosis(x)
    #skew = np.mean(xdiff**3) / (np.mean(xdiff**2)**(3./2.))
    skew = stats.skew(x)

    # Coefficient of variation:
    cvar = compute_cv(x)

    # Quartiles:
    upper25 = stats.scoreatpercentile(x, 75)
    lower25 = stats.scoreatpercentile(x, 25)
    inter50 = upper25 - lower25

    return num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, \
        lower25, upper25, inter50


def signal_features(data):
    """
    Extract various features from time series data.

    Parameters
    ----------
    data : numpy array of floats
        time series data

    Returns
    -------
    num : integer
        number of elements
    min : integer
        minimum
    max : integer
        maximum
    rng : integer
        range
    avg : float
        mean
    std : float
        standard deviation
    med : float
        median
    mad : float
        median absolute deviation
    kurt : float
        kurtosis
    skew : float
        skewness
    cvar : float
        coefficient of variation
    lower25 : float
        lower quartile
    upper25 : float
        upper quartile
    inter50 : float
        interquartile range
    rms : float
        root mean squared error
    entropy : float
        entropy measure
    tk_energy : float
        mean Teager-Kaiser energy

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.signals import signal_features
    >>> data = np.random.random(100)
    >>> num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, lower25, upper25, inter50, rms, entropy, tk_energy = signal_features(data)

    """
    from scipy.stats import entropy as scipy_entropy

    from mhealthx.signals import compute_stats, root_mean_square, \
        compute_mean_teagerkaiser_energy

    num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, lower25, \
    upper25, inter50 = compute_stats(data)

    rms = root_mean_square(data)

    entropy = scipy_entropy(data)

    tk_energy = compute_mean_teagerkaiser_energy(data)

    return num, min, max, rng, avg, std, med, mad, kurt, skew, cvar, \
           lower25, upper25, inter50, rms, entropy, tk_energy


def gravity_min_mse(gx, gy, gz):
    """
    Compute QC score based on gravity acceleration only.

    Elias Chaibub-Neto used this to find gross rotations of the phone.

    Parameters
    ----------
    gx : list or numpy array
        x-axis gravity accelerometer data
    gy : list or numpy array
        y-axis gravity accelerometer data
    gz : list or numpy array
        z-axis gravity accelerometer data

    Returns
    -------
    min_mse : float
        minimum mean squared error
    vertical : string
        primary direction of vertical ('x', 'y', or 'z')

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> gx, gy, gz = gxyz
    >>> from mhealthx.signals import gravity_min_mse
    >>> min_mse, vertical = gravity_min_mse(gx, gy, gz)

    """
    import numpy as np

    mse1 = np.mean((np.asarray(gx) - 1)**2)
    mse2 = np.mean((np.asarray(gx) + 1)**2)
    mse3 = np.mean((np.asarray(gy) - 1)**2)
    mse4 = np.mean((np.asarray(gy) + 1)**2)
    mse5 = np.mean((np.asarray(gz) - 1)**2)
    mse6 = np.mean((np.asarray(gz) + 1)**2)

    min_mse = np.min([mse1, mse2, mse3, mse4, mse5, mse6])
    imin = np.argmin([mse1, mse2, mse3, mse4, mse5, mse6])

    if imin == 0 or imin == 1:
        vertical = "x"
    elif imin == 2 or imin == 3:
        vertical = "y"
    else:
        vertical = "z"

    return min_mse, vertical


def accelerometer_signal_quality(gx, gy, gz):
    """
    Compute accelerometer signal quality.

    Parameters
    ----------
    gx : list
        x-axis gravity acceleration
    gy : list
        y-axis gravity acceleration
    gz : list
        z-axis gravity acceleration

    Returns
    -------
    min_mse : float
        minimum mean squared error
    vertical : string
        primary direction of vertical ('x', 'y', or 'z')

    Examples
    --------
    >>> from mhealthx.xio import read_accel_json
    >>> input_file = '/Users/arno/DriveWork/mhealthx/mpower_sample_data/deviceMotion_walking_outbound.json.items-a2ab9333-6d63-4676-977a-08591a5d837f5221783798792869048.tmp'
    >>> device_motion = True
    >>> start = 150
    >>> t, axyz, gxyz, uxyz, rxyz, sample_rate, duration = read_accel_json(input_file, start, device_motion)
    >>> gx, gy, gz = gxyz
    >>> from mhealthx.signals import accelerometer_signal_quality
    >>> min_mse, vertical = accelerometer_signal_quality(gx, gy, gz)

    """
    from mhealthx.signals import gravity_min_mse

    min_mse, vertical = gravity_min_mse(gx, gy, gz)

    return min_mse, vertical

