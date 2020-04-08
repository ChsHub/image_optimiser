from os.path import abspath

from utility.setup_lib import setup_exe

text_view_title = 'image optimiser'
icon_path = abspath('icon.ico')
path = abspath("image_optimiser/__main__.py")
setup_exe(main_path=path, app_name=text_view_title, icon_path=icon_path, options='--console')
