import cv2
import numpy as np

# Cargar la imagen
image = cv2.imread('captura_3.jpg', cv2.IMREAD_GRAYSCALE)

# Aplicar suavizado para reducir el ruido
blurred = cv2.GaussianBlur(image, (5, 5), 0)

# Aplicar detección de bordes con el operador Canny
edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

# Realizar una dilatación para conectar bordes cercanos
kernel = np.ones((3, 3), np.uint8)
dilated_edges = cv2.dilate(edges, kernel, iterations=1)

# Encontrar contornos en los bordes dilatados
contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filtrar y obtener los contornos más grandes (pueden ser más de uno)
min_contour_area = 100  # Ajusta este valor según tu imagen
filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]

# Ordenar los contornos filtrados por área en orden descendente
filtered_contours.sort(key=lambda contour: cv2.contourArea(contour), reverse=True)

# Si hay al menos dos contornos filtrados, usar el segundo más grande
if len(filtered_contours) >= 2:
    second_largest_contour = filtered_contours[1]
    result = np.zeros_like(image)
    cv2.drawContours(result, [second_largest_contour], -1, 255, thickness=cv2.FILLED)

    # Redimensionar la imagen resultante para que tenga las mismas dimensiones que la original
    result_resized = cv2.resize(result, (image.shape[1], image.shape[0]))

    # Guardar la imagen resultante en un archivo
    cv2.imwrite('imagen_resultante2.jpg', result_resized)

    print("Imagen resultante guardada como 'imagen_resultante.jpg'")
else:
    print("No se encontraron suficientes contornos para aplicar la transformación.")

