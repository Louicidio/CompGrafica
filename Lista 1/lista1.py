import numpy as np 
import cv2 
 
def equalizar_histograma(img): 
    if len(img.shape) == 3: 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    return cv2.equalizeHist(img) 
 
def histograma(img): 
    hist = np.zeros(256, dtype=int) 
    for valor in img.flatten(): 
        hist[valor] += 1 
    return hist 
 
def histograma_normalizado(img): 
    hist = histograma(img) 
    return hist / hist.sum() 
 
def histograma_acumulado(img): 
    hist = histograma(img) 
    return np.cumsum(hist) 
 
def histograma_acumulado_normalizado(img): 
    hist_acum = histograma_acumulado(img) 
    return hist_acum / hist_acum[-1] 
 
def mostrar_histograma(hist, titulo='Histograma'): 
    import matplotlib.pyplot as plt 
    plt.figure() 
    plt.title(titulo) 
    plt.xlabel('Intensidade') 
    plt.ylabel('Frequência') 
    plt.plot(hist) 
    plt.xlim([0,255]) 
    plt.show() 
 
 
def planos_de_bits(img, nome='Imagem'): 
    if img is None: 
        print(f"Imagem não carregada: {nome}") 
        return 
    if len(img.shape) == 3: 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    for i in range(8): 
        plano = cv2.bitwise_and(img, 1 << i) 
        plano = np.where(plano > 0, 255, 0).astype(np.uint8) 
        cv2.imshow(f'{nome} - Plano de bit {i}', plano) 
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 
 
def cinza (img): 
    c = img[:,:,0]/3 + img[:,:,1]/3 + img[:,:,2]/3 
    result = c.astype(np.uint8) 
    return result.astype(np.uint8) 
 
def negativo(img): 
    return 255 - img 
 
def normalização(img): 
    return cv2.normalize(img, None, 0, 100, cv2.NORM_MINMAX) 
 
def oplogaritmico(img, c=1): 
    if img is None or np.max(img) == 0: 
        return np.zeros_like(img, dtype=np.uint8) 
    img_float = img.astype(np.float32) 
    c = np.log1p(img_float) * (255 / np.log1p(np.max(img_float))) 
    c = cv2.normalize(c, None, 0, 255, cv2.NORM_MINMAX) 
    return c.astype(np.uint8) 
 
def potencia(img, gamma=2, c=1): 
    img = img / 255.0 
    img = c * (img ** gamma) 
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX) 
    return img.astype(np.uint8) 
 
 
img_unequalized = cv2.imread('unequalized.jpg') 
img_lena = cv2.imread('Aula 2/lena.png') 
img_aluno = cv2.imread('Aula 2/img_aluno.jpg') 
 
 
cinza_img_lena = cinza(img_lena) 
cinza_img_aluno = cinza(img_aluno) 
 
equalizado_lena = equalizar_histograma(cinza_img_lena) 
equalizado_aluno = equalizar_histograma(cinza_img_aluno) 
cv2.imshow('Lena', equalizado_lena) 
cv2.imshow('Aluno', equalizado_aluno) 
cv2.waitKey(0) 
cv2.destroyAllWindows()