from tempfile import TemporaryDirectory

from PIL import Image
from hypothesis import given
from hypothesis.strategies import text, integers
from mock_image import MockImage
from utility.os_interface import exists
from utility.path_str import get_full_path

from image_optimiser.opti import *


@given(integers(min_value=1))
def test_get_max_perception(size):
    assert (get_max_perception(size) >= -1.0)
    assert (get_max_perception(size) <= 0.0)


@given(integers(min_value=10, max_value=200))
def test_find_minimum(n):
    file_name = 'a'
    with MockImage(file_name, n) as image:
        temp_file = find_minimum(temp_path=image.temp_path, original_file=image.full_path, img=image.image)
        assert (exists(temp_file))


def test_find_minimum_example():
    image_name = 'test.png'
    image = Image.open(image_name)
    with TemporaryDirectory() as temp_path:
        image.save(get_full_path(temp_path, image_name))
        temp_file = find_minimum(temp_path=temp_path, original_file=image_name, img=image)
        assert (exists(temp_file))


if __name__ == '__main__':
    test_find_minimum()
    test_get_max_perception()
    test_find_minimum_example()
