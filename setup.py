from distutils.core import setup
import setuptools

setup(
    name='image_optimiser',
    version='0.2dev',
    description='Optimise image size',
    author='Christian',
    author_email='christian1193@web.com',
    packages=['image_optimiser'],
    license='MIT License',
    classifiers=['Programming Language :: Python :: 3.6'],
    install_requires=['Cython', 'pillow', 'utility']
    # http://scikit-image.org/docs/dev/install.html
    # python.exe -m pip install scikit-image
)
