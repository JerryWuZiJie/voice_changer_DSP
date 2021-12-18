import inspect
import sys

import numpy as np
from scipy import signal


class Effect:
    # the default input argument (exclude rate), all should be float
    default_input = "frequency=200"

    def __init__(self, frequency, rate):
        """
        initialize the effect

        @param np.array frequency: normalized frequency
        """
        self.rate = rate
        self.frequency = frequency / int(self.rate/2)  # use nyquist frequency
        if isinstance(self.frequency, np.ndarray):
            for i in range(len(self.frequency)):
                if self.frequency[i] >= 1:
                    print('\033[91m' + 'Warning: maximum frequency exceeded, tune to smaller frequency' + '\033[0m')
                    self.frequency[i] = 0.999
                    print(self.frequency)
        elif self.frequency >= 1:
            print('\033[91m' + 'Warning: maximum frequency exceeded, tune to smaller frequency' + '\033[0m')
            self.frequency = 0.999
        self.n = 0  # notice: if play for too long, this can grow very large

    def cal_output(self, x):
        """
        Calculate the next output. Will not perform clipping!

        @param array_like x: sound inputs

        @return array_like output: filter output
        """
        pass

    def clear(self):
        """
        clear all values that would affect the reuse of the effect
        e.g. clear self.n and self.buffer
        """
        self.n = 0


class NoEffect(Effect):
    default_input = "# no tunable parameters"

    def cal_output(self, x):
        return x


class AM(Effect):
    def cal_output(self, x):
        # single input
        if isinstance(x, int):
            output = x * np.cos(2 * np.pi * self.frequency * self.n)
            self.n += 1
        # block inputs
        else:
            output = np.zeros(len(x))
            for i in range(len(x)):
                output[i] = x[i] * np.cos(2 * np.pi * self.frequency * self.n)
                self.n += 1

        return output


class ComplexAM(Effect):
    default_input = "frequency=200, order=6  # order should be between 1 to 10"

    def __init__(self, frequency, rate, order=6):
        super().__init__(frequency, rate)
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
        t = np.array([self.n + i for i in range(len(x))])  # calculate increment
        complex_output = complex_output * np.exp(
            1j * 2 * np.pi * self.frequency * t)
        self.n += len(x)  # increment self.n
        # take the real part
        output = np.real(complex_output)

        return output

    def clear(self):
        super().clear()
        self.prev_states = np.zeros(self.prev_states)


class Delay(Effect):
    pass


class Vibrato(Effect):
    default_input = "frequency=2, T=0.5, W=0.02  # T>=W, can be decimal"

    def __init__(self, frequency, rate, delay=0.5, vary_delay=0.02):
        """

        @param float frequency: frequency of the varying delay
        @param float delay: constant delay T
        @param float vary_delay: varying delay W
        """
        if delay < vary_delay:
            raise Exception(
                "delay (T) should be greater or equal to varying delay (W)")
        super().__init__(frequency, rate)
        self.T = int(delay * self.rate)
        self.W = int(vary_delay * self.rate)
        # buffer
        self.buffer = np.zeros(self.T + self.W)
        # write index
        self.kw = 0

    def cal_output(self, x):
        def cal_singe_output(single_input):
            """
            helper function for calculating single output

            @param int single_input: single bit sound input
            @return float output: single bit sound output
            """
            tau = self.T + self.W * np.sin(2 * np.pi * self.frequency * self.n)
            kr_prev = int(np.floor(self.kw - tau))
            frac = (self.kw - tau) - kr_prev
            kr_prev %= len(self.buffer)
            kr_next = (kr_prev + 1) % len(self.buffer)
            output = (1 - frac) * self.buffer[kr_prev] + frac * self.buffer[kr_next]

            # update buffer and time
            self.buffer[self.kw] = single_input
            self.kw = (self.kw + 1) % len(self.buffer)
            self.n += 1

            return output

        # single input
        if isinstance(x, int):
            output = cal_singe_output(x)
        # block inputs
        else:
            output = np.zeros(len(x))
            for i in range(len(x)):
                output[i] = cal_singe_output(x[i])

        return output

    def clear(self):
        super().clear()
        self.kw = 0
        self.buffer = np.zeros(self.buffer)


class ButterWorth(Effect):
    """
    this is more like a wrapper for the scipy signal.butter function, for consistence we decide to make it into the child class of Effect
    """
    default_input = "frequency=200, order=5, btype='lowpass'"

    def __init__(self, frequency, rate, order=5, btype='lowpass'):
        """
        initialize butterworth filter

        @param int order: the order of the filter
        @param array_like frequency: normalized cutoff frequency (between 0 and 1)
        @param str btype: optional, the type of filter, default is "lowpass"
        """
        super().__init__(frequency, rate)

        self.b, self.a = signal.butter(order, self.frequency, btype)
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


class LPF(ButterWorth):
    default_input = "frequency=200"

    def __init__(self, frequency, rate):
        super().__init__(frequency, rate, btype='lowpass')


class HPF(ButterWorth):
    default_input = "frequency=200"

    def __init__(self, frequency, rate):
        super().__init__(frequency, rate, btype='highpass')


class BPF(ButterWorth):
    default_input = "frequency=200, freq_l=200, freq_h=1000)  # first fl < second fh"

    def __init__(self, frequency1, rate, frequency2):
        super().__init__(np.array([frequency1, frequency2]), rate, btype='bandpass')


class PP(Effect):
    default_input = "a1=1, a2=1, b1=0.7, b2=0.7, c1=1, c2=1, delay_sec=0.2"

    def __init__(self, rate, frequency, a1=1, a2=1, b1=0.7, b2=0.7, c1=1, c2=1,
                 delay_sec=0.2):
        super().__init__(frequency, rate)

        self.N = int(rate * delay_sec)
        self.buffer1 = self.N * [0]
        self.buffer2 = self.N * [0]
        self.a1, self.a2 = a1, a2
        self.b1, self.b2 = b1, b2
        self.c1, self.c2 = c1, c2

    def cal_output(self, x):
        k = 0
        output1 = np.zeros(len(x))
        output2 = np.zeros(len(x))
        for i, x_i in enumerate(x):
            x_i1 = x_i
            x_i2 = x_i

            u0_1 = self.a1 * x_i1 + self.b1 * self.buffer2[k]
            u0_2 = self.a2 * x_i2 + self.b2 * self.buffer1[k]

            y0_1 = self.a1 * x_i1 + self.c1 * self.buffer1[k]
            y0_2 = self.a2 * x_i2 + self.c2 * self.buffer2[k]

            self.buffer1[k] = u0_1
            self.buffer2[k] = u0_2
            k = (k + 1) % self.N
            output1[i] = y0_1
            output2[i] = y0_2

        return output1


class Echo(Effect):
    default_input = "frequency=200, dly_in_sec=0.2, gain=0.5"

    def __init__(self, frequency, rate, dly_in_sec=0.2, gain=0.5):
        super().__init__(frequency, rate)
        self.gain = gain
        self.dly_in_samp = int(dly_in_sec * rate)
        self.buffer = np.zeros(self.dly_in_samp)
        self.k = 0

    def cal_output(self, x):
        output = np.zeros(len(x)).astype(int)
        for i, x_i in enumerate(x):
            y_i = int(x_i + self.gain * self.buffer[self.k])
            output[i] = y_i
            self.buffer[self.k] = x_i
            self.k = (self.k + 1) % self.dly_in_samp

        return output


class Alien(Effect):
    default_input = "frequency=200, dly_in_sec=0.2, delay_gain=1"

    def __init__(self, frequency, rate, dly_in_sec=0.2, delay_gain=1):
        super().__init__(frequency, rate)

        self.bufferLen = int(rate * dly_in_sec)
        self.delay_gain = delay_gain

    def cal_output(self, x):
        output = np.zeros(len(x))
        buffer = self.bufferLen * [0]
        k = 0
        for i, x_i in enumerate(x):
            output[i] = x_i * np.cos(2 * np.pi * 0.6 * i) + self.delay_gain * buffer[k]
            buffer[k] = output[i]
            k = (k + 1) % len(buffer)

        return output


class Autobots(Effect):
    default_input = "frequency=200, low_freq=0.1, high_freq=0.2 # 0 < low_freq < high_freq < 1"

    def __init__(self, frequency, rate, low_freq=0.1, high_freq=0.2):
        super().__init__(frequency, rate)
        self.cutoff_freq = [low_freq, high_freq]

    def cal_output(self, x):
        b, a = signal.butter(4, self.cutoff_freq, 'bandpass')
        
        output = signal.filtfilt(b, a, x)
        return output

class Drunk(Effect):
    default_input = "frequency=200, delay_sec=0.2"

    def __init__(self, frequency, rate, delay_sec=0.2):
        super().__init__(frequency, rate)
        self.bufferLen = int(delay_sec * rate)
        self.buffer = self.bufferLen * [0]
        self.k = 0

    def cal_output(self, x):
        output = np.zeros(x.shape[0])
        for i, x_i in enumerate(x):
            y_i = x_i * np.cos(i) + x_i * np.sin(i) + self.buffer[self.k]
            output[i] = y_i
            self.buffer[self.k] = x_i
            self.k = (self.k + 1) % self.bufferLen

        return output

# get a list of all the effects
effects_dict = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
# remove abstract class from the list
del effects_dict[Effect.__name__]
del effects_dict[ButterWorth.__name__]
