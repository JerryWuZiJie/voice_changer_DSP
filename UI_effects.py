import PySimpleGUI as sg


def main(window):
    # pysimplegui window passed in
    while True:

        event, values = window.read(timeout=1)

        if event == sg.WIN_CLOSED or event == 'exit':
            break

        elif event == 'start':
            print('sg start')

        elif event == 'ui':
            print('break')
            break

