import json
import sys

import cv2
from termcolor import colored

from calculate_beam_angle import main_cba
from calculate_exposure import main_ce
from calibrate import main_cal, write_parameters
from colorama import init


def print_menu(menu_options):
    for key in menu_options.keys():
        print(key, '--', menu_options[key])
    pass


def load_parameters(path):
    # TODO read text file and load preferences
    with open(path) as f:
        parameters = json.load(f)
        parameters['fov_width'] = parameters['sensor_width'] * parameters['distance'] / parameters['focal_length']
        parameters['fov_height'] = parameters['fov_width'] * 3 / 4
        parameters['meter_per_pixels_width'] = parameters['fov_width'] / parameters['pixels_width']
        parameters['meter_per_pixels_height'] = parameters['fov_height'] / parameters['pixels_height']

    return parameters


if __name__ == '__main__':
    init()

    try:
        parameters = load_parameters('parameters.txt')
        write_parameters('parameters.txt', parameters)
    except:
        print(colored("Error! Badly formatted parameters.txt file!"))
        sys.exit()

    while True:
        menu_options = {
            1: 'Algorithmically choose the best image and calculate the beam angle',
            2: 'Choose the image by the image path in the parameters file and calculate the beam angle',
            3: 'Calibrate',
            4: 'Exit',
        }
        print_menu(menu_options)
        option = int(input('Enter your choice: '))

        if option == 1:
            img = main_ce(parameters)
            main_cba(parameters, img)
        elif option == 2:
            main_cba(parameters, None)
        elif option == 3:
            main_cal(parameters)
        elif option == 4:
            print('Exiting...')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 4.')
