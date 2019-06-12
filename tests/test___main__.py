from os import makedirs
from shutil import copy2, move

from MockImage import MockImage
from os.path import join

from hypothesis import given, settings
from hypothesis.strategies import booleans

from image_optimiser import optimise


@settings(deadline=None)
@given(booleans())
def test_optimise(path):
    with MockImage() as image:
        if path:
            optimise(image.full_path)
        else:
            optimise(image.temp_path)


# https://medium.com/@george.shuklin/how-to-test-if-name-main-1928367290cb
def test_init():
    import image_optimiser.__main__ as main
    a = main
    a.__name__ = '__main__'
    main.input = lambda x: ''  # replace input() function
    try:
        main.init()
    except Exception as e:
        print(e)
        assert False
    assert True


if __name__ == '__main__':
    test_init()
    test_optimise()
