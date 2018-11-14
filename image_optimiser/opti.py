from PIL import Image
from utility.timer import Timer
from utility.os_interface import write_file_data, delete_file
from utility.utilities import get_file_type
from SSIM_PIL import compare_ssim
from image_optimiser.perception_ssim import get_temp_image


def get_max_perception(size):
    return -0.997 + ((size - 741104) / 300000000)


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
        with Image.open(temp_file_path) as temp_image:
            value = -compare_ssim(img, temp_image)

        log_data += '\t' + str(quality) + '\t' + str(value)

        if value > target_value:
            low, high = quality + 1, high
        else:
            low, high = low, quality - 1

    with Timer('WRITE LOG'):
        write_file_data('.', 'quality+' + get_file_type(temp_file_path) + '.log', log_data + '\n', mode='a')

    return temp_file_path
