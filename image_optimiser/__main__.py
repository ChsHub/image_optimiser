# python3
#  python.exe -m pip install scikit-image
#  sudo chmod -R a+rX /usr/local/lib/python3.4/
from concurrent.futures import ThreadPoolExecutor
from logging import info, error, exception
from shutil import move, copyfile
from tempfile import TemporaryDirectory

from PIL import Image
from utility.logger import Logger
from utility.os_interface import depth_search_files, get_file_size, make_directory, move_file, exists, \
    delete_file
from utility.path_str import get_full_path
from utility.timer import Timer
from utility.utilities import format_bit, is_file_type, remove_file_type, get_file_type

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


# file tuple
def is_compressable(img):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        info("TRANSPARENT IMAGE")

        alpha = img.split()[-1]
        pixel_data = alpha.load()
        color_sum = 0
        for x in range(alpha.width):
            for y in range(alpha.height):
                color_sum += pixel_data[x, y]
        # if large parts are transparent don't convert to RGB
        return color_sum / (255 * alpha.width * alpha.height) >= 0.99

    return True


# returns new file: (path, name)
def get_new_picture(temp_path, temp_name, img):
    new_file = find_minimum(temp_path, temp_name, img)
    return temp_path, new_file.split('/')[-1]


def optimise_image(file, types=(".jpg", ".png", ".jpeg"), insta_delete=False):

    with Timer('OPT FILE: ' + get_full_path(*file)):
        if is_file_type(file[1], types):

            trash_path = get_full_path(file[0], 'TRASH')
            if accept_file(file, types, trash_path):

                with TemporaryDirectory() as temp_path:

                    temp_name = get_full_path(temp_path, 'a' + get_file_type(file[1]))  # TODO Rename
                    copyfile(get_full_path(*file), temp_name)

                    with Image.open(temp_name) as img:

                        if is_compressable(img):

                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            old_file_size = get_file_size(temp_name)

                            new_file = get_new_picture(temp_path, temp_name, img)
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
        return 0, 0


def convert(path, insta_delete=False):
    if exists(path):

        types = [".jpg", ".png", ".jpeg"]
        d_files = depth_search_files(path, types)

        with ThreadPoolExecutor(max_workers=16) as executor:
            result = executor.map(lambda file: optimise_image(file, insta_delete=insta_delete), d_files)

        total_old_size, total_new_size = zip(*result)
        total_old_size, total_new_size = sum(total_old_size), sum(total_new_size)

        info("FILES: " + str(len(d_files)))
        info("SAVED: " + format_bit(total_old_size - total_new_size))

def _clean_input(s_in):
    if s_in[-1] == '"' or s_in[-1] == "'":
        s_in = s_in[:-1]
    if s_in[0] == '"' or s_in[0] == "'":
        s_in = s_in[2:]
    return s_in

if __name__ == "__main__":

    with Logger(10):
        try:
            s_in = input('OPTIMISE PATH: ')
            if len(s_in) > 2:
                s_in = _clean_input(s_in)
                convert(s_in)
        except Exception as e:
            exception(e)
