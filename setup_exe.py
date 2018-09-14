from subprocess import Popen
from utility.os_interface import read_file_data, write_file_data, delete_file

text_view_title = 'image optimiser'
icon_path = 'icon.ico'

delete_file(text_view_title + ".spec")

Popen('pyinstaller "__main__.py"  --noconfirm --onedir --noconsole --name "' + text_view_title +
      '" --icon "' + icon_path + '"').communicate()

spec_data = read_file_data(text_view_title + ".spec")
spec_data = spec_data.replace('datas=[',
                              "datas=[('artist_path.cfg', '.'),('icon.ico', '.')")
write_file_data(".", text_view_title + ".spec", spec_data)

Popen('pyinstaller "' + text_view_title + '.spec"  --noconfirm').communicate()
delete_file(text_view_title + ".spec")
