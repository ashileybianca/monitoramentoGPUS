import subprocess
from datetime import datetime

def get_gpu_info():
    try:
        # Obter o horário da consulta usando o comando date
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
        gpu = {
            'Index': values[0],
            'Name': values[1],
            'UUID': values[2],
            'Temperature': values[3] + '°C',
            'Fan Speed': values[4],
            'Power Draw': values[5],
            'Power Limit': values[6],
            'Memory Used': values[7],
            'Memory Total': values[8]
        }
        gpu_list.append(gpu)
    return gpu_list

timestamp, output = get_gpu_info()
if output is not None:
    gpu_info = parse_gpu_info(output)

    print("=================================================")
    print(f"GPU Information (Timestamp: {timestamp}):")
    print()
    for gpu in gpu_info:
        print(f"GPU-{gpu['Index']} ({gpu['Name']}):")
        print(f"  UUID: {gpu['UUID']}")
        print(f"  Temperature: {gpu['Temperature']}")
        print(f"  Fan Speed: {gpu['Fan Speed']}")
        print(f"  Power Draw: {gpu['Power Draw']} / Power Limit: {gpu['Power Limit']}")
        print(f"  Memory Used: {gpu['Memory Used']} / Memory Total: {gpu['Memory Total']}")
        print()
