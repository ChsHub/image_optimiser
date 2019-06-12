import setuptools
from distutils.core import setup
from image_optimiser import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='image_optimiser',
    version=__version__,
    description='Optimise image size',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='ChsHub',
    author_email='christian1193@web.com',
    packages=['image_optimiser'],
    license='MIT License',
    classifiers=['Programming Language :: Python :: 3.7'],
    install_requires=['SSIM-PIL', 'pillow', 'utility']
)
# C:\Python37\python.exe -m pip install . --upgrade