from logging import info, error
# python3

from os.path import getsize
from subprocess import check_output
from tempfile import NamedTemporaryFile

from PIL import Image
from utility.logger import Logger
from utility.os_interface import depth_search_files, delete_file, get_file_size
from utility.path_str import get_full_path
from utility.utilities import format_bit

# file BytesIO object
# def get_file_size(file):
#   return file.tell()

def convert(path):
    total_old_size = 0
    total_new_size = 0
    file_counter = 0
    tries_counter = 0
    types = [".jpg", ".jpeg", ".png"]

    for file in depth_search_files(path, types):

        img = Image.open(get_full_path(file[0], file[1]))
        old_file_size = get_file_size(*file)

        counter, quality, new_file_size, img_type = get_new_picture(img, get_full_path(*file))

        if old_file_size > new_file_size:
            file_counter += 1
            tries_counter += counter
            total_new_size += new_file_size
            total_old_size += old_file_size

            delete_file(file[0], file[1])
            img.save(get_full_path(*file), img_type, quality=quality, optimized=True)

            info(str(total_new_size) + " / " + str(total_old_size))
            info("File count " + str(file_counter))
            info("Average Minimum count: " + str(int(tries_counter / file_counter)))
        else:
            error("OLD FILE SMALLER")

        info(file[0] + " " + file[1])

    # info(str(total_new_size) + "/" + str(total_old_size) + " " + str(file_counter))
    info("SAVED " + format_bit(total_old_size - total_new_size))


def get_butteraugli(file_name, temp_file):
    return check_output('butteraugli/butteraugli.sh ' + file_name + ' ' + temp_file,
                        stdin=None, stderr=None, shell=True)


def get_perception(quality, img, file_name, result, max_perception=1.1):
    with NamedTemporaryFile(mode="wb", suffix=".jpg") as temp_file:
        img.save(temp_file, quality=quality, optimize=True)
        result[0] = temp_file
        return float(get_butteraugli(file_name, temp_file)) - max_perception


def find_minimum(x_1, x_2, f_1, max_domain, function):
    counter = 0
    while abs(x_1 - x_2) != 0:
        counter += 1
        f_2 = function(x_2)

        if (f_1 - f_2) and (x_1 - x_2):
            # x_2 = x_2 - f_2 / f_2'
            x_1, f_1, x_2 = x_2, f_2, int(x_2 - f_2 / (f_1 - f_2) * (x_1 - x_2))
        else:
            x_1, f_1, x_2 = x_2, f_2, max_domain

    info("COUNTER: " + str(counter))
    return x_1, counter


def get_perception_mock(x):
    return pow(x - 100, 2) * 1.1 / 225 - 1.1


def get_new_picture(img, file_name, max_perception=1.1):
    # JPG
    result = [None]
    quality, counter = find_minimum(x_1=100, x_2=80, f_1=-max_perception, max_domain=100,
                                    function=lambda x: get_perception(quality=x, img=img, file_name=file_name,
                                                                      result=result,
                                                                      max_perception=max_perception))
    jpg_size = getsize(result[0])

    # PNG
    with NamedTemporaryFile(mode="wb", suffix=".png") as temp_file:
        img.save(temp_file, 'png', optimized=True)
        png_size = getsize(temp_file)
    if png_size < jpg_size and get_butteraugli(file_name, temp_file) <= max_perception:
        return counter, quality, png_size, "png"

    return counter, quality, jpg_size, "jpg"


if __name__ == "__main__":
    log = Logger()
    print(find_minimum(x_1=100, x_2=80, f_1=0.0, max_domain=100,
                       function=get_perception_mock))
    # convert("test_images")
    log.shutdown()

    # 76,8 mb
