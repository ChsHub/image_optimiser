from logging import info, error
from tempfile import NamedTemporaryFile
from os.path import getsize
# python.exe -m pip install scikit-image

from PIL import Image

# sudo chmod -R a+rX /usr/local/lib/python3.4/
from utility.logger import Logger
from utility.os_interface import depth_search_files, delete_file, get_file_size, make_directory, move_file
from os import rename
from utility.path_str import get_full_path
from utility.utilities import format_bit
from utility.utilities import remove_file_type, get_file_type
from opti import find_minimum
from perception_ssim import get_perception, get_value


# python3

def clear_temp_dir():
    for temp_file in depth_search_files("temp_img", ""):
        if not delete_file(*temp_file):
            raise RuntimeError


# file BytesIO object
# def get_file_size(file):
#   return file.tell()

def convert(path):
    total_old_size = 0
    total_new_size = 0
    file_counter = 0
    tries_counter = 0
    types = [".jpg", ".jpeg", ".png"]

    make_directory('temp_img')

    for file in depth_search_files(path, types):

        clear_temp_dir()

        img = Image.open(get_full_path(file[0], file[1]))
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            error("TRANSPARENT IMAGE")
        else:

            old_file_size = get_file_size(*file)
            info(file)

            new_file = get_new_picture(img, get_full_path(*file))

            if old_file_size > get_file_size(*new_file):
                file_counter += 1
                # tries_counter += counter
                total_new_size += get_file_size(*new_file)
                total_old_size += old_file_size

                make_directory(file[0] + '/TRASH')
                move_file(file[0], file[0] + '/TRASH', file[1])  # delete old file

                rename(get_full_path(new_file[0], new_file[1]),
                       remove_file_type(get_full_path(*file)) + get_file_type(new_file[1]))  # rename and move new file

                info(str(total_new_size) + " / " + str(total_old_size))
                info("File count " + str(file_counter))
                info("Average Minimum count: " + str(int(tries_counter / file_counter)))
            else:
                error("OLD FILE SMALLER")

            info(file[0] + " " + file[1])

    # info(str(total_new_size) + "/" + str(total_old_size) + " " + str(file_counter))
    info("SAVED " + format_bit(total_old_size - total_new_size))


def get_new_picture(img, file_path):
    counter, quality, img_type = get_new_picture_jpg(img, file_path)
    info('COUNT: ' + str(counter) + ' JPG QUALITY: ' + str(quality))

    return "temp_img", str(quality) + ".jpg"


def get_new_picture_jpg(img, file_name, max_perception=100):

    quality, counter = find_minimum(x_1=100, x_2=70, min_domain=40, max_domain=100,
                                    function=lambda x: get_perception(quality=x, img=img, file_name=file_name),
                                    offset=max_perception)

    return counter, quality, "jpg"


def get_new_picture_png(img, file_name, max_perception=1.1):
    # PNG
    with NamedTemporaryFile(mode="wb", suffix=".png") as temp_file:
        img.save(temp_file, 'png', optimized=True)
        png_size = getsize(temp_file)

    if get_value(file_name, temp_file) <= max_perception:
        return 0, 0, png_size, "png"
    else:
        return None


if __name__ == "__main__":
    log = Logger(50)
    convert("test_images")
    log.shutdown()
