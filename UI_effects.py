import struct

import PySimpleGUI as sg
import numpy as np
import pyaudio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure

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

    # keep an original copy of the play button color if color changed
    original_pBut_color = window['play_but'].ButtonColor

    # ------------effect setup-------------- (TODO: frequency)
    effect = Effects.effects_dict[window['effect_dropdown'].get()](500, RATE)

    # ------------plotting setup--------------
    frequency_domain = True
    f_x_limit = [0, RATE/2]  # frequency domain y limit
    t_x_limit = [0, BLOCKLEN]  # time domain y limit
    f_y_limit = [0, RATE*20]
    t_y_limit = [-32768, 32767]

    # figure out which type of plot should be drawn
    plot_type = None
    if window['time_r'].get() is True:
        plot_type = 't'
    elif window['freq_r'].get() is True:
        plot_type = 'f'
    elif window['no_r'].get() is True:
        plot_type = 'n'

    # draw the initial plot in the window
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)
    ax.grid()
    if plot_type == 'f':
        ax.set_xlim(f_x_limit)
        ax.set_ylim(f_y_limit)
    elif plot_type == 't':
        ax.set_xlim(t_x_limit)
        ax.set_ylim(t_y_limit)
    x_data = RATE / BLOCKLEN * np.arange(BLOCKLEN)
    # else: no, nothing need to do
    fig_agg = FigureCanvasTkAgg(fig, window['-CANVAS-'].TKCanvas)
    fig_agg.draw()
    fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)


    # ------------event loop--------------
    while True:

        event, values = window.read(timeout=1)

        # no event
        if event == "__TIMEOUT__":
            pass

        # windows closed or back to start menu
        elif event == sg.WIN_CLOSED or event == 'back_start_but':
            # stop streaming
            stream.stop_stream()
            stream.close()
            p.terminate()
            if event == 'back_start_but':
                # reset visibility
                window['menu'].update(visible=True)
                window['start_interface'].update(visible=False)
                # change display text in case for reopen next time
                window['play_but'].update('Play')
                window['play_but'].update(button_color=original_pBut_color)
                # remove plot
                fig_agg.get_tk_widget().pack_forget()
            break

        # start applying effect and output sound
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

        # effect type is changed
        elif event == 'effect_dropdown':
            # TODO: other param
            effect = Effects.effects_dict[window['effect_dropdown'].get()](1000, RATE)

        # check which plot type is selected
        elif event == 'time_r':
            plot_type = 't'
        elif event == 'freq_r':
            plot_type = 'f'
        elif event == 'no_r':
            plot_type = 'n'

        if play_sound:
            input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
            x = np.array(struct.unpack('h' * BLOCKLEN, input_bytes))

            # get output
            y = effect.cal_output(x) * (window['gain_slider'].TKIntVar.get()/100)

            # Convert numeric list to binary data
            y = np.clip(np.array(y, np.int), -32768, 32767)
            output_bytes = struct.pack('h' * BLOCKLEN, *y)

            # Write binary data to audio output stream
            stream.write(output_bytes, BLOCKLEN)

            # update plot
            ax.cla()  # clear the subplot
            ax.grid()  # draw the grid
            if plot_type == 'f':
                ax.set_xlim(f_x_limit)
                ax.set_ylim(f_y_limit)
                ax.plot(x_data, np.abs(np.fft.fft(y)), color='purple')
            elif plot_type == 't':
                ax.set_xlim(t_x_limit)
                ax.set_ylim(t_y_limit)
                ax.plot(y, color='purple')

            fig_agg.draw()

