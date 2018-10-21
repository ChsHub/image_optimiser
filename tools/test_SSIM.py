from logging import info
from tempfile import TemporaryDirectory

from utility.logger import Logger
from tools.SSIM import SSIM
from tools.SSIM_old import SSIM as SSIM_old
from PIL import Image
from utility.timer import Timer

from image_optimiser.perception_ssim import get_perception, cv_open_image


def test_SSIM():
    with Logger(_max_count_logfiles=10):
        temp_name = "D:\Making\Python\image_optimiser/tests/test.png"
        with TemporaryDirectory() as temp_path:
            with Image.open(temp_name) as img_x:
                with Timer('CV'):
                    temp_file, value = get_perception(1, img_x, cv_open_image(temp_name), temp_path)

                with Timer('HOME MADE NEW'):
                    value2 = SSIM(img_x, Image.open(temp_file))

                with Timer('HOME MADE OLD'):
                    value3 = SSIM_old(img_x, Image.open(temp_file))

                assert abs(value3 - value2) < 0.0005
                info(str(value) + '  ///  ' + str(value2) + '  ///  ' + str(value3))
                #assert abs(value - value2) < 0.2


if __name__ == '__main__':
    test_SSIM()
