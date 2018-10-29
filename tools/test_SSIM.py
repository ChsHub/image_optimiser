from logging import info
from tempfile import TemporaryDirectory

from utility.logger import Logger
from tools.SSIM import SSIM
from tools.SSIM_old import SSIM as SSIM_old
from PIL import Image
from utility.os_interface import get_dir_list
from utility.path_str import get_full_path
from utility.utilities import is_file_type

from image_optimiser.perception_ssim import get_perception, cv_open_image, get_temp_image


def test_SSIM():
    with Logger(_max_count_logfiles=10):
        from tools.paths import path
        images = get_dir_list(path)
        """for temp_name in images:
            temp_name = get_full_path(path, temp_name)
            if is_file_type(temp_name, ('.png', '.jpg', '.webm')):"""#
        temp_name = "D:\Making\Python\image_optimiser/tests/test.png"

        with TemporaryDirectory() as temp_path:
            with Image.open(temp_name) as img_x:
                img_b_path = get_temp_image(1, img_x, temp_path)
                value = get_perception(cv_open_image(temp_name), img_b_path)

                value2 = -SSIM(img_x, Image.open(img_b_path))

                #with Timer('HOME MADE OLD'):
                 #   value3 = SSIM_old(img_x, Image.open(temp_file))

                info(str(value) + '  ///  ' + str(value2))
                assert abs(value - value2) < 0.09
                #assert abs(value - value2) < 0.2


if __name__ == '__main__':

    test_SSIM()
