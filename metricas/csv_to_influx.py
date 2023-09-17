from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

# Configuración de la conexión a la base de datos InfluxDB
url = "http://localhost:8086"  # Cambia esto a la URL de tu servidor InfluxDB
token = "recolector_de_basura"  # Cambia esto a tu token de acceso
org = "recolector"  # Cambia esto a tu organización
bucket = "metricas"  # Cambia esto a tu bucket

# Crear un cliente InfluxDB
client = InfluxDBClient(url=url, token=token, org=org)

# Crear un objeto WriteApi para escribir datos en el bucket
write_api = client.write_api(write_options=SYNCHRONOUS)

# Ruta al archivo CSV
csv_file = 'datos_completos.csv'  # Asegúrate de que esta ruta sea correcta

# Carga los datos desde el archivo CSV en un DataFrame de Pandas
df = pd.read_csv(csv_file)

# Itera a través de las filas del DataFrame y escribe los puntos en InfluxDB
for index, row in df.iterrows():
    point = Point(row["_measurement"]).tag("sensor", row["sensor"]).field(row["_field"], row["_value"]).time(row["_time"])
    write_api.write(bucket=bucket, org=org, record=point)

# Cierra el cliente
client.close()
