from subprocess import getoutput, call
from utility.os_interface import get_absolute_path
from tempfile import NamedTemporaryFile
from io import StringIO
from os.path import getsize
import butteraugli as main


def get_butteraugli(file_name, temp_file):
    result = call('ls')
    print(result)
    result = call(get_absolute_path('butteraugli/butteraugli.sh') + ' ' +
                  get_absolute_path(file_name) + " " +
                  get_absolute_path(temp_file.name))  # + ' ' + temp_file.name)

    print(result)
    return result


def get_perception(quality, img, file_name, result, max_perception=1.1):
    with NamedTemporaryFile(mode="wb", suffix=".jpg") as temp_file:
        img.save(temp_file, quality=quality, optimize=True)
        result[0] = getsize(temp_file.name)
        print(temp_file.name)
        return float(get_butteraugli(file_name, temp_file)) - max_perception
