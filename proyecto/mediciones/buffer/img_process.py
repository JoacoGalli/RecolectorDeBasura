import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgba2rgb


from tqdm import tqdm

from hilbertcurve.hilbertcurve import HilbertCurve

hilbert_curves = []
hilbert_curves_points = []
hilbert_curves.append([])
hilbert_curves_points.append([])
n_hil = 2

for p_hil in range(1, 12): # resolución máxima 4K
    hilbert_curves.append(HilbertCurve(p_hil, n_hil))
    hilbert_curves_points.append(hilbert_curves[p_hil].points_from_distances(range(1, (n_hil**p_hil)**2)))

"""## Preprocesamiento"""

# Genera una imagen a partir del filtro de gabor y una imagen en escala de grises
def gabor_img(img, kernel):
    img = (img - img.mean())/img.std() # normaliza la imagen
    return np.sqrt(ndi.convolve(img, np.real(kernel), mode='wrap')**2 +
                   ndi.convolve(img, np.imag(kernel), mode='wrap')**2)

# Genera una imagen a partir de la curva de Hilbert y una imagen en escala de grises
def hilbert_img(img, edge_thr = 0.05):
    max_dim = np.max(img.shape[:2])
    n_hil = 2
    p_hil = np.ceil(np.log2(max_dim)).astype(int)
    square_size = n_hil**p_hil
    img_edge = np.ones((square_size, square_size))
    img_hilbert = np.zeros((square_size, square_size))

    previous_point = hilbert_curves_points[p_hil][0]
    for point in hilbert_curves_points[p_hil]:
        if point[0] < img.shape[0] and point[1] < img.shape[1]:
            img_hilbert[point[0], point[1]] = np.abs(img[point[0], point[1]] - img[previous_point[0], previous_point[1]])
            if(img_hilbert[point[0], point[1]] > edge_thr):
                img_edge[point[0], point[1]] = 0
            previous_point = point
    return img_edge[:img.shape[0], :img.shape[1]], 1 - img_hilbert[:img.shape[0], :img.shape[1]]

"""## Transformadas"""

# Genera una imagen en base a la entropía parcial de una imagen en escala de grises
def entropy_transform(img, img_buffer, kernel_size = 32, entropy_thr = 5, progress_bar = False):
    assert kernel_size <= img.shape[0] or kernel_size <= img.shape[1]

    kernel_half_size = int(np.ceil(kernel_size/2))

    img_tr = np.zeros(img.shape)
    img_entropy = np.zeros(img.shape)
    bins = np.histogramdd([0, 1], bins = 256)[1]

    if progress_bar:
        iterator = tqdm(range(img.shape[0] - kernel_size + 1))
    else:
        iterator = range(img.shape[0] - kernel_size + 1)

    for i in iterator:
        for j in range(img.shape[1] - kernel_size + 1):
            if img_buffer[i + kernel_half_size - 1, j + kernel_half_size - 1] > 0:
                img_kernel = img[i:i + kernel_size, j:j + kernel_size]
                img_buffer_kernel = img_buffer[i:i + kernel_size, j:j + kernel_size]
                img_kernel_limited = img_kernel[(img_buffer_kernel > 0)]
                density = np.histogramdd(np.ravel(img_kernel_limited), bins = bins)[0]/img_kernel_limited.size
                density = list(filter(lambda p: p > 0, np.ravel(density)))
                entropy = -np.sum(np.multiply(density, np.log2(density)))
                img_entropy[i + kernel_half_size - 1, j + kernel_half_size - 1] = entropy
                img_tr[i + kernel_half_size - 1, j + kernel_half_size - 1] = float(entropy > entropy_thr)

    return img_tr, img_entropy/8

# Genera una imagen en base a la media parcial de una imagen en escala de grises
def mean_transform(img, img_buffer, kernel_size = 32, mean_thr = 0.1, progress_bar = False):
    assert kernel_size <= img.shape[0] or kernel_size <= img.shape[1]

    kernel_half_size = int(np.ceil(kernel_size/2))

    img_tr = np.zeros(img.shape)
    img_mean = np.zeros(img.shape)

    if progress_bar:
        iterator = tqdm(range(img.shape[0] - kernel_half_size))
    else:
        iterator = range(img.shape[0] - kernel_half_size)

    for i in iterator:
        for j in range(img.shape[1] - kernel_half_size):
            if img_buffer[i + kernel_half_size - 1, j + kernel_half_size - 1] > 0:
                img_kernel = img[i:i + kernel_size, j:j + kernel_size]
                img_buffer_kernel = img_buffer[i:i + kernel_size, j:j + kernel_size]
                img_kernel_limited = img_kernel[(img_buffer_kernel > 0)]
                mean = np.mean(img_kernel_limited)
                img_mean[i + kernel_half_size - 1, j + kernel_half_size - 1] = mean
                img_tr[i + kernel_half_size - 1, j + kernel_half_size - 1] = float(mean < mean_thr)

    return img_tr, img_mean

"""## Contorno"""

# Marca el contorno de las imágenes binarias
def outline(img_bn, img_source, widen_n = 4, color = 1):
    assert color == 0 or color == 1 or color == 2
    img_bn_edge = hilbert_img(img_bn)[0]

    widen_img = img_bn_edge.copy()
    for it in range(widen_n):
        for i in range(1, img_bn_edge.shape[0] - 1):
            for j in range(1, img_bn_edge.shape[1] - 1):
                if img_bn_edge[i, j] == 0:
                    widen_img[i - 1, j] = 0
                    widen_img[i, j - 1] = 0
                    widen_img[i + 1, j] = 0
                    widen_img[i, j + 1] = 0
        img_bn_edge = widen_img.copy()

    if img_source.shape[2] == 4:
        outline_img = rgba2rgb(img_source)
    else:
        outline_img = img_source.copy()

    border_index = (img_bn_edge == 0).nonzero()
    outline_img[border_index[0], border_index[1], :] = 0
    outline_img[border_index[0], border_index[1], color] = 255 if np.max(outline_img) > 1 else 1

    return outline_img
