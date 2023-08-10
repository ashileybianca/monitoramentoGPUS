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

def parse_gpu_info(output):
    gpu_list = []
    lines = output.strip().split('\n')
    for line in lines:
        values = line.split(', ')
        gpu = {
            'Index': int(values[0]),
            'Name': values[1],
            'UUID': values[2],
            'Temperature': values[3].replace('°C', ''),
            'Fan Speed': values[4].replace(' %', ''),
            'Power Draw': values[5].replace(' W', ''),
            'Power Limit': values[6].replace(' W', ''),
            'Memory Used': values[7].split()[0],
            'Memory Total': values[8].split()[0]
        }
        gpu_list.append(gpu)
    return gpu_list

def find_peak_values(gpu_data, peak_values):
    timestamp = gpu_data[0]['Timestamp']

    for gpu in gpu_data:
        gpu_index = gpu['Index']
        if gpu_index not in peak_values:
            peak_values[gpu_index] = {
                'Temperature': {'Value': gpu['Temperature'], 'Time': timestamp},
                'Fan Speed': {'Value': gpu['Fan Speed'], 'Time': timestamp},
                'Power Draw': {'Value': gpu['Power Draw'], 'Time': timestamp},
            }
        else:
            if gpu['Temperature'] > peak_values[gpu_index]['Temperature']['Value']:
                peak_values[gpu_index]['Temperature'] = {'Value': gpu['Temperature'], 'Time': timestamp}
            if gpu['Fan Speed'] > peak_values[gpu_index]['Fan Speed']['Value']:
                peak_values[gpu_index]['Fan Speed'] = {'Value': gpu['Fan Speed'], 'Time': timestamp}
            if gpu['Power Draw'] > peak_values[gpu_index]['Power Draw']['Value']:
                peak_values[gpu_index]['Power Draw'] = {'Value': gpu['Power Draw'], 'Time': timestamp}
    return peak_values

output_filename = "gpu_logs.txt"

def main():
    peak_values = {}
    while True:
        timestamp, output = get_gpu_info()
        if output is not None:
            gpu_info = parse_gpu_info(output)
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

            # Check for errors in GPU values
            for gpu in gpu_info:
                if not gpu['Temperature'].isdigit() or not gpu['Fan Speed'].isdigit() or not gpu['Power Draw'].replace('.', '', 1).isdigit():
                    formatted_output += f"\nERROR in GPU-{gpu['Index']} ({gpu['Name']}) values at {timestamp}\n"

            peak_values = find_peak_values(gpu_info, peak_values)

            formatted_output += f"\nPEAK VALUES (until Timestamp: {timestamp}):\n"
            for gpu, values in peak_values.items():
                formatted_output += f"\nGPU {gpu} ({gpu_info[gpu]['Name']}):\n"
                formatted_output += f"  UUID: {gpu_info[gpu]['UUID']}\n"
                formatted_output += f"  Temperature: {values['Temperature']['Value']}°C (Time: {values['Temperature']['Time']})\n"
                formatted_output += f"  Fan Speed: {values['Fan Speed']['Value']} % (Time: {values['Fan Speed']['Time']})\n"
                formatted_output += f"  Power Draw: {values['Power Draw']['Value']} W (Time: {values['Power Draw']['Time']})\n"

            # Write the formatted output to the file
            with open(output_filename, "a") as log_file:
                log_file.write(formatted_output)

        time.sleep(120)

if __name__ == "__main__":
    main()
