"""processamento de videos """

import cv2
import numpy as np
import threading
import pygame
from filtros import Filtros


class ProcessadorVideo:
    def parar_rastreamento(self):
        """Parar o rastreamento de objetos"""
        self.tracking_enabled = False
        self.tracker = None
        self.tracker_bbox = None
    """Classe responsável por processar vídeos e câmera"""
    def __init__(self, music_file=None):
        self.video_capture = None
        self.is_camera_running = False
        self.is_video_file_running = False
        self.video_paused = False
        self.video_after_id = None
        self.video_thread = None
                # Filtros ativos
        self.video_filters = []
                # Rastreamento
        self.tracking_enabled = False
        self.tracker = None
        self.tracker_bbox = None
                # Detecção facial
        self.face_detection_enabled = False
        self.object_detected = False
        self.sound_playing = False
        self.frame_count = 0
        self.detection_interval = 3
        self.last_faces = []
                # Detector de rosto
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.music_file = music_file
        pygame.mixer.init()
        if music_file:
            self.carregar_musica(music_file)
    
    def carregar_musica(self, music_file):
        import os
        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
        else:
            print(f" Arquivo de música não encontrado: {music_file}")
    
    def iniciar_camera(self):
        if not self.is_camera_running:
            self.video_capture = cv2.VideoCapture(0)
            self.is_camera_running = True
            return True
        return False
    
    def carregar_video(self, file_path):
        self.video_capture = cv2.VideoCapture(file_path)
        self.is_video_file_running = True
        self.video_paused = False
        return True
    
    def parar(self):
        self.is_camera_running = False
        self.is_video_file_running = False
        self.video_paused = False
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        self.video_filters.clear()
    
    def pausar_retomar(self):
        self.video_paused = not self.video_paused
        return "pausado" if self.video_paused else "retomado"
    
    def processar_frame_camera(self):
        if not self.is_camera_running:
            return None
        
        ret, frame = self.video_capture.read()
        if not ret:
            return None
        
        # Aplicar filtros
        processed_frame = Filtros.aplicar_filtros(frame, self.video_filters)
        
        # Aplicar rastreamento
        if self.tracking_enabled and self.tracker and self.tracker_bbox:
            processed_frame = self._aplicar_rastreamento(processed_frame)
        
        # Aplicar detecção facial
        if self.face_detection_enabled:
            processed_frame = self._aplicar_deteccao_facial_camera(processed_frame)
        
        return processed_frame
    
    def processar_frame_video(self):
        if not self.is_video_file_running or self.video_paused:
            return None
        
        ret, frame = self.video_capture.read()
        
        if not ret:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return None
        
        # Aplicar filtros
        processed_frame = Filtros.aplicar_filtros(frame, self.video_filters)
        
        # Aplicar rastreamento
        if self.tracker:
            processed_frame = self._aplicar_rastreamento(processed_frame)
        
        # Aplicar detecção facial (otimizado)
        if self.face_detection_enabled:
            processed_frame = self._aplicar_deteccao_facial_video(processed_frame)
        
        return processed_frame
    
    def _aplicar_rastreamento(self, frame):
        success, bbox = self.tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Rastreando", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame
    
    def _aplicar_deteccao_facial_camera(self, frame):
        # Redimensionar para detecção mais rápida
        scale_percent = 50
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        small_frame = cv2.resize(frame, (width, height))
        
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            if not self.object_detected:
                self.object_detected = True
                self.tocar_som()
            
            # Desenhar retângulos nos rostos
            for (x, y, w, h) in faces:
                x_orig = int(x * 100 / scale_percent)
                y_orig = int(y * 100 / scale_percent)
                w_orig = int(w * 100 / scale_percent)
                h_orig = int(h * 100 / scale_percent)
                cv2.rectangle(frame, (x_orig, y_orig), (x_orig + w_orig, y_orig + h_orig), 
                            (255, 0, 0), 2)
                cv2.putText(frame, "DETECTADO", (x_orig, y_orig - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        else:
            if self.object_detected:
                self.object_detected = False
                self.parar_musica()
        
        return frame
    
    def _aplicar_deteccao_facial_video(self, frame):
        self.frame_count += 1
        # Detectar apenas a cada N frames
        if self.frame_count % self.detection_interval == 0:
            scale_percent = 50
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            small_frame = cv2.resize(frame, (width, height))
            
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Escalar coordenadas
            faces_scaled = []
            for (x, y, w, h) in faces:
                x_orig = int(x * 100 / scale_percent)
                y_orig = int(y * 100 / scale_percent)
                w_orig = int(w * 100 / scale_percent)
                h_orig = int(h * 100 / scale_percent)
                faces_scaled.append((x_orig, y_orig, w_orig, h_orig))
            
            self.last_faces = faces_scaled
        
        # Usar última detecção conhecida
        if len(self.last_faces) > 0:
            for (x, y, w, h) in self.last_faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "PULANDO NA MADEIRA", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            if not self.sound_playing:
                self.sound_playing = True
                self.tocar_som()
        else:
            if self.sound_playing:
                self.sound_playing = False
                self.parar_musica()
                self.last_faces = []
        
        return frame
    
    def iniciar_rastreamento(self, frame):
        if frame is not None:
            roi = cv2.selectROI("Selecione o objeto para rastrear", frame, False)
            cv2.destroyWindow("Selecione o objeto para rastrear")
            
            if roi[2] > 0 and roi[3] > 0:
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, roi)
                self.tracker_bbox = roi
                self.tracking_enabled = True
                return True
        return False
    
    def alternar_deteccao_facial(self):
        self.face_detection_enabled = not self.face_detection_enabled
        
        if not self.face_detection_enabled:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        
        return self.face_detection_enabled
    
    def tocar_som(self):
            if self.music_file:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            else:
                print(f"Erro ao tocar som: ")
    
    def parar_musica(self):
        """Parar música"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    
    def limpar_filtros(self):
        """Limpar todos os filtros"""
        self.video_filters.clear()
    
    def adicionar_remover_filtro(self, filter_name):
        """Adicionar ou remover filtro da lista"""
        if filter_name in self.video_filters:
            self.video_filters.remove(filter_name)
            return False  # Filtro removido
        else:
            self.video_filters.append(filter_name)
            return True  # Filtro adicionado
