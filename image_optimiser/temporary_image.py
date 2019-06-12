from multiprocessing import freeze_support

from os.path import join


def get_temp_image(quality:int, image, temp_path:str, file_type:str= ".webp") -> str:
    """
    Save temporary image with specified quality setting.
    :param quality: Compression quality
    :param image: Comparison image (PILLOW version)
    :param temp_path: Destination for temporary image
    :param file_type: File type for new image (PIL allows jpg or webp with 1 to 100 quality setting)
    :return: temp_file_path: Destination for temporary image
    """
    temp_file_path = join(temp_path, str(quality) + file_type)
    image.save(temp_file_path, quality=quality, optimize=True, method=6)
    return temp_file_path

if __name__ == "__main__":
    freeze_support()