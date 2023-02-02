# -*- coding: utf-8 -*-
"""buffer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qwSsss8_37XUVky8bwZB2tnuaCMNIrMx

# Inicialización
"""

# Inicialización

#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#from google.colab import auth
#from oauth2client.client import GoogleCredentials

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as img

import numpy as np
from scipy import ndimage as ndi
import random

from skimage.color import rgb2gray
from skimage.filters import gabor_kernel

#!pip install hilbertcurve # IPython command para jupyter google colab 
from hilbertcurve.hilbertcurve import HilbertCurve

from tqdm import tqdm

import os

# Buscamos los archivos en la carpeta compartida

img_acumar = img.imread('basura_000.png')
img_buffer = img.imread('buffer_000.png')



"""# Pruebas de detección de textura

## Funciones
"""

# Definición de funciones

# Recorta una imagen para que sea cuadrada
def square_img(img, square_size, offset_x = 0, offset_y = 0):
    max_size = np.max([img.shape])
    assert max_size >= square_size
    if len(img.shape) == 3 and img.shape[2] == 3:
        img_square = np.zeros((max_size, max_size, 3))
        img_type = type(img[0, 0, 0])
    else:
        img_square = np.zeros((max_size, max_size))
        img_type = type(img[0, 0])

    img_square[:img.shape[0], :img.shape[1]] = img
    assert offset_y + square_size < img_square.shape[0] and offset_x + square_size < img_square.shape[1]
    return img_square[offset_y:offset_y + square_size, offset_x:offset_x + square_size].astype(img_type)


# Genera una imagen a partir del filtro de gabor y una imagen en escala de grises
def gabor_img(img, kernel):
    img = (img - img.mean())/img.std() # normaliza la imagen
    return np.sqrt(ndi.convolve(img, np.real(kernel), mode='wrap')**2 +
                   ndi.convolve(img, np.imag(kernel), mode='wrap')**2)


# Genera una imagen a partir de la curva de Hilbert y una imagen en escala de grises
def hilbert_img(img, edge_thr = 0.05):
    assert img.shape[0] == img.shape[1]
    n_hil = 2
    p_hil = np.ceil(np.log2(img.shape[0]))
    square_size = (n_hil**p_hil).astype(int)
    hilbert_curve = HilbertCurve(p_hil, n_hil)
    img_edge = np.ones((square_size, square_size))
    img_hilbert = np.zeros((square_size, square_size))

    offset_x = 0
    offset_y = 0
    if img.shape[0] < square_size or img.shape[1] < square_size:
        offset_y = int(np.floor((square_size - img.shape[0])/2))
        offset_x = int(np.floor((square_size - img.shape[1])/2))
    square_img = np.zeros(img_edge.shape)
    square_img[offset_y:offset_y + img.shape[0], offset_x:offset_x + img.shape[1]] = img

    previous_point = hilbert_curve.point_from_distance(0)
    for point in hilbert_curve.points_from_distances(range(1, square_size**2)):
        img_hilbert[point[0], point[1]] = np.abs(square_img[point[0], point[1]] - square_img[previous_point[0], previous_point[1]])
        if(img_hilbert[point[0], point[1]] > edge_thr):
            img_edge[point[0], point[1]] = 0
        previous_point = point
    return img_edge, 1 - img_hilbert


# Genera una imagen a partir de la curva de Hilbert y una imagen a color
def color_hilbert_img(img, edge_thr = 0.05):
    assert img.shape[0] == img.shape[1]
    n_hil = 2
    p_hil = np.ceil(np.log2(img.shape[0]))
    square_size = (n_hil**p_hil).astype(int)
    hilbert_curve = HilbertCurve(p_hil, n_hil)
    img_edge = np.ones((square_size, square_size))
    img_hilbert = np.zeros((square_size, square_size))

    offset_x = 0
    offset_y = 0
    if img.shape[0] < square_size or img.shape[1] < square_size:
        offset_y = int(np.floor((square_size - img.shape[0])/2))
        offset_x = int(np.floor((square_size - img.shape[1])/2))
    if len(img) < 3:
        square_img = np.zeros(img_edge.shape)
    else:
        square_img = np.zeros((square_size, square_size, 3))
    square_img[offset_y:offset_y + img.shape[0], offset_x:offset_x + img.shape[1]] = img

    previous_point = hilbert_curve.point_from_distance(0)
    for point in hilbert_curve.points_from_distances(range(1, square_size**2)):
        img_hilbert[point[0], point[1]] = np.linalg.norm(square_img[point[0], point[1]] - square_img[previous_point[0], previous_point[1]])
        if(img_hilbert[point[0], point[1]] > edge_thr):
            img_edge[point[0], point[1]] = 0
        previous_point = point
    return img_edge, 1 - img_hilbert


# Genera una imagen considerando el contraste entre píxeles vecinos en una imagen en escala de grises
def hf_img(img, hf_thr = 0.05):
    assert img.shape[0] == img.shape[1]
    n_hil = 2
    p_hil = np.ceil(np.log2(img.shape[0]))
    square_size = (n_hil**p_hil).astype(int)
    img_edge = np.ones((square_size, square_size))
    img_hf = np.ones((square_size, square_size))

    offset_x = 0
    offset_y = 0
    if img.shape[0] < square_size or img.shape[1] < square_size:
        offset_y = int(np.floor((square_size - img.shape[0])/2))
        offset_x = int(np.floor((square_size - img.shape[1])/2))
    square_img = np.zeros(img_edge.shape)
    square_img[offset_y:offset_y + img.shape[0], offset_x:offset_x + img.shape[1]] = img

    for i in range(1, square_size - 1):
        for j in range(1, square_size - 1):
            img_hf[i, j] = np.abs(img[i - 1, j] - img[i, j])
            img_hf[i, j] += np.abs(img[i, j - 1] - img[i, j])
            img_hf[i, j] += np.abs(img[i + 1, j] - img[i, j])
            img_hf[i, j] += np.abs(img[i, j + 1] - img[i, j])
            img_hf[i, j] /= 4
            if(img_hf[i, j] > hf_thr):
                img_edge[i, j] = 0
    return img_edge, 1 - img_hf


# Genera una imagen en base a la entropía parcial de una imagen en escala de grises
def entropy_transform(img, kernel_size = 32, entropy_thr = 5, progress_bar = False):
    assert img.shape[0] == img.shape[1]
    assert kernel_size <= img.shape[0]

    img_tr_size = img.shape[0] - kernel_size + 1
    img_tr = np.zeros((img_tr_size, img_tr_size))
    img_entropy = np.zeros((img_tr_size, img_tr_size))
    bins = np.histogramdd([0, 1], bins = 256)[1]

    if progress_bar:
        iterator = tqdm(range(img_tr_size))
    else:
        iterator = range(img_tr_size)

    for i in iterator:
        for j in range(img_tr_size):
            img_kernel = img[i:i + kernel_size, j:j + kernel_size]
            density = np.histogramdd(np.ravel(img_kernel), bins = bins)[0]/img_kernel.size
            density = list(filter(lambda p: p > 0, np.ravel(density)))
            entropy = -np.sum(np.multiply(density, np.log2(density)))
            img_entropy[i, j] = entropy
            img_tr[i, j] = float(entropy > entropy_thr)

    return img_tr, img_entropy


# Genera una imagen en base a la entropía parcial de una imagen a color
def color_entropy_transform(img, kernel_size = 32, entropy_thr = 3, progress_bar = False, bins = 10, ds = 2):
    assert img.shape[0] == img.shape[1]
    assert np.mod(img.shape[0], ds) == 0
    assert kernel_size <= img.shape[0]

    img_tr_size = int(img.shape[0]/ds)
    img_tr = np.zeros((img_tr_size, img_tr_size))
    img_entropy = np.zeros((img_tr_size, img_tr_size))
    bins_color = np.histogramdd(np.array([[0, 0, 0], [256, 256, 256]]), bins = bins)[1]

    if progress_bar:
        iterator = tqdm(range(img_tr_size - int(np.ceil(kernel_size/ds))))
    else:
        iterator = range(img_tr_size - int(np.ceil(kernel_size/ds)))

    for i in iterator:
        for j in range(img_tr_size - int(np.ceil(kernel_size/ds))):
            img_kernel = img[i*ds:i*ds + kernel_size, j*ds:j*ds + kernel_size]
            img_reshaped = img_kernel[:, :].reshape(kernel_size**2, 3)
            density = np.histogramdd(img_reshaped, bins = bins_color)[0]
            density = np.array(list(filter(lambda p: p > 0, density.ravel())))/kernel_size**2
            entropy = -np.sum(np.multiply(density, np.log2(density)))
            img_entropy[i, j] = entropy
            img_tr[i, j] = float(entropy > entropy_thr)

    return img_tr, img_entropy


# Genera una imagen en base a la varianza parcial de una imagen en escala de grises
def var_transform(img, kernel_size = 32, var_thr = 0.1, progress_bar = False):
    assert img.shape[0] == img.shape[1]
    assert kernel_size <= img.shape[0]

    img_tr_size = img.shape[0] - kernel_size + 1
    img_tr = np.zeros((img_tr_size, img_tr_size))
    img_var = np.zeros((img_tr_size, img_tr_size))

    if progress_bar:
        iterator = tqdm(range(img_tr_size))
    else:
        iterator = range(img_tr_size)

    for i in iterator:
        for j in range(img_tr_size):
            img_kernel = img[i:i + kernel_size, j:j + kernel_size]
            var = np.var(img_kernel)
            img_var[i, j] = var
            img_tr[i, j] = float(var > var_thr)

    return img_tr, img_var


# Genera una imagen en base a la media parcial de una imagen en escala de grises
def mean_transform(img, kernel_size = 32, mean_thr = 0.1, progress_bar = False):
    assert img.shape[0] == img.shape[1]
    assert kernel_size <= img.shape[0]

    img_tr_size = img.shape[0] - kernel_size + 1
    img_tr = np.zeros((img_tr_size, img_tr_size))
    img_mean = np.zeros((img_tr_size, img_tr_size))

    if progress_bar:
        iterator = tqdm(range(img_tr_size))
    else:
        iterator = range(img_tr_size)

    for i in iterator:
        for j in range(img_tr_size):
            img_kernel = img[i:i + kernel_size, j:j + kernel_size]
            mean = np.mean(img_kernel)
            img_mean[i, j] = mean
            img_tr[i, j] = float(mean < mean_thr)

    return img_tr, img_mean


# Marca el borde de la basura en el buffer
def garbage_border(garbage_img, real_img, widen_n = 4, offset_x = 0, offset_y = 0, color = 1):
    garbage_img_edge = hilbert_img(garbage_img)[0]

    widen_img = garbage_img_edge.copy()
    for it in range(widen_n):
        for i in range(1, garbage_img_edge.shape[0] - 1):
            for j in range(1, garbage_img_edge.shape[1] - 1):
                if garbage_img_edge[i, j] == 0:
                    widen_img[i - 1, j] = 0
                    widen_img[i, j - 1] = 0
                    widen_img[i + 1, j] = 0
                    widen_img[i, j + 1] = 0
        garbage_img_edge = widen_img.copy()

    garbage_border_img = real_img.copy()
    expanded_garbage_img_edge = np.ones(garbage_border_img.shape[:2])
    expanded_garbage_img_edge[offset_y:offset_y + garbage_img_edge.shape[0], offset_x:offset_x + garbage_img_edge.shape[1]] = garbage_img_edge
    border_index = (expanded_garbage_img_edge == 0).nonzero()
    garbage_border_img[border_index[0], border_index[1], np.ones(border_index[0].shape).astype(int)*color] = 255

    return garbage_border_img

"""##Definiciones"""

# Definiciones de la imagen

# dpi de la imagen para imprimir en pantalla
mpl.rcParams['figure.dpi'] = 300

img_acumarr = img_acumar[:,:,:3]
img_bufferr = img_buffer[:,:,:3]
# imágenes en blanco y negro
acumar_gray = rgb2gray(img_acumarr)
buffer_gray = rgb2gray(img_bufferr)

start_x = 300
start_y = 300
p_square = 9

# imágnes recortadas
img_main_color = square_img(img_acumar, square_size = 2**p_square, offset_x = start_x, offset_y = start_y)
img_main_gray = square_img(acumar_gray, 2**p_square, start_x, start_y)

# valor medio de la imagen
m = np.mean(img_main_gray)

plt.figure(figsize = (3, 3))

plt.subplot(2, 2, 1)
plt.imshow(img_acumar)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(2, 2, 2)
plt.imshow(img_main_color)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(2, 2, 3)
plt.imshow(img_main_gray, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(2, 2, 4)
plt.imshow(img_buffer)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

aux = img_main_gray.copy()
aux[50:450, 50:450] = 0

plt.figure(figsize = (3, 3))
plt.imshow(aux, cmap = 'gray', vmin = 0, vmax = 1)

plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)
np.mean(aux)

"""##Prueba principal

###Detección de bordes
"""

# Prueba de las transformadas por entropía y media

# imagen obtenida con el filtro de Gabor
lam = 4 # lambda (longitud de onda)
pi_fraction = np.array(range(10))/10
angles = pi_fraction*np.pi
sigma = 2
sigma_x = sigma
sigma_y = sigma

gabor_kernels = [gabor_kernel(1/lam, theta = theta, sigma_x = sigma_x, sigma_y = sigma_y) for theta in angles]

img_gabor = np.zeros(img_main_gray.shape)
for kernel in gabor_kernels:
    filtered_img = gabor_img(img_main_gray, kernel)
    img_gabor += filtered_img

img_gabor /= len(gabor_kernels)

# imagen obtenida con el recorrido de Hilbert

edge_thr = 0.1
img_edge = hilbert_img(img_main_gray, edge_thr)[0]

# parámetros del kernel para las transformadas
p_kernel = 5
kernel_size = 2**p_kernel

# umbrales para la detección de basura
entropy_main_thr = 7 # bajar para detectar más basura
entropy_gabor_thr = 5.3 # bajar para detectar más basura
entropy_edge_thr = 0.9 # bajar para detectar más basura
mean_edge_thr = 0.7 # subir para detectar más basura

# imágenes transformadas
img_main_gray_entropy_tr, entropy_main = entropy_transform(img_main_gray, kernel_size, entropy_main_thr, True)
img_gabor_entropy_tr, entropy_gabor = entropy_transform(img_gabor, kernel_size, entropy_gabor_thr, True)
img_edge_entropy_tr, entropy_edge = entropy_transform(img_edge, kernel_size, entropy_edge_thr, True)
img_edge_mean_tr, mean_edge = mean_transform(img_edge, kernel_size, mean_edge_thr, True)

# borde de la basura detectada sobre la imagen original
garbage_border_img_main_gray_entropy = garbage_border(img_main_gray_entropy_tr, square_img(img_acumar, offset_x = start_x, offset_y = start_y, square_size = img_main_gray.shape[0]))
garbage_border_img_gabor_entropy = garbage_border(img_gabor_entropy_tr, square_img(img_acumar, offset_x = start_x, offset_y = start_y, square_size = img_main_gray.shape[0]))
garbage_border_img_edge_entropy = garbage_border(img_edge_entropy_tr, square_img(img_acumar, offset_x = start_x, offset_y = start_y, square_size = img_main_gray.shape[0]))
garbage_border_img_edge_mean = garbage_border(img_edge_entropy_tr, square_img(img_acumar, offset_x = start_x, offset_y = start_y, square_size = img_main_gray.shape[0]))

# impresión en pantalla
plt.figure(figsize = (4, 4))

plt.subplot(3, 4, 1)
plt.imshow(img_main_gray, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 2)
plt.imshow(1 - img_gabor, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 3)
plt.imshow(img_edge, cmap ='gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 4)
plt.imshow(img_edge, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 5)
plt.imshow(img_main_gray_entropy_tr, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 6)
plt.imshow(img_gabor_entropy_tr, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 7)
plt.imshow(img_edge_entropy_tr, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 8)
plt.imshow(img_edge_mean_tr, cmap = 'gray', vmin = 0, vmax = 1)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 9)
plt.imshow(garbage_border_img_main_gray_entropy)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 10)
plt.imshow(garbage_border_img_gabor_entropy)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 11)
plt.imshow(garbage_border_img_edge_entropy)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

plt.subplot(3, 4, 12)
plt.imshow(garbage_border_img_edge_mean)
plt.xticks([])
plt.yticks([])
plt.grid(False)
plt.box(False)

"""###Cálculo de la superficie"""

# Cálculo de la superficie

img_tr = [img_main_gray_entropy_tr, img_gabor_entropy_tr, img_edge_entropy_tr, img_edge_mean_tr]
kernel_half_size = int(kernel_size/2)
buffer_gray_red = np.round(buffer_gray[kernel_half_size:-kernel_half_size + 1, kernel_half_size:-kernel_half_size + 1])
proyection_map = np.ones([len(img_main_gray_entropy_tr), len(img_main_gray_entropy_tr)]) # matriz de ponderación del buffer

gamma = np.deg2rad(60) # ángulo de visión de la cámara
phi = np.deg2rad(15) # posición de la cámara

h = 3 # altura de la cámara
D = (np.tan(gamma + phi) - np.tan(phi))*h # largo de la superficie del agua en la imagen
delta = gamma/len(img_main_gray_entropy_tr) # ángulo por píxel

proyection_map[0, :] = np.tan(phi + delta)*h/D

for i in range(2, len(img_main_gray_entropy_tr) + 1):
    proyection_map[i - 1, :]= (np.tan(phi + delta*i) - np.tan(phi + delta*(i - 1)))*h/D
proyection_map = np.flipud(proyection_map)

# nivel de llenado del buffer para cada imagen
b = []

for tri in img_tr:
    b.append(np.sum(buffer_gray_red*proyection_map*tri)/np.sum(buffer_gray_red*proyection_map)*100)

print(b)
