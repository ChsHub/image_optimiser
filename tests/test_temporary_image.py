from MockImage import MockImage
from os.path import isfile

from hypothesis import given
from hypothesis.strategies import integers

from image_optimiser.temporary_image import get_temp_image



@given(integers(min_value=10, max_value=1000), integers(min_value=1, max_value=100))
def test_get_temp_image(size, quality):
    with MockImage(name='a', size=size, extension=1, palette=0) as image:
        temp_file_path = get_temp_image(quality, image.image, image.temp_path, '.webp')
        assert isfile(temp_file_path)


if __name__ == '__main__':
    test_get_temp_image()
