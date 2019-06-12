"""
Accept input and filter wrong arguments.
"""

from logging import info, exception
from multiprocessing import freeze_support
from os import cpu_count
from os import walk

from PIL.Image import Image
from os.path import isdir, isfile, join, splitext, split
from utility.logger import Logger

from image_optimiser.runner import convert


def optimise(image_input, types=(".jpg", ".png", ".jpeg", ".bmp"), new_type: str = '.webp', depth_search: bool = True,
             direct_delete: bool = False, log_file: str = None,
             processes: int = cpu_count() // 2):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param image_input: Path of target directory, or image, or list of image paths
    :param types: Allowed types of input images. (Must be supported by PILLOW)
    :param new_type: Type of output images. (Must be supported by PILLOW and have quality range of 1 to 100. -> .webp or .jpg)
    :param depth_search: Search in sub-directories for images.
    :param direct_delete: If True instantly delete old images. If False move old images to a new folder called "TRASH"
    :param log_file: Logging file path string.
    :param processes: Number of parallel processes, that run the image optimization. More processes might block other
                      programs and use more memory.
    """
    images = []

    # Log unexpected exceptions
    try:
        if type(image_input) == str:
            # Strip possible parenthesis
            path = image_input.strip('"').strip("'")

            if isdir(path):
                # Find all files
                for root, _, files in walk(path):
                    for file in files:
                        images.append((root, file))
                    if not depth_search:
                        break
            elif isfile(path):
                root, file = split(path)
                images.append((root, file))

            else:
                raise AttributeError('Path not found.')

        elif type(image_input) == Image:
            raise NotImplementedError  # TODO
        elif type(image_input) == list:
            for root, file in image_input:
                images.append((root, file))

        else:
            raise AttributeError('Input invalid.')

        convert(images, direct_delete=direct_delete, log_file=log_file, processes=processes, types=types,
                new_type=new_type)

    except Exception as e:
        exception(e)


def init():
    if __name__ == "__main__":
        freeze_support()
        with Logger(10, debug=False) as logger:
            s_input = True
            while s_input:
                s_input = input('OPTIMISE PATH: ')
                info('INPUT: ' + s_input)
                optimise(s_input, log_file=logger.log_name)


init()
if __name__ == "__main__": # TODO remove all freeze support
    freeze_support()
