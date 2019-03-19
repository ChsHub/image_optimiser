# python3
from concurrent.futures import ProcessPoolExecutor
from logging import info, error, exception
from os import cpu_count
from os.path import isdir, isfile
from shutil import move, copyfile
from tempfile import TemporaryDirectory

from PIL import Image
from utility.logger import Logger
from utility.os_interface import depth_search_files, get_file_size, make_directory, move_file, delete_file
from utility.path_str import get_full_path
from utility.timer import Timer
from utility.utilities import format_byte, is_file_type, remove_file_type, get_file_type

from image_optimiser.optimize import find_minimum


def print_progress(iteration: int, total: int, prefix='', decimals=1, bar_length=100):
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


def accept_file(file: (str,), types: list, trash_path: str) -> bool:
    """
    Test if file is of right type and not already converted
    :param file: Image path
    :param types: Acceptable image types
    :param trash_path: Path for old images
    :return: True if convertable or false if not
    """
    if file[0].endswith('TRASH'):
        info('already compressed')
        return False

    elif isdir(trash_path):
        # if image in TRASH, then don't compress again
        file_name = remove_file_type(file[1])
        for extension in types:
            if isfile(get_full_path(trash_path, file_name + extension)):
                return False

    return True


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


def get_new_picture(temp_path: str, image: Image) -> (str, str):
    """
    Convert the image to new type
    :param temp_path: Temporary path to store temporary images
    :param image: Original PIL image object
    :return: Path and file name of new image
    """
    new_file = find_minimum(temp_path, image)
    return temp_path, new_file.split('/')[-1]


def optimise_image(file: (str, str), types: (str,) = (".jpg", ".png", ".jpeg"), insta_delete: bool = False) -> (
        int, int):
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

    with Timer('OPT FILE: ' + get_full_path(*file)):
        try:
            if is_file_type(file[1], types):

                trash_path = get_full_path(file[0], 'TRASH')
                if accept_file(file, types, trash_path):

                    with TemporaryDirectory() as temp_path:

                        temp_name = get_full_path(temp_path, 'a' + get_file_type(file[1]))  # TODO Rename
                        copyfile(get_full_path(*file), temp_name)

                        with Image.open(temp_name) as image:

                            if is_compressable(image):

                                if image.mode != 'RGB':
                                    image = image.convert('RGB')
                                # no else

                                old_file_size = get_file_size(temp_name)
                                info(old_file_size)

                                new_file = get_new_picture(temp_path, image)

                                new_file_size = get_file_size(*new_file)

                                if old_file_size > new_file_size:

                                    if insta_delete:
                                        delete_file(*file)
                                    else:
                                        make_directory(trash_path)
                                        move_file(file[0], trash_path, file[1])  # delete old file

                                    # rename and move new file
                                    move(get_full_path(new_file[0], new_file[1]),
                                         get_full_path(file[0], remove_file_type(file[1]) + get_file_type(new_file[1])))

                                    return old_file_size, new_file_size

                                else:
                                    info("OLD FILE SMALLER")
                            # no else
                # no else
            # no else
            return 0, 0
        except MemoryError as e:
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
    print_progress(index, images_len, bar_length=50)

    return result


def convert(path: str, insta_delete: bool = False, log_file: str = None, processes: int = cpu_count() // 2,
            types=(".jpg", ".png", ".jpeg")):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param path: Target directory.
    :param insta_delete: If True instantly delete old images. If False move old images to a new folder called "TRASH"
    :param log_file: Logging file path string.
    :param processes: Number of parallel processes, that run the image optimization. More processes might block other
                      programs and use more memory.
    :param types: Types of input images. (Must be supported by PIL)
    """

    # Strip possible parenthesis and test if exists
    path = path.strip('"').strip("'")
    if not isdir(path):
        info("Directory does not exist")
        return

    with Timer("CONVERT"):

        images = depth_search_files(path, types)
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
                                          zip(images, [insta_delete] * len(images), [log_file] * len(images),
                                              range(1, len(images) + 1), [len(images)] * len(images)))

                    images = list(images)
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


def init():
    if __name__ == "__main__":
        with Logger(10) as logger:
            try:
                s_input = True
                while s_input:
                    s_input = input('OPTIMISE PATH: ')
                    info('INPUT: ' + s_input)
                    convert(s_input, log_file=logger.log_name)
            except Exception as e:
                exception(e)


init()
