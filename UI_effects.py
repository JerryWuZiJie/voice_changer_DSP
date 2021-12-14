import struct

import PySimpleGUI as sg
import numpy as np
import pyaudio
import Effects

# sound properties
BLOCKLEN = 1024  # Number of frames per block
WIDTH = 2  # Bytes per sample
CHANNELS = 1  # Number of channels
RATE = 8000  # Sampling rate in Hz (samples/second)

open_sound = False


def play_effects(window):
    # pysimplegui window passed in

    # ------------pyaudio setup--------------

    # Open the audio output stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=256,
                    start=False)  # turn off at first
    play_sound = False

    # keep a original copy of the play button color if color changed
    original_pBut_color = window['play_but'].ButtonColor

    # default effect (TODO: frequency)
    effect = Effects.effects_dict[window['effect_dropdown'].get()](500, RATE)

    while True:

        event, values = window.read(timeout=1)

        # windows closed or back to start menu
        if event == sg.WIN_CLOSED or event == 'back_start_but':
            stream.stop_stream()
            stream.close()
            p.terminate()
            if event == 'back_start_but':
                window['menu'].update(visible=True)
                window['start_interface'].update(visible=False)
            break

        elif event == 'play_but':
            if play_sound:  # before playing, now need to stop
                play_sound = False

                # change display text
                window['play_but'].update('Play')
                window['play_but'].update(button_color=original_pBut_color)

                # start streaming
                stream.stop_stream()
            else:  # before stop, now need to play
                play_sound = True

                # change display text
                window['play_but'].update('Stop')
                window['play_but'].update(button_color='red')

                # stop streaming
                stream.start_stream()

        elif event == 'effect_dropdown':
            # TODO: other param
            effect = Effects.effects_dict[window['effect_dropdown'].get()](500, RATE)

        if play_sound:
            # TODO: still raise error with no overflow exception
            input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
            x = np.array(struct.unpack('h' * BLOCKLEN, input_bytes))

            # get output
            y = effect.cal_output(x)

            # Convert numeric list to binary data
            y = np.clip(np.array(y, np.int), -32768, 32767)
            output_bytes = struct.pack('h' * BLOCKLEN, *y)

            # Write binary data to audio output stream
            stream.write(output_bytes, BLOCKLEN)
