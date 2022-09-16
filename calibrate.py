import glob
import json
import re
import sys

import cv2
import numpy as np
from scipy.optimize import curve_fit

from calculate_beam_angle import find_circle, find_beam_angle, objective


def write_parameters(path, parameters):
    with open(path, "w") as f:
        f.write(json.dumps(parameters))

    return


def load_images_folder(path):
    # load images from folder at path
    return glob.glob(path + '\\*.bmp')


def calculate_beam_angle(img_arr, parameters):
    info_beam_angle_width = {}
    info_beam_angle_height = {}
    for img in img_arr:

        real_ba = float(re.findall("BA-(.+).bmp", img)[0])

        img = cv2.imread(img)
        circles = find_circle(img)

        if real_ba not in info_beam_angle_width:
            info_beam_angle_width[real_ba] = np.array([])
            info_beam_angle_height[real_ba] = np.array([])

        ba_width, ba_height = find_beam_angle(img, circles, parameters)
        info_beam_angle_width[real_ba] = np.append(info_beam_angle_width[real_ba], ba_width)
        info_beam_angle_height[real_ba] = np.append(info_beam_angle_height[real_ba], ba_height)

    return info_beam_angle_width, info_beam_angle_height


def function_fit(info_beam_angle, parameters, type):
    # define the true objective function
    real_beam_angles = np.array(list(info_beam_angle.keys())).astype(np.float32)

    calculated_beam_angles = np.array([])
    for value in info_beam_angle.values():
        calculated_beam_angles = np.append(calculated_beam_angles, np.mean(value))

    popt, _ = curve_fit(objective, calculated_beam_angles, real_beam_angles)
    # summarize the parameter values
    a, b, c, d = popt
    print('y = %.5f * x + %.5f * x^2 + %.5f * x^3 + %.5f' % (a, b, c, d))
    parameters['a_' + type] = a
    parameters['b_' + type] = b
    parameters['c_' + type] = c
    parameters['d_' + type] = d
    return parameters


def main_cal(parameters):
    try:
        img_arr = load_images_folder(parameters['calibration_path'])
    except Exception as e:
        print(e)
        sys.exit("Error with folder path. Try Again.")

    info_beam_angle_width, info_beam_angle_height = calculate_beam_angle(img_arr, parameters)
    parameters = function_fit(info_beam_angle_width, parameters, 'width')
    parameters = function_fit(info_beam_angle_height, parameters, 'height')

    write_parameters('parameters.txt', parameters)
    print("Successfully calibrated!")
    #print(objective(23, parameters['a_width'], parameters['b_width'], parameters['c_width'], parameters['d_width']))
    #print(objective(20, parameters['a_height'], parameters['b_height'], parameters['c_height'], parameters['d_height']))
    #print(objective(16, parameters['a_height'], parameters['b_height'], parameters['c_height'], parameters['d_height']))


if __name__ == '__main__':
    main_cal(None)
