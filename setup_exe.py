from subprocess import Popen
from utility.os_interface import read_file_data, write_file_data, delete_file, exists, get_absolute_path

text_view_title = 'image optimiser'
icon_path = 'icon.ico'
path = get_absolute_path("image_optimiser/__main__.py")
if not exists(text_view_title + ".spec"):
    Popen('pyinstaller "' + path + '"  --onedir --debug --noconfirm --name "' + text_view_title +
          '" --icon "' + icon_path + '"').communicate()

    spec_data = read_file_data(text_view_title + ".spec")
    spec_data = spec_data.replace('datas=[',
                                  "datas=[('icon.ico', '.')")
    spec_data = spec_data.replace('excludes=[]',
                                  "excludes=[]")
    write_file_data(".", text_view_title + ".spec", spec_data)

print('pyinstaller "' + text_view_title + '.spec"  --noconfirm')
Popen('pyinstaller "' + text_view_title + '.spec"  --noconfirm').communicate()
# delete_file(text_view_title + ".spec")
