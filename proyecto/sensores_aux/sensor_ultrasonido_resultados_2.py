import os
import matplotlib.pyplot as plt
import numpy as np

# Ruta de la carpeta de mediciones
carpeta_mediciones = 'ultrasonido_muestras/'

# Ruta de la carpeta donde se guardarán las gráficas
carpeta_graficas = 'ultrasonido_muestras_resultados/'

# Leer los archivos de mediciones en la carpeta
archivos_mediciones = os.listdir(carpeta_mediciones)

# Recorrer cada archivo de mediciones
for archivo_mediciones in archivos_mediciones:
    ruta_archivo = os.path.join(carpeta_mediciones, archivo_mediciones)

    # Leer las distancias desde el archivo
    distancias = []
    with open(ruta_archivo, 'r') as archivo:
        for linea in archivo:
            distancia = float(linea.strip())
            distancias.append(distancia)

    # Descartar mediciones que difieren significativamente de la mediana
    mediana = np.median(distancias)
    diff = np.abs(distancias - mediana)
    mediana_absoluta = np.median(diff)
    factor = 10  # Ajusta el factor según sea necesario
    umbral = factor * mediana_absoluta
    distancias_filtradas = [
        d for d in distancias if np.abs(d - mediana) <= umbral]
    distancias_descartadas = [
        d for d in distancias if np.abs(d - mediana) > umbral]

    # Calcular el promedio de las 5 mediciones más altas y las 5 más bajas
    distancias_ordenadas = sorted(distancias_filtradas)
    mediciones_bajas = distancias_ordenadas[:5]
    mediciones_altas = distancias_ordenadas[-5:]
    promedio = np.mean(mediciones_bajas + mediciones_altas)

    # Crear una lista de números de muestra para el eje x
    muestras = range(1, len(distancias_filtradas) + 1)

    # Graficar las distancias
    plt.plot(muestras, distancias_filtradas, 'ro-', label='Mediciones')
    plt.scatter([len(distancias_filtradas) + i + 1 for i in range(len(distancias_descartadas))],
                distancias_descartadas, color='gray', label='Descartadas')
    plt.xlabel('Muestra')
    plt.ylabel('Distancia (cm)')
    plt.title('Mediciones del sensor HC-SR04')
    plt.grid(True)

    # Establecer límites en el eje y
    plt.ylim([min(distancias_filtradas) - 5, max(distancias_filtradas) + 5])

    # Mostrar el promedio en el gráfico
    plt.text(0.02, 0.95, f'Promedio: {promedio:.2f}',
             transform=plt.gca().transAxes)

    # Mostrar leyenda
    plt.legend()

    # Generar un nombre único para el archivo de gráfica
    # Por ejemplo: grafica_archivo1.png
    nombre_grafica = f'grafica_{archivo_mediciones[:-4]}.png'

    # Ruta completa de la gráfica a guardar
    ruta_grafica = os.path.join(carpeta_graficas, nombre_grafica)

    # Guardar la gráfica en la carpeta de gráficas
    plt.savefig(ruta_grafica)

    # Cerrar la figura para liberar memoria
    plt.close()
