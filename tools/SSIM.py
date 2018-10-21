from collections import defaultdict
from ctypes import c_ubyte

def get_expected_value(color_count, pixel_sum):
    return sum(pixel * count * count
               for pixel, count in zip(color_count.keys(), color_count.values())) / pixel_sum


def covariance(tile_x, tile_y):
    for pixel, count in zip(tile_y.color_count.keys(), tile_y.color_count.values()):
        tile_x.color_count[pixel] += count

    return get_expected_value(tile_x.color_count,
                              tile_x.pixel_sum + tile_y.pixel_sum) - tile_x.expected_value * tile_y.expected_value


class Tile:
    def __init__(self, pixels, pixel_len):
        self.color_count = defaultdict(int)

        for pixel in pixels:
            self.color_count[pixel] += 1

        self.pixel_sum = sum(pixels)

        self.average = self.pixel_sum / pixel_len
        self.expected_value = get_expected_value(self.color_count, self.pixel_sum)

        self.variance = sum((count * (pixel - self.expected_value)) ** 2
                            for pixel, count in
                            zip(self.color_count.keys(), self.color_count.values())) / self.pixel_sum


def _ssim_tile(pixels_x, pixels_y, dynamic_range, pixel_len):
    # https: // en.wikipedia.org / wiki / Structural_similarity  # Algorithm

    tile_x = Tile(pixels_x, pixel_len)
    tile_y = Tile(pixels_y, pixel_len)

    cov = covariance(tile_x, tile_y)

    c_1 = (dynamic_range * 0.01) ** 2
    c_2 = (dynamic_range * 0.03) ** 2

    return (2 * tile_x.average * tile_y.average + c_1) * (2 * cov + c_2) \
           / (tile_x.average * tile_x.average + tile_y.average * tile_y.average + c_1) \
           / (tile_x.variance + tile_y.variance + c_2)


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
