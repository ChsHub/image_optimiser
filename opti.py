from logging import info


def binarysearch_recursive(offset, low, high, function, count):
    if high < low:
        return low, count

    quality = (low + high) // 2
    if function(quality) > offset:
        return binarysearch_recursive(offset, quality + 1, high, function, count + 1)
    else:
        return binarysearch_recursive(offset, low, quality - 1, function, count + 1)


def find_minimum(x_1, x_2, min_domain, max_domain, offset, function):
    return binarysearch_recursive(offset, min_domain, max_domain, function, 0)
