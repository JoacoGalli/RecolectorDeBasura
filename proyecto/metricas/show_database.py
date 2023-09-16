import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta al archivo CSV
csv_file = 'datos_completos.csv'  # Asegúrate de que esta ruta sea correcta

# Carpeta donde se guardarán los gráficos
output_folder = 'graficos_tachos'  # Cambia a la carpeta deseada

# Crear la carpeta si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Carga los datos desde el archivo CSV en un DataFrame de Pandas
df = pd.read_csv(csv_file)

# Obtén la lista de tachos disponibles en los datos
tachos = df['sensor'].unique()

# Genera un gráfico de dispersión para cada tacho
for tacho in tachos:
    # Filtra los datos para el tacho actual
    tacho_data = df[df['sensor'] == tacho]
    
    # Selecciona las columnas '_time' y '_value'
    x = tacho_data['_time']
    y = tacho_data['_value']
    
    # Crea el gráfico de dispersión
    plt.figure(figsize=(10, 6))  # Tamaño del gráfico
    plt.scatter(x, y, label=tacho, s=5)  # Crea el gráfico de dispersión
    
    # Etiquetas y título del gráfico
    plt.xlabel('Tiempo')
    plt.ylabel('Valor')
    plt.title(f'Gráfico de dispersión para {tacho}')
    
    # Guarda el gráfico en la carpeta de salida
    output_file = os.path.join(output_folder, f'grafico_{tacho}.png')
    plt.savefig(output_file)
    
    # Cierra el gráfico para evitar la superposición
    plt.close()

print('Gráficos generados y guardados en la carpeta de salida.')

