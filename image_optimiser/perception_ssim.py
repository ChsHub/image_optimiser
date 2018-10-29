from logging import exception, info

from utility.os_interface import get_absolute_path
from utility.path_str import get_full_path
from cv2 import cvtColor, imread, COLOR_BGR2GRAY
from skimage.measure import compare_ssim
from utility.timer import Timer
from PIL import Image


def cv_open_image(file_name):
    path = get_absolute_path(file_name)
    image = imread(path)
    if image is None:
        raise ValueError

    # convert the images to grayscale
    # return cvtColor(image, COLOR_BGR2GRAY)
    return image


def get_temp_image(quality, img, temp_path, file_type=".webp"):
    """

    :param quality: Compression quality
    :param img: Comparison image (PILLOW version)
    :param temp_path: Destination for temporary image
    :return: temp_file_path: Destination for temporary image
    """
    temp_file_path = get_full_path(temp_path, str(quality) + file_type)
    img.save(temp_file_path, quality=quality, optimize=True, method=6)
    return temp_file_path


def get_perception(original, temp_file_path):
    """

    :param original: Comparison image (CV version)
    :param temp_file_path: Destination for temporary image
    :return: Path of new image, and it's SSIM value
    """
    with Timer('SSIM'):
        value = -float(compare_ssim(original, cv_open_image(temp_file_path), multichannel=True))

    return value
