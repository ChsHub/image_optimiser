"""
Find the output image with optimal quality.
"""

from os import remove
from os.path import isfile
from pathlib import Path

from PIL import Image
from SSIM_PIL import compare_ssim

from image_optimiser.temporary_image import get_temp_image


def get_max_perception(size: (int, int)) -> float:
    """
    Get perception value for the optimisation. (adjusted to the image size)
    :param size: Width and height of pixels
    :return: Value for the optimisation
    """
    size = size[0] * size[1]
    return 0.997 - min(0.05, ((size - 741104) / 300000000))


def find_minimum(temp_path: str, img: Image, new_type: str) -> Path:
    """
    Find optimal image quality using a binary search.
    :param temp_path:
    :param img:
    :param new_type:
    :return: Smallest image with specified quality
    """
    low, high = 36, 100  # 30, 100
    temp_file_path = ''
    target_value = get_max_perception(img.size)

    while high > low:
        # Delete previous image
        if isfile(temp_file_path):
            remove(temp_file_path)

        # Create temporary image
        quality = (low + high) // 2
        temp_file_path = get_temp_image(quality=quality, image=img, temp_path=temp_path, new_type=new_type)
        # Open temporary image and compare to original
        with Image.open(temp_file_path) as temp_image:
            value = compare_ssim(img, temp_image, GPU=True)

        # Set up bounds for next iteration
        if value > target_value:
            high = quality - 1
        else:
            low = quality + 1

    return Path(temp_file_path)
