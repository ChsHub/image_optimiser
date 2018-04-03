# encoding utf-8

from PIL import Image
from PIL.Image import LANCZOS, HAMMING, BILINEAR, LANCZOS, BICUBIC
from utility.os_interface import make_directory, get_dir_list, is_file_type


def resize_directory(path="", factor=1.0, sample=LANCZOS, prefix="r_", quality=85,
                     convert_type=(".png", ".jpg", ".RW2", ".tif"),
                     save_type="jpg", palette="RGB", width=0):
    if not path:
        return

    files = get_dir_list(path)
    new_dir = path + "/resize " + save_type + " " + palette + " " + str(quality) + " " + str(factor)
    make_directory(new_dir)

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

            if save_type:
                file = file.split(".")
                file[-1] = save_type
                file = ".".join(file)
                file = file.replace("..", ".")

            img.save(new_dir + "/" + prefix + file, quality=quality, optimize=True)
            print(i+1, file, size)

        except Exception as e:
            print(e)

    print("DONE")


if __name__ == "__main__":
    resize_directory(path="", factor=1, quality=93,
                     # convert_type=(".png"),
                     # width=1000,
                     save_type="jpg", prefix="", sample=LANCZOS)
