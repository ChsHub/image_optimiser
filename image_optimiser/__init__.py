from multiprocessing import freeze_support

from .__main__ import optimise

__all__ = ['optimise']
__name__ = 'image_optimiser'
__version__ = '3.0.6.dev0'

if __name__ == "__main__":
    freeze_support()