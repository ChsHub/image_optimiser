from collections import defaultdict
from ctypes import c_ubyte

def naive_covariance(pixel0, pixel1, image0, image1, pixel_len):
    total_sum = 0
    for i1, i2 in zip(pixel0, pixel1):
        total_sum += i1 * i2

    return (total_sum - image0.pixel_sum * image1.pixel_sum / pixel_len) / pixel_len


def covariance(pixels_0, pixel_1, image0, image1, pixel_len):
    cov = 0
    for pixel_0, pixel_1 in zip(pixels_0, pixel_1):
        cov += (pixel_0 - image0.average) * (pixel_1 - image1.average)
    return cov / pixel_len

    # return (image0.average + image1.average) / 2 - image0.average * image1.average


class Tile:
    def __init__(self, pixels, pixel_len):
        color_count = defaultdict(int)
        for pixel in pixels:
            color_count[pixel] += 1

        self.pixel_sum = sum(pixels)
        # self.pixel_sum = get_expected_value(color_count)
        self.average = self.pixel_sum / pixel_len

        # https://en.wikipedia.org/wiki/Standard_deviation#Population_standard_deviation_of_grades_of_eight_students
        self.variance = 0
        for pixel, count in zip(color_count.keys(), color_count.values()):
            a = pixel - self.average
            self.variance += count * a * a
        self.variance /= pixel_len


def _ssim_tile(pixel0, pixel1, dynamic_range, pixel_len):
    # https: // en.wikipedia.org / wiki / Structural_similarity  # Algorithm

    image0 = Tile(pixel0, pixel_len)
    image1 = Tile(pixel1, pixel_len)
    cov = naive_covariance(pixel0, pixel1, image0, image1, pixel_len)
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
    ssim = 0
    dynamic_range = 255  # *3
    pixel_len = window_size * window_size
    width, height = image_0.size
    image_0 = list(image_0.getdata(band=0))
    image_1 = list(image_1.getdata(band=0))
    # image_1 = image_0

    for x in range(0, width - width % window_size, window_size):
        for y in range(0, height - height % window_size, window_size):

            _pixels_0 = []
            _pixels_1 = []
            for w in range(y, y + window_size):
                w *= width

                _pixels_0 += image_0[x + w:x + window_size + w]
                _pixels_1 += image_1[x + w:x + window_size + w]

            ssim += _ssim_tile(_pixels_0, _pixels_1, dynamic_range, pixel_len)

    return ssim / (width // window_size * height // window_size)
