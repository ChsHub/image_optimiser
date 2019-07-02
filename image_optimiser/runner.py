"""
Process the input images.
"""
from concurrent.futures import ProcessPoolExecutor
from logging import info, error, exception
from os import remove, cpu_count
from shutil import copyfile
from shutil import move
from tempfile import TemporaryDirectory

from PIL import Image
from format_byte import format_byte
from os.path import join, getsize, splitext
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


def optimise_image(file: (str, str), types: (str,) = (".jpg", ".png", ".jpeg"), direct_delete: bool = False,
                   new_type: str = '.webp') \
        -> (int, int) or (str, str):
    """
    Convert image to smaller size, if possible
    :param file: Path and file name of input image
    :param types: Allowed types for input images
    :param direct_delete: True if old files should be deleted, False if old files should be move to a trash directory
    :param new_type: Type of output images.
    :return: Size of original and new image file, Zeroes if old file can't be made smaller,
             Input file path if exception occurred
    """

    # Return if image was already successfully converted
    if type(file[0]) == int:
        return file
    if type(file) != tuple:
        return file

    file_name, extension = splitext(file[1])

    if not extension.lower() in types:
        return 0, 0

    try:
        with TemporaryDirectory() as temp_path:
            # Copy file into temporary directory
            temp_file = join(temp_path, 'a' + extension)
            copyfile(join(*file), temp_file)

            with Image.open(temp_file) as image:

                if _has_no_alpha(image):
                    info('CONVERT RGB')
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                elif new_type != '.webp':  # If type is webp transparency is supported
                    return 0, 0
                # no else

                old_file_size = getsize(temp_file)
                info(old_file_size)

                # Get new optimized image, and retrieve size
                new_file = find_minimum(temp_path, image, new_type)
                new_file_size = getsize(new_file)

                if old_file_size <= new_file_size:
                    info("OLD FILE SMALLER")
                    return 0, 0

                # Delete old file or move to trash
                if direct_delete:
                    remove(join(*file))
                else:
                    try:
                        send2trash(join(*file))
                    except Exception as e:
                        exception(e)  # Log OSError

                # Replace the old file
                move(new_file, join(file[0], file_name + new_type))  # TODO make changeable type .webp

                return old_file_size, new_file_size

    except MemoryError as e:
        exception(e)
        exception('OUT OF MEMORY')
    except Exception as e:
        exception(e)

    error(str(file))
    return file


def run_process(*args):
    """
    Optimize a single image.
    :param args: Arguments for the optimise_image method.
    :return: Output from the optimise_image method.
    """
    file, insta_delete, log_file, index, images_len, new_type, types = args[0]
    with Timer('OPT FILE: ' + join(*file), log_function=info):
        result = optimise_image(file, direct_delete=insta_delete, new_type=new_type, types=types)
    print_progress(index, images_len)

    return result


def _map_convert(map_function, images, direct_delete, log_file, new_type, total_old_size, total_new_size, types):
    # Set arguments for each process
    images = map_function(run_process, zip(images, [direct_delete] * len(images),
                                           [log_file] * len(images),
                                           range(1, len(images) + 1),
                                           [len(images) + 1] * len(images),
                                           [new_type] * len(images),
                                           [types] * len(images)))
    images = list(images)  # Converting to list triggers execution
    sizes = list(filter(lambda x: type(x[0]) == int, images))  # Filter successful terminated
    if sizes:
        total_old_size1, total_new_size1 = zip(*sizes)
        total_old_size += sum(total_old_size1)
        total_new_size += sum(total_new_size1)
    images = list(filter(lambda x: type(x[0]) == str, images))  # Filter failed
    return images, total_old_size, total_new_size


def convert(images: list, direct_delete: bool = False, log_file: str = None, processes: int = cpu_count() // 2,
            types=(".jpg", ".png", ".jpeg"), new_type: str = '.webp'):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param images: Target images.
    :param direct_delete: If True instantly delete old images. If False move old images to the OS's trash directory
    :param log_file: Logging file path string.
    :param processes: Number of parallel processes, that run the image optimization. More processes might block other
                      programs and use more memory.
    :param types: Types of input images. (Must be supported by PIL)
    :param new_type: Type of output images.
    """

    with Timer("CONVERT", log_function=info):

        info("FILES: " + str(len(images)))
        total_old_size = 0
        total_new_size = 0
        processes = min(processes, len(images))

        # If there are images convert them
        if images:
            for processes in list({processes, 1}):
                with ProcessPoolExecutor(max_workers=processes) as executor:
                    images, total_old_size, total_new_size = _map_convert(executor.map, images, direct_delete, log_file,
                                                                          new_type, total_old_size, total_new_size,
                                                                          types)

            print_progress(iteration=1, total=1)
            print()

        # No else

        info("FAILED: " + str(len(images)) + ' FILES')
        info("FAILED: " + str(images))
        info("SAVED: " + format_byte(total_old_size - total_new_size))
