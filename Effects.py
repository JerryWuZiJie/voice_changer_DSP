import numpy as np
from scipy import signal


class Effect:
    def __init__(self, frequency):
        """
        initialize the effect

        @param np.array frequency: normalized frequency
        """
        self.frequency = frequency
        self.n = 0  # TODO: what if self.n keep getting larger?

    def cal_output(self, x):
        """
        Calculate the next output. Will not perform clipping!

        @param array_like x: sound inputs

        @return array_like output: filter output
        """
        pass


class NoEffect(Effect):
    def cal_output(self, x):
        return x

    def clear(self):
        """
        clear all values that would affect the reuse of the effect
        e.g. clear self.n and self.buffer
        """
        self.n = 0


class AM(Effect):
    def cal_output(self, x):
        # signal input
        if isinstance(x, int):
            output = x * np.cos(2 * np.pi * self.frequency * self.n)
            self.n += 1
        # block inputs
        else:
            output = np.zeros(len(x), np.int)
            for i in range(len(x)):
                output[i] = x[i] * np.cos(2 * np.pi * self.frequency * self.n)
                self.n += 1

        return output

    def clear(self):
        super().clear()


class ComplexAM(Effect):
    def __init__(self, frequency, order=6):
        super().__init__(frequency)
        # TODO: how to choose Rp, Rs, and edge for elliptic filter?
        b, a = signal.ellip(order, 0.2, 50, 0.48)
        self.b = [b[i] * 1j ** i for i in range(len(b))]
        self.a = [a[i] * 1j ** i for i in range(len(a))]
        self.prev_states = np.zeros(order)

    def cal_output(self, x):
        """
        Filter data with the designed filter.

        @param array_like x: sound inputs

        @return array_like output: the output of the filter
        """

        # calculate complex output
        complex_output, self.prev_states = signal.lfilter(
            self.b, self.a, x, zi=self.prev_states)
        # shift the output
        t = np.array([self.n+i for i in range(len(x))])  # calculate increment
        complex_output = complex_output * np.exp(
            1j * 2 * np.pi * self.frequency * t)
        self.n += len(x)  # increment self.n
        # take the real part
        output = np.real(complex_output)


        return output


class Delay(Effect):
    def __init__(self, frequency):
        super().__init__(frequency)


class Vibrato(Effect):
    def __init__(self, frequency):
        super().__init__(frequency)


class ButterWorth(Effect):
    """
    this is more like a wrapper for the scipy signal.butter function, for consistence we decide to make it into the child class of Effect
    """

    def __init__(self, order, frequency, btype='lowpass'):
        """
        initialize butterworth filter

        @param int order: the order of the filter
        @param array_like frequency: normalized cutoff frequency (between 0 and 1)
        @param str btype: optional, the type of filter, default is "lowpass"
        """
        super().__init__(frequency)

        # normalized frequency * 2 since signal.butter use Nyquist frequency as normalization constant
        self.b, self.a = signal.butter(order, self.frequency * 2, btype)
        self.prev_states = np.zeros(len(self.b) - 1)

    def cal_output(self, x):
        """
        Filter data with the designed filter.

        @param array_like x: sound inputs

        @return array_like output: the output of the filter
        """
        output, self.prev_states = signal.lfilter(
            self.b, self.a, x, zi=self.prev_states)

        return output

    def clear(self):
        super(ButterWorth, self).clear()
        self.prev_states = np.zeros_like(self.prev_states)


class LPF(Effect):
    def __init__(self, frequency):
        super().__init__()


class HPF(Effect):
    def __init__(self, frequency):
        super().__init__()