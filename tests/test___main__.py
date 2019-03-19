from os import makedirs
from os.path import isdir, isfile
from shutil import copy2, move

from hypothesis import given, settings
from hypothesis.strategies import text, integers, booleans, SearchStrategy
from image_optimiser.__main__ import *
from mock_image import MockImage
from unittest.mock import patch


def test_accept_file():
    with MockImage() as mock:
        trash_path = mock.temp_path + '/TRASH'
        makedirs(trash_path)

        result = accept_file(file=(mock.temp_path, mock.file_name), types=[".jpg", ".png", ".jpeg"], trash_path=trash_path)
        assert result


def test_accept_file_exists():
    with MockImage() as mock:
        trash_path = mock.temp_path + '/TRASH'
        makedirs(trash_path)

        copy2(mock.full_path, get_full_path(trash_path, mock.file_name))

        result = accept_file((mock.temp_path, mock.file_name), [".jpg", ".png", ".jpeg"], trash_path)
        assert not result


def test_accept_file_trash():
    with MockImage() as mock:
        trash_path = mock.temp_path + '/TRASH'
        makedirs(trash_path)
        move(mock.full_path, get_full_path(trash_path, mock.file_name))

        result = accept_file((trash_path, mock.file_name), [".jpg", ".png", ".jpeg"], trash_path)
        assert not result


@given(text(min_size=1, alphabet='a'), integers(min_value=0, max_value=3), integers(min_value=0, max_value=6))
def test_is_compressable(name, palette, ext):
    with MockImage(name, 10, palette=palette, extension=ext) as mock:
        result = is_compressable(mock.image)  # , (mock.temp_path, mock.file_name), types, trash_path)
        assert result  # TODO TEST FALSE


@given(text(min_size=1, alphabet='a'), integers(min_value=1, max_value=2))
def test_is_compressable_trans(name, palette):
    size = 10
    with MockImage(name, size, palette=palette, extension=1) as mock:

        channels = mock.image.split()

        size = int(size / 2)
        alpha = channels[-1].load()
        for x in range(size):
            for y in range(size):
                alpha[x, y] = 0

        mock.image = Image.merge(mock.image.mode, channels)

        result = is_compressable(mock.image)  # , (mock.temp_path, mock.file_name), types, trash_path)
        assert not result


@given(text(min_size=1, alphabet='abcshtwdfw'), integers(min_value=0, max_value=5), booleans(),
       integers(min_value=0, max_value=3), integers(min_value=8, max_value=1000))
def test_optimise_image(file_name, ext, insta_delete, palette, size):
    types = (".jpg", ".png", ".jpeg")
    with MockImage(file_name, 10, extension=ext, palette=palette) as mock:
        old_size, new_size = optimise_image((mock.temp_path, mock.file_name), types, insta_delete)

        if type(old_size) == str and type(new_size) == str:
            assert old_size == mock.temp_path
            assert new_size == mock.file_name
        else:
            assert type(old_size) == type(new_size) == int
            assert old_size >= 0
            assert new_size >= 0
            assert isdir(mock.temp_path + '/TRASH') != insta_delete or '.' + get_file_type(mock.full_path) not in types
            assert isfile(mock.full_path) == (old_size == 0)


@given(text(min_size=1, alphabet='abcsht'), booleans(), integers(min_value=0, max_value=1))
def test_optimise_image_old_smaller(file_name, insta_delete, types):
    with MockImage(file_name, 10, extension=6) as mock:
        mock.image.save(mock.full_path, quality=1, optimize=True)
        old_size, new_size = optimise_image((mock.temp_path, mock.file_name), [".jpg", ".webp"][types], insta_delete)

        assert not isdir(mock.temp_path + '/TRASH')
        assert type(old_size) == type(new_size) == int
        assert old_size == 0
        assert new_size == 0
        assert isfile(mock.full_path)


@given(integers(), integers(), text(), booleans())
def test_optimise_image_abort(number, number2, types, insta_delete):
    old_size, new_size = optimise_image((number, number2), types, insta_delete)

    assert old_size == number
    assert new_size == number2



@settings(deadline=None)
@given(text(min_size=1, alphabet='abcdefghijklmnop'), booleans())
def test_convert(file_name, insta_delete):
    with MockImage(file_name, 10) as mock:
        convert(mock.temp_path, insta_delete)

        assert isdir(mock.temp_path + '/TRASH') != insta_delete


def test_get_new_picture():
    with MockImage('a', 10) as mock:
        path, name = get_new_picture(mock.temp_path, mock.image)
        assert isfile(get_full_path(path, name))


# https://medium.com/@george.shuklin/how-to-test-if-name-main-1928367290cb
def test_init():

    import image_optimiser.__main__ as main
    a = main
    a.__name__ = '__main__'
    main.input = lambda x: '' # replace input() function
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

    test_is_compressable()
    test_is_compressable_trans()

    test_optimise_image()
    test_optimise_image_old_smaller()
    test_optimise_image_abort()

    test_convert()

    test_get_new_picture()

    test_init()
