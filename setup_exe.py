from subprocess import Popen
from utility.os_interface import read_file_data, write_file_data, delete_file, exists, get_absolute_path
from utility.setup_lib import setup_exe

text_view_title = 'image optimiser'
icon_path = get_absolute_path('icon.ico')
path = get_absolute_path("image_optimiser/__main__.py")
setup_exe(main_path=path, app_name=text_view_title, icon_path=icon_path, options='--console')
