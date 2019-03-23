"""
Accept input and filter wrong arguments.
"""

from logging import info, exception
from os import cpu_count
from os import walk

from PIL.Image import Image
from os.path import isdir, isfile, join, splitext, split
from utility.logger import Logger

from image_optimiser.runner import convert


def accept_file(path: str, file_name: str, trash_directory: str, types: list) -> bool:
    """
    Test if file is of right type and not already converted
    :param path: Image path
    :param file_name: Image file name
    :param trash_directory: Path for old images
    :param types: Acceptable image types
    :return: True if convertable or false if not
    """
    if path.endswith(trash_directory):
        info('%s already compressed' % file_name)
        return False

    # TODO Should this be removed?
    elif isdir(join(path, trash_directory)):
        # If image in TRASH, then don't compress again
        file_name, _ = splitext(file_name) # TODO upper and lower
        for extension in types:
            if isfile(join(path, trash_directory, file_name + extension)):
                return False

    return True


def optimise(image_input, types=(".jpg", ".png", ".jpeg"), new_type: str = '.webp', depth_search: bool = True,
             direct_delete: bool = False, trash_directory='TRASH', log_file: str = None,
             processes: int = cpu_count() // 2):
    """
    Optimize images for smaller sizes in directory and sub-directories. May convert to jpg or webp.
    :param image_input: PILLOW image object, or path of target directory, or image
    :param types: Allowed types of input images. (Must be supported by PILLOW)
    :param new_type: Type of output images. (Must be supported by PILLOW and have quality range of 1 to 100. -> .webp or .jpg)
    :param depth_search: Search in sub-directories for images.
    :param direct_delete: If True instantly delete old images. If False move old images to a new folder called "TRASH"
    :param trash_directory: Directory name for moving old files, if direct_delete is enabled.
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
                    if not root.endswith(trash_directory): # Exclude trash directory
                        for file in files:
                            if accept_file(root, file, trash_directory, types):
                                images.append((root, file))

                    if not depth_search:
                        break
            elif isfile(path):
                root, file = split(path)
                if accept_file(root, file, trash_directory, types):
                    images.append((root, file))

            else:
                raise AttributeError('Path not found.')

        elif type(image_input) == Image:
            raise NotImplementedError # TODO
        else:
            raise AttributeError('Input invalid.')

        convert(images, direct_delete, log_file, processes, types)

    except Exception as e:
        exception(e)


def init():
    if __name__ == "__main__":
        with Logger(10) as logger:
            s_input = True
            while s_input:
                s_input = input('OPTIMISE PATH: ')
                info('INPUT: ' + s_input)
                optimise(s_input, log_file=logger.log_name)


init()

# TODO transparancy for webp
