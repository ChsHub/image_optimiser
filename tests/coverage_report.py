from subprocess import Popen, run

from utility.os_interface import get_dir_list, get_absolute_path


def run_test(file):
    command = 'coverage run --parallel-mode "%s"' % get_absolute_path(file).replace('/', '\\')
    return Popen(command)


files = filter(lambda x: x.startswith('test_'), get_dir_list('.'))
files = list(map(run_test, files))
files = list(map(lambda x: x.communicate(), files))

run('coverage combine')
run('coverage report -m')
