from logging import info

from utility.os_interface import write_file_data, delete_file
from utility.utilities import get_file_type


# binary search
def find_minimum(img_resolution, low, high, target_value, function):
    quality = 0
    counter = 0
    log = str(img_resolution) + '\n'
    temp_file = ''

    while high > low:
        counter += 1
        quality = (low + high) // 2
        delete_file(temp_file)

        temp_file, value = function(quality)
        log += str(quality) + '\t' + str(value) + '\n'

        if value > target_value:
            low, high = quality + 1, high
        else:
            low, high = low, quality - 1

    info('COUNT: ' + str(counter))
    write_file_data('.', 'quality+' + get_file_type(temp_file) + '.log', log, mode='a')
    return temp_file
