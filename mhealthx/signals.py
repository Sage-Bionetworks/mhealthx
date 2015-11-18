#!/usr/bin/env python
"""
Signal processing functions from different sources.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

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

