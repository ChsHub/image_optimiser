from tempfile import TemporaryDirectory

from hypothesis import given, settings
from hypothesis.strategies import integers
from os.path import isfile, join
from utility.path_str import get_full_path

from image_optimiser.optimize import *
from mock_image import MockImage


@given(integers(min_value=1), integers(min_value=1))
def test_get_max_perception(x, y):
    assert (get_max_perception((x, y)) >= 0.0)
    assert (get_max_perception((x, y)) <= 1.0)

@settings(deadline=None)
@given(integers(min_value=10, max_value=200))
def test_find_minimum(n):
    file_name = 'a'
    with MockImage(file_name, n) as image:
        temp_file = find_minimum(temp_path=image.temp_path, img=image.image)
        assert isfile(temp_file)


def test_find_minimum_example():
    image_name = 'test.png'
    image = Image.open('test_images/test.png')
    with TemporaryDirectory() as temp_path:
        image.save(join(temp_path, image_name))
        temp_file = find_minimum(temp_path=temp_path, img=image)
        assert (isfile(temp_file))


if __name__ == '__main__':
    test_find_minimum()
    test_get_max_perception()
    test_find_minimum_example()
