from hypothesis import given
from hypothesis.strategies import integers
from utility.os_interface import exists

from image_optimiser.perception_ssim import get_temp_image

from mock_image import MockImage


@given(integers(min_value=10, max_value=1000), integers(min_value=1, max_value=100))
def test_get_temp_image(size, quality):
    with MockImage(name='a', size=size, extension=1, palette=0) as image:
        temp_file_path = get_temp_image(quality, image.image, image.temp_path, '.webp')
        assert exists(temp_file_path)


if __name__ == '__main__':
    test_get_temp_image()
