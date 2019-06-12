"""
Find the output image with optimal quality.
"""

from math import log
from multiprocessing import freeze_support
from os import remove

from PIL import Image
from SSIM_PIL import compare_ssim
from os.path import isfile

from image_optimiser.temporary_image import get_temp_image


def get_max_perception(size: (int, int)) -> float:
    """
    Get perception value for the optimisation. (adjusted to the image size)
    :param size: Width and height of pixels
    :return: Value for the optimisation
    """
    size = size[0] * size[1]
    return 0.997 - min(0.05, ((size - 741104) / 300000000))

 # TODO scale perceived value with image size
def perceived_value(value):
    const = 0.5
    value = const * log(value)

    return value

# TODO remove logging? Analyse data
def find_minimum(temp_path: str, img: Image) -> str:
    """
    Find optimal image quality using a binary search.
    :param temp_path:
    :param img:
    :return:
    """
    low, high = 36, 100  # 30, 100
    temp_file_path = ''
    target_value = get_max_perception(img.size)
    log_data = "\n" + str(img.size) + '\t' + str(target_value)

    while high > low:
        # Delete previous image
        if isfile(temp_file_path):
            remove(temp_file_path)

        # Create temporary image
        quality = (low + high) // 2
        temp_file_path = get_temp_image(quality=quality, image=img, temp_path=temp_path)
        # Open temporary image and compare to original
        with Image.open(temp_file_path) as temp_image:
            value = compare_ssim(img, temp_image, GPU=True)

        # Set up bounds for next iteration
        if value > target_value:
            high = quality - 1
        else:
            low = quality + 1

        # Log data
        log_data += '\n' + str(quality) + '\t' + str(value)

    # Write log data to file
    with open('quality+' + temp_file_path[-4:] + '.log', mode='a') as f:
        f.write(log_data + '\n')

    return temp_file_path

if __name__ == "__main__":
    freeze_support()