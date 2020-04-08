"""
TODO Accept input and filter wrong arguments.
"""
from logging import info
from os import cpu_count
from os import walk
from os.path import isdir, isfile, split, abspath

from logger_default import Logger
from timerpy import Timer

from image_optimiser.runner import convert


def _add_images(path_list, depth_search):
    result = []

    for path in path_list:
        if type(path) == str:
            # Strip possible parenthesis
            path = path.strip('"').strip("'").strip("/")
            path = abspath(path)
            if isdir(path):
                # Find all files
                for root, _, files in walk(path):
                    for file in files:
                        result.append((root, file))
                    if not depth_search:
                        break

            elif isfile(path):
                result.append(split(path))
        elif type(path) == tuple:
            result.append(path)
    return result


def optimise(image_input, types: (str,) = (".jpg", ".png", ".jpeg", ".bmp"), new_type: str = '.webp',
             depth_search: bool = True, direct_delete: bool = False, log_file: str = None,
             processes: int = cpu_count() // 2):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param image_input: Path, or list of paths of target directory, or image
    :param types: Allowed types of input images. (Must be supported by PILLOW)
    :param new_type: Type of output images. (Must be supported by PILLOW and have quality range of 1 to 100. -> .webp or .jpg)
    :param depth_search: Search in sub-directories for images.
    :param direct_delete: If True instantly delete old images. If False move old images to the recycle bin
    :param log_file: Logging file path string.
    :param processes: Number of parallel processes, that run the image optimization. More processes might block other
                      programs and use more memory.
    """

    if type(image_input) in [str, tuple]:
        image_input = [image_input]

    if type(image_input) == list:
        images = _add_images(image_input, depth_search)
        convert(images, direct_delete=direct_delete, log_file=log_file, processes=processes, types=types,
                new_type=new_type)
    else:
        info('Input invalid.')
        return


def init():
    if __name__ == "__main__":
        with Logger(10, debug=False) as logger:
            with Timer('Run-time', log_function=info):
                # Create argument parser
                # parser = ArgumentParser(description='Process some integers.')

                # Input loop
                s_input = True
                while s_input:
                    s_input = input('OPTIMISE PATH: ')
                    info('INPUT: ' + s_input)
                    optimise(s_input, log_file=logger.log_name)


init()
