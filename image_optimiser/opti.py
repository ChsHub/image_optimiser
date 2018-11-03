from logging import info

from PIL import Image
from utility.timer import Timer
from utility.os_interface import write_file_data, delete_file
from utility.utilities import get_file_type

from image_optimiser.perception_ssim import get_perception, cv_open_image, get_temp_image
from SSIM_PIL import compare_ssim


def get_max_perception(size):
    # 741104
    # 324900
    return -0.997 + ((size - 741104) / 300000000)  # min(-0.950, )  # -0.997 *


# binary search
def find_minimum(temp_path, img):
    low, high = 30, 100

    img_resolution = img.size[0] * img.size[1]

    temp_file_path = ''
    target_value = get_max_perception(img_resolution)

    log_data = str(img_resolution) + '\t' + str(target_value)

    while high > low:

        quality = (low + high) // 2
        delete_file(temp_file_path)
        temp_file_path = get_temp_image(quality=quality, img=img, temp_path=temp_path)
        value = -compare_ssim(img, Image.open(temp_file_path))
        # value = get_perception(original=original_cv, temp_file_path=temp_file_path)

        log_data += '\t' + str(quality) + '\t' + str(value)

        if value > target_value:
            low, high = quality + 1, high
        else:
            low, high = low, quality - 1

    with Timer('WRITE LOG'):
        write_file_data('.', 'quality+' + get_file_type(temp_file_path) + '.log', log_data + '\n', mode='a')

    return temp_file_path
