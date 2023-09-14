import pandas as pd

# Ruta al archivo CSV
csv_file = 'datos_completos.csv'  # Asegúrate de que esta ruta sea correcta

# Carga los datos desde el archivo CSV en un DataFrame de Pandas
df = pd.read_csv(csv_file)

# Filtra los datos de la métrica "metricas" y el campo "distribucion_pos_cm"
#metricas_df = df[df['measurement'] == 'metricas']
# Muestra los nombres de todas las columnas en el DataFrame
# Filtra los datos donde la columna 'sensor' es igual a 'tacho7'
tacho7_data = df[df['sensor'] == 'distribucion_pos_cm']

# Selecciona solo las columnas '_time' y '_value'
tacho7_data = tacho7_data[['sensor', '_time', '_value']]
print(tacho7_data)
# # Muestra los primeros n registros del campo "distribucion_pos_cm"
# n = 50
# print(distribucion_pos_cm.head(n))

