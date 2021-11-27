import numpy as np
import struct
import pyaudio


def mic_in_spkr_out(effect_class, frequency, duration=10, **kwargs):
    """
    play the specified effect using microphone input and will output to speaker

    @param Effect effect_class: the filter of type Effect
    @param np.array frequency: frequencies of the filter
    @param int duration: the duration of the time
    @param **kwargs: other kwargs for specific effects

    @return: None
    """

    # sound properties
    BLOCKLEN = 1024  # Number of frames per block
    WIDTH = 2  # Bytes per sample
    CHANNELS = 1  # Number of channels
    RATE = 8000  # Sampling rate in Hz (samples/second)

    # implement effect
    effect = effect_class(frequency=frequency / RATE, **kwargs)

    # Open the audio output stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=256)

    print('start playing for %f seconds ...' % duration)

    # Loop through blocks
    for i in range(int(duration * RATE / BLOCKLEN)):
        input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
        x = struct.unpack('h' * BLOCKLEN, input_bytes)
        y = effect.cal_output(x)

        y = np.clip(y.astype(np.int), -32768, 32767)

        # Convert numeric list to binary data
        output_bytes = struct.pack('h' * BLOCKLEN, *y)

        # Write binary data to audio output stream
        stream.write(output_bytes, BLOCKLEN)

    print('* Finished')

    stream.stop_stream()
    stream.close()
    p.terminate()
