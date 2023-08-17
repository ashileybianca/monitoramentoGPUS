import subprocess
from datetime import datetime
import time

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

def parse_gpu_info(output, elapsed_time):
    gpu_list = []
    lines = output.strip().split('\n')
    for line in lines:
        values = line.split(', ')
        gpu = {
            'Index': int(values[0]),
            'Name': values[1],
            'UUID': values[2],
            'Temperature': int(values[3].replace('°C', '')),
            'Fan Speed': int(values[4].replace(' %', '')),
            'Power Draw': float(values[5].replace(' W', '')),
            'Power Limit': float(values[6].replace(' W', '')),
            'Memory Used': int(values[7].split()[0]),
            'Memory Total': int(values[8].split()[0]),
            'Elapsed Time': elapsed_time  # Armazena o tempo decorrido desde a última coleta
        }
        gpu_list.append(gpu)
    return gpu_list

def find_peak_values(gpu_data, peak_values):
    timestamp = gpu_data[0]['Timestamp']

    for gpu in gpu_data:
        gpu_index = gpu['Index']
        elapsed_time = gpu['Elapsed Time']
        
        # Adiciona tempo aos valores de pico a cada iteração
        if elapsed_time <= 604800:  # Uma semana
            elapsed_time += 300
        
        # Armazena os valores nas listas de informações para cada intervalo de tempo
        if elapsed_time <= 3600:  # Última hora
            metrics['Temperature'][gpu_index].append((gpu['Temperature'], timestamp, elapsed_time))
            metrics['Fan Speed'][gpu_index].append((gpu['Fan Speed'], timestamp, elapsed_time))
            metrics['Power Draw'][gpu_index].append((gpu['Power Draw'], timestamp, elapsed_time))
        
        if elapsed_time <= 86400:  # Último dia
            metrics_24h['Temperature'][gpu_index].append((gpu['Temperature'], timestamp, elapsed_time))
            metrics_24h['Fan Speed'][gpu_index].append((gpu['Fan Speed'], timestamp, elapsed_time))
            metrics_24h['Power Draw'][gpu_index].append((gpu['Power Draw'], timestamp, elapsed_time))
        
        if elapsed_time <= 604800:  # Última semana
            metrics_1w['Temperature'][gpu_index].append((gpu['Temperature'], timestamp, elapsed_time))
            metrics_1w['Fan Speed'][gpu_index].append((gpu['Fan Speed'], timestamp, elapsed_time))
            metrics_1w['Power Draw'][gpu_index].append((gpu['Power Draw'], timestamp, elapsed_time))

        # Atualiza os valores de pico
        if gpu_index not in peak_values:
            peak_values[gpu_index] = {
                'Temperature': {'Value': gpu['Temperature'], 'Time': timestamp},
                'Fan Speed': {'Value': gpu['Fan Speed'], 'Time': timestamp},
                'Power Draw': {'Value': gpu['Power Draw'], 'Time': timestamp},
            }
        else:
            if gpu['Temperature'] > peak_values[gpu_index]['Temperature']['Value'] or gpu['Temperature'] == peak_values[gpu_index]['Temperature']['Value']:
                peak_values[gpu_index]['Temperature'] = {'Value': gpu['Temperature'], 'Time': timestamp}
            if gpu['Fan Speed'] > peak_values[gpu_index]['Fan Speed']['Value'] or gpu['Fan Speed'] == peak_values[gpu_index]['Fan Speed']['Value']:
                peak_values[gpu_index]['Fan Speed'] = {'Value': gpu['Fan Speed'], 'Time': timestamp}
            if gpu['Power Draw'] > peak_values[gpu_index]['Power Draw']['Value'] or gpu['Power Draw'] == peak_values[gpu_index]['Power Draw']['Value']:
                peak_values[gpu_index]['Power Draw'] = {'Value': gpu['Power Draw'], 'Time': timestamp}
    return peak_values

output_filename = "gpu_logs.txt"

# Dicionários para armazenar as informações de cada intervalo de tempo
metrics = {
    'Temperature': {0: [], 1: [], 2: []},
    'Fan Speed': {0: [], 1: [], 2: []},
    'Power Draw': {0: [], 1: [], 2: []}
}

metrics_24h = {
    'Temperature': {0: [], 1: [], 2: []},
    'Fan Speed': {0: [], 1: [], 2: []},
    'Power Draw': {0: [], 1: [], 2: []}
}

metrics_1w = {
    'Temperature': {0: [], 1: [], 2: []},
    'Fan Speed': {0: [], 1: [], 2: []},
    'Power Draw': {0: [], 1: [], 2: []}
}

def main():
    peak_values_hour = {}
    peak_values_day = {}
    peak_values_week = {}
    elapsed_time = 0

    while True:
        timestamp, output = get_gpu_info()
        if output is not None:
            gpu_info = parse_gpu_info(output, elapsed_time)
            elapsed_time += 300

            gpu_info[0]['Timestamp'] = timestamp 

            formatted_output = f"=================================================\n"
            formatted_output += f"GPU Information (Timestamp: {timestamp}):\n"
            for gpu in gpu_info:
                formatted_output += f"\nGPU-{gpu['Index']} ({gpu['Name']}):\n"
                formatted_output += f"  UUID: {gpu['UUID']}\n"
                formatted_output += f"  Temperature: {gpu['Temperature']}°C\n"
                formatted_output += f"  Fan Speed: {gpu['Fan Speed']} %\n"
                formatted_output += f"  Power Draw: {gpu['Power Draw']} W\n"
                formatted_output += f"  Memory Used: {gpu['Memory Used']} MiB\n"

            for gpu in gpu_info:
                if not isinstance(gpu['Temperature'], int) or not isinstance(gpu['Fan Speed'], int) or not isinstance(gpu['Power Draw'], float):
                    formatted_output += f"\nERROR in GPU-{gpu['Index']} ({gpu['Name']}) values at {timestamp}\n"

            peak_values_hour = find_peak_values(gpu_info, peak_values_hour)  # Última hora
            peak_values_day = find_peak_values(gpu_info, peak_values_day)    # Último dia
            peak_values_week = find_peak_values(gpu_info, peak_values_week)  # Última semana

            formatted_output += f"\nPEAK VALUES (until Timestamp: {timestamp}):\n"

            formatted_output += f"\nPeak 1h:\n"
            for gpu, values in peak_values_hour.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']['Value']}°C (Time: {values['Temperature']['Time']})\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']['Value']} % (Time: {values['Fan Speed']['Time']})\n"
                formatted_output += f"  Power Draw: {values['Power Draw']['Value']} W (Time: {values['Power Draw']['Time']})\n"

            formatted_output += f"\nPeak 24h:\n"
            for gpu, values in peak_values_day.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']['Value']}°C (Time: {values['Temperature']['Time']})\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']['Value']} % (Time: {values['Fan Speed']['Time']})\n"
                formatted_output += f"  Power Draw: {values['Power Draw']['Value']} W (Time: {values['Power Draw']['Time']})\n"

            formatted_output += f"\nPeak 1w:\n"
            for gpu, values in peak_values_week.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']['Value']}°C (Time: {values['Temperature']['Time']})\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']['Value']} % (Time: {values['Fan Speed']['Time']})\n"
                formatted_output += f"  Power Draw: {values['Power Draw']['Value']} W (Time: {values['Power Draw']['Time']})\n"

            # Write the formatted output to the file
            with open(output_filename, "a") as log_file:
                log_file.write(formatted_output)

        time.sleep(60)

if __name__ == "__main__":
    main()
    
#luana testing branch