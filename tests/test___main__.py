from os.path import exists, join

from MockImage import MockImage
from hypothesis import given, settings
from hypothesis.strategies import booleans

from image_optimiser import optimise
from image_optimiser.__main__ import _add_images


@settings(deadline=None)
@given(booleans())
def test__add_images(depth_search):
    with MockImage() as image:
        result = _add_images([image.temp_path], depth_search)
        result += _add_images([(image.temp_path, image.file_name)], depth_search)

        for image in result:
            assert type(image) == tuple
            image = join(image[0], image[1])
            assert exists(image)


@settings(deadline=None)
@given(booleans())
def test_optimise(path):
    with MockImage() as image:
        if path:
            optimise(image.full_path)
        else:
            optimise(image.temp_path)


def test_optimise_invalid():
    optimise(None)


# https://medium.com/@george.shuklin/how-to-test-if-name-main-1928367290cb
def test_init():
    import image_optimiser.__main__ as main
    main.__name__ = '__main__'

    def optimise_stub(image_input, log_file):
        raise SystemExit

    main.optimise = optimise_stub
    with MockImage() as image:
        try:
            main.input = lambda x: image.full_path  # replace input() function
            main.init()
        except SystemExit as e:
            assert True
        except Exception as e:
            print(e)
            assert False


if __name__ == '__main__':
    test__add_images()
    test_init()
    test_optimise()
    test_optimise_invalid()
