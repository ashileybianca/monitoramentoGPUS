import subprocess
from datetime import datetime
import time

# Inicializa os dicionários de métricas para cada período
metrics = {
    'Temperature': {
        'Hour': {0: [], 1: [], 2: []},
        'Day': {0: [], 1: [], 2: []},
        'Week': {0: [], 1: [], 2: []}
    },
    'Fan Speed': {
        'Hour': {0: [], 1: [], 2: []},
        'Day': {0: [], 1: [], 2: []},
        'Week': {0: [], 1: [], 2: []}
    },
    'Power Draw': {
        'Hour': {0: [], 1: [], 2: []},
        'Day': {0: [], 1: [], 2: []},
        'Week': {0: [], 1: [], 2: []}
    }
}

# Inicializa os dicionários de picos para cada período
peak_values_hour = {
    0: {'Temperature': {'Value': 0, 'Time': None}, 'Fan Speed': {'Value': 0, 'Time': None}, 'Power Draw': {'Value': 0, 'Time': None}},
    1: {'Temperature': {'Value': 0, 'Time': None}, 'Fan Speed': {'Value': 0, 'Time': None}, 'Power Draw': {'Value': 0, 'Time': None}},
    2: {'Temperature': {'Value': 0, 'Time': None}, 'Fan Speed': {'Value': 0, 'Time': None}, 'Power Draw': {'Value': 0, 'Time': None}}
}

peak_values_day = {
    0: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0},
    1: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0},
    2: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0}
}

peak_values_week = {
    0: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0},
    1: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0},
    2: {'Temperature': 0, 'Fan Speed': 0, 'Power Draw': 0}
}

def get_gpu_info():
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        gpu_index = int(values[0])
        gpu = {
            'Index': gpu_index,
            'Name': values[1],
            'UUID': values[2],
            'Temperature': int(values[3].replace('°C', '')),
            'Fan Speed': int(values[4].replace(' %', '')),
            'Power Draw': float(values[5].replace(' W', '')),
            'Power Limit': float(values[6].replace(' W', '')),
            'Memory Used': int(values[7].split()[0]),
            'Memory Total': int(values[8].split()[0]),
            'Timestamp': None
        }
        gpu_list.append(gpu)
    return gpu_list

def find_peak_values(gpu_data, peak_values, timestamp):
    for gpu in gpu_data:
        gpu_index = gpu['Index']
        timestamp = gpu['Timestamp']
        temperature = gpu['Temperature']
        fan_speed = gpu['Fan Speed']
        power_draw = gpu['Power Draw']
        
        if len(metrics['Temperature']['Hour'][gpu_index]) <= 3:
            candidates_hour_temp = metrics['Temperature']['Hour'][gpu_index][-3:]
            max_candidate_hour_temp = max(candidates_hour_temp)
            peak_values_hour[gpu_index]['Temperature']['Value'] = max_candidate_hour_temp
            peak_values_hour[gpu_index]['Temperature']['Time'] = timestamp

        # Atualização de picos para o período de dia
        if len(metrics['Temperature']['Day'][gpu_index]) <= 289:
            candidates_day_temp = metrics['Temperature']['Day'][gpu_index][-289:]
            max_candidate_day_temp = max(candidates_day_temp)
            peak_values_day[gpu_index]['Temperature'] = max_candidate_day_temp

        # Atualização de picos para o período de semana
        if len(metrics['Temperature']['Week'][gpu_index]) <= 2024:
            candidates_week_temp = metrics['Temperature']['Week'][gpu_index][-2024:]
            max_candidate_week_temp = max(candidates_week_temp)
            peak_values_week[gpu_index]['Temperature'] = max_candidate_week_temp

        if len(metrics['Fan Speed']['Hour'][gpu_index]) <= 3:
            candidates_hour_fan = metrics['Fan Speed']['Hour'][gpu_index][-3:]
            max_candidate_hour_fan = max(candidates_hour_fan)
            peak_values_hour[gpu_index]['Fan Speed']['Value'] = max_candidate_hour_fan
            peak_values_hour[gpu_index]['Fan Speed']['Time'] = timestamp

        # Atualização de picos para o período de dia
        if len(metrics['Fan Speed']['Day'][gpu_index]) <= 289:
            candidates_day_fan = metrics['Fan Speed']['Day'][gpu_index][-289:]
            max_candidate_day_fan = max(candidates_day_fan)
            peak_values_day[gpu_index]['Fan Speed'] = max_candidate_day_fan

        # Atualização de picos para o período de semana
        if len(metrics['Fan Speed']['Week'][gpu_index]) <= 2024:
            candidates_week_fan = metrics['Fan Speed']['Week'][gpu_index][-2024:]
            max_candidate_week_fan = max(candidates_week_fan)
            peak_values_week[gpu_index]['Fan Speed'] = max_candidate_week_fan

def main():
    output_filename = "gpu_logs.txt"

    while True:
        timestamp, output = get_gpu_info()
        if output is not None:
            gpu_info = parse_gpu_info(output)

            for gpu in gpu_info:
                gpu['Timestamp'] = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            find_peak_values(gpu_info, peak_values_hour, timestamp)

            formatted_output = f"=================================================\n"
            formatted_output += f"GPU Information (Timestamp: {timestamp}):\n"
            for gpu in gpu_info:
                formatted_output += f"\nGPU-{gpu['Index']} ({gpu['Name']}):\n"
                formatted_output += f"  UUID: {gpu['UUID']}\n"
                formatted_output += f"  Temperature: {gpu['Temperature']}°C\n"
                formatted_output += f"  Fan Speed: {gpu['Fan Speed']} %\n"
                formatted_output += f"  Power Draw: {gpu['Power Draw']} W\n"
                formatted_output += f"  Memory Used: {gpu['Memory Used']} MiB\n"

            # Printa picos de hora
            formatted_output += f"\nPEAK VALUES (until Timestamp: {timestamp}):\n"
            formatted_output += f"\nPeak 1h:\n"
            for gpu, values in peak_values_hour.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']['Value']}°C\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']['Value']} %\n"
                formatted_output += f"  Power Draw: {values['Power Draw']['Value']} W\n"
                formatted_output += f"    Time: {values['Power Draw']['Time']}\n"

            # Printa picos de dia
            formatted_output += f"\nPeak 24h:\n"
            for gpu, values in peak_values_day.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']}°C\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']} %\n"
                formatted_output += f"  Power Draw: {values['Power Draw']} W\n"

            # Printa picos de semana
            formatted_output += f"\nPeak 1w:\n"
            for gpu, values in peak_values_week.items():
                formatted_output += f"\nGPU-{gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']}°C\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']} %\n"
                formatted_output += f"  Power Draw: {values['Power Draw']} W\n"

            # Write the formatted output to the file
            with open(output_filename, "a") as log_file:
                log_file.write(formatted_output)

        time.sleep(30)  # Sleep for 5 minutes (300 seconds)

if __name__ == "__main__":
    main()
