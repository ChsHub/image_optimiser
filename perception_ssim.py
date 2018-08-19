from logging import info
from subprocess import getoutput, call
from utility.os_interface import get_absolute_path
from tempfile import NamedTemporaryFile
from io import StringIO
from os.path import getsize
from skimage.measure import compare_ssim
from numpy import sum
from cv2 import cvtColor, imread, COLOR_BGR2GRAY, IMREAD_UNCHANGED, IMREAD_ANYCOLOR, IMREAD_ANYDEPTH


# python.exe -m pip install scikit-image

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def _compare(file_name, temp_file):
    return mse(file_name, temp_file)


def get_value(file_name, temp_file):
    original = imread(get_absolute_path(file_name))
    converted = imread(get_absolute_path(temp_file))

    if original is None or converted is None:
        raise ValueError

    # convert the images to grayscale
    original = cvtColor(original, COLOR_BGR2GRAY)
    converted = cvtColor(converted, COLOR_BGR2GRAY)

    result = _compare(original, converted)

    info("MSE VALUE: " + str(result))
    return result


def get_perception(quality, img, file_name):
    # with NamedTemporaryFile(mode="wb", suffix=".jpg") as temp_file:
    temp_file = "temp_img/" + str(quality) + ".jpg"
    img.save(temp_file, quality=quality, optimize=True)

    info('JPG QUALITY: ' + str(quality))
    return float(get_value(file_name, temp_file))
