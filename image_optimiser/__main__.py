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
from utility.utilities import format_bit, is_file_type, remove_file_type, get_file_type

from image_optimiser.opti import find_minimum
from image_optimiser.perception_ssim import cv_open_image, get_perception


def is_compressable(img, file, types, trash_path):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        info("TRANSPARENT IMAGE")

        red, green, blue, alpha = img.split()
        pixel_data = alpha.load()
        color_sum = 0
        for x in range(alpha.width):
            for y in range(alpha.height):
                color_sum += pixel_data[x, y]
        # if large parts are transparent don't convert to RGB
        return color_sum / (255 * alpha.width * alpha.height) > 0.99

    elif file[0].endswith('TRASH'):
        info('already compressed')
        return False

    elif exists(trash_path):
        # if image in TRASH, then don't compress again
        file_name = remove_file_type(file[1])
        for extension in types:
            if exists(get_full_path(trash_path, file_name + extension)):
                return False

    return True


def optimise_image(file, types=(".jpg", ".png", ".jpeg"), insta_delete=False):
    if not is_file_type(file[1], types):
        return 0, 0
    info('OPT FILE: ' + get_full_path(*file))

    with TemporaryDirectory() as temp_path:

        temp_name = get_full_path(temp_path, 'a' + get_file_type(file[1]))
        copyfile(get_full_path(*file), temp_name)

        trash_path = get_full_path(file[0], 'TRASH')

        try:
            with Image.open(temp_name) as img:

                if is_compressable(img, file, types, trash_path):

                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    old_file_size = get_file_size(temp_name)

                    new_file = get_new_picture(img, temp_name, temp_path)
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

        except Exception as e:
            exception(e)
            error("IMAGE FAILED")

    return 0, 0


def convert(path, insta_delete=False):

    types = [".jpg", ".png", ".jpeg"]
    d_files = depth_search_files(path, types)

    with ThreadPoolExecutor(max_workers=4) as executor:
        result = executor.map(lambda file: optimise_image(file, insta_delete=insta_delete), d_files)

    total_old_size, total_new_size = zip(*result)
    total_old_size, total_new_size = sum(total_old_size), sum(total_new_size)

    info("FILES: " + str(len(d_files)))
    info("SAVED: " + format_bit(total_old_size - total_new_size))


# returns new file: (path, name)
def get_new_picture(img, file_name, temp_path):

    img_resolution = img.size[0] * img.size[1]
    max_perception = get_max_perception(img_resolution)
    original_cv = cv_open_image(file_name)
    info('MAX PERCEPTION: ' + str(max_perception))

    new_file = find_minimum(img_resolution=img_resolution, low=40, high=100,
                                    function=lambda x: get_perception(quality=x, img=img,
                                                                      original=original_cv, temp_path=temp_path),
                                    target_value=max_perception)

    return temp_path, new_file.split('/')[-1]


def get_max_perception(size):
    # 741104
    # 324900
    return -0.997 + ((size - 741104) / 300000000)  # min(-0.950, )  # -0.997 *

if __name__ == "__main__":
    s_in = 's'
    while s_in:
        with Logger(10):
            try:
                s_in = input('OPTIMISE PATH: ')
                if s_in[-1] == '"' or s_in[-1] == "'":
                    s_in = s_in[:-1]

                if s_in[0] == '"' or s_in[0] == "'":
                    s_in = s_in[1:]

                convert(s_in)
            except Exception as e:
                exception(e)
