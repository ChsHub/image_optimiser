from distutils.core import setup, Extension
from utility.os_interface import get_cwd
module1 = Extension('demo',
                    sources=[get_cwd()+'/butteraugli/'+'butteraugli.cc'])
                             #get_cwd()+'/butteraugli/'+'butteraugli.h',
                             #get_cwd()+'/butteraugli/'+'butteraugli_main.cc'])

setup(name='PackageName',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
