import numpy as np
from scipy import signal


class Effect:
    def __init__(self,):
        pass

    def filter(x):
        pass


class AM(Effect):
    def __init__(self):
        pass


class Delay(Effect):
    def __init__(self):
        pass


class ButterWorth(Effect):
    """
    this is more like a wrapper for the scipy signal.butter function, for consistence we decide to make it into the child class of Effect
    """

    def __init__(self, N, Wn, btype='lowpass'):
        """
        initialize butterworth filter

        Parameters
        ----------
        N : int
            The order of the filter.
        Wn : array_like
            normalized cutoff frequency (between 0 and 1)
        btype : {'bandpass', 'lowpass', 'highpass', 'bandstop'}, optional
            The type of filter.  Default is 'bandpass'.
        """

        self.b, self.a = signal.butter(N, Wn, btype)
        self.prev_states = np.zeros(len(self.b) - 1)

    def lfilter(self, x, zi=None):
        """
        Filter data with the designed filter.

        Parameters
        ----------
        x : array_like
            An N-dimensional input array.
        zi : array_like, optional
            Initial conditions for the filter delays.

        Returns
        -------
        y : array
            The output of the digital filter.
        zf : array, optional
            If `zi` is None, this is not returned, otherwise, `zf` holds the
            final filter delay values.
        """
        y, self.prev_states = signal.lfilter(
            self.b, self.a, x, zi=self.prev_states)
        
        return y


class LPF(Effect):
    def __init__(self):
        pass


class HPF(Effect):
    def __init__(self):
        pass
