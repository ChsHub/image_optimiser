from logging import info
from subprocess import getoutput, call
from utility.os_interface import get_absolute_path
from tempfile import NamedTemporaryFile
from io import StringIO
from os.path import getsize
from numpy import sum
from utility.os_interface import write_file_data
from skimage.measure import compare_ssim

# python.exe -m pip install scikit-image
from utility.path_str import get_full_path


def _compare(file_name, temp_file):
    # multichannel for RGB images
    return -compare_ssim(file_name, temp_file, multichannel=True)


def get_value(file_name, temp_file):
    from cv2 import cvtColor, imread, COLOR_BGR2GRAY, IMREAD_UNCHANGED, IMREAD_ANYCOLOR, IMREAD_ANYDEPTH

    original = imread(get_absolute_path(file_name))
    converted = imread(get_absolute_path(temp_file))

    if original is None or converted is None:
        raise ValueError

    # convert the images to grayscale
    original = cvtColor(original, COLOR_BGR2GRAY)
    converted = cvtColor(converted, COLOR_BGR2GRAY)

    result = _compare(original, converted)

    info("SSIM VALUE: " + str(result))
    write_file_data('.', 'quality.log', str(result) + '\n', mode='a')

    return result


def get_perception(quality, img, file_name, temp_path):
    temp_file = get_full_path(temp_path, str(quality) + ".jpg")
    img.save(temp_file, quality=quality, optimize=True)
    info('JPG QUALITY: ' + str(quality))
    write_file_data('.', 'quality.log', str(quality) + '\t', mode='a')

    return float(get_value(file_name, temp_file))
