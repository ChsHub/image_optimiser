from collections import defaultdict
from ctypes import c_ubyte


def get_expected_value(color_count, total_count):
    return sum(pixel * count
               for pixel, count in zip(color_count.keys(), color_count.values())) / total_count


def covariance(tile_x, tile_y, pixel_len):
    for pixel, count in zip(tile_y.color_count.keys(), tile_y.color_count.values()):
        tile_x.color_count[pixel] += count

    return (tile_x.average+tile_y.average)/2- tile_x.average * tile_y.average
    """
    covariance = 0

    for x, y in zip(tile_x.color_count.keys(), tile_y.color_count.keys()):
        covariance += (x - tile_x.average) * (y - tile_y.average) / pixel_len
    return covariance"""


class Tile:
    def __init__(self, pixels, pixel_len):
        self.color_count = defaultdict(int)

        for pixel in pixels:
            self.color_count[pixel] += 1

        self.average = sum(pixels) / pixel_len

        # https://en.wikipedia.org/wiki/Standard_deviation#Population_standard_deviation_of_grades_of_eight_students
        self.variance = sum(count * (pixel - self.average) * (pixel - self.average)
                            for pixel, count in zip(self.color_count.keys(), self.color_count.values())) / pixel_len


def _ssim_tile(image0, image1, dynamic_range, pixel_len):
    # https: // en.wikipedia.org / wiki / Structural_similarity  # Algorithm

    image0 = Tile(image0, pixel_len)
    image1 = Tile(image1, pixel_len)

    cov = covariance(image0, image1, pixel_len)
    c_1 = (dynamic_range * 0.01) ** 2
    c_2 = (dynamic_range * 0.03) ** 2

    return (2 * image0.average * image1.average + c_1) * (2 * cov + c_2) \
           / (image0.average * image0.average + image1.average * image1.average + c_1) \
           / (image0.variance + image1.variance + c_2)


def SSIM(image_0, image_1):
    if image_0.size != image_1.size:
        print('ERROR images are not same size')
        return
    # no else

    window_size = 8
    ssim, i = 0, 0
    dynamic_range = 255  # *3
    pixel_len = window_size * window_size
    width, height = image_0.size
    image_0 = list(image_0.getdata(band=0))
    image_1 = list(image_1.getdata(band=0))
    image_1 = image_0

    for x in range(0, width - width % window_size, window_size):
        for y in range(0, height - height % window_size, window_size):

            _pixels_0 = []
            _pixels_1 = []
            for w in range(y, y + window_size):
                w *= width

                _pixels_0 += image_0[x + w:x + window_size + w]
                _pixels_1 += image_1[x + w:x + window_size + w]

            ssim += _ssim_tile(_pixels_0, _pixels_1, dynamic_range, pixel_len)
            i += 1

    return ssim / i
