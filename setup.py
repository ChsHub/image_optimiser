from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='image_optimiser',
    version='0.2dev',
    description='Optimise image size',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Christian',
    author_email='christian1193@web.com',
    packages=['image_optimiser'],
    license='MIT License',
    classifiers=['Programming Language :: Python :: 3.6'],
    install_requires=['SSIM-PIL', 'pillow', 'utility']
)
