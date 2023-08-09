import subprocess
from datetime import datetime
import time
import re

def get_gpu_info():
    try:
        timestamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S'], universal_newlines=True).strip()

        command = [
            'nvidia-smi', 
            '--query-gpu=index,name,uuid,temperature.gpu,fan.speed,power.draw,power.limit,memory.used,memory.total',
            '--format=csv,noheader'
        ]
        output = subprocess.check_output(command, universal_newlines=True)
        return timestamp, output
    except Exception as e:
        print("Error:", e)
        return None, None

def parse_gpu_info(output):
    gpu_list = []
    lines = output.strip().split('\n')
    for line in lines:
        values = line.split(', ')
        temperature_str = re.findall(r'\d+', values[3])[0]  # Extrair o primeiro número da string
        gpu = {
            'Index': int(values[0]),
            'Name': values[1],
            'UUID': values[2],
            'Temperature': int(temperature_str),
            'Fan Speed': int(values[4].split()[0]),
            'Power Draw': float(values[5].split()[0]),
            'Power Limit': float(values[6].split()[0]),
            'Memory Used': int(values[7].split()[0]),
            'Memory Total': int(values[8].split()[0])
        }
        gpu_list.append(gpu)
    return gpu_list

while True:
    timestamp, output = get_gpu_info()
    if output is not None:
        gpu_info = parse_gpu_info(output)

        with open('gpu_info.txt', 'a') as file:
            file.write("=================================================\n")
            file.write(f"GPU Information (Timestamp: {timestamp}):\n\n")
            for gpu in gpu_info:
                file.write(f"GPU-{gpu['Index']} ({gpu['Name']}):\n")
                file.write(f"  UUID: {gpu['UUID']}\n")
                file.write(f"  Temperature: {gpu['Temperature']}°C\n")
                file.write(f"  Fan Speed: {gpu['Fan Speed']} %\n")
                file.write(f"  Power Draw: {gpu['Power Draw']} W / Power Limit: {gpu['Power Limit']} W\n")
                file.write(f"  Memory Used: {gpu['Memory Used']} MiB / Memory Total: {gpu['Memory Total']} MiB\n\n")

    time.sleep(300)  # 5 minutos
    filename = 'gpu_info.txt'
    gpu_data = load_data(filename)
    peak_values = find_peak_values(gpu_data)

    for gpu, values in peak_values.items():
        print(f"GPU {gpu} - Peak Values:")
        print(f"  Temperature: {values['Temperature']}°C")
        print(f"  Fan Speed: {values['Fan Speed']} %")
        print(f"  Power Draw: {values['Power Draw']} W")
        print(f"  Memory Used: {values['Memory Used']} MiB")
        print()
