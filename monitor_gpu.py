import subprocess
from datetime import datetime
import time

# Dicionário para armazenar os dados históricos das GPUs
gpu_historic_data = {}

# Lista para armazenar os timestamps
timestamps = []

def get_gpu_info():
    """
    Obtém informações das GPUs usando o comando 'nvidia-smi'.
    Retorna um timestamp e a saída do comando.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        command = [
            'nvidia-smi', 
            '--query-gpu=index,name,uuid,temperature.gpu,fan.speed,power.draw,power.limit,memory.used,memory.total',
            '--format=csv,noheader'
        ]
        output = subprocess.check_output(command, universal_newlines=True)
        timestamps.append(timestamp)
        return timestamp, output
    except Exception as e:
        print("Error:", e)
        return None, None

def parse_gpu_info(output):
    """
    Analisa a saída do comando 'nvidia-smi' e retorna uma lista de dicionários com as informações das GPUs.
    """
    gpu_list = []
    lines = output.strip().split('\n')
    for line in lines:
        values = line.split(', ')
        gpu_index = int(values[0])
        
        try:
            temperature = int(values[3].replace('°C', ''))
            fanspeed = int(values[4].replace(' %', ''))
            power_draw = float(values[5].replace(' W', ''))
        except ValueError:
            print(f"Erro na GPU {gpu_index}")
            continue
        
        gpu = {
            'Index': gpu_index,
            'Name': values[1],
            'UUID': values[2],
            'Temperature': temperature,
            'Fan Speed': fanspeed,
            'Power Draw': power_draw,
            'Power Limit': float(values[6].replace(' W', '')),
            'Memory Used': int(values[7].split()[0]),
            'Memory Total': int(values[8].split()[0]),
            'Timestamp': None
        }
        gpu_list.append(gpu)
    return gpu_list

def find_last_occurrence(data, value):
    """
    Encontra a última ocorrência de um valor em uma lista.
    """
    for i in range(len(data) - 1, -1, -1):
        if data[i] == value:
            return i
    return None

def find_peak_value(data, timestamps, positions):
    """
    Encontra o valor máximo e seu timestamp correspondente.
    """
    candidates = data[-positions:]
    peak_value = max(candidates)
    
    peak_position = find_last_occurrence(data, peak_value)
    corresponding_timestamp = timestamps[peak_position]

    return peak_value, corresponding_timestamp

def process_gpu_data(gpu, max_length):
    """
    Processa os dados da GPU, mantendo um histórico de dados.
    """
    gpu_index = gpu['Index']

    if gpu_index not in gpu_historic_data:
        gpu_historic_data[gpu_index] = {
            'temperature': [],
            'fanspeed': [],
            'power_draw': []
        }

    temperature_data = gpu_historic_data[gpu_index]['temperature']
    fanspeed_data = gpu_historic_data[gpu_index]['fanspeed']
    power_draw_data = gpu_historic_data[gpu_index]['power_draw']

    temperature = gpu['Temperature']
    fanspeed = gpu['Fan Speed']
    power_draw = gpu['Power Draw']

    temperature_data.append(temperature)
    fanspeed_data.append(fanspeed)
    power_draw_data.append(power_draw)

    if len(timestamps) > max_length:
        timestamps.pop(0)

    if len(temperature_data) >= max_length:
        temperature_data.pop(0)

    if len(fanspeed_data) >= max_length:
        fanspeed_data.pop(0)

    if len(power_draw_data) >= max_length:
        power_draw_data.pop(0)

    # Encontra os valores máximos e seus timestamps correspondentes
    peak_value_hour_temperature, timestamp_hour_temperature = find_peak_value(temperature_data, timestamps, 2)
    peak_value_hour_fanspeed, timestamp_hour_fanspeed = find_peak_value(fanspeed_data, timestamps, 2)
    peak_value_hour_power_draw, timestamp_hour_power_draw = find_peak_value(power_draw_data, timestamps, 2)

    peak_value_day_temperature, timestamp_day_temperature = find_peak_value(temperature_data, timestamps, 5)
    peak_value_day_fanspeed, timestamp_day_fanspeed = find_peak_value(fanspeed_data, timestamps, 5)
    peak_value_day_power_draw, timestamp_day_power_draw = find_peak_value(power_draw_data, timestamps, 5)

    peak_value_week_temperature, timestamp_week_temperature = find_peak_value(temperature_data, timestamps, 10)
    peak_value_week_fanspeed, timestamp_week_fanspeed = find_peak_value(fanspeed_data, timestamps, 10)
    peak_value_week_power_draw, timestamp_week_power_draw = find_peak_value(power_draw_data, timestamps, 10)

    # Imprime os resultados
    print("="*50)
    print(f"GPU {gpu_index}:\n")
    print("HOUR\n")
    print(f"  Temperature: {peak_value_hour_temperature} (Timestamp: {timestamp_hour_temperature})")
    print(f"  Fan speed: {peak_value_hour_fanspeed} (Timestamp: {timestamp_hour_fanspeed})")
    print(f"  Power Draw: {peak_value_hour_power_draw} (Timestamp: {timestamp_hour_power_draw})\n")
    print("DAY\n")
    print(f"  Temperature: {peak_value_day_temperature} (Timestamp: {timestamp_day_temperature})")
    print(f"  Fan speed: {peak_value_day_fanspeed} (Timestamp: {timestamp_day_fanspeed})")
    print(f"  Power Draw: {peak_value_day_power_draw} (Timestamp: {timestamp_day_power_draw})\n")
    print("WEEK\n")
    print(f"  Temperature: {peak_value_week_temperature} (Timestamp: {timestamp_week_temperature})")
    print(f"  Fan speed: {peak_value_week_fanspeed} (Timestamp: {timestamp_week_fanspeed})")
    print(f"  Power Draw: {peak_value_week_power_draw} (Timestamp: {timestamp_week_power_draw})")
    print()
    print("="*50)

if __name__ == "__main__":
    # Loop principal para coletar e processar dados das GPUs
    while True:
        timestamp, gpu_info_output = get_gpu_info()
        if timestamp and gpu_info_output:
            gpu_data = parse_gpu_info(gpu_info_output)
            for gpu in gpu_data:
                process_gpu_data(gpu, max_length=10)
        time.sleep(10)  # Aguarda 10 segundos
