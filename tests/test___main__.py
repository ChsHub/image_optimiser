from os import makedirs
from shutil import copy2, move

from os.path import join

from PIL import Image
from hypothesis import given, settings
from hypothesis.strategies import booleans

from image_optimiser import optimise
from image_optimiser.__main__ import accept_file
from mock_image import MockImage


def test_accept_file():
    with MockImage() as mock:
        trash_path = mock.temp_path + '/TRASH'
        makedirs(trash_path)

        result = accept_file(mock.temp_path, file_name=mock.file_name, types=[".jpg", ".png", ".jpeg"],
                             trash_directory=trash_path)
        assert result


def test_accept_file_exists():
    with MockImage() as mock:
        trash_path = join(mock.temp_path, 'TRASH')
        makedirs(trash_path)

        copy2(mock.full_path, join(trash_path, mock.file_name))

        result = accept_file(mock.temp_path, mock.file_name, types=[".jpg", ".png", ".jpeg"],
                             trash_directory=trash_path)
        assert not result


def test_accept_file_trash():
    with MockImage() as mock:
        trash_path = mock.temp_path + '/TRASH'
        makedirs(trash_path)
        move(mock.full_path, join(trash_path, mock.file_name))

        result = accept_file(trash_path, mock.file_name, trash_path, [".jpg", ".png", ".jpeg"])
        assert not result


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
    test_accept_file()
    test_accept_file_exists()
    test_accept_file_trash()
    test_init()
    test_optimise()
