from re import findall

from utility.os_interface import read_file_data, get_dir_list

log = get_dir_list('../image_optimiser/log_files')
data = read_file_data(log[-1])
data = findall(r'EXE TIME: (\d+)', data)
data = list(map(float, data))
print(sum(data)/len(data))