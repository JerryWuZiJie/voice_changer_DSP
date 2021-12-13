import PySimpleGUI as sg
import traceback
import time
import os
import winsound
import platform

import Effects

BUTTON_SIZE = (100, 5)
BUTTON_PAD_SIZE = (100, 20)
COLUMN_SIZE = (1000, 600)

BACK_COLOR = 'grey'

DEFAULT_FONT = 'Helvetica'
DEFAULT_FONT_SIZE = 10

HELP_TEXT_SIZE = (int(BUTTON_SIZE[0] * 0.8), 0)


def main(theme='Python'):
    # set GUI theme
    sg.theme(theme)

    # directory to save log file
    if not os.path.isdir("voice_changer log"):
        os.makedirs("voice_changer log")

    # file to save user setting
    sg.user_settings_filename(path='./voice_changer log')

    # log user system type
    if not sg.user_settings_get_entry('system_info', None):
        sg.user_settings_set_entry('system_info', str(platform.system()) + ' ' + str(platform.release()))

    # widget for main menu: display text, voice changer, help menu, exit
    welcome_text = sg.Text(
        "Voice Changer",
        text_color='white', font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 8)),
        justification='l')
    start_but = sg.Button('Start', key='start_but', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0)
    diy_but = sg.Button('DIY effect', key='diy_but', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0)
    help_but = sg.Button('Help', key='help_but', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0)
    exit_but = sg.Button('Exit', key='exit_but', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0,
                         button_color=BACK_COLOR)

    menu = sg.Column(layout=[[welcome_text], [start_but], [diy_but], [help_but], [exit_but]], element_justification='c',)

    # widget for effect (start) menu: train and test
    train_but = sg.Button('Train', key='train', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0)
    test_but = sg.Button('Test', key='test', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0)
    back_start_but = sg.Button('Back', key='back_s', pad=BUTTON_PAD_SIZE, size=BUTTON_SIZE, border_width=0,
                               button_color=BACK_COLOR)

    start_interface = sg.Column(layout=[[train_but], [test_but], [back_start_but]], element_justification='c', visible=False,
                           size=COLUMN_SIZE)

    # widget for help menu
    back_help_but_t = sg.Button("Back", key='back_h_t', pad=BUTTON_PAD_SIZE, size=(BUTTON_SIZE[0], BUTTON_SIZE[1] // 2),
                                border_width=0, button_color=BACK_COLOR)

    # instruction
    instruction_info = []
    instruction_info.append([sg.Text("Warning: user data will be collected, but no private info will be collected\n"
                                     "All the collected data can be viewed in 'voice_changer log' folder",
                                     text_color='red', font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 1.5)),
                                     justification='l')])
    instruction_info.append([sg.Text(
        'User ID: type in the main menu your user id and click enter, only need to do it once TODO: specify the format of user id',
        font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 1.2)), justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        'Start Menu: the Start Menu has two options, they are almost the same with slight difference',
        font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 1.2)), justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        "Train: reward showed for each step (for more details scroll below to 'Simulation' section). Only use 'Train' when you getting start, once you're familiar with the environment, use 'Test'\n"
        "\nTest: your control will be collected and used as baseline",
        text_color='white', justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        'Help Menu: you are viewing the Help Menu now',
        font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 1.2)), justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        'Simulation: when you click on Train/Test in Start Menu',
        font=(DEFAULT_FONT, int(DEFAULT_FONT_SIZE * 1.2)), justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        "The following image indicates what the window looks like when you start simulation",
        text_color='white', justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([sg.Text(
        "If you press 'pickup' button and nothing happened, you might be too far away from the object, try getting closer\n"
        "If you press 'drop' and nothing happened, there might be not enough space in front of you",
        text_color='white', justification='l', size=HELP_TEXT_SIZE)])
    instruction_info.append([])
    instruction_info.append([])

    # help_col = sg.Column(layout=[[help_text2]], element_justification='c', visible=True, scrollable=True, size=(800, 300))
    back_help_but_b = sg.Button('Back', key='back_h_b', pad=BUTTON_PAD_SIZE, size=(BUTTON_SIZE[0], BUTTON_SIZE[1] // 2),
                                border_width=0, button_color=BACK_COLOR)

    help_menu = sg.Column(layout=[[back_help_but_t], *instruction_info, [back_help_but_b]], element_justification='c',
                          visible=False, size=COLUMN_SIZE)

    # start the window
    # window = sg.Window("Voice Changer", layout=[[sg.pin(menu, shrink=True)], [sg.pin(help_menu, shrink=True)],
    #                                                  [sg.pin(start_interface, shrink=True)]],
    #                    resizable=True, element_justification='c', finalize=True, use_ttk_buttons=True)

    window = sg.Window("Voice Changer", layout=[[sg.pin(menu, shrink=True)], [
        sg.pin(help_menu, shrink=True)], [sg.pin(start_interface, shrink=True)]],
                       resizable=True, element_justification='c', finalize=True,
                       use_ttk_buttons=True)


    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == exit_but.Key:
            window.close()
            break

        # help menu
        elif event == help_but.Key:  # go to help menu
            sg.user_settings_set_entry('help_check', True)
            menu.update(visible=False)
            help_menu.update(visible=True)
        elif event == 'back_h_b' or event == 'back_h_t':  # back from help menu to main menu
            menu.update(visible=True)
            help_menu.update(visible=False)

        # start menu
        elif event == start_but.Key:  # go to start menu  # start the env, catch all error and save
            menu.update(visible=False)
            start_interface.update(visible=True)
        elif event == 'back_s':  # return from start menu
            menu.update(visible=True)
            start_interface.update(visible=False)
        elif event == 'train':
            try:
                # manual_control.main(train=True)
                pass
            except Exception as e:
                # save exception and popup a user window
                with open('voice_changer log/' + "ERROR_" + str(int(time.time())) + '.txt', 'w') as f:
                    f.write(traceback.format_exc())
                winsound.PlaySound("ButtonClick.wav", 1)
                sg.popup('An unexpected error occur during simulation! Error message saved', title='ERROR',
                         keep_on_top=True, button_color=('white', 'red'), grab_anywhere=True)
        elif event == 'test':
            try:
                # manual_control.main(train=False)
                pass
            except Exception as e:
                # save exception and popup a user window
                with open('voice_changer log/' + "ERROR_" + str(int(time.time())) + '.txt', 'w') as f:
                    f.write(traceback.format_exc())
                winsound.PlaySound("ButtonClick.wav", 1)
                sg.popup('An unexpected error occur during simulation! Error message saved', title='ERROR',
                         keep_on_top=True, button_color=('white', 'red'), grab_anywhere=True)


if __name__ == '__main__':
    main()