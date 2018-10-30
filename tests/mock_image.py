from tempfile import TemporaryDirectory

import Image
from utility.path_str import get_full_path


class MockImage:
    def __init__(self, name='a', size=10, extension=1, palette=0):
        types = [".jpg", ".png", ".jpeg", ".webp"]
        types += list(map(lambda x: x.upper(), types))

        if extension == 1:
            palette = ['RGB', 'RGBA', 'LA', 'L'][palette]
        else:
            palette = 'RGB'

        self.file_name = name + types[extension]
        self.size = (size, size)
        self.image = Image.new(palette, self.size, "black")

    def __enter__(self):
        self._temp_dir = TemporaryDirectory()
        self.temp_path = self._temp_dir.name


        self.full_path = get_full_path(self.temp_path, self.file_name)
        self.image.save(self.full_path)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.__exit__(exc_type, exc_val, exc_tb)
        self.image.__exit__(exc_type, exc_val, exc_tb)