from collections import defaultdict


def _get_pixel_array(window_size, position, pixels):
    return [pixels[x, y] for x in range(position[0], position[0] + window_size) for y in
            range(position[1], position[1] + window_size)]


def _get_color_count(pixels):
    color_count = defaultdict(int)
    for pixel in pixels:
        color_count[pixel] += 1

    return color_count


class Tile:
    def __init__(self, window_size, position, image, pixel_len):
        self._pixels = _get_pixel_array(window_size, position, image)
        self.pixel_sum = sum(self._pixels)
        self.average = self.pixel_sum / pixel_len
        self.color_count = _get_color_count(self._pixels)
        self.expected_value = self._get_expected_value()
        self.variance = self._get_variance()

    # https://en.wikipedia.org/wiki/Expected_value
    def _get_expected_value(self):
        """
        Calculate the expected value, SUM(x * p) = SUM(x * count(x)) / SUM(X)
        :return: expected value
        """
        return sum([pixel * self.color_count[pixel] for pixel in self._pixels]) / self.pixel_sum

    def _get_variance(self):
        """
        Calculate the variance of the pixels, SUM(p*(x - E)^2) = SUM(count(x)*(x - E)^2) / SUM(X) with expected value E
        :return: Variance
        """
        return sum([self.color_count[pixel] * (pixel - self.expected_value) ** 2
                    for pixel in self._pixels]) / self.pixel_sum


def covariance(pixels, tile_x, tile_y):
    expected_value = sum([pixel * (tile_x.color_count[pixel] + tile_y.color_count[pixel])
                          for pixel in pixels]) / (tile_x.pixel_sum + tile_y.pixel_sum)

    return expected_value - tile_x.expected_value * tile_y.expected_value


def _ssim_tile(img_x, img_y, dynamic_range, pixel_len, window_size=8, position=(0, 0)):
    # https: // en.wikipedia.org / wiki / Structural_similarity  # Algorithm

    tile_x = Tile(window_size, position, img_x, pixel_len)
    tile_y = Tile(window_size, position, img_y, pixel_len)

    cov = covariance(tile_x._pixels + tile_y._pixels, tile_x, tile_y)

    c_1 = (dynamic_range * 0.01) ** 2
    c_2 = (dynamic_range * 0.03) ** 2

    return (2 * tile_x.average * tile_y.average + c_1) * (2 * cov + c_2) \
           / (tile_x.average ** 2 + tile_y.average ** 2 + c_1) \
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
    image_0 = image_0.split()[0].load()
    image_1 = image_1.split()[0].load()

    for x in range(0, width - window_size, window_size):
        for y in range(0, height - window_size, window_size):
            ssim += _ssim_tile(image_0, image_1, dynamic_range, pixel_len, position=(x, y))
            i += 1
    print(i)
    return ssim / i
