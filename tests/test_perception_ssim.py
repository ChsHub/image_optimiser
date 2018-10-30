from hypothesis import given
from hypothesis.strategies import text, integers
from mock_image import MockImage
from utility.os_interface import exists
from image_optimiser.perception_ssim import *
from numpy import ndarray


@given(integers(min_value=10, max_value=100), text(min_size=1, alphabet='abcdefghi'))
def test_cv_open_image(n, file_name):
    with MockImage(file_name, n) as image:
        cv_image = cv_open_image(image.full_path)
        assert type(cv_image) == ndarray


def test_cv_open_image_fail():
    with MockImage('あ', 10) as image:
        try:
            cv_image = cv_open_image(image.file_name)
        except ValueError:
            assert True


def test_cv_open_image_fail2():
    try:
        cv_image = cv_open_image('')
    except ValueError:
        assert True


@given(integers(min_value=0, max_value=100))
def test_get_perception(quality):
    with MockImage('a', 10) as image:
        original = cv_open_image(image.full_path)
        temp_image_path = get_temp_image(quality, image.image, image.temp_path)
        value = get_perception(original, temp_image_path)

        assert value <= 0.0
        assert value >= -1.0


if __name__ == '__main__':
    test_cv_open_image()
    test_cv_open_image_fail()
    test_cv_open_image_fail2()
    test_get_perception()
