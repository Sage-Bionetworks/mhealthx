#!/usr/bin/env python
"""
This program implements some touch screen tapping feature extraction methods.

Elias's R code translated by Arno to Python.

Authors:
    - Elias Chaibub-Neto, 2015  (neto@sagebase.org)
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org) Apache v2.0 License
"""


def compute_tap_intervals(xtaps, t, threshold=20):
    """
    Compute tapping time series (tapping interval and tapping position).

    Parameters
    ----------
    xtaps : numpy array of floats
        x coordinates of touch screen where tapped
    t : numpy array of floats
        time points of taps
    threshold : integer
        x offset threshold for left/right press event (pixels)

    Return
    ------
    ipress : numpy array of integers
        indices of taps above threshold pixels from mean x coordinate
    tap_intervals : numpy array of floats
        time intervals between taps (above threshold from mean x coordinate)

    Examples
    --------
    >>> from mhealthx.extractors.tapping import compute_tap_intervals
    >>> xtaps = [10,  20, 50, 80, 110]
    >>> t = [1.1, 2.3, 3.4, 6.7, 9.0]
    >>> threshold = 20
    >>> ipress, tap_intervals = compute_tap_intervals(xtaps, t, threshold)

    """
    import numpy as np

    if isinstance(xtaps, list):
        xtaps = np.asarray(xtaps)
    if isinstance(t, list):
        t = np.asarray(t)

    # Set time points:
    tap_times = t - t[0]

    # Calculate x offset:
    xtaps_offset = xtaps - np.mean(xtaps)

    # Find left/right finger "press" events:
    dx = xtaps_offset[1:] - xtaps_offset[:-1]
    ipress = np.where(np.abs(dx) > threshold)

    # Filter data:
    #xtaps = xtaps[ipress]
    tap_times = tap_times[ipress]

    # Find press event intervals:
    tap_intervals = tap_times[1:] - tap_times[:-1]

    return ipress, tap_intervals


def compute_intertap_gap(intervals):
    """
    Difference between fastest and slowest intertap intervals.

    Parameters
    ----------
    intervals : list or array of floats
        intertap intervals (s)

    Return
    ------
    delta10 : float
        difference between mean slowest 10 percent and mean fastest 10 percent
    delta25 : float
        difference between mean slowest 25 percent and mean fastest 25 percent
    delta50 : float
        difference between mean slowest 50 percent and mean fastest 50 percent

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.tapping import compute_intertap_gap
    >>> intervals = np.random.random(100)
    >>> delta10, delta25, delta50 = compute_intertap_gap(intervals)

    """
    import numpy as np

    n = len(intervals)

    fast10 = intervals[0:np.round(0.10 * n)]
    fast25 = intervals[0:np.round(0.25 * n)]
    fast50 = intervals[0:np.round(0.50 * n)]
    slow10 = intervals[n - np.round(0.10 * n):n]
    slow25 = intervals[n - np.round(0.25 * n):n]
    slow50 = intervals[n - np.round(0.50 * n):n]

    delta10 = np.mean(fast10) - np.mean(slow10)
    delta25 = np.mean(fast25) - np.mean(slow25)
    delta50 = np.mean(fast50) - np.mean(slow50)

    return delta10, delta25, delta50


def compute_drift(x, y):
    """
    Compute drift.

    Parameters
    ----------
    x : numpy array of floats
    y : numpy array of floats

    Return
    ------
    drift : float

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.tapping import compute_drift
    >>> x = np.random.random(100)
    >>> y = np.random.random(100)
    >>> drift = compute_drift(x, y)

    """
    import numpy as np

    if isinstance(x, list):
        x = np.asarray(x)
    if isinstance(y, list):
        y = np.asarray(y)

    dx = x[1:] - x[:-1]
    dy = y[1:] - y[:-1]
 
    drift = np.sqrt(dx**2 + dy**2)

    return drift


class TapFeatures:
    """Class to add tap features."""
    # Initialize object method:
    def __init__(self):
        """
        Initialize attributes of object:
        """
        self.xtaps = None
        self.ytaps = None
        self.t = None
        self.threshold = None


def compute_tap_features(xtaps, ytaps, t, threshold=20):
    """
    Elias Chaibub-Neto's tapping feature extraction methods.

    Arno translated Elias's R code to Python.

    Parameters
    ----------
    xtaps : numpy array of integers
        x coordinates of touch screen where tapped
    ytaps : numpy array of integers
        y coordinates of touch screen where tapped
    t : numpy array of floats
        time points of taps
    threshold : integer
        x offset threshold for left/right press event (pixels)

    Return
    ------
    T : class
        many features stored in TapFeatures class

    Examples
    --------
    >>> import numpy as np
    >>> from mhealthx.extractors.tapping import compute_tap_features
    >>> xtaps = np.round(200 * np.random.random(100))
    >>> ytaps = np.round(300 * np.random.random(100))
    >>> t = np.linspace(1, 100, 100) / 5.0
    >>> threshold = 20
    >>> T = compute_tap_features(xtaps, ytaps, t, threshold)

    """
    import numpy as np

    from mhealthx.extractors.tapping import compute_drift, \
        compute_tap_intervals, compute_intertap_gap
    from mhealthx.extractors.tapping import TapFeatures as T
    from mhealthx.signals import signal_features

    if isinstance(xtaps, list):
        xtaps = np.array(xtaps)
    if isinstance(ytaps, list):
        ytaps = np.array(ytaps)
    if isinstance(t, list):
        t = np.array(t)

    # Intertap intervals:
    ipress, intervals = compute_tap_intervals(xtaps, t, threshold)

    # Filter data:
    t = t[ipress]
    xtaps = xtaps[ipress]
    ytaps = ytaps[ipress]

    # Delta between fastest and slowest intertap intervals:
    T.intertap_gap10, T.intertap_gap25, \
    T.intertap_gap50 = compute_intertap_gap(intervals)

    # Left and right taps and drift:
    mean_x = np.mean(xtaps)
    iL = np.where(xtaps < mean_x)
    iR = np.where(xtaps >= mean_x)
    xL = xtaps[iL]
    yL = ytaps[iL]
    xR = xtaps[iR]
    yR = ytaps[iR]
    driftL = compute_drift(xL, yL)
    driftR = compute_drift(xR, yR)

    # Number of taps:
    T.num_taps = xtaps.size
    T.num_taps_left = xL.size
    T.num_taps_right = xR.size

    # Time:
    T.time_rng = t[-1] - t[0]

    # Intertap interval statistics:
    T.intertap_num, T.intertap_min, T.intertap_max, T.intertap_rng, \
    T.intertap_avg, T.intertap_std, T.intertap_med, T.intertap_mad, \
    T.intertap_kurt, T.intertap_skew, T.intertap_cvar, T.intertap_lower25, \
    T.intertap_upper25, T.intertap_inter50, T.intertap_rms, \
    T.intertap_entropy, T.intertap_tk_energy = signal_features(intervals)

    # Tap statistics:
    T.xL_num, T.xL_min, T.xL_max, T.xL_rng, T.xL_avg, T.xL_std, \
    T.xL_med, T.xL_mad, T.xL_kurt, T.xL_skew, T.xL_cvar, \
    T.xL_lower25, T.xL_upper25, T.xL_inter50, T.xL_rms, \
    T.xL_entropy, T.xL_tk_energy = signal_features(xL)

    T.xR_num, T.xR_min, T.xR_max, T.xR_rng, T.xR_avg, T.xR_std, \
    T.xR_med, T.xR_mad, T.xR_kurt, T.xR_skew, T.xR_cvar, \
    T.xR_lower25, T.xR_upper25, T.xR_inter50, T.xR_rms, \
    T.xR_entropy, T.xR_tk_energy = signal_features(xR)

    # T.yL_num, T.yL_min, T.yL_max, T.yL_rng, T.yL_avg, T.yL_std, \
    # T.yL_med, T.yL_mad, T.yL_kurt, T.yL_skew, T.yL_cvar, \
    # T.yL_lower25, T.yL_upper25, T.yL_inter50, T.yL_rms, \
    # T.yL_entropy, T.yL_tk_energy = signal_features(yL)

    # T.yR_num, T.yR_min, T.yR_max, T.yR_rng, T.yR_avg, T.yR_std, \
    # T.yR_med, T.yR_mad, T.yR_kurt, T.yR_skew, T.yR_cvar, \
    # T.yR_lower25, T.yR_upper25, T.yR_inter50, T.yR_rms, \
    # T.yR_entropy, T.yR_tk_energy = signal_features(yR)

    # Drift statistics:
    T.driftL_num, T.driftL_min, T.driftL_max, T.driftL_rng, T.driftL_avg, \
    T.driftL_std, T.driftL_med, T.driftL_mad, T.driftL_kurt, T.driftL_skew, \
    T.driftL_cvar, T.driftL_lower25, T.driftL_upper25, T.driftL_inter50, \
    T.driftL_rms, T.driftL_entropy, T.driftL_tk_energy = \
        signal_features(driftL)

    T.driftR_num, T.driftR_min, T.driftR_max, T.driftR_rng, T.driftR_avg, \
    T.driftR_std, T.driftR_med, T.driftR_mad, T.driftR_kurt, T.driftR_skew, \
    T.driftR_cvar, T.driftR_lower25, T.driftR_upper25, T.driftR_inter50, \
    T.driftR_rms, T.driftR_entropy, T.driftR_tk_energy = \
        signal_features(driftR)

    return T