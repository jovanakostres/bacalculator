# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import sys
from termcolor import colored
import numpy as np
import cv2  # OpenCV biblioteka
import luxpy as lx  # package for color science calculations


def load_image(path):
    # TODO load image based on path

    return cv2.imread(path)


def find_circle(img):
    # TODO calculate circle center

    # isolate a circle from image by preprocessing and Hough algorithm
    img_phone_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    max_value = np.max(img_phone_gray)
    ret, image_bin = cv2.threshold(img_phone_gray, max_value - 20, 255,
                                   cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))

    img_dil = cv2.dilate(image_bin, kernel, iterations=1)
    img_close = cv2.erode(img_dil, kernel, iterations=1)

    radius = 150
    while True:
        circles = cv2.HoughCircles(img_close, cv2.HOUGH_GRADIENT, 1, 2000,
                                   param1=10, param2=10, minRadius=radius, maxRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            break

        radius -= 25

        if radius < 0:
            # if it's impossible to isolate a circle, the beam angle cant be calculated
            sys.exit("Can't calculate beam angle")

    return circles


def find_beam_angle(img, circles, parameters):
    # TODO calculate beam angle
    xyz = lx.srgb_to_xyz(img)

    img_decimal_gray = lx.xyz_to_lab(xyz)[:, :, 0]
    maxx = np.max(img_decimal_gray)

    img_decimal_gray = np.array(img_decimal_gray)
    img_decimal_gray = np.reshape(img_decimal_gray, (-1, int(parameters['pixels_width'])))

    mid_value = maxx / 2
    #print("mid value", mid_value)

    x = round(circles.flatten()[1])
    #print("X: ", x)

    y = round(circles.flatten()[0])
    #print("Y: ", y)

    ###WIDTH
    beam_angle_width = calc_by_w_h('meter_per_pixels_width', parameters, y, img_decimal_gray[x], mid_value)
    #print(beam_angle_width)
    ###HEIGHT
    beam_angle_height = calc_by_w_h('meter_per_pixels_height', parameters, x, img_decimal_gray[:, y], mid_value)
    #print(beam_angle_height)

    return beam_angle_width, beam_angle_height


def calc_by_w_h(option, parameters, i, row, mid_value):
    row1 = row[:i]
    row2 = row[i:]

    array_closest = np.asarray(row1)
    idx1 = (np.abs(array_closest - mid_value)).argmin()

    array_closest = np.asarray(row2)
    idx2 = (np.abs(array_closest - mid_value)).argmin()

    diameter = np.abs((i - idx1) * parameters[option]) + np.abs(
        (idx2 * parameters[option]))
    return np.degrees(2 * np.arctan(diameter / (2 * int(parameters['distance']))))


def objective(x, a, b, c, d):
    return a * x + b * np.power(x, 2) + c * np.power(x, 3) + d


def main_cba(parameters, path):
    # print(parameters)

    while True:
        try:
            if path is None:
                path = parameters['image_path']

            img = load_image(path)
            circles = find_circle(img)
            break
        except:
            print(colored("Error! No image with specified path.", 'red'))
            sys.exit()

    calculated_ba_width, calculated_ba_height = find_beam_angle(img, circles, parameters)
    ba_width = objective(calculated_ba_width, parameters['a_width'], parameters['b_width'], parameters['c_width'], parameters['d_width'])
    ba_height = objective(calculated_ba_height, parameters['a_height'], parameters['b_height'], parameters['c_height'], parameters['d_height'])
    print("Beam angle-width: ", ba_width)
    #if ba_height - ba_width > 2:
    print("Beam angle-height: ", ba_height)


if __name__ == '__main__':
    main_cba(None, None)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
