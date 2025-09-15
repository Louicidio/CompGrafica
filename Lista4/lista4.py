
import cv2
import numpy as np
from matplotlib import pyplot as plt

def medianax3():
    img = cv2.imread('circuito.tif', 0)
    med1 = cv2.medianBlur(img, 3)
    med2 = cv2.medianBlur(med1, 3)
    med3 = cv2.medianBlur(med2, 3)
    cv2.imwrite('circuito_mediana1.png', med1)
    cv2.imwrite('circuito_mediana2.png', med2)
    cv2.imwrite('circuito_mediana3.png', med3)
    plt.figure(figsize=(12,4))
    plt.subplot(141); plt.imshow(img, cmap='gray'); plt.title('Original'); plt.axis('off')
    plt.subplot(142); plt.imshow(med1, cmap='gray'); plt.title('Mediana 1x'); plt.axis('off')
    plt.subplot(143); plt.imshow(med2, cmap='gray'); plt.title('Mediana 2x'); plt.axis('off')
    plt.subplot(144); plt.imshow(med3, cmap='gray'); plt.title('Mediana 3x'); plt.axis('off')
    plt.show()

def pisolados():
    img = cv2.imread('pontos.png', 0)
    kernel = np.array([[1, 1, 1],
                      [1, -8, 1],
                      [1, 1, 1]])
    pontos = cv2.filter2D(img, -1, kernel)
    _, pontos_bin = cv2.threshold(pontos, 200, 255, cv2.THRESH_BINARY)
    cv2.imwrite('pontos_detectados.png', pontos_bin)
    plt.figure(figsize=(10,4))
    plt.subplot(121); plt.imshow(img, cmap='gray'); plt.title('Original'); plt.axis('off')
    plt.subplot(122); plt.imshow(pontos_bin, cmap='gray'); plt.title('Pontos isolados'); plt.axis('off')
    plt.show()

def linhas():
    img = cv2.imread('linhas.png', 0)
   # Templates
    k_h = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
    k_v = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    k_45 = np.array([[0, 1, 1], [-1, 0, 1], [-1, -1, 0]])
    k_135 = np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]])
    # Convoluções
    h = cv2.filter2D(img, -1, k_h)
    v = cv2.filter2D(img, -1, k_v)
    d45 = cv2.filter2D(img, -1, k_45)
    d135 = cv2.filter2D(img, -1, k_135)
    # Limiarização
    _, h_bin = cv2.threshold(h, 50, 255, cv2.THRESH_BINARY)
    _, v_bin = cv2.threshold(v, 50, 255, cv2.THRESH_BINARY)
    _, d45_bin = cv2.threshold(d45, 50, 255, cv2.THRESH_BINARY)
    _, d135_bin = cv2.threshold(d135, 50, 255, cv2.THRESH_BINARY)
    # Combinação OR
    combined = cv2.bitwise_or(h_bin, v_bin)
    combined = cv2.bitwise_or(combined, d45_bin)
    combined = cv2.bitwise_or(combined, d135_bin)
    cv2.imwrite('linhas_horizontal.png', h_bin)
    cv2.imwrite('linhas_vertical.png', v_bin)
    cv2.imwrite('linhas_45.png', d45_bin)
    cv2.imwrite('linhas_135.png', d135_bin)
    cv2.imwrite('linhas_combinadas.png', combined)
    plt.figure(figsize=(15,6))
    plt.subplot(251); plt.imshow(img, cmap='gray'); plt.title('Original'); plt.axis('off')
    plt.subplot(252); plt.imshow(h_bin, cmap='gray'); plt.title('Horizontal'); plt.axis('off')
    plt.subplot(253); plt.imshow(v_bin, cmap='gray'); plt.title('Vertical'); plt.axis('off')
    plt.subplot(254); plt.imshow(d45_bin, cmap='gray'); plt.title('+45°'); plt.axis('off')
    plt.subplot(255); plt.imshow(d135_bin, cmap='gray'); plt.title('-45°'); plt.axis('off')
    plt.subplot(256); plt.imshow(combined, cmap='gray'); plt.title('Combinada'); plt.axis('off')
    plt.show()

def bordas():
    img = cv2.imread('igreja.png', 0)
    edges = cv2.Canny(img, 100, 200)
    cv2.imwrite('igreja_canny.png', edges)
    plt.figure(figsize=(10,4))
    plt.subplot(121); plt.imshow(img, cmap='gray'); plt.title('Original'); plt.axis('off')
    plt.subplot(122); plt.imshow(edges, cmap='gray'); plt.title('Canny'); plt.axis('off')
    plt.show()

def regiao(img, seed, thresh=5):
    output = np.zeros_like(img)
    visited = np.zeros_like(img, dtype=bool)
    h, w = img.shape
    stack = [seed]
    seed_val = img[seed]
    while stack:
        x, y = stack.pop()
        if visited[x, y]:
            continue
        visited[x, y] = True
        if abs(int(img[x, y]) - int(seed_val)) < thresh:
            output[x, y] = 255
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < h and 0 <= ny < w and not visited[nx, ny]:
                        stack.append((nx, ny))
    return output

def exerc5():
    img = cv2.imread('root.jpg', 0)
    seed = (100, 100)
    region = regiao(img, seed, thresh=10)
    cv2.imwrite('root_region.png', region)
    plt.figure(figsize=(10,4))
    plt.subplot(121); plt.imshow(img, cmap='gray'); plt.title('Original'); plt.axis('off')
    plt.subplot(122); plt.imshow(region, cmap='gray'); plt.title('Crescimento de Região'); plt.axis('off')
    plt.show()

def exerc6():
    for nome in ['harewood.jpg', 'nuts.jpg', 'snow.jpg', 'img_aluno.jpg']:
        img = cv2.imread(nome, 0)
        _, otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        cv2.imwrite(f'{nome}_otsu.png', otsu)
        plt.figure(figsize=(8,4))
        plt.subplot(121); plt.imshow(img, cmap='gray'); plt.title(nome); plt.axis('off')
        plt.subplot(122); plt.imshow(otsu, cmap='gray'); plt.title('Otsu'); plt.axis('off')
        plt.show()

# medianax3()
# pisolados()
# linhas()
# bordas()
# exerc5()
exerc6()