""" filtros das imagens """
import cv2
import numpy as np

class Filtros:
    """Classe responsável por aplicar filtros em imagens"""
    @staticmethod
    def aplicar_filtros(frame, lista_filtros):
        processed_frame = frame.copy()
        
        for filter_name in lista_filtros:
            if filter_name == 'grayscale':
                processed_frame = Filtros.niveis_cinza(processed_frame)
            elif filter_name == 'negative':
                processed_frame = Filtros.negativo(processed_frame)
            elif filter_name == 'binary':
                processed_frame = Filtros.binario_otsu(processed_frame)
            elif filter_name == 'mean':
                processed_frame = Filtros.media(processed_frame)
            elif filter_name == 'median':
                processed_frame = Filtros.mediana(processed_frame)
            elif filter_name == 'canny':
                processed_frame = Filtros.canny(processed_frame)
            elif filter_name == 'erosion':
                processed_frame = Filtros.erosao(processed_frame)
            elif filter_name == 'dilation':
                processed_frame = Filtros.dilatacao(processed_frame)
            elif filter_name == 'opening':
                processed_frame = Filtros.abertura(processed_frame)
            elif filter_name == 'closing':
                processed_frame = Filtros.fechamento(processed_frame)
        
        return processed_frame
    
    @staticmethod
    def niveis_cinza(image):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return image
    
    @staticmethod
    def negativo(image):
        return cv2.bitwise_not(image)
    
    @staticmethod
    def binario_otsu(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def media(image):
        return cv2.blur(image, (5, 5))
    
    @staticmethod
    def mediana(image):
        return cv2.medianBlur(image, 5)
    
    @staticmethod
    def canny(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    @staticmethod
    def erosao(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)
    
    @staticmethod
    def dilatacao(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)
    
    @staticmethod
    def abertura(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    
    @staticmethod
    def fechamento(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
