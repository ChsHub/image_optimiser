from os.path import isfile
from os import remove
from PIL import Image
from SSIM_PIL import compare_ssim

from image_optimiser.perception_ssim import get_temp_image


def get_max_perception(size: int) -> float:
    """
    Get perception value for the optimisation. (adjusted to the image size)
    :param size: Number of pixels
    :return: Value for the optimisation
    """
    return -0.997 + ((size - 741104) / 200000000)


def find_minimum(temp_path:str, img:Image)->str:
    """
    Find optimal image quality using a binary search.
    :param temp_path:
    :param img:
    :return:
    """
    low, high = 1, 100 # 30, 100
    temp_file_path = ''
    img_resolution = img.size[0] * img.size[1]
    target_value = get_max_perception(img_resolution)
    log_data = str(img_resolution) + '\t' + str(target_value)

    while high > low:
        # Delete previous image
        if isfile(temp_file_path):
            remove(temp_file_path)

        # Create temporary image
        quality = (low + high) // 2
        temp_file_path = get_temp_image(quality=quality, image=img, temp_path=temp_path)
        # Open temporary image and compare to original
        with Image.open(temp_file_path) as temp_image:
            value = -compare_ssim(img, temp_image, GPU=True)

        # Set up bounds for next iteration
        if value > target_value:
            low = quality + 1
        else:
            high = quality - 1

        # Log data
        log_data += '\t' + str(quality) + '\t' + str(value)


    # Write log data to file
    with open('quality+' + temp_file_path[-4:] + '.log', mode='a') as f:
        f.write(log_data + '\n')

    return temp_file_path
