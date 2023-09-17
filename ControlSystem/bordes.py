import cv2
import numpy as np

# Cargar la imagen
image = cv2.imread('captura_3.jpg', cv2.IMREAD_GRAYSCALE)


# Aplicar suavizado para reducir el ruido
blurred = cv2.GaussianBlur(image, (9, 9), 0)
#blurred = cv2.blur(image, (5, 5))
#blurred = cv2.medianBlur(image, 9)
# Ajustar los parámetros del operador Canny
threshold1 = 52  # Prueba con diferentes valores (más bajo)
threshold2 = 98  # Prueba con diferentes valores (más alto)

# Aplicar detección de bordes con el operador Canny
edges = cv2.Canny(blurred, threshold1=threshold1, threshold2=threshold2)

# Realizar una dilatación para conectar bordes cercanos
kernel = np.ones((2, 2), np.uint8)
dilated_edges = cv2.dilate(edges, kernel, iterations=2)

# Encontrar contornos en los bordes dilatados
contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filtrar y obtener solo los contornos más grandes (pueden ser más de uno)
min_contour_area = 0.2 # Ajusta este valor según tu imagen
filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]

# Encontrar y dibujar el contorno más grande entre los filtrados
largest_contour = max(filtered_contours, key=cv2.contourArea)
result = np.zeros_like(image)
cv2.drawContours(result, [largest_contour], -1, 255, thickness=cv2.FILLED)

# Redimensionar la imagen resultante para que tenga las mismas dimensiones que la original
result_resized = cv2.resize(result, (image.shape[1], image.shape[0]))

# Guardar la imagen resultante en un archivo
cv2.imwrite('imagen_resultante0.jpg', result_resized)

print("Imagen resultante guardada como 'imagen_resultante.jpg'")
