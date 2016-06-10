import numpy as np
from PIL import Image
import piexif


def imread(filepath):
    image = Image.open(filepath)
    try:
        exf = piexif.load(image.info['exif'])
    except:
        exf = None
    return image, exf


def imwrite(image, filename, exif=None):
    if exif:
        image.save(filename, exif=piexif.dump(exif))
    else:
        image.save(filename)


def try_rot_exif(image, exf):
    ret_exf, ret_img = exf, image
    rotated = False
    if exf:
        orientation_flag = exf['0th'][piexif.ImageIFD.Orientation]
        ret_exf['0th'][piexif.ImageIFD.Orientation] = 1
        if orientation_flag == 3:
            k = 2
        elif orientation_flag == 6:
            k = -1
        elif orientation_flag == 8:
            k = 1
        else:
            k = 0
        if k != 0:
            rotated = True
        mat = np.asarray(image, dtype=np.uint8)
        mat2 = np.rot90(mat, k)
        ret_img = Image.fromarray(mat2)
    return rotated, ret_img, ret_exf


def append_postfix(filename, postfix):
    arr = filename.split('.')
    arr[-2] = arr[-2] + postfix
    result = '.'.join(arr)
    return result
