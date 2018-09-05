from logging import info


def binarysearch(offset, low, high, function, count, quality):
    while high > low:
        count += 1
        quality = (low + high) // 2
        if function(quality) > offset:
            low, high = quality + 1, high
        else:
            low, high = low, quality - 1

    return quality, count

def find_minimum(x_1, x_2, min_domain, max_domain, offset, function):
    return binarysearch(offset, min_domain, max_domain, function, 0, 0)
