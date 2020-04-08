from os.path import join, abspath
from tempfile import TemporaryDirectory

from MockImage import MockImage
from hypothesis import given, settings
from hypothesis.strategies import integers

from image_optimiser.optimize import *


@given(integers(min_value=1), integers(min_value=1))
def test_get_max_perception(x, y):
    assert (get_max_perception((x, y)) >= 0.0)
    assert (get_max_perception((x, y)) <= 1.0)


@settings(deadline=None)
@given(integers(min_value=10, max_value=200))
def test_find_minimum(n):
    file_name = 'a'
    with MockImage(file_name, n) as image:
        temp_file = find_minimum(temp_path=image.temp_path, img=image.image, new_type='.webp')
        assert isfile(temp_file)


def test_find_minimum_example():
    image_name = 'test.png'
    image = Image.open(abspath('test_images/test.png'))
    with TemporaryDirectory() as temp_path:
        image.save(join(temp_path, image_name))  # Write test image to temporary file
        temp_file = find_minimum(temp_path=temp_path, img=image, new_type='.webp')
        assert (isfile(temp_file))


if __name__ == '__main__':
    test_find_minimum()
    test_get_max_perception()
    test_find_minimum_example()
