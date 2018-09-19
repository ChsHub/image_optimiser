from hypothesis import given
from hypothesis.strategies import text, integers
from mock_image import MockImage
from utility.os_interface import exists

from image_optimiser.opti import *


@given(integers(min_value=1))
def test_get_max_perception(size):
    assert (get_max_perception(size) >= -1.0)
    assert (get_max_perception(size) <= 0.0)


@given(integers(min_value=10, max_value=100), text(min_size=1, alphabet='abcdefghi'))
def test_find_minimum(n, file_name):
    with MockImage(file_name, n) as image:
        temp_file = find_minimum(temp_path=image.temp_path, original_file=image.full_path, img=image.image)
        assert (exists(temp_file))


if __name__ == '__main__':
    test_find_minimum()
    test_get_max_perception()
