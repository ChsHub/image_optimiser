from re import findall

from utility.os_interface import read_file_data, get_dir_list
path = '../image_optimiser/log_files'
log = get_dir_list(path)
data = read_file_data(path, log[-1])
data = findall(r'EXE TIME: (\d+)', data) # TODO BUG get EXE only for SSIM
data = list(map(float, data))
print(sum(data)/len(data))