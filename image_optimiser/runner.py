"""
Process the input images.
"""
from logging import info, error, exception
from os import remove
from pathlib import Path
from shutil import copyfile
from shutil import move
from tempfile import TemporaryDirectory

from PIL import Image
from format_byte import format_byte
from send2trash import send2trash
from timerpy import Timer

from image_optimiser.optimize import find_minimum


def print_progress(iteration: int, total: int, prefix='', decimals=1, bar_length=50):
    """
    Call in a loop to create terminal progress bar (https://stackoverflow.com/a/34325723)
    :param iteration: current iteration
    :param total: total iteration
    :param prefix: prefix string
    :param decimals: positive number of decimals in percent complete
    :param bar_length: character length of bar
    """

    str_format = "{0:.%sf}" % decimals
    percents = str_format.format(100 * iteration / float(total))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    print('\r%s%s %s%%' % (prefix, bar, percents), end='')


def _has_no_alpha(image: Image) -> bool:
    """
    Test if transparent layer is used.
    :param image: PIL image object
    :return: True if no alpha layer exists or alpha layer mostly not transparent.
    """
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        info("TRANSPARENT IMAGE")
        # if large parts are transparent don't convert to RGB
        alpha = image.split()[-1]
        alpha = alpha.getdata()
        color_sum = sum(alpha)
        return color_sum / (255 * len(alpha)) >= 0.99

    return True


def delete_larger(file: Path, new_file: Path, delete_method, new_type: str):
    old_file_size = file.stat().st_size
    new_file_size = new_file.stat().st_size

    if old_file_size <= new_file_size:
        info("OLD FILE SMALLER")
        return 0, 0

    # Delete old file or move to trash
    try:
        delete_method(file)
    except Exception as e:
        exception(e)  # Log OSError

    # Replace the old file
    move(new_file, file.with_suffix(new_type))
    return old_file_size, new_file_size


def _covert_image(temp_path, temp_file: Path, new_type, direct_delete: bool, file: Path) -> (int, int):
    """
    Convert the image to the new type
    :param temp_path:
    :param temp_file: Copy of original image
    :param new_type:
    :param direct_delete:
    :param file:
    :param file_name:
    :return:
    """
    with Image.open(temp_file) as image:

        supports_transparency = new_type.endswith('webp')
        if _has_no_alpha(image):
            image = image if image.mode == 'RGB' else image.convert('RGB')
        elif not supports_transparency:
            return 0, 0

        # Get new optimized image, and retrieve size
        new_file = find_minimum(temp_path, image, new_type)
        return delete_larger(file, new_file, remove if direct_delete else send2trash, new_type)


def optimise_image(file: (str, str), types: (str,) = (".jpg", ".png", ".jpeg"), direct_delete: bool = False,
                   new_type: str = '.webp') -> (int, int):
    """
    Convert image to smaller size, if possible
    :param file: Path and file name of input image
    :param types: Allowed types for input images
    :param direct_delete: True if old files should be deleted, False if old files should be move to a trash directory
    :param new_type: Type of output images.
    :return: Size of original and new image file, Zeroes if old file can't be made smaller, or Error occured
    """

    # Return if image was already successfully converted
    if type(file[0]) == int:
        return file

    file = Path(*file)

    if not file.suffix.lower() in types:
        return 0, 0

    try:
        # Copy file into temporary directory
        with TemporaryDirectory() as temp_path:
            temp_file = Path(temp_path, 'a' + file.suffix)
            copyfile(file, temp_file)
            return _covert_image(temp_path, temp_file, new_type, direct_delete, file)

    except MemoryError as e:
        exception(e)
        exception('OUT OF MEMORY')
    except Exception as e:
        exception(e)

    error(str(file))
    return 0, 0


def convert(images: list, direct_delete: bool = False, types=(".jpg", ".png", ".jpeg"), new_type: str = '.webp'):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param images: Target images.
    :param direct_delete: If True instantly delete old images. If False move old images to the OS's trash directory
    :param types: Types of input images. (Must be supported by PIL)
    :param new_type: Type of output images.
    """

    with Timer("CONVERT", log_function=info):
        info("FILES: " + str(len(images)))
        total_old_size = 0
        total_new_size = 0
        total_images = len(images)
        if not images:
            info('No Images found')
            return

        for i, file in enumerate(images):
            old_file_size, new_file_size = optimise_image(file, direct_delete=direct_delete, new_type=new_type,
                                                          types=types)
            total_old_size += old_file_size
            total_new_size += new_file_size
            print_progress(iteration=i, total=total_images, prefix=format_byte(total_old_size - total_new_size))

        info("SAVED: " + format_byte(total_old_size - total_new_size))
