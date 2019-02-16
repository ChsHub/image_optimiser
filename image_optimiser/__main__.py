# python3
from concurrent.futures import ProcessPoolExecutor
from logging import info, error, exception
from os import cpu_count
from shutil import move, copyfile
from sys import exit as sys_exit, stdout
from tempfile import TemporaryDirectory

from PIL import Image
from utility.logger import Logger
from utility.os_interface import depth_search_files, get_file_size, make_directory, move_file, exists, \
    delete_file
from utility.path_str import get_full_path
from utility.timer import Timer
from utility.utilities import format_byte, is_file_type, remove_file_type, get_file_type

from image_optimiser.opti import find_minimum


def accept_file(file, types, trash_path):
    if file[0].endswith('TRASH'):
        info('already compressed')
        return False

    elif exists(trash_path):
        # if image in TRASH, then don't compress again
        file_name = remove_file_type(file[1])
        for extension in types:
            if exists(get_full_path(trash_path, file_name + extension)):
                return False

    return True


def is_compressable(image):
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


# returns new file: (path, name)
def get_new_picture(temp_path, image):
    new_file = find_minimum(temp_path, image)
    return temp_path, new_file.split('/')[-1]


def optimise_image(file, types=(".jpg", ".png", ".jpeg"), insta_delete=False):
    if type(file[0]) == int:  # TODO Remove maybe
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
    file, insta_delete, log_file = args[0]
    with Logger(10, parent=log_file, debug=False):
        info(file)
        result = optimise_image(file, insta_delete=insta_delete)
        # 'https://stackoverflow.com/a/50819819/7062162'
        stdout.write("-")  # prints a dash for each image
        stdout.flush()  # ensures bar is displayed incrementally
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
    if not exists(path):
        info("Directory does not exist")
        return

    with Timer("convert"):

        images = depth_search_files(path, types)
        info("FILES: " + str(len(images)))
        total_old_size = 0
        total_new_size = 0

        for workers in [processes, 1]:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                images = executor.map(run_process,
                                      zip(images, [insta_delete] * len(images), [log_file] * len(images)))
            images = list(images)
            if images:
                sizes = list(filter(lambda x: type(x[0]) == int, images))
                if sizes:
                    total_old_size1, total_new_size1 = zip(*sizes)
                    total_old_size += sum(total_old_size1)
                    total_new_size += sum(total_new_size1)
                images = list(filter(lambda x: type(x[0]) == str, images))

        info("FAILED: " + str(len(images)) + ' FILES')
        info("FAILED: " + str(images))
        info("SAVED: " + format_byte(total_old_size - total_new_size))


def init(wait=60):
    if __name__ == "__main__":
        with Logger(10, debug=True) as logger:
            try:
                s_input = True
                while s_input:
                    s_input = input('OPTIMISE PATH: ')
                    info('INPUT: ' + s_input)
                    convert(s_input, log_file=logger.log_name)
            except Exception as e:
                exception(e)
        sys_exit()


init()
