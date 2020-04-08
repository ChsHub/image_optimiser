from os import listdir
from os.path import abspath
from subprocess import Popen, run


def run_test(file):
    file = abspath(file)
    command = 'coverage run --parallel-mode "%s"' % file
    return Popen(command)

if __name__ == '__main__':
    files = filter(lambda x: x.startswith('test_'), listdir('.'))
    files = list(map(run_test, files))
    files = list(map(lambda x: x.communicate(), files))

    run('coverage combine')
    run('coverage report -m')
