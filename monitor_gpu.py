from datetime import datetime
import subprocess
import time

# Dicionário para armazenar os dados históricos das GPUs
gpu_historic_data = {}

# Lista para armazenar os timestamps
timestamps = []

# Lista para armazenar erros históricos
gpu_historic_errors = []

hour_errors = []
day_errors = []
week_errors = []

def is_error_already_recorded(error_type, gpu_index):
    """
    Verifica se um erro já foi registrado com base no tipo de erro e índice da GPU.
    """
    for error in gpu_historic_errors:
        if error[0] == error_type and error[2] == gpu_index:
            return True
    return False

#Essa parte está comentada pois estamos usando a simulação para poder testar os erros.
'''
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
'''

#Simulando a função que está comentada
def get_gpu_info():
    """
    Simula a obtenção de informações das GPUs e retorna um timestamp e a saída simulada.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = """0, NVIDIA RTX A6000, GPU-0472e0b4-22a5-992d-e99a-b924703a82f7, [Unknown Error], [Unknown Error], [Unknown Error], 300.00 W, 6 MiB, 49140 MiB
1, NVIDIA RTX A6000, GPU-ec5ae7f5-28ec-d423-7a74-f1a00dd8f3ec, 32, [Unknown Error], 25.02 W, 300.00 W, 6 MiB, 49140 MiB
2, NVIDIA RTX A6000, GPU-0857e97c-1ba2-bf16-fd11-b29740d305f6, [Unknown Error], 30 %, 15.47 W, 300.00 W, 6 MiB, 49140 MiB
3, NVIDIA RTX A6000, GPU-d5f30760-8d84-ad72-4544-201d3476aaf0, 34, [Unknown Error],[Unknown Error], 300.00 W, 6 MiB, 49140 MiB
4, NVIDIA RTX A6000, GPU-88d64245-6778-a3c6-ee0b-d11d8834a714, [Unknown Error], [Unknown Error], 26.83 W, 300.00 W, 6 MiB, 49140 MiB"""
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
        except (IndexError, ValueError) as e:
            error_type = "Temperature Conversion Error"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not is_error_already_recorded(error_type, gpu_index):
                gpu_historic_errors.append((error_type, timestamp, gpu_index))
                temperature = -1
            continue

        try:
            fanspeed = int(values[4].replace(' %', ''))
        except (IndexError, ValueError) as e:
            error_type = "Fan Speed Conversion Error"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not is_error_already_recorded(error_type, gpu_index):
                gpu_historic_errors.append((error_type, timestamp, gpu_index))
            fanspeed =  -1
        try:
            power_draw = float(values[5].replace(' W', ''))
        except (IndexError, ValueError) as e:
            error_type = "Power Draw Conversion Error"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not is_error_already_recorded(error_type, gpu_index):
                gpu_historic_errors.append((error_type, timestamp, gpu_index))
            power_draw = -1

        gpu = {
            'Index': gpu_index,
            'Name': values[1],
            'UUID': values[2],
            'Temperature': temperature,
            'Fan Speed': fanspeed,
            'Power Draw': power_draw,
            'Memory Used': int(values[7].split()[0]),
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

def find_hour_errors(gpu_historic_errors, timestamps):
    candidates_hour = timestamps[-2:]
    hour_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_hour:
            hour_errors.append(error)

    return hour_errors

def find_day_errors(gpu_historic_errors, timestamps):
    candidates_day = timestamps[-5:]
    day_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_day:
            day_errors.append(error)

    return day_errors

def find_week_errors(gpu_historic_errors, timestamps):
    candidates_week = timestamps[-10:]
    week_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_week:
            week_errors.append(error)

    return week_errors

def print_errors(errors_array, time_frame):
    print(f"LAST {time_frame} \n")

    for error in errors_array:
        error_type = error[0]
        timestamp = error[1]
        gpu_index = error[2]
        print(f"  Error Type: {error_type}, Timestamp: {timestamp}, GPU Index: {gpu_index}")

    print()

if __name__ == "__main__":
    # Inicialize as listas antes do loop principal
    hour_errors = []
    day_errors = []
    week_errors = []

    while True:
        timestamp, gpu_info_output = get_gpu_info()
        if timestamp and gpu_info_output:
            gpu_data = parse_gpu_info(gpu_info_output)
            for gpu in gpu_data:
                process_gpu_data(gpu, max_length=10)

            # Encontre e adicione os erros nas listas apropriadas
            hour_errors = find_hour_errors(gpu_historic_errors, timestamps)
            day_errors = find_day_errors(gpu_historic_errors, timestamps)
            week_errors = find_week_errors(gpu_historic_errors, timestamps)
            
            # Imprima os erros para cada período de tempo
            print_errors(hour_errors, "HOUR")
            print_errors(day_errors, "DAY")
            print_errors(week_errors, "WEEK")
            print()

            # Verifique se os erros não estão mais em nenhum dos períodos e remova-os do histórico
            remaining_errors = []
            for error in gpu_historic_errors:
                if error not in hour_errors and error not in day_errors and error not in week_errors:
                    continue
                remaining_errors.append(error)
            gpu_historic_errors = remaining_errors

            #PRINTS SOMENTE PARA TESTE DO CODIGO!
            print("hour --",hour_errors)
            print("day --",day_errors)
            print("week --",week_errors)
            print()
            print(gpu_historic_errors)
            print(timestamps)
        time.sleep(2)  # Aguarda 10 segundos
