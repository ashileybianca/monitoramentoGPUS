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
    """
    Obtém informações sobre as GPUs utilizando o comando 'nvidia-smi'.

    Esta função executa o comando 'nvidia-smi' para obter informações detalhadas sobre as GPUs presentes
    no sistema. As informações coletadas incluem o índice da GPU, nome, UUID, temperatura da GPU, velocidade
    do ventilador, consumo de energia, limite de energia, uso de memória e total de memória.

    Returns:
        tuple: Uma tupla contendo dois elementos. O primeiro elemento é uma string representando o timestamp
        no formato '%Y-%m-%d %H:%M:%S', indicando o momento em que as informações foram obtidas. O segundo
        elemento é uma string contendo a saída do comando 'nvidia-smi' que contém as informações das GPUs.

    Raises:
        Exception: Se ocorrer algum erro ao executar o comando 'nvidia-smi', uma exceção será capturada
        e uma mensagem de erro será exibida no console. Nesse caso, a função retornará uma tupla contendo
        dois elementos None.
    """
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
    """
    Analisa a saída do comando 'nvidia-smi' para extrair informações sobre as GPUs.

    Esta função recebe a saída do comando 'nvidia-smi' como entrada e a analisa para extrair informações
    detalhadas sobre as GPUs. Cada linha da saída representa uma GPU e contém informações como índice, nome,
    UUID, temperatura da GPU, velocidade do ventilador, consumo de energia, limite de energia, uso de memória
    e total de memória.

    Args:
        output (str): A saída do comando 'nvidia-smi' que contém informações das GPUs.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma GPU e contém informações como índice,
        nome, UUID, temperatura, velocidade do ventilador, consumo de energia, limite de energia, uso de memória
        e total de memória.

    Example:
        A linha da saída do 'nvidia-smi' pode ser assim:
        "0, GeForce GTX 1080, GPU-0d6769db-dedd-54f4-560f-a32c207842e2, 61°C, 22 %, 150.30 W, 180.00 W, 8192 MiB / 8192 MiB"
        Nesse caso, o dicionário correspondente seria:
        {
            'Index': 0,
            'Name': 'GeForce GTX 1080',
            'UUID': 'GPU-0d6769db-dedd-54f4-560f-a32c207842e2',
            'Temperature': 61,
            'Fan Speed': 22,
            'Power Draw': 150.30,
            'Power Limit': 180.00,
            'Memory Used': 8192,
            'Memory Total': 8192,
            'Timestamp': None
        }
    """
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
    for gpu_info in gpu_data:
        gpu_index = gpu_info['Index']
        temperature = gpu_info['Temperature']

        metrics['Temperature']['Hour'][gpu_index].append(temperature)

        if len(metrics['Temperature']['Hour'][gpu_index]) > 12:
            last_hour_temps = metrics['Temperature']['Hour'][gpu_index][-12:]
            max_temp_hour = max(last_hour_temps)
            if max_temp_hour > peak_values_hour[gpu_index]['Temperature']['Value']:
                peak_values_hour[gpu_index]['Temperature']['Value'] = max_temp_hour
                peak_values_hour[gpu_index]['Temperature']['Time'] = timestamp

        if len(metrics['Temperature']['Hour'][gpu_index]) > 288:
            last_day_temps = metrics['Temperature']['Hour'][gpu_index][-288:]
            max_temp_day = max(last_day_temps)
            if max_temp_day > peak_values_day[gpu_index]['Temperature']:
                peak_values_day[gpu_index]['Temperature'] = max_temp_day

        if len(metrics['Temperature']['Hour'][gpu_index]) > 2016:
            last_week_temps = metrics['Temperature']['Hour'][gpu_index][-2016:]
            max_temp_week = max(last_week_temps)
            if max_temp_week > peak_values_week[gpu_index]['Temperature']:
                peak_values_week[gpu_index]['Temperature'] = max_temp_week

    # Armazenar o último horário em que as informações foram atualizadas
    peak_values_hour['LastUpdate'] = timestamp
    peak_values_day['LastUpdate'] = timestamp
    peak_values_week['LastUpdate'] = timestamp

def print_peak_values(peak_values):
    print("\nPicos de Power Usage:")
    for gpu_index, values in peak_values.items():
        print(f"GPU-{gpu_index}:")
        for period, metrics in values.items():
            print(f"  {period} Peak Temperature: {metrics['Temperature']['Value']}°C at {metrics['Temperature']['Time']}")
        print()

# Função principal
if __name__ == "__main__":
    while True:
        timestamp, output = get_gpu_info()
        if timestamp is not None and output is not None:
            gpu_data = parse_gpu_info(output)
            find_peak_values(gpu_data, peak_values_hour, timestamp)
        
        # Imprimir os picos de temperatura acumulados a cada 5 minutos
        print_peak_values(peak_values_hour)
        
        # Aguardar 5 minutos
        time.sleep(300)  # 300 segundos = 5 minutos




