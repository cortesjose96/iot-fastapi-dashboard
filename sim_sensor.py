import requests
import time
import random
from datetime import datetime

url = "http://127.0.0.1:8000/report"

print("Iniciando simulación de sensores...")

while True:
    payload = {
        "sensor_id"     : 1,
        "temperature"   : round(random.uniform(20.0, 80.0), 2),
        "cpu"           : random.randint(10, 100),
        "ram"           : random.randint(40, 90),
        "disk"          : random.randint(10, 30),
        "network"       : random.randint(100, 5000),
        "latency"       : random.randint(1, 50),
        "timestamp"     : datetime.now().isoformat() # formato ISO string
    }

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Enviado: T={payload['temperature']}°C | CPU={payload['cpu']}%")
        else:
            print(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Error de conexión: {e}")

    time.sleep(2)