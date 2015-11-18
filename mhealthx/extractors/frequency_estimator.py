#!/usr/bin/env python
"""
This program implements some of the frequency estimation functions from:
https://gist.github.com/endolith/255291 and
https://github.com/endolith/waveform-analyzer
"""


def freq_from_autocorr(signal, fs):
    """
    Estimate frequency using autocorrelation.

    Pros: Best method for finding the true fundamental of any repeating wave,
    even with strong harmonics or completely missing fundamental

    Cons: Not as accurate, doesn't work for inharmonic things like musical
    instruments, this implementation has trouble with finding the true peak

    From: https://gist.github.com/endolith/255291 and
          https://github.com/endolith/waveform-analyzer

    Parameters
    ----------
    signal : list or array
        time series data
    fs : integer
        sample rate

    Returns
    -------
    frequency : float
        frequency (Hz)

    """
    import numpy as np
    from scipy.signal import fftconvolve
    from matplotlib.mlab import find

    from mhealthx.signals import parabolic

    # Calculate autocorrelation (same thing as convolution, but with one input
    # reversed in time), and throw away the negative lags:
    signal -= np.mean(signal) # Remove DC offset
    corr = fftconvolve(signal, signal[::-1], mode='full')
    corr = corr[len(corr)/2:]

    # Find the first low point:
    d = np.diff(corr)
    start = find(d > 0)[0]

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    i_peak = np.argmax(corr[start:]) + start
    i_interp = parabolic(corr, i_peak)[0]
    frequency = fs / i_interp

    return frequency


def freq_from_hps(signal, fs):
    """
    Estimate frequency using harmonic product spectrum.

    Note: Low frequency noise piles up and overwhelms the desired peaks.

    From: https://gist.github.com/endolith/255291 and
          https://github.com/endolith/waveform-analyzer

    Parameters
    ----------
    signal : list or array
        time series data
    fs : integer
        sample rate

    Returns
    -------
    frequency : float
        frequency (Hz)

    """
    import numpy as np
    from scipy.signal import blackmanharris, decimate

    from mhealthx.signals import parabolic

    N = len(signal)
    signal -= np.mean(signal) # Remove DC offset

    # Compute Fourier transform of windowed signal:
    windowed = signal * blackmanharris(len(signal))

    # Get spectrum:
    X = np.log(abs(np.fft.rfft(windowed)))

    # Downsample sum logs of spectra instead of multiplying:
    hps = np.copy(X)
    for h in np.arange(2, 9): # TODO: choose a smarter upper limit
        dec = decimate(X, h)
        hps[:len(dec)] += dec

    # Find the peak and interpolate to get a more accurate peak:
    i_peak = np.argmax(hps[:len(dec)])
    i_interp = parabolic(hps, i_peak)[0]

    # Convert to equivalent frequency:
    frequency = fs * i_interp / N # Hz

    return frequency
