import subprocess
import time
import re

def collect_gpu_info():
    try:
        output = subprocess.check_output(['nvidia-smi'], universal_newlines=True)
        return output
    except Exception as e:
        print("Error:", e)
        return None

def extract_gpu_info(gpu_info):

    for caractere in gpu_info:

        match = re.match(r'(\d+%) +(\d+)C +(\d+)W / (\d+)W +(\d+)MiB / (\d+)MiB')
        if match:
            fan, temp, pwr_usage, _, mem_used = match.groups()
            print("Fan:", fan)
            print("Temperature:", temp)
            print("Power Usage:", pwr_usage)
            print("Memory Used:", mem_used)
            gpu_data.append((gpu_name, fan, temp, pwr_usage, mem_used))

    return gpu_data

print(extract_gpu_info(collect_gpu_info()))
