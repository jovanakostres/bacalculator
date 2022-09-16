import sys

import cv2
import luxpy as lx
from calibrate import load_images_folder


def find_good_img(img_fn):
    img_list = [cv2.imread(fn) for fn in img_fn]
    pic = []
    pic_name = ""
    max_val = 0
    Y_val = []

    for i in range(0, len(img_list)):
        image = cv2.cvtColor(img_list[i], cv2.COLOR_BGR2RGB)

        xyz = lx.srgb_to_xyz(image)

        lab = lx.xyz_to_lab(xyz)
        L = lab[:, :, 0]

        maxx = L.max()

        if len(L[L > 98].flatten()) < 10 and max_val < maxx:
            pic = image
            pic_name = img_fn[i]
            max_val = maxx
            Y_val = L

    return pic_name, max_val


def main_ce(parameters):

    try:
        img_arr = load_images_folder(parameters['exposure_path'])
    except Exception as e:
        print(e)
        sys.exit("Error with folder path. Try Again.")

    img_name, max_val = find_good_img(img_arr)
    print("Image path:", img_name)
    print("Maximum lightness value:",max_val)
    return img_name


if __name__ == '__main__':
    main_ce(None)
