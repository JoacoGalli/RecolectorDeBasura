import pandas as pd

# Ruta al archivo CSV
csv_file = 'datos_completos.csv'  # Asegúrate de que esta ruta sea correcta

# Carga los datos desde el archivo CSV en un DataFrame de Pandas
df = pd.read_csv(csv_file)

# Muestra los primeros n registros del DataFrame
n = 2000
print(df.head(n))
