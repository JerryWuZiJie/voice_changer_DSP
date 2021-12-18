import sys
import traceback
import time
import os
import platform
import inspect
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure

import PySimpleGUI as sg

import Effects
import UI_effects

# constant setup
# default element size
PIXEL_W = 700
PIXEL_H = 30
# pixel size to button size conversion
PW_TO_B = 1 / 7
PH_TO_B = 1 / 30
# default button size
BUTTON_W = int(PIXEL_W * PW_TO_B)
BUTTON_H = int(PIXEL_H * PH_TO_B * 3)
BUTTON_SIZE = (BUTTON_W, BUTTON_H)
BUTTON_PAD_SIZE = (100, 20)
COLUMN_SIZE = (1000, 600)
# default text attributes
BACK_COLOR = 'grey'
DEFAULT_FONT = 'Helvetica'
DEFAULT_FONT_SIZE = 10
# help menu text size
HELP_TEXT_SIZE = (int(BUTTON_SIZE[0] * 0.8), 0)


def main(theme='Python'):
    # effects list
    effects_list = list(Effects.effects_dict.keys())

    # set GUI theme
    sg.theme(theme)

    # ---------------main menu-----------------
    # widget for main menu: display text, voice changer, help menu, exit
    welcome_text = sg.Text("Voice Changer", text_color='white',
                           font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 5)),
                           justification='l')
    start_but = sg.Button('Start', key='start_but', pad=BUTTON_PAD_SIZE,
                          size=BUTTON_SIZE, border_width=0)
    help_but = sg.Button('Help', key='help_but', pad=BUTTON_PAD_SIZE,
                         size=BUTTON_SIZE, border_width=0)
    exit_but = sg.Button('Exit', key='exit_but', pad=BUTTON_PAD_SIZE,
                         size=BUTTON_SIZE, border_width=0,
                         button_color=BACK_COLOR)

    menu = sg.Column(key='menu',
                     layout=[[welcome_text], [start_but], [help_but],
                             [exit_but]], element_justification='c',
                     size=COLUMN_SIZE)

    # ---------------start menu-----------------
    # widget for effect (start) menu: play/stop button, effects dropdown menu, slider, graph for signal display
    play_but = sg.Button('Play', key='play_but',
                         size=(int(BUTTON_W / 3), int(BUTTON_H / 2)))
    effect_dropdown = sg.Combo(effects_list, key='effect_dropdown',
                               default_value=effects_list[0], readonly=True,
                               size=(int(BUTTON_W * 0.6)), enable_events=True)
    apply_but = sg.Button('Apply', key='apply_but',
                          size=(int(BUTTON_W / 3), int(BUTTON_H / 2)))
    input_parameters = sg.Input(key='input_parameters',
                                size=(int(BUTTON_W * 0.62), int(BUTTON_H / 3)))
    # the change will apply by pressing enter
    apply_enter = sg.Button('Apply', key='apply_enter', visible=False,
                            bind_return_key=True)

    # tunable value frame
    gain_slider = sg.Slider(range=(0, 100), key='gain_slider',
                            default_value=100, orientation='vertical',
                            enable_events=True)
    gain_slider_text = sg.Text('gain', key='gain_slider_text')
    gain_column = sg.Column([[gain_slider], [gain_slider_text]],
                            element_justification='r')
    start_slider_frame = sg.Frame(layout=[[gain_column]],
                                  title='tunable values',
                                  size=(int(PIXEL_W / 8), int(PIXEL_H * 15)))

    # plot frame
    time_r = sg.Radio('time', 'radio_group1', key='time_r', enable_events=True,
                      default=True)
    freq_r = sg.Radio('frequency', 'radio_group1', key='freq_r',
                      enable_events=True)
    no_r = sg.Radio('no', 'radio_group1', key='no_r', enable_events=True)
    signal_plot = sg.Canvas(size=(int(PIXEL_W / 2), int(PIXEL_H * 10)),
                            key='-CANVAS-')
    start_plot_frame = sg.Frame(
        layout=[[sg.Column([[time_r, freq_r, no_r], [signal_plot]])]],
        title='signal plot')
    back_start_but = sg.Button('Back', key='back_start_but',
                               pad=BUTTON_PAD_SIZE,
                               size=(BUTTON_W, int(BUTTON_H / 2)),
                               border_width=0,
                               button_color=BACK_COLOR)

    start_menu = sg.Column(key='start_menu',
                           layout=[[play_but, effect_dropdown],
                                   [apply_but, input_parameters, apply_enter],
                                   [start_slider_frame, start_plot_frame],
                                   [back_start_but]], element_justification='c',
                           visible=False, size=COLUMN_SIZE)

    # ---------------help menu-----------------
    # widget for help menu: back button, text blocks, back button
    back_help_but_t = sg.Button("Back", key='back_h_t', pad=BUTTON_PAD_SIZE,
                                size=(BUTTON_SIZE[0], BUTTON_SIZE[1] // 2),
                                border_width=0, button_color=BACK_COLOR)
    instruction = "This is the instruction for how to use this program\n\n" \
                  "There are four buttons on startup menu: Start," \
                  "Help, and Exit\n" \
                  "\n\n>>> Start:\n" \
                  "The start menu let you play the sound effect.\n" \
                  "You can choose effect from the dropdown menu, and change " \
                  "parameters for the effect in the input bar.\n" \
                  "You can show the sound signal in time domain and frequency" \
                  "domain. If the voice sound laggy, choose no to turn off" \
                  "plotting might help.\n" \
                  "\n\n>>> Help\n" \
                  "This is the help menu you are looking at.\n" \
                  "\n\n>>> Exit\n" \
                  "Press this button will exit the program. You could also" \
                  "click 'x' on top right corner to close the program.\n"
    instruction_info = sg.Multiline(instruction, size=(BUTTON_W, BUTTON_H * 9),
                                    disabled=True, no_scrollbar=True)
    back_help_but_b = sg.Button('Back', key='back_h_b', pad=BUTTON_PAD_SIZE,
                                size=(BUTTON_W, BUTTON_H // 2),
                                border_width=0, button_color=BACK_COLOR)

    help_menu = sg.Column(
        layout=[[back_help_but_t], [instruction_info], [back_help_but_b]],
        element_justification='c',
        visible=False, size=COLUMN_SIZE)

    # start the window, all widget should be initialized before this
    window = sg.Window("Voice Changer", layout=[[sg.pin(menu, shrink=True)],
                                                [sg.pin(help_menu,
                                                        shrink=True)],
                                                [sg.pin(start_menu,
                                                        shrink=True)]],
                       resizable=True, element_justification='c', finalize=True,
                       use_ttk_buttons=True)

    # enter event loop
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # -------------start menu-------------
        elif event == start_but.Key:  # go to start menu
            menu.update(visible=False)
            start_menu.update(visible=True)
            try:
                UI_effects.play_effects(window)
            except Exception as e:
                # popup error message
                sg.popup('An unexpected error occur during simulation! Error message: '+str(e), title='ERROR',
                         keep_on_top=True, button_color=('white', 'red'), grab_anywhere=True)
                # break the loop
                break

        # -------------help menu-------------
        elif event == help_but.Key:  # go to help menu
            menu.update(visible=False)
            help_menu.update(visible=True)
        # back from help menu to main menu
        elif event == 'back_h_b' or event == 'back_h_t':
            menu.update(visible=True)
            help_menu.update(visible=False)

        # -------------exit program-------------
        elif event == exit_but.Key:
            window.close()
            break


if __name__ == '__main__':
    main()
