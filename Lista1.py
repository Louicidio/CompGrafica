import cv2
import numpy as np


def cinza (img):
    c = img[:,:,0]/3 + img[:,:,1]/3 + img[:,:,2]/3
    result = c.astype(np.uint8)
    return result.astype(np.uint8)

def negativo(img):
    return 255 - img

def normalização(img):
    return cv2.normalize(img, None, 0, 100, cv2.NORM_MINMAX)

def oplogaritmico(img, c=1):
    c = np.log(1 + img) * (255 / np.log(1 + np.max(img))).astype(np.uint8)
    return c.astype(np.uint8)

img = cv2.imread('lena.png')
cv2.imshow('Edit', oplogaritmico(img))
cv2.waitKey(0)
cv2.destroyAllWindows()