# encoding utf-8
from os.path import join

from PIL import Image
from PIL.Image import LANCZOS, HAMMING, BILINEAR, LANCZOS, BICUBIC
from send2trash import send2trash
from utility.os_interface import make_directory, get_dir_list, is_file_type, get_file_size, exists, \
    move_file

from logging import info, error, exception
from utility.logger import Logger


def _delete_file(path, file):
    full_path = join(path, file)
    full_path = full_path.replace('/', '\\')
    send2trash(full_path)
    if exists(full_path):
        error("MOVE FAIL: " + full_path)


def resize_directory(path="", factor=1.0, sample=LANCZOS, prefix="", quality=85,
                     convert_type=(".png", ".jpg", ".RW2", ".tif", ".bmp"),
                     save_type="jpg", palette="RGB", width=0, delete_largest=False, crop=None):
    if not path:
        pass

    # Create target directory with appropriate name
    files = get_dir_list(path)
    if width != 0:
        new_dir = path + "/" + save_type + " " + palette + " " + str(quality) + " w" + str(width)
    else:
        new_dir = path + "/" + save_type + " " + palette + " " + str(quality) + " s" + str(factor)
    make_directory(new_dir)

    # Iterate all files and resize
    info(str(len(files)) + " FILES")
    for i, file in enumerate(filter(lambda image: is_file_type(image, convert_type), files)):

        try:

            with Image.open(path + "/" + file) as  img:
                # Convert to RGB, because of palette resize issues
                img = img.convert(palette)  # TODO makes files bigger

                # Resize with factor or direct value
                x, y = img.size
                # img = img.rotate(90, expand=True) # rotate
                if width != 0:
                    factor = width / x
                size = (int(x * factor), int(y * factor))
                img = img.resize(size, resample=sample)

                # Crop image
                if crop:
                    img = img.crop(box=crop)

                # Get new file name
                new_file = file
                if save_type:
                    new_file = file.split(".")
                    new_file[-1] = save_type
                    new_file = ".".join(new_file)
                    new_file = prefix + new_file.replace("..", ".")

                # Save new image
                new_file_path = join(new_dir, new_file)
                if not exists(new_file_path):
                    img.save(new_file_path, quality=quality, optimize=True)
                    info(str(i + 1) + ' ' + new_file + ' ' + str(size))
                else:
                    info("FILE ALREADY CONVERTED: " + new_file_path)

                # Delete largest image
                if delete_largest:

                    # if new file larger
                    if get_file_size(new_dir, new_file) > get_file_size(path, file):
                        _delete_file(new_dir, new_file)
                    else:
                        _delete_file(path, file)

                # no else
        except Exception as e:
            exception(e)

    info("DONE")
