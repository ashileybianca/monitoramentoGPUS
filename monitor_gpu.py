from datetime import datetime
import subprocess
import time

# Dicionário para armazenar os dados históricos das GPUs
gpu_historic_data = {}

# Lista para armazenar os timestamps
timestamps = []

# Lista para armazenar erros históricos
gpu_historic_errors = []

def is_error_already_recorded(error_type, gpu_index):
    """
    Verifica se um erro já foi registrado com base no tipo de erro e índice da GPU.
    """
    for error in gpu_historic_errors:
        if error[0] == error_type and error[2] == gpu_index:
            return True
    return False

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
    except subprocess.CalledProcessError as e:
        with open(filename, 'a') as file:
            file.write(f"Error executing 'nvidia-smi': {e}")

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
    peak_value_hour_temperature, timestamp_hour_temperature = find_peak_value(temperature_data, timestamps, POSITIONS_HOUR)
    peak_value_hour_fanspeed, timestamp_hour_fanspeed = find_peak_value(fanspeed_data, timestamps, POSITIONS_HOUR)
    peak_value_hour_power_draw, timestamp_hour_power_draw = find_peak_value(power_draw_data, timestamps, POSITIONS_HOUR)

    peak_value_day_temperature, timestamp_day_temperature = find_peak_value(temperature_data, timestamps, POSITIONS_DAY)
    peak_value_day_fanspeed, timestamp_day_fanspeed = find_peak_value(fanspeed_data, timestamps, POSITIONS_DAY)
    peak_value_day_power_draw, timestamp_day_power_draw = find_peak_value(power_draw_data, timestamps, POSITIONS_DAY)

    peak_value_week_temperature, timestamp_week_temperature = find_peak_value(temperature_data, timestamps, POSITIONS_WEEK)
    peak_value_week_fanspeed, timestamp_week_fanspeed = find_peak_value(fanspeed_data, timestamps, POSITIONS_WEEK)
    peak_value_week_power_draw, timestamp_week_power_draw = find_peak_value(power_draw_data, timestamps, POSITIONS_WEEK)

    all_info = "\n"+"=" * 50 + "\n"
    all_info += f"GPU {gpu_index}:\n"
    all_info += "\nHOUR\n"
    all_info += f"  Temperature: {peak_value_hour_temperature} (Timestamp: {timestamp_hour_temperature})\n"
    all_info += f"  Fan speed: {peak_value_hour_fanspeed} (Timestamp: {timestamp_hour_fanspeed})\n"
    all_info += f"  Power Draw: {peak_value_hour_power_draw} (Timestamp: {timestamp_hour_power_draw})\n"
    all_info += "\nDAY\n"
    all_info += f"  Temperature: {peak_value_day_temperature} (Timestamp: {timestamp_day_temperature})\n"
    all_info += f"  Fan speed: {peak_value_day_fanspeed} (Timestamp: {timestamp_day_fanspeed})\n"
    all_info += f"  Power Draw: {peak_value_day_power_draw} (Timestamp: {timestamp_day_power_draw})\n"
    all_info += "\nWEEK\n"
    all_info += f"  Temperature: {peak_value_week_temperature} (Timestamp: {timestamp_week_temperature})\n"
    all_info += f"  Fan speed: {peak_value_week_fanspeed} (Timestamp: {timestamp_week_fanspeed})\n"
    all_info += f"  Power Draw: {peak_value_week_power_draw} (Timestamp: {timestamp_week_power_draw})\n"

    # Escreva as informações no arquivo de texto
    with open(filename, 'a') as file:
        file.write(all_info)


def call_find_errors(gpu_historic_errors, hour_errors, day_errors):
    with open(filename, 'a') as file:
        file.write("\n"+"=" * 50 + "\n")
        file.write("ERRORS FOUND:\n\n")

    if len(hour_errors) == 0:
        with open(filename, 'a') as file:
            file.write("No errors found in the last hour.\n")
    else:
        print_errors(hour_errors, "HOUR")

    if len(day_errors) == 0:
        with open(filename, 'a') as file:
            file.write("No errors found in the last day.\n")
    else:
        print_errors(day_errors, "DAY")

    if len(gpu_historic_errors) == 0:
        with open(filename, 'a') as file:
            file.write("No errors found in the last week.\n")
        return
    else:
        print_errors(week_errors, "WEEK")

#Encontrando os erros de cada período:

def find_hour_errors(gpu_historic_errors, timestamps):
    candidates_hour = timestamps[-POSITIONS_HOUR:]
    hour_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_hour:
            hour_errors.append(error)

    return hour_errors

def find_day_errors(gpu_historic_errors, timestamps):
    candidates_day = timestamps[-POSITIONS_DAY:]
    day_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_day:
            day_errors.append(error)

    return day_errors

def find_week_errors(gpu_historic_errors, timestamps):
    candidates_week = timestamps[-POSITIONS_WEEK:]
    week_errors = []

    for error in gpu_historic_errors:
        if error[1] in candidates_week:
            week_errors.append(error)

    return week_errors

def print_errors(errors_array, time_frame):
    with open(filename, 'a') as file:
        file.write(f"LAST {time_frame}\n")

        for error in errors_array:
            error_type = error[0]
            timestamp = error[1]
            gpu_index = error[2]
            file.write(f"  GPU Index: {gpu_index}, Error Type: {error_type}, Timestamp: {timestamp}\n")

if __name__ == "__main__":

    POSITIONS_WEEK = 2017 # Quantidade de vezes que coletamos informações em uma semana
    POSITIONS_DAY = 289 # Quantidade de vezes que coletamos informações em um dia 
    POSITIONS_HOUR = 13 # Quantidade de vezes que coletamos informações em uma hora

    hour_errors = []
    day_errors = []
    week_errors = []

    filename = "gpu_info.txt"

    while True:

        with open(filename, 'w') as file:
            pass

        timestamp, gpu_info_output = get_gpu_info()
        if timestamp and gpu_info_output:
            gpu_data = parse_gpu_info(gpu_info_output)
            for gpu in gpu_data:
                process_gpu_data(gpu, max_length=POSITIONS_WEEK)

            # Encontra e adiciona os erros nas listas 
            hour_errors = find_hour_errors(gpu_historic_errors, timestamps)
            day_errors = find_day_errors(gpu_historic_errors, timestamps)
            week_errors = find_week_errors(gpu_historic_errors, timestamps)
            
            # Imprime os erros para cada período de tempo
            call_find_errors(gpu_historic_errors, hour_errors, day_errors)

            remaining_errors = []
            for error in gpu_historic_errors:
                if error not in hour_errors and error not in day_errors and error not in week_errors:
                    continue
                remaining_errors.append(error)
            gpu_historic_errors = remaining_errors
        
        time.sleep(300)  #Coleta de 5 em 5 min
