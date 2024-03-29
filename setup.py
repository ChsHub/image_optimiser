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
    packages=['image_optimiser'],
    license='MIT License',
    classifiers=['Programming Language :: Python :: 3.7'],
    install_requires=['SSIM-PIL', 'pillow', 'format-byte', 'send2trash', 'timerpy', 'logger-default']
)
# C:\Python38\python.exe -m pip install . --upgrade