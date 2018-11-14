from utility.path_str import get_full_path


def get_temp_image(quality, img, temp_path, file_type=".webp"):
    """

    :param quality: Compression quality
    :param img: Comparison image (PILLOW version)
    :param temp_path: Destination for temporary image
    :return: temp_file_path: Destination for temporary image
    """
    temp_file_path = get_full_path(temp_path, str(quality) + file_type)
    img.save(temp_file_path, quality=quality, optimize=True, method=6)
    return temp_file_path
