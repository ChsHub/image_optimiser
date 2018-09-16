from utility.os_interface import get_absolute_path
# python.exe -m pip install scikit-image
from utility.path_str import get_full_path
from cv2 import cvtColor, imread, COLOR_BGR2GRAY
from skimage.measure import compare_ssim

def cv_open_image(file_name):
    image = imread(get_absolute_path(file_name))
    if image is None:
        raise ValueError

    # convert the images to grayscale
    return cvtColor(image, COLOR_BGR2GRAY)


def get_value(original, temp_file):
    return -compare_ssim(original, cv_open_image(temp_file), multichannel=True)


def get_perception(quality, img, original, temp_path):

    temp_file = get_full_path(temp_path, str(quality) + ".webp")  # jpg
    img.save(temp_file, quality=quality, optimize=True, method=6)  # )

    return temp_file, float(get_value(original, temp_file))
