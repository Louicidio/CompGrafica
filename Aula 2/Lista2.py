import numpy as np
import cv2
import matplotlib.pyplot as plt

def mean_filter(img, window_size=3):
    """
    Aplica filtro de suavização pela média da vizinhança.
    img: imagem numpy array (grayscale)
    window_size: tamanho da janela (ímpar)
    """
    if window_size % 2 == 0:
        raise ValueError("O tamanho da janela deve ser ímpar.")
    kernel = np.ones((window_size, window_size), dtype=np.float32) / (window_size * window_size)
    return cv2.filter2D(img, -1, kernel)

# Exemplo de uso:
img = cv2.imread("lena.png")
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

window_size = 5  # você pode alterar para 3, 7, etc.
img_filtered = mean_filter(img_gray, window_size)

plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(img_gray, cmap="gray")
plt.title("Original")
plt.axis('off')
plt.subplot(1,2,2)
plt.imshow(img_filtered, cmap="gray")
plt.title(f"Filtro média {window_size}x{window_size}")
plt.axis('off')
plt.show()

