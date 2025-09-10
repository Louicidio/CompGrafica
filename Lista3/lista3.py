import numpy as np
import cv2 
from matplotlib import pyplot as plt

img1 = cv2.imread('arara.png', 0)
img2 = cv2.imread('barra1.png', 0)
img3 = cv2.imread('barra2.png', 0)
img4 = cv2.imread('barra3.png', 0)
img5 = cv2.imread('barra4.png', 0)
img6 = cv2.imread('teste.tif', 0)
img7 = cv2.imread('img_aluno.jpg', 0)


F1s = cv2.dft(np.float32(img1),flags = cv2.DFT_COMPLEX_OUTPUT)
F2s = cv2.dft(np.float32(img2),flags = cv2.DFT_COMPLEX_OUTPUT)
F3s = cv2.dft(np.float32(img3),flags = cv2.DFT_COMPLEX_OUTPUT)
F4s = cv2.dft(np.float32(img4),flags = cv2.DFT_COMPLEX_OUTPUT)
F5s = cv2.dft(np.float32(img5),flags = cv2.DFT_COMPLEX_OUTPUT)
F6s = cv2.dft(np.float32(img6),flags = cv2.DFT_COMPLEX_OUTPUT)
F7s = cv2.dft(np.float32(img7),flags = cv2.DFT_COMPLEX_OUTPUT)

n2 = F1s.shape[0]//2
m2 = F1s.shape[1]//2

n2 = F2s.shape[0]//2
m2 = F2s.shape[1]//2

n2 = F3s.shape[0]//2
m2 = F3s.shape[1]//2

n2 = F4s.shape[0]//2
m2 = F4s.shape[1]//2

n2 = F5s.shape[0]//2
m2 = F5s.shape[1]//2

n2 = F6s.shape[0]//2
m2 = F6s.shape[1]//2

n2 = F7s.shape[0]//2
m2 = F7s.shape[1]//2

dft_shift1 = np.fft.fftshift(F1s)
dft_shift2 = np.fft.fftshift(F2s)
dft_shift3 = np.fft.fftshift(F3s)
dft_shift4 = np.fft.fftshift(F4s)
dft_shift5 = np.fft.fftshift(F5s)
dft_shift6 = np.fft.fftshift(F6s)
dft_shift7 = np.fft.fftshift(F7s)

magnitude_spectrum1 = 20*np.log(cv2.magnitude(dft_shift1[:,:,0],dft_shift1[:,:,1]))
magnitude_spectrum2 = 20*np.log(cv2.magnitude(dft_shift2[:,:,0],dft_shift2[:,:,1]))
magnitude_spectrum3 = 20*np.log(cv2.magnitude(dft_shift3[:,:,0],dft_shift3[:,:,1]))
magnitude_spectrum4 = 20*np.log(cv2.magnitude(dft_shift4[:,:,0],dft_shift4[:,:,1]))
magnitude_spectrum5 = 20*np.log(cv2.magnitude(dft_shift5[:,:,0],dft_shift5[:,:,1]))
magnitude_spectrum6 = 20*np.log(cv2.magnitude(dft_shift6[:,:,0],dft_shift6[:,:,1]))
magnitude_spectrum7 = 20*np.log(cv2.magnitude(dft_shift7[:,:,0],dft_shift7[:,:,1]))

plt.figure(figsize=(12,8)) 
plt.subplot(241)
plt.imshow(img1, cmap="gray"); plt.axis('off'); plt.title('Original 1')
plt.subplot(242)
plt.imshow(img2, cmap="gray"); plt.axis('off'); plt.title('Original 2')
plt.subplot(243)
plt.imshow(img3, cmap="gray"); plt.axis('off'); plt.title('Original 3')
plt.subplot(244)
plt.imshow(img4, cmap="gray"); plt.axis('off'); plt.title('Original 4')
plt.subplot(245)
plt.imshow(magnitude_spectrum1, cmap="gray"); plt.axis('off'); plt.title('Filtered 1')
plt.subplot(246)
plt.imshow(magnitude_spectrum2, cmap="gray"); plt.axis('off'); plt.title('Filtered 2')
plt.subplot(247)
plt.imshow(magnitude_spectrum3, cmap="gray"); plt.axis('off'); plt.title('Filtered 3')
plt.subplot(248)
plt.imshow(magnitude_spectrum4, cmap="gray"); plt.axis('off'); plt.title('Filtered 4')
plt.show()
plt.figure(figsize=(12,6)) 
plt.subplot(231)
plt.imshow(img5, cmap="gray"); plt.axis('off'); plt.title('Original 5')
plt.subplot(232)
plt.imshow(img6, cmap="gray"); plt.axis('off'); plt.title('Original 6')
plt.subplot(233)
plt.imshow(img7, cmap="gray"); plt.axis('off'); plt.title('Original 7')
plt.subplot(234)
plt.imshow(magnitude_spectrum5, cmap="gray"); plt.axis('off'); plt.title('Filtered 5')
plt.subplot(235)
plt.imshow(magnitude_spectrum6, cmap="gray"); plt.axis('off'); plt.title('Filtered 6')
plt.subplot(236)
plt.imshow(magnitude_spectrum7, cmap="gray"); plt.axis('off'); plt.title('Filtered 7')
plt.show()

def show_result(img, filtered, title1="Original", title2="Filtrada"):
    plt.figure(figsize=(10,5))
    plt.subplot(121), plt.imshow(img, cmap="gray"), plt.title(title1), plt.axis("off")
    plt.subplot(122), plt.imshow(filtered, cmap="gray"), plt.title(title2), plt.axis("off")
    plt.show()

def dft_image(img):
    F = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    return np.fft.fftshift(F)

def idft_image(F_shift):
    F_ishift = np.fft.ifftshift(F_shift)
    img_back = cv2.idft(F_ishift)
    return cv2.magnitude(img_back[:,:,0], img_back[:,:,1])

def gaussian_filter(shape, cutoff, highpass=False):
    rows, cols = shape
    crow, ccol = rows//2, cols//2
    mask = np.zeros((rows, cols), np.float32)
    for u in range(rows):
        for v in range(cols):
            D = ((u-crow)**2 + (v-ccol)**2)**0.5
            mask[u,v] = np.exp(-(D**2) / (2*(cutoff**2)))
    if highpass:
        mask = 1 - mask
    return mask

def band_filters(shape, D1, D2, reject=False):
    rows, cols = shape
    crow, ccol = rows//2, cols//2
    mask = np.zeros((rows, cols), np.float32)
    for u in range(rows):
        for v in range(cols):
            D = ((u-crow)**2 + (v-ccol)**2)**0.5
            if D1 < D < D2:   # dentro do anel
                mask[u,v] = 0 if reject else 1
            else:
                mask[u,v] = 1 if reject else 0
    return mask

#2
img_teste = cv2.imread("teste.tif", 0)
img_aluno = cv2.imread("img_aluno.jpg", 0)  

for nome, img in [("teste.tif", img_teste), ("img_aluno.jpg", img_aluno)]:
    F = dft_image(img)
    rows, cols = img.shape

    # Passa-baixa gaussiano
    lowpass = gaussian_filter((rows, cols), cutoff=30, highpass=False)
    F_low = F * lowpass[:,:,None]
    img_low = idft_image(F_low)

    # Passa-alta gaussiano
    highpass = gaussian_filter((rows, cols), cutoff=30, highpass=True)
    F_high = F * highpass[:,:,None]
    img_high = idft_image(F_high)

    show_result(img, img_low, f"{nome} - Original", "Passa-baixa Gaussiano")
    show_result(img, img_high, f"{nome} - Original", "Passa-alta Gaussiano")


#3
arara = cv2.imread("arara.png", 0)
mask = cv2.imread("arara_filtro.png", 0)
mask = cv2.resize(mask, (arara.shape[1], arara.shape[0]))
mask = mask / 255.0

F_arara = dft_image(arara)
F_arara_filt = F_arara * mask[:,:,None]
arara_filtered = idft_image(F_arara_filt)

show_result(arara, arara_filtered, "Arara original", "Arara filtrada (rejeita-banda)")

#4
for nome, img in [("teste.tif", img_teste), ("img_aluno", img_aluno)]:
    F = dft_image(img)
    rows, cols = img.shape

    # Passa-banda
    pb = band_filters((rows, cols), D1=20, D2=60, reject=False)
    F_pb = F * pb[:,:,None]
    img_pb = idft_image(F_pb)

    # Rejeita-banda
    rb = band_filters((rows, cols), D1=20, D2=60, reject=True)
    F_rb = F * rb[:,:,None]
    img_rb = idft_image(F_rb)

    show_result(img, img_pb, f"{nome} - Original", "Passa-banda")
    show_result(img, img_rb, f"{nome} - Original", "Rejeita-banda")