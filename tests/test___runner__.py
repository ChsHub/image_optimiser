from os.path import splitext

from MockImage import MockImage
from PIL.Image import merge
from hypothesis import given, settings
from hypothesis.strategies import text, integers, booleans

from image_optimiser.__main__ import *
from image_optimiser.runner import _has_no_alpha, optimise_image


@settings(deadline=None)
@given(text(min_size=1, alphabet='a'), integers(min_value=0, max_value=3), integers(min_value=0, max_value=6))
def test_is_compressable(name, palette, ext):
    with MockImage(name, 10, palette=palette, extension=ext) as mock:
        result = _has_no_alpha(mock.image)
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

        mock.image = merge(mock.image.mode, bands=channels)

        result = _has_no_alpha(mock.image)  # , (mock.temp_path, mock.file_name), types, trash_path)
        assert not result


@settings(deadline=None)
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
            _, extension = splitext(mock.full_path)
            # assert isdir(mock.temp_path + '/TRASH') != insta_delete or extension not in types TODO test in trash directory
            assert isfile(mock.full_path) == (old_size == 0)


@settings(deadline=None)
@given(text(min_size=1, alphabet='abcsht'), booleans(), integers(min_value=0, max_value=1))
def test_optimise_image_old_smaller(file_name, insta_delete, types):
    with MockImage(file_name, 10, extension=6) as mock:
        mock.image.save(mock.full_path, quality=1, optimize=True)
        old_size, new_size = optimise_image(file=(mock.temp_path, mock.file_name),
                                            new_type=[".jpg", ".webp"][types], direct_delete=insta_delete)

        assert type(old_size) == type(new_size)
        assert type(old_size) == str or type(old_size) == int
        # assert isdir(mock.temp_path + '/TRASH') != insta_delete or old_size == 0 TODO in trash directory


@settings(deadline=None)
@given(integers(), integers(), text(), booleans())
def test_optimise_image_abort(number, number2, types, insta_delete):
    old_size, new_size = optimise_image((number, number2), types, insta_delete)

    assert old_size == number
    assert new_size == number2


@settings(deadline=None)
@given(text(min_size=1, alphabet='abcdefghijklmnop'), booleans())
def test_convert(file_name, insta_delete):
    with MockImage(file_name, 10) as mock:
        inp = (mock.temp_path, mock.file_name)
        convert(images=[inp], direct_delete=insta_delete)
        # TODO more checks
        # assert isdir(join(mock.temp_path, 'TRASH')) != insta_delete TODO in trash directory


if __name__ == '__main__':
    test_is_compressable()
    test_is_compressable_trans()

    test_optimise_image()
    test_optimise_image_old_smaller()
    test_optimise_image_abort()

    test_convert()
