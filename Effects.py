import numpy as np
from scipy import signal


class Effect:
    def __init__(self, frequency):
        """
        frequency: normalized frequency
        """
        self.frequency = frequency
        self.n = 0

    def cal_output(self, x):
        """
        calculate the next output
        """
        self.n += 1

    def clear(self):
        """
        clear all the buffer
        """
        self.n = 0


class AM(Effect):
    def __init__(self, frequency):
        super().__init__(frequency)


class Delay(Effect):
    def __init__(self, frequency):
        super().__init__(frequency)


class vibrato(Effect):
    def __init__(self, frequency):
        super().__init__(frequency)


class ButterWorth(Effect):
    """
    this is more like a wrapper for the scipy signal.butter function, for consistence we decide to make it into the child class of Effect
    """

    def __init__(self, order, frequency, btype='lowpass'):
        super().__init__(frequency)
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

        # normalized frequency * 2 since signal.butter use Nyquist frequency as normalization constant
        self.b, self.a = signal.butter(order, self.frequency * 2, btype)
        self.prev_states = np.zeros(len(self.b) - 1)

    def cal_output(self, x, zi=None):
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

    def clear(self):
        super(ButterWorth, self).clear()
        self.prev_states = np.zeros_like(self.prev_states)


class LPF(Effect):
    def __init__(self, frequency):
        super().__init__()


class HPF(Effect):
    def __init__(self, frequency):
        super().__init__()
