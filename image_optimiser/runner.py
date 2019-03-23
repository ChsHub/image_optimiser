"""
Process the input images.
"""

from concurrent.futures import ProcessPoolExecutor
from logging import info, error, exception
from os import makedirs, remove, cpu_count
from shutil import copyfile
from shutil import move
from tempfile import TemporaryDirectory

from PIL import Image
from format_byte import format_byte
from os.path import join, getsize, splitext
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


def is_compressable(image: Image) -> bool:
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


def optimise_image(file: (str, str), types: (str,) = (".jpg", ".png", ".jpeg"), insta_delete: bool = False) \
        -> (int, int):
    """
    Convert image to smaller size, if possible
    :param file: Path and file name of input image
    :param types: Allowed types for input images
    :param insta_delete: True if old files should be deleted, False if old files should be move to a trash directory
    :return: Size of original and new image file, Zeroes if old file can't be made smaller,
             Input file path if exception occurred
    """

    # Return if image was already successfully converted
    if type(file[0]) == int:
        return file
    if type(file) != tuple:
        raise TypeError
    file_name, extension = splitext(file[1])

    with Timer('OPT FILE: ' + join(*file), log_function=info):
        try:
            if extension in types:

                trash_path = join(file[0], 'TRASH')

                with TemporaryDirectory() as temp_path:
                    # Copy file into temporary directory
                    temp_name = join(temp_path, 'a' + extension)
                    copyfile(join(*file), temp_name)

                    with Image.open(temp_name) as image:

                        if is_compressable(image):

                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            # no else

                            old_file_size = getsize(temp_name)
                            info(old_file_size)

                            # Get new optimized image, and retrieve size
                            new_file = find_minimum(temp_path, image)
                            new_file_size = getsize(new_file)

                            if old_file_size > new_file_size:

                                if insta_delete:
                                    # Delete old file
                                    remove(join(*file))
                                else:
                                    # Move to trash
                                    try:
                                        makedirs(trash_path)
                                    except Exception as e:
                                        info(e)  # Log OSError
                                    try:
                                        move(join(*file), join(trash_path, file[1]))
                                    except Exception as e:
                                        info(e)  # Log OSError

                                # Replace the old file
                                move(new_file, join(file[0], file_name + '.webp'))  # TODO make changeable type .webp

                                return old_file_size, new_file_size

                            else:
                                info("OLD FILE SMALLER")
            # no else
            return 0, 0
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
    file, insta_delete, log_file, index, images_len = args[0]
    info(file)
    result = optimise_image(file, insta_delete=insta_delete)
    print_progress(index, images_len + 1)

    return result


def convert(images: list, direct_delete: bool = False, log_file: str = None, processes: int = cpu_count() // 2,
            types=(".jpg", ".png", ".jpeg")):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param images: Target images.
    :param direct_delete: If True instantly delete old images. If False move old images to a new folder called "TRASH"
    :param log_file: Logging file path string.
    :param processes: Number of parallel processes, that run the image optimization. More processes might block other
                      programs and use more memory.
    :param types: Types of input images. (Must be supported by PIL)
    """

    with Timer("CONVERT", log_function=info):

        info("FILES: " + str(len(images)))
        total_old_size = 0
        total_new_size = 0
        processes = min(processes, len(images))

        # If there are images convert them
        if images:
            for workers in [processes, 1]:
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    # Set arguments for each process
                    images = executor.map(run_process,
                                          zip(images, [direct_delete] * len(images), [log_file] * len(images),
                                              range(1, len(images) + 1), [len(images)] * len(images)))

                    images = list(images)  # Converting to list triggers exectuion
                    sizes = list(filter(lambda x: type(x[0]) == int, images))
                    if sizes:
                        total_old_size1, total_new_size1 = zip(*sizes)
                        total_old_size += sum(total_old_size1)
                        total_new_size += sum(total_new_size1)
                    images = list(filter(lambda x: type(x[0]) == str, images))

            print_progress(iteration=1, total=1)
            print()

        # No else

        info("FAILED: " + str(len(images)) + ' FILES')
        info("FAILED: " + str(images))
        info("SAVED: " + format_byte(total_old_size - total_new_size))
