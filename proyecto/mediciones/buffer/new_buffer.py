# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.image as img

import numpy as np
from img_process import gabor_img, hilbert_img, mean_transform, outline
from skimage.color import rgba2rgb, rgb2gray
from skimage.filters import gabor_kernel


img_camara = img.imread('foto.jpg') # esta va a ser la foto que vamos a ir sacando con la camara
img_buffer = img.imread('foto.jpg') # Esta es la imagen del buffer en blanco y negro

def porcentaje_buffer(img_camara):


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


    #img_buffer_outline = outline(img_buffer_bn, img_camara)

    total_rows = img_buffer_bn.shape[0]
    total_columns = img_buffer_bn.shape[1]
    buffer_start_row = np.min(np.where(img_buffer_bn == 1)[0]) # filas y columnas que limitan al buffer
    buffer_end_row = np.max(np.where(img_buffer_bn == 1)[0]) # filas y columnas que limitan al buffer
    buffer_start_column = np.min(np.where(np.matrix.transpose(img_buffer_bn) == 1)[0]) # filas y columnas que limitan al buffer
    buffer_end_column = np.max(np.where(np.matrix.transpose(img_buffer_bn) == 1)[0]) # filas y columnas que limitan al buffer
    index_margin = 50
    index_img = [np.max([buffer_start_row - index_margin, 0]), np.min([total_rows, buffer_end_row + index_margin]),np.max([buffer_start_column - index_margin, 0]), np.min([total_columns, buffer_end_column + index_margin])]


    lam = 4 # lambda (longitud de onda)
    pi_fraction = np.array(range(10))/10
    angles = pi_fraction*np.pi
    sigma = 2
    sigma_x = sigma
    sigma_y = sigma

    gabor_kernels = [gabor_kernel(1/lam, theta = theta, sigma_x = sigma_x, sigma_y = sigma_y) for theta in angles]

    img_gabor_g = np.zeros(img_camara_g.shape)
    for kernel in gabor_kernels:
        filtered_img = gabor_img(img_camara_g, kernel)
        img_gabor_g += filtered_img

    img_gabor_g /= len(gabor_kernels)

    img_gabor_g = 1 - img_gabor_g

    # imagen obtenida con el recorrido de Hilbert
    edge_thr = 0.1 # bajar para detectar más basura
    img_edge_bn, img_edge_g = hilbert_img(img_camara_g, edge_thr)

    """## Transformadas"""

    # parámetros del kernel para las transformadas
    kernel_size = 32

    # umbrales para la detección de basura
    mean_edge_thr = 0.97 # subir para detectar más basura

    # imágenes transformadas

    # ACA TENEMOS QUE DECIDIR CON QUE METODO NOS QUEDAMOS
    img_edge_mean_tr_bn, img_edge_mean_tr_g = mean_transform(img_edge_bn, img_buffer_bn, kernel_size, mean_edge_thr, True)

    img_edge_mean_outline = outline(img_edge_mean_tr_bn, img_camara)

    # Impresión la dejo comentada pero no la vamos a necesitar
    plt.figure(figsize = (2.5, 2.5)) #individuales para el informe

    plt.subplot(2, 2, 2)
    plt.imshow(img_edge_mean_tr_bn[index_img[0]:index_img[1], index_img[2]:index_img[3]], cmap = 'gray', vmin = 0, vmax = 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.box(False)

    plt.subplot(2, 2, 4)
    plt.imshow(img_edge_mean_outline[index_img[0]:index_img[1], index_img[2]:index_img[3]])
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.box(False)
    plt.show()

    filling_percentage = np.sum(img_buffer_bn* img_edge_mean_tr_bn)/np.sum(img_buffer_bn)*100

    print(f'El % de llenado del buffer es de {filling_percentage}')