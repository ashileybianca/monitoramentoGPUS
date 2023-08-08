import subprocess
import time

def collect_gpu_info():
    try:
        output = subprocess.check_output(['nvidia-smi'], universal_newlines=True)
        return output

    except Exception as e:
        print("Error: ", e)
        return None

print(collect_gpu_info())

