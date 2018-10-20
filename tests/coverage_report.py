from subprocess import Popen
from utility.os_interface import get_dir_list, get_absolute_path


def run_test(file):
    command = 'coverage run --parallel-mode ' + get_absolute_path(file)
    return Popen(command)


files = filter(lambda x: x.startswith('test___'), get_dir_list('.'))
files = list(map(run_test, files))
files = map(lambda x: x.communicate(), files)

Popen('coverage combine').communicate()
Popen('coverage report -m').communicate()
