import numpy as np
import Effects
from ex_template import mic_in_spkr_out

# make 6 order band-pass butterworth filter using scipy.signal
frequency = 300

mic_in_spkr_out(Effects.AM, frequency=np.array(frequency))
