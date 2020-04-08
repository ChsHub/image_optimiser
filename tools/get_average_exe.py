from os import listdir
from os.path import join
from re import findall

path = '../image_optimiser/log_files'
log = listdir(path)
with open(join(path, log[-1]), 'r') as f:
    data = f.read()
data = findall(r'EXE TIME: (\d+)', data)  # TODO BUG get EXE only for SSIM
data = list(map(float, data))
print(sum(data) / len(data))
