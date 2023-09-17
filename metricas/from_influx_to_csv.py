from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

# Configuración de la conexión a la base de datos InfluxDB
url = 'http://localhost:8086'  # Reemplaza con la URL correcta
token = 'recolector_de_basura'  # Reemplaza esto con tu token
org = 'recolector'
bucket = 'metricas'

client = InfluxDBClient(url=url, token=token)

# Consulta para obtener todos los datos de la base de datos
query = f'from(bucket:"{bucket}") |> range(start: 0)'

result = client.query_api().query_data_frame(org=org, query=query)

# Guarda el DataFrame en un archivo CSV
csv_file = 'datos_completos.csv'
result.to_csv(csv_file, index=False)

print(f'Datos exportados a {csv_file}')
