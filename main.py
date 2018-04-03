from logging import info, error
from tempfile import NamedTemporaryFile
from os.path import getsize

from PIL import Image

# sudo chmod -R a+rX /usr/local/lib/python3.4/
from utility.logger import Logger
from utility.os_interface import depth_search_files, delete_file, get_file_size
from utility.path_str import get_full_path
from utility.utilities import format_bit

from newton import find_minimum
from perception_butteraugli import get_perception, get_butteraugli


# python3

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

        counter, quality, new_file_size, img_type = get_new_picture_jpg(img, get_full_path(*file))

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


def get_new_picture_jpg(img, file_name, max_perception=1.1):
    # JPG
    result = [None]
    quality, counter = find_minimum(x_1=100, x_2=80, f_1=-max_perception, max_domain=100,
                                    function=lambda x: get_perception(quality=x, img=img, file_name=file_name,
                                                                      result=result,
                                                                      max_perception=max_perception))
    jpg_size = result[0]
    return counter, quality, jpg_size, "jpg"


def get_new_picture_png(img, file_name, max_perception=1.1):
    # PNG
    with NamedTemporaryFile(mode="wb", suffix=".png") as temp_file:
        img.save(temp_file, 'png', optimized=True)
        png_size = getsize(temp_file)

    if get_butteraugli(file_name, temp_file) <= max_perception:
        return 0, 0, png_size, "png"
    else:
        return None


if __name__ == "__main__":
    log = Logger()
    # print(find_minimum(x_1=100, x_2=80, f_1=0.0, max_domain=100,                       function=perception_mock.get_perception))
    convert("test_images")
    log.shutdown()

    # 76,8 mb
