# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.image as img

import os
import pandas as pd

import numpy as np
from img_process import gabor_img, hilbert_img, mean_transform, outline, entropy_transform
from skimage.color import rgba2rgb, rgb2gray
from skimage.filters import gabor_kernel

from tqdm import tqdm


def calcular_porcentaje_buffer(img_camara, imagen_path):
    print(imagen_path)
    # img.imread('../fotos_buffer/buffer_2/buffer_2_colores_amarillo.png') # esta va a ser la foto que vamos a ir sacando con la camara
    img_camara = img_camara
    # Esta es la imagen del buffer en blanco y negro
    img_buffer = img.imread('../fotos_buffer/buffer_vacio_negro.png')

    img_total_number = len(img_camara)

    if img_camara.shape[2] == 4:

        img_aux_color = rgba2rgb(img_camara)
    else:
        img_aux_color = img_camara
    img_camara_g = rgb2gray(img_aux_color)

    if img_buffer.shape[2] == 4:
        img_aux_color = rgba2rgb(img_buffer)
    else:
        img_aux_color = img_buffer
    img_buffer_bn = np.round(rgb2gray(img_aux_color))

    # img_buffer_outline = outline(img_buffer_bn, img_camara)

    total_rows = img_buffer_bn.shape[0]
    total_columns = img_buffer_bn.shape[1]
    # filas y columnas que limitan al buffer
    buffer_start_row = np.min(np.where(img_buffer_bn == 1)[0])
    # filas y columnas que limitan al buffer
    buffer_end_row = np.max(np.where(img_buffer_bn == 1)[0])
    buffer_start_column = np.min(np.where(np.matrix.transpose(img_buffer_bn) == 1)[
                                 0])  # filas y columnas que limitan al buffer
    buffer_end_column = np.max(np.where(np.matrix.transpose(img_buffer_bn) == 1)[
                               0])  # filas y columnas que limitan al buffer
    index_margin = 50
    index_img = [np.max([buffer_start_row - index_margin, 0]), np.min([total_rows, buffer_end_row + index_margin]),
                 np.max([buffer_start_column - index_margin, 0]), np.min([total_columns, buffer_end_column + index_margin])]

    lam = 4  # lambda (longitud de onda)
    pi_fraction = np.array(range(10))/10
    angles = pi_fraction*np.pi
    sigma = 2
    sigma_x = sigma
    sigma_y = sigma

    gabor_kernels = [gabor_kernel(
        1/lam, theta=theta, sigma_x=sigma_x, sigma_y=sigma_y) for theta in angles]

    img_gabor_g = np.zeros(img_camara_g.shape)
    for kernel in gabor_kernels:
        filtered_img = gabor_img(img_camara_g, kernel)
        img_gabor_g += filtered_img

    img_gabor_g /= len(gabor_kernels)

    img_gabor_g = 1 - img_gabor_g

    # imagen obtenida con el recorrido de Hilbert
    edge_thr = 0.1  # bajar para detectar más basura
    img_edge_bn, img_edge_g = hilbert_img(img_camara_g, edge_thr)

    """## Transformadas"""

    # parámetros del kernel para las transformadas
    kernel_size = 32

    # umbrales para la detección de basura
    entropy_thr = 5  # bajar para detectar más basura
    entropy_gabor_thr = 3  # bajar para detectar más basura
    entropy_edge_thr = 0.2  # bajar para detectar más basura
    # mean_edge_thr = 0.85 # subir para detectar más basura
    # mean_edge_thr_2 = 0.91 # subir para detectar más basura
    # mean_edge_thr = 0.97 # subir para detectar más basura

    # imágenes transformadas

    # ACA TENEMOS QUE DECIDIR CON QUE METODO NOS QUEDAMOS
    img_source_entropy_tr_bn, img_camara_entropy_tr_g = entropy_transform(
        img_camara_g, img_buffer_bn, kernel_size, entropy_thr, True)
    img_gabor_entropy_tr_bn, img_gabor_entropy_tr_g = entropy_transform(
        img_gabor_g, img_buffer_bn, kernel_size, entropy_gabor_thr, True)
    img_edge_entropy_tr_bn, img_edge_entropy_tr_g = entropy_transform(
        img_edge_bn, img_buffer_bn, kernel_size, entropy_edge_thr, True)
    # img_edge_mean_tr_bn, img_edge_mean_tr_g = mean_transform(img_edge_bn, img_buffer_bn, kernel_size, mean_edge_thr, True)
    # img_edge_mean_tr_bn_2, img_edge_mean_tr_g_2 = mean_transform(img_edge_bn, img_buffer_bn, kernel_size, mean_edge_thr_2, True)

    # img_camara_entropy_outline = outline(img_source_entropy_tr_bn, img_camara)
    # img_gabor_entropy_outline = outline(img_gabor_entropy_tr_bn, img_camara)
    # img_edge_entropy_outline = outline(img_edge_entropy_tr_bn, img_camara)
    # img_edge_mean_outline = outline(img_edge_mean_tr_bn, img_camara)

    # Impresión la dejo comentada pero no la vamos a necesitar
    # plt.figure(figsize = (2.5, 2.5)) #individuales para el informe

    # plt.subplot(2, 2, 2)
    # plt.imshow(img_edge_mean_tr_bn[index_img[0]:index_img[1], index_img[2]:index_img[3]], cmap = 'gray', vmin = 0, vmax = 1)
    # plt.xticks([])
    # plt.yticks([])
    # plt.grid(False)
    # plt.box(False)

    # plt.subplot(2, 2, 4)
    # plt.imshow(img_edge_mean_outline[index_img[0]:index_img[1], index_img[2]:index_img[3]])
    # plt.xticks([])
    # plt.yticks([])
    # plt.grid(False)
    # plt.box(False)
    # # plt.show()
    # plt.savefig(imagen_path.replace('.png','_plot.png'))
    # plt.close()

    img_tr = [img_source_entropy_tr_bn, img_gabor_entropy_tr_bn,
              img_edge_entropy_tr_bn]  # , img_edge_mean_tr_bn]
    # img_tr = [img_edge_mean_tr_bn, img_edge_mean_tr_bn_2]
    # img_tr = img_edge_entropy_tr_bn

    # matriz de ponderación del buffer
    proyection_map = np.zeros(img_buffer_bn.shape)

    h_cam = 3  # altura de la cámara

    gamma_h = np.deg2rad(70)  # ángulo de visión de la cámara
    delta_alpha_h = gamma_h/total_columns  # ángulo por píxel

    # gamma_v/2 tiene que ser < min(theta) o se tiene que limitar la imagen según buffer_start_row
    # ángulo de visión de la cámara # definirlo como gamma_col*total_rows/total_columns
    gamma_v = gamma_h*total_rows/total_columns
    phi = np.deg2rad(35)  # posición de la cámara
    delta_alpha_v = gamma_v/total_rows  # ángulo por píxel

    n_cam = np.array([-np.sin(phi), 0, np.cos(phi)])
    n_wat = np.array([0, 0, 1])

    for i in tqdm(range(buffer_start_row, total_rows)):
        alpha_v = -gamma_v/2 + (total_rows - i)*delta_alpha_v
        for j in range(total_columns):
            alpha_h = -gamma_h/2 + j*delta_alpha_h
            n_theta = np.array([np.sin(alpha_h), np.cos(alpha_h), 0])
            theta = np.arccos(np.dot(np.cross(n_wat, n_theta), np.cross(n_cam, n_theta))/(
                np.linalg.norm(np.cross(n_wat, n_theta))*np.linalg.norm(np.cross(n_cam, n_theta))))

            r = np.abs((np.sin(theta) + np.tan(np.deg2rad(90) +
                       alpha_v - theta)*np.cos(theta))*h_cam)
            delta_r = np.abs(np.abs((np.sin(theta) + np.tan(np.deg2rad(90) +
                             alpha_v + delta_alpha_v - theta)*np.cos(theta))*h_cam) - r)
            proyection_map[i, j] = delta_r*r*delta_alpha_h

    filling_percentage = []

    # nivel de llenado del buffer para cada imagen
    for tri in img_tr:
        filling_percentage.append(np.sum(
            img_buffer_bn*proyection_map*tri)/np.sum(img_buffer_bn*proyection_map)*100)

    # print(f'El % de llenado del buffer es de {filling_percentage}')
    return filling_percentage


ruta_carpeta = '../fotos_buffer/buffer_1'

# Crear un DataFrame vacío para almacenar los resultados de todas las imágenes
df_resultados = pd.DataFrame(columns=['imagen', 'resultado'])

# Obtener una lista de todas las imágenes en la carpeta
lista_imagenes = [archivo for archivo in os.listdir(
    ruta_carpeta) if archivo.endswith('.png')]

# Iterar sobre la lista de imágenes
for imagen in lista_imagenes:
    # Leer la imagen
    imagen_path = os.path.join(ruta_carpeta, imagen)
    # img_nombre = os.path.basename(imagen)
    imagen_source = img.imread(imagen_path)
    # Aquí agregar tu código para procesar la imagen
    # ...
    resultado = calcular_porcentaje_buffer(imagen_source, imagen_path)

    # Agregar el resultado a un DataFrame
    resultado = {'imagen': imagen, 'resultado': resultado}
    df_resultados = df_resultados.append(resultado, ignore_index=True)

    # Crear un plot con matplotlib y guardarlo como una nueva imagen
    # plt.plot(x, y)
    # plt.savefig(imagen.replace('.jpg', '_plot.png'))
    # plt.close()

# Guardar todos los resultados en un archivo CSV
df_resultados.to_csv(
    '/home/joaco/Documents/facultad/RecolectorDeBasura/proyecto/mediciones/fotos_buffer/buffer_1_resultados/todos_los_resultados_1_metodos_buffer_3_5_3_0_2.csv', index=False)
