from distutils.core import setup

setup(
    name='image_optimiser',
    version='1.0',
    description='Optimise image size',
    author='Christian',
    author_email='christian1193@web.com',
    packages=['image_optimiser'],
    install_requires=['scikit-image', 'opencv-python', 'numpy', 'Cython', 'utility', 'pillow']
    # http://scikit-image.org/docs/dev/install.html
)
