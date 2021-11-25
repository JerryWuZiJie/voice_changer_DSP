import numpy as np
import struct
import pyaudio
import Effects


BLOCKLEN = 1024    # Number of frames per block
WIDTH = 2          # Bytes per sample
CHANNELS = 1       # Number of channels
RATE = 8000        # Sampling rate in Hz (samples/second)

# Parameters
T = 10       # Total play time (seconds)

NumBlocks = int(T * RATE / BLOCKLEN)

# make 6 order band-pass butterworth filter using scipy.signal
f1 = 200
f2 = 1000
nyq = 0.5 * RATE
low = f1 / nyq
high = f2 / nyq
butter_filter = Effects.ButterWorth(6, [low, high], btype='bandpass')

# Open the audio output stream
p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(format=PA_FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=256)

print('Playing for %f seconds ...' % T)


# Loop through blocks
for i in range(NumBlocks):

    input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
    x = struct.unpack('h'*BLOCKLEN, input_bytes)
    y = butter_filter.lfilter(x)

    y = np.clip(y.astype(np.int), -32768, 32767)

    # Convert numeric list to binary data
    output_bytes = struct.pack('h' * BLOCKLEN, *y)

    # Write binary data to audio output stream
    stream.write(output_bytes, BLOCKLEN)

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
