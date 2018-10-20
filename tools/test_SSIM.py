from tempfile import TemporaryDirectory
from tools.SSIM import SSIM
from PIL import Image
from utility.timer import Timer

from image_optimiser.perception_ssim import get_perception, cv_open_image


def test_SSIM():
    temp_name = "D:\Making\Python\image_optimiser/tests/test.png"
    with TemporaryDirectory() as temp_path:
        with Image.open(temp_name) as img_x:
            with Timer('CV', log=False):
                temp_file, value = get_perception(1, img_x, cv_open_image(temp_name), temp_path)

            with Timer('HOME MADE', log=False):
                value2 = SSIM(img_x, Image.open(temp_file))
            print(value, value2)
            assert abs(value - value2) < 0.2


if __name__ == '__main__':
    test_SSIM()
