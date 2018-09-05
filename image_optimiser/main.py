# python3
#  python.exe -m pip install scikit-image
#  sudo chmod -R a+rX /usr/local/lib/python3.4/
from logging import info, error, exception
from shutil import move, copyfile
from tempfile import TemporaryDirectory

from PIL import Image
from image_optimiser.opti import find_minimum
from image_optimiser.perception_ssim import get_perception, get_value
from utility.logger import Logger
from utility.os_interface import depth_search_files, get_file_size, make_directory, move_file, exists, \
    write_file_data, read_file_data
from utility.path_str import get_full_path
from utility.utilities import format_bit
from utility.utilities import remove_file_type, get_file_type


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


def optimise_image(file, types=(".jpg", ".png", ".jpeg")):

    info(get_full_path(*file))
    with TemporaryDirectory() as temp_path:

        temp_name = get_full_path(temp_path, 'a' + get_file_type(file[1]))
        copyfile(get_full_path(*file), temp_name)

        trash_path = get_full_path(file[0], 'TRASH')

        try:
            img = Image.open(temp_name)

            if is_compressable(img, file, types, trash_path):

                img = img.convert("RGB")
                old_file_size = get_file_size(temp_name)

                new_file = get_new_picture(img, temp_name, temp_path)
                new_file_size = get_file_size(*new_file)

                if old_file_size > new_file_size:

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


def convert(path):
    if path in read_file_data('.', 'paths.log').split(','):
        info('Path already optimised')
        return

    total_old_size = 0
    total_new_size = 0

    tries_counter = 0
    types = [".jpg", ".png", ".jpeg"]

    d_files = depth_search_files(path, types)
    write_file_data('.', 'paths.log', path + ',', mode='a')

    for file in d_files:
        old_file_size, new_file_size = optimise_image(file)
        total_old_size += old_file_size
        total_new_size += new_file_size

    info("FILES: " + str(len(d_files)))
    info("SAVED: " + format_bit(total_old_size - total_new_size))


def get_new_picture(img, file_path, temp_path):
    counter, quality, img_type = get_new_picture_jpg(img, file_path, temp_path)
    info('COUNT: ' + str(counter) + ' JPG QUALITY: ' + str(quality))

    return temp_path, str(quality) + ".jpg"


def get_max_perception(size):
    # 741104
    # 324900
    write_file_data('.', 'quality.log', str(size) + '\n', mode='a')

    return -0.997 + (size - 741104) / 300000000  # min(-0.950, )  # -0.997 *


def get_new_picture_jpg(img, file_name, temp_path):
    max_perception = get_max_perception(img.size[0] * img.size[1])

    info('MAX PERCEPTION: ' + str(max_perception))

    quality, counter = find_minimum(x_1=100, x_2=70, min_domain=40, max_domain=100,
                                    function=lambda x: get_perception(quality=x, img=img,
                                                                      file_name=file_name, temp_path=temp_path),
                                    offset=max_perception)

    return counter, quality, "jpg"


def get_new_picture_png(img, file_name, max_perception):
    # PNG
    # with NamedTemporaryFile(mode="wb", suffix=".png") as temp_file:
    img.save(temp_file, 'png', optimized=True)

    if get_value(file_name, temp_file) <= max_perception:
        return 0, 0, png_size, "png"
    else:
        return None


if __name__ == "__main__":
    log = Logger(10)
    convert("")
    log.shutdown()
