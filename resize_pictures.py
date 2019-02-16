# encoding utf-8
from PIL import Image
from PIL.Image import LANCZOS, HAMMING, BILINEAR, LANCZOS, BICUBIC
from utility.os_interface import make_directory, get_dir_list, is_file_type, get_file_size, get_full_path, exists, \
    move_file

from logging import info, error, exception
from utility.logger import Logger


def resize_directory(path="", factor=1.0, sample=LANCZOS, prefix="", quality=85,
                     convert_type=(".png", ".jpg", ".RW2", ".tif", ".bmp"),
                     save_type="jpg", palette="RGB", width=0, delete_largest=False, crop=None):
    if not path:
        pass
        # return

    files = get_dir_list(path)
    if width != 0:
        new_dir = path + "/" + save_type + " " + palette + " " + str(quality) + " w" + str(width)
    else:
        new_dir = path + "/" + save_type + " " + palette + " " + str(quality) + " s" + str(factor)

    make_directory(new_dir)

    info(str(len(files)) + " FILES")
    for i, file in enumerate(filter(lambda image: is_file_type(image, convert_type), files)):

        try:

            img = Image.open(path + "/" + file)
            img = img.convert(palette)  # TODO makes files bigger
            x, y = img.size
            # img = img.rotate(90, expand=True) # rotate
            if width != 0:
                factor = width / x

            size = (int(x * factor), int(y * factor))
            img = img.resize(size, resample=sample)
            if crop:
                img = img.crop(box=crop)

            new_file = file
            if save_type:
                new_file = file.split(".")
                new_file[-1] = save_type
                new_file = ".".join(new_file)
                new_file = prefix + new_file.replace("..", ".")

            new_file_path = get_full_path(new_dir, new_file)
            if not exists(new_file_path):
                img.save(new_file_path, quality=quality, optimize=True)
                info(str(i + 1) + ' ' + new_file + ' ' + str(size))
            else:
                info("FILE ALREADY CONVERTED: " + new_file_path)

            if delete_largest:
                trash_path = get_full_path(path, "TRASH")
                make_directory(trash_path)
                # if new file larger
                if get_file_size(new_dir, new_file) > get_file_size(path, file):

                    move_file(new_dir, trash_path, new_file)
                    if exists(new_file_path):
                        error("MOVE FAIL: " + new_file_path)
                else:
                    move_file(path, trash_path, file)
                    if exists(get_full_path(path, file)):
                        error("MOVE FAIL: " + get_full_path(path, file))
            # no else
        except Exception as e:
            exception(e)

    info("DONE")


if __name__ == "__main__":
    with Logger() as l:
        resize_directory(path="",
                         delete_largest=True,
                        # convert_type=(".png")
                         convert_type=(".png", ".jpg"),
                         # width=1500, convert_type=(".jpg"),
                         factor=1, quality=90, save_type="jpg")
