import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import pygame
from collections import deque
import time

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Processamento de Imagens e Vídeos")
        self.root.geometry("1400x800")
        
        # Variáveis de estado
        self.current_image = None
        self.original_image = None
        self.video_capture = None
        self.is_camera_running = False
        self.video_thread = None
        self.tracking_enabled = False
        self.tracker = None
        self.tracker_bbox = None
        self.object_detected = False
        
        # Variáveis para vídeo de arquivo
        self.is_video_file_running = False
        self.video_file_path = None
        self.video_paused = False
        self.video_after_id = None  # ID do agendamento after() para vídeo

        # Filtros para aplicar em tempo real no vídeo
        self.video_filters = []  # Lista de filtros ativos no vídeo

        # Variáveis de detecção facial e som
        self.face_detection_active = False
        self.sound_playing = False
        
        # ===== CONFIGURE AQUI O CAMINHO DA MÚSICA =====
        # Coloque o caminho completo do arquivo de música (MP3, WAV ou OGG)
        # Exemplo: r"C:\Users\SeuNome\Musicas\minha_musica.mp3"
        self.music_file = r"C:\Users\Luis Eduardo\Desktop\2025\2 Semestre\CompGrafica\TrabCompGrafica\homelander.wav"  # Altere este caminho para sua música
        # ================================================

        # Inicializar pygame para tocar música
        pygame.mixer.init()
        
        # Carregar música automaticamente se o arquivo existir
        self.load_music_from_path()

        # Detector de objeto (YOLO ou cascade para detecção de pessoa)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Criar interface
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame esquerdo com scrollbar - Controles
        left_container = ttk.Frame(main_frame)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Canvas e scrollbar para os controles
        canvas_controls = tk.Canvas(left_container, width=280)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas_controls.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_controls.configure(yscrollcommand=scrollbar.set)
        
        # Frame para os botões dentro do canvas
        left_frame = ttk.LabelFrame(canvas_controls, text="Controles", padding=10)
        canvas_window = canvas_controls.create_window((0, 0), window=left_frame, anchor="nw")
        
        # Atualizar região de scroll quando o frame mudar de tamanho
        def on_frame_configure(event):
            canvas_controls.configure(scrollregion=canvas_controls.bbox("all"))
        left_frame.bind("<Configure>", on_frame_configure)
        
        # Permitir scroll com mouse wheel
        def on_mousewheel(event):
            canvas_controls.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_controls.bind_all("<MouseWheel>", on_mousewheel)
        
        # Seção: Aquisição de Imagens
        ttk.Label(left_frame, text="AQUISIÇÃO", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="📁 Carregar Imagem", command=self.load_image, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🎬 Carregar Vídeo", command=self.load_video, width=25).pack(pady=2)
        ttk.Button(left_frame, text="📹 Iniciar Câmera", command=self.start_camera, width=25).pack(pady=2)
        ttk.Button(left_frame, text="⏹ Parar Câmera/Vídeo", command=self.stop_camera, width=25).pack(pady=2)
        ttk.Button(left_frame, text="⏸ Pausar/Retomar Vídeo", command=self.toggle_pause_video, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🧹 Limpar Filtros Vídeo", command=self.clear_video_filters, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Seção: Conversões
        ttk.Label(left_frame, text="CONVERSÕES", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="⚪ Níveis de Cinza", command=self.convert_grayscale, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🔄 Negativo", command=self.convert_negative, width=25).pack(pady=2)
        ttk.Button(left_frame, text="⚫ Binária (Otsu)", command=self.convert_binary_otsu, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Seção: Filtros
        ttk.Label(left_frame, text="FILTROS", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="🔲 Média", command=self.apply_mean_filter, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🔳 Mediana", command=self.apply_median_filter, width=25).pack(pady=2)
        ttk.Button(left_frame, text="📐 Canny (Bordas)", command=self.apply_canny, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Seção: Morfologia
        ttk.Label(left_frame, text="MORFOLOGIA", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="➖ Erosão", command=self.apply_erosion, width=25).pack(pady=2)
        ttk.Button(left_frame, text="➕ Dilatação", command=self.apply_dilation, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🔓 Abertura", command=self.apply_opening, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🔒 Fechamento", command=self.apply_closing, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Seção: Análise
        ttk.Label(left_frame, text="ANÁLISE", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="📊 Histograma", command=self.show_histogram, width=25).pack(pady=2)
        ttk.Button(left_frame, text="📏 Métricas", command=self.calculate_metrics, width=25).pack(pady=2)
        ttk.Button(left_frame, text="🔢 Contar Objetos", command=self.count_objects, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Seção: Rastreamento
        ttk.Label(left_frame, text="RASTREAMENTO", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(left_frame, text="🎯 Iniciar Rastreamento", command=self.init_tracking, width=25).pack(pady=2)
        ttk.Button(left_frame, text="👤 Detectar Rosto + Música", command=self.toggle_face_detection, width=25).pack(pady=2)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Botão de reset
        ttk.Button(left_frame, text="🔄 Resetar Imagem", command=self.reset_image, width=25).pack(pady=10)
        
        # Frame direito - Display
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas para exibir imagem
        self.canvas = tk.Canvas(right_frame, bg='gray', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        self.status_label = ttk.Label(right_frame, text="Carregue uma imagem ou inicie a câmera", 
                                      relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
    def load_image(self):
        """Carregar imagem de arquivo"""
        # Parar vídeo se estiver rodando
        if self.is_camera_running or self.is_video_file_running:
            self.stop_camera()
        
        file_path = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.display_image(self.current_image)
                self.status_label.config(text=f"Imagem carregada: {file_path}")
            else:
                messagebox.showerror("Erro", "Não foi possível carregar a imagem")
    
    def load_video(self):
        """Carregar vídeo de arquivo"""
        # Parar câmera/vídeo se estiver rodando
        if self.is_camera_running or self.is_video_file_running:
            self.stop_camera()
        
        file_path = filedialog.askopenfilename(
            title="Selecione um vídeo",
            filetypes=[
                ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            self.video_file_path = file_path
            self.video_capture = cv2.VideoCapture(file_path)
            
            if self.video_capture.isOpened():
                self.is_video_file_running = True
                self.video_paused = False
                # Usar after() em vez de thread para melhor desempenho
                self.update_video_file()
                self.status_label.config(text=f"Vídeo carregado: {file_path}")
            else:
                messagebox.showerror("Erro", "Não foi possível carregar o vídeo")
                self.video_file_path = None
                
    def start_camera(self):
        """Iniciar captura de vídeo da câmera"""
        if not self.is_camera_running:
            self.video_capture = cv2.VideoCapture(0)
            if self.video_capture.isOpened():
                self.is_camera_running = True
                self.video_thread = threading.Thread(target=self.update_camera, daemon=True)
                self.video_thread.start()
                self.status_label.config(text="Câmera iniciada")
            else:
                messagebox.showerror("Erro", "Não foi possível acessar a câmera")
                
    def stop_camera(self):
        """Parar captura de câmera ou vídeo"""
        self.is_camera_running = False
        self.is_video_file_running = False
        self.video_paused = False
        
        # Cancelar agendamento de vídeo se existir
        if self.video_after_id:
            self.root.after_cancel(self.video_after_id)
            self.video_after_id = None
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        self.video_file_path = None
        self.video_filters.clear()  # Limpar filtros ao parar câmera/vídeo
        self.status_label.config(text="Câmera/Vídeo parado")
    
    def toggle_pause_video(self):
        """Pausar/retomar reprodução de vídeo"""
        if not self.is_video_file_running:
            messagebox.showinfo("Aviso", "Nenhum vídeo está sendo reproduzido")
            return
        
        self.video_paused = not self.video_paused
        status = "pausado" if self.video_paused else "retomado"
        self.status_label.config(text=f"Vídeo {status}")
    
    def update_video_file(self):
        """Atualizar frames do vídeo de arquivo com filtros aplicados"""
        if not self.is_video_file_running:
            return
            
        if not self.video_paused:
            ret, frame = self.video_capture.read()
            
            if not ret:
                # Reiniciar vídeo quando terminar
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                # Aplicar filtros selecionados
                processed_frame = frame.copy()
                for filter_name in self.video_filters:
                    if filter_name == 'grayscale':
                        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'negative':
                        processed_frame = cv2.bitwise_not(processed_frame)
                    elif filter_name == 'binary':
                        gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        processed_frame = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'mean':
                        processed_frame = cv2.blur(processed_frame, (5, 5))
                    elif filter_name == 'median':
                        processed_frame = cv2.medianBlur(processed_frame, 5)
                    elif filter_name == 'canny':
                        gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        edges = cv2.Canny(gray, 100, 200)
                        processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'erosion':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.erode(processed_frame, kernel, iterations=1)
                    elif filter_name == 'dilation':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.dilate(processed_frame, kernel, iterations=1)
                    elif filter_name == 'opening':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.morphologyEx(processed_frame, cv2.MORPH_OPEN, kernel)
                    elif filter_name == 'closing':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.morphologyEx(processed_frame, cv2.MORPH_CLOSE, kernel)
                
                # Aplicar rastreamento se ativo
                if self.tracker:
                    success, box = self.tracker.update(processed_frame)
                    if success:
                        x, y, w, h = [int(v) for v in box]
                        cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Aplicar detecção facial se ativa
                if self.face_detection_active:
                    gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) > 0:
                        for (x, y, w, h) in faces:
                            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            cv2.putText(processed_frame, "ROSTO DETECTADO!", (x, y - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        
                        if not self.sound_playing:
                            self.sound_playing = True
                            self.play_sound()
                    else:
                        if self.sound_playing:
                            self.sound_playing = False
                            self.stop_music()
                
                self.display_image(processed_frame)
        
        # Agendar próxima atualização (30 FPS = ~33ms por frame)
        self.video_after_id = self.root.after(20, self.update_video_file)

    def clear_video_filters(self):
        """Limpar todos os filtros aplicados ao vídeo"""
        if not self.is_camera_running and not self.is_video_file_running:
            messagebox.showinfo("Info", "Inicie a câmera ou carregue um vídeo para usar filtros")
            return
        
        self.video_filters.clear()
        self.status_label.config(text="Todos os filtros do vídeo foram removidos")
        
    def update_camera(self):
        """Atualizar frame da câmera continuamente"""
        while self.is_camera_running:
            ret, frame = self.video_capture.read()
            if ret:
                # Aplicar filtros em tempo real
                processed_frame = frame.copy()
                
                for filter_name in self.video_filters:
                    if filter_name == 'grayscale':
                        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'negative':
                        processed_frame = 255 - processed_frame
                    elif filter_name == 'binary':
                        gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        processed_frame = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'mean':
                        processed_frame = cv2.blur(processed_frame, (5, 5))
                    elif filter_name == 'median':
                        processed_frame = cv2.medianBlur(processed_frame, 5)
                    elif filter_name == 'canny':
                        gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                        edges = cv2.Canny(gray, 100, 200)
                        processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                    elif filter_name == 'erosion':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.erode(processed_frame, kernel, iterations=1)
                    elif filter_name == 'dilation':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.dilate(processed_frame, kernel, iterations=1)
                    elif filter_name == 'opening':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.morphologyEx(processed_frame, cv2.MORPH_OPEN, kernel)
                    elif filter_name == 'closing':
                        kernel = np.ones((5, 5), np.uint8)
                        processed_frame = cv2.morphologyEx(processed_frame, cv2.MORPH_CLOSE, kernel)
                
                # Aplicar rastreamento se habilitado
                if self.tracking_enabled and self.tracker and self.tracker_bbox:
                    success, bbox = self.tracker.update(processed_frame)
                    if success:
                        x, y, w, h = [int(v) for v in bbox]
                        cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(processed_frame, "Rastreando", (x, y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Detecção de rosto
                if hasattr(self, 'face_detection_enabled') and self.face_detection_enabled:
                    gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) > 0:
                        if not self.object_detected:
                            # Rosto detectado - tocar música
                            self.object_detected = True
                            self.play_sound()
                        
                        for (x, y, w, h) in faces:
                            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            cv2.putText(processed_frame, "ROSTO DETECTADO!", (x, y - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    else:
                        if self.object_detected:
                            self.object_detected = False
                            self.stop_music()
                
                self.current_image = processed_frame
                self.display_image(processed_frame)
                
    def display_image(self, image):
        """Exibir imagem no canvas"""
        if image is None:
            return
            
        # Converter BGR para RGB
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Redimensionar para caber no canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            h, w = image_rgb.shape[:2]
            scale = min(canvas_width / w, canvas_height / h)
            new_w, new_h = int(w * scale), int(h * scale)
            image_resized = cv2.resize(image_rgb, (new_w, new_h))
            
            # Converter para ImageTk
            image_pil = Image.fromarray(image_resized)
            image_tk = ImageTk.PhotoImage(image_pil)
            
            # Atualizar canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                    image=image_tk, anchor=tk.CENTER)
            self.canvas.image = image_tk  # Manter referência
            
    def convert_grayscale(self):
        """Converter para níveis de cinza"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera ou vídeo, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'grayscale' in self.video_filters:
                self.video_filters.remove('grayscale')
                self.status_label.config(text="Filtro de níveis de cinza desativado no vídeo")
            else:
                self.video_filters.append('grayscale')
                self.status_label.config(text="Filtro de níveis de cinza ativado no vídeo")
            return
            
        # Para imagens estáticas
        if len(self.current_image.shape) == 3:
            self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            self.display_image(self.current_image)
            self.status_label.config(text="Convertido para níveis de cinza")
        else:
            messagebox.showinfo("Info", "A imagem já está em níveis de cinza")
            
    def convert_negative(self):
        """Converter para negativo"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera ou vídeo, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'negative' in self.video_filters:
                self.video_filters.remove('negative')
                self.status_label.config(text="Filtro negativo desativado no vídeo")
            else:
                self.video_filters.append('negative')
                self.status_label.config(text="Filtro negativo ativado no vídeo")
            return
            
        # Para imagens estáticas
        self.current_image = 255 - self.current_image
        self.display_image(self.current_image)
        self.status_label.config(text="Negativo aplicado")
        
    def convert_binary_otsu(self):
        """Converter para binária usando Otsu"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera ou vídeo, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'binary' in self.video_filters:
                self.video_filters.remove('binary')
                self.status_label.config(text="Filtro binário desativado no vídeo")
            else:
                self.video_filters.append('binary')
                self.status_label.config(text="Filtro binário ativado no vídeo")
            return
            
        # Para imagens estáticas
        # Converter para cinza se necessário
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
            
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.current_image = binary
        self.display_image(self.current_image)
        self.status_label.config(text="Limiarização por Otsu aplicada")
        
    def apply_mean_filter(self):
        """Aplicar filtro de média"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'mean' in self.video_filters:
                self.video_filters.remove('mean')
                self.status_label.config(text="Filtro de média desativado no vídeo")
            else:
                self.video_filters.append('mean')
                self.status_label.config(text="Filtro de média ativado no vídeo")
            return
            
        # Para imagens estáticas
        self.current_image = cv2.blur(self.current_image, (5, 5))
        self.display_image(self.current_image)
        self.status_label.config(text="Filtro de média aplicado")
        
    def apply_median_filter(self):
        """Aplicar filtro de mediana"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'median' in self.video_filters:
                self.video_filters.remove('median')
                self.status_label.config(text="Filtro de mediana desativado no vídeo")
            else:
                self.video_filters.append('median')
                self.status_label.config(text="Filtro de mediana ativado no vídeo")
            return
            
        # Para imagens estáticas
        self.current_image = cv2.medianBlur(self.current_image, 5)
        self.display_image(self.current_image)
        self.status_label.config(text="Filtro de mediana aplicado")
        
    def apply_canny(self):
        """Aplicar detector de bordas Canny"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'canny' in self.video_filters:
                self.video_filters.remove('canny')
                self.status_label.config(text="Detector Canny desativado no vídeo")
            else:
                self.video_filters.append('canny')
                self.status_label.config(text="Detector Canny ativado no vídeo")
            return
            
        # Para imagens estáticas
        # Converter para cinza se necessário
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
            
        edges = cv2.Canny(gray, 100, 200)
        self.current_image = edges
        self.display_image(self.current_image)
        self.status_label.config(text="Detector de bordas Canny aplicado")
        
    def apply_erosion(self):
        """Aplicar erosão"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'erosion' in self.video_filters:
                self.video_filters.remove('erosion')
                self.status_label.config(text="Erosão desativada no vídeo")
            else:
                self.video_filters.append('erosion')
                self.status_label.config(text="Erosão ativada no vídeo")
            return
            
        # Para imagens estáticas
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.erode(self.current_image, kernel, iterations=1)
        self.display_image(self.current_image)
        self.status_label.config(text="Erosão aplicada")
        
    def apply_dilation(self):
        """Aplicar dilatação"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'dilation' in self.video_filters:
                self.video_filters.remove('dilation')
                self.status_label.config(text="Dilatação desativada no vídeo")
            else:
                self.video_filters.append('dilation')
                self.status_label.config(text="Dilatação ativada no vídeo")
            return
            
        # Para imagens estáticas
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.dilate(self.current_image, kernel, iterations=1)
        self.display_image(self.current_image)
        self.status_label.config(text="Dilatação aplicada")
        
    def apply_opening(self):
        """Aplicar abertura"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'opening' in self.video_filters:
                self.video_filters.remove('opening')
                self.status_label.config(text="Abertura desativada no vídeo")
            else:
                self.video_filters.append('opening')
                self.status_label.config(text="Abertura ativada no vídeo")
            return
            
        # Para imagens estáticas
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.morphologyEx(self.current_image, cv2.MORPH_OPEN, kernel)
        self.display_image(self.current_image)
        self.status_label.config(text="Abertura aplicada")
        
    def apply_closing(self):
        """Aplicar fechamento"""
        if self.current_image is None and not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Carregue uma imagem, vídeo ou inicie a câmera primeiro")
            return
        
        # Se estiver com câmera, adicionar/remover filtro em tempo real
        if self.is_camera_running or self.is_video_file_running:
            if 'closing' in self.video_filters:
                self.video_filters.remove('closing')
                self.status_label.config(text="Fechamento desativado no vídeo")
            else:
                self.video_filters.append('closing')
                self.status_label.config(text="Fechamento ativado no vídeo")
            return
            
        # Para imagens estáticas
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.morphologyEx(self.current_image, cv2.MORPH_CLOSE, kernel)
        self.display_image(self.current_image)
        self.status_label.config(text="Fechamento aplicado")
        
    def show_histogram(self):
        """Mostrar histograma"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 4))
        
        if len(self.current_image.shape) == 2:
            # Imagem em cinza
            hist = cv2.calcHist([self.current_image], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
            plt.title('Histograma - Níveis de Cinza')
            plt.xlabel('Intensidade')
            plt.ylabel('Frequência')
        else:
            # Imagem colorida
            colors = ('b', 'g', 'r')
            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.current_image], [i], None, [256], [0, 256])
                plt.plot(hist, color=color, label=f'Canal {color.upper()}')
            plt.title('Histograma - Imagem Colorida')
            plt.xlabel('Intensidade')
            plt.ylabel('Frequência')
            plt.legend()
            
        plt.grid(True, alpha=0.3)
        plt.show()
        self.status_label.config(text="Histograma exibido")
        
    def calculate_metrics(self):
        """Calcular área, perímetro e diâmetro em imagem binária"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        # Verificar se é binária
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
            
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            messagebox.showinfo("Info", "Nenhum objeto encontrado na imagem")
            return
            
        # Calcular métricas para cada contorno
        result_text = "MÉTRICAS DOS OBJETOS:\n\n"
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 100:  # Filtrar objetos muito pequenos
                perimeter = cv2.arcLength(contour, True)
                
                # Calcular diâmetro (círculo equivalente)
                equivalent_diameter = np.sqrt(4 * area / np.pi)
                
                result_text += f"Objeto {i + 1}:\n"
                result_text += f"  Área: {area:.2f} pixels²\n"
                result_text += f"  Perímetro: {perimeter:.2f} pixels\n"
                result_text += f"  Diâmetro equivalente: {equivalent_diameter:.2f} pixels\n\n"
                
        messagebox.showinfo("Métricas", result_text)
        self.status_label.config(text=f"Métricas calculadas para {len(contours)} objetos")
        
    def count_objects(self):
        """Contar objetos usando crescimento de região"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        # Converter para binária
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
            
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Implementar contagem por crescimento de região
        visited = np.zeros_like(binary, dtype=bool)
        object_count = 0
        h, w = binary.shape
        
        def region_growing(start_y, start_x):
            """Algoritmo de crescimento de região"""
            queue = deque([(start_y, start_x)])
            visited[start_y, start_x] = True
            
            while queue:
                y, x = queue.popleft()
                
                # Verificar vizinhos (8-conectividade)
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                            
                        ny, nx = y + dy, x + dx
                        
                        if (0 <= ny < h and 0 <= nx < w and 
                            not visited[ny, nx] and binary[ny, nx] == 255):
                            visited[ny, nx] = True
                            queue.append((ny, nx))
        
        # Percorrer imagem procurando objetos
        for y in range(h):
            for x in range(w):
                if binary[y, x] == 255 and not visited[y, x]:
                    region_growing(y, x)
                    object_count += 1
        
        # Criar imagem colorida para mostrar objetos contados
        colored = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(colored, contours, -1, (0, 255, 0), 2)
        
        # Numerar objetos
        for i, contour in enumerate(contours):
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(colored, str(i + 1), (cx, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        self.current_image = colored
        self.display_image(self.current_image)
        
        messagebox.showinfo("Contagem de Objetos", 
                           f"Total de objetos encontrados: {object_count}")
        self.status_label.config(text=f"Objetos contados: {object_count}")
        
    def init_tracking(self):
        """Inicializar rastreamento de objeto"""
        if not self.is_camera_running:
            messagebox.showwarning("Aviso", "Inicie a câmera primeiro")
            return
            
        # Selecionar ROI
        if self.current_image is not None:
            roi = cv2.selectROI("Selecione o objeto para rastrear", self.current_image, False)
            cv2.destroyWindow("Selecione o objeto para rastrear")
            
            if roi[2] > 0 and roi[3] > 0:
                # Criar tracker (usando CSRT - mais preciso)
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(self.current_image, roi)
                self.tracker_bbox = roi
                self.tracking_enabled = True
                self.status_label.config(text="Rastreamento iniciado")
            else:
                messagebox.showwarning("Aviso", "ROI inválida")
                
    def toggle_face_detection(self):
        """Alternar detecção de rosto com música"""
        if not self.is_camera_running and not self.is_video_file_running:
            messagebox.showwarning("Aviso", "Inicie a câmera ou carregue um vídeo primeiro")
            return
            
        if not hasattr(self, 'face_detection_enabled'):
            self.face_detection_enabled = False
            
        self.face_detection_enabled = not self.face_detection_enabled
        
        if self.face_detection_enabled:
            self.status_label.config(text="Detecção de rosto ATIVADA (música ao detectar)")
        else:
            self.status_label.config(text="Detecção de rosto DESATIVADA")
            # Parar música se estiver tocando
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
    
    def load_music_from_path(self):
        """Carregar música do caminho definido no código"""
        if self.music_file:
            try:
                import os
                if os.path.exists(self.music_file):
                    pygame.mixer.music.load(self.music_file)
                    print(f"✅ Música carregada: {self.music_file}")
                else:
                    print(f"⚠️ Arquivo de música não encontrado: {self.music_file}")
                    print(f"   O sistema usará beep quando detectar rosto.")
                    print(f"   Altere o caminho da música na linha ~40 do código (self.music_file)")
            except Exception as e:
                print(f"❌ Erro ao carregar música: {e}")
                print(f"   O sistema usará beep quando detectar rosto.")
            
    def play_sound(self):
        """Tocar música quando objeto detectado"""
        try:
            if self.music_file:
                # Se há arquivo de música carregado, tocar
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)  # -1 = loop infinito
                    print(f"🎵 ROSTO DETECTADO - Tocando música!")
            else:
                # Se não há música, tocar beep
                frequency = 440  # Hz
                duration = 500  # ms (reduzido para 500ms)
                
                # Gerar tom
                sample_rate = 22050
                n_samples = int(round(duration * sample_rate / 1000))
                
                buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate)
                buf = (buf * 32767).astype(np.int16)
                
                # Stereo
                buf = np.column_stack((buf, buf))
                
                sound = pygame.sndarray.make_sound(buf)
                sound.play()
                
                print("🎵 ROSTO DETECTADO - Som beep tocado (carregue uma música para tocar)")
            
        except Exception as e:
            print(f"Erro ao tocar som: {e}")
    
    def stop_music(self):
        """Parar música quando não detectar mais rosto"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("🔇 Música parada - Nenhum rosto detectado")
            
    def reset_image(self):
        """Resetar para imagem original"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            self.status_label.config(text="Imagem resetada para original")
        else:
            messagebox.showinfo("Info", "Nenhuma imagem original para resetar")
            
    def __del__(self):
        """Limpeza ao fechar"""
        self.stop_camera()
        pygame.mixer.quit()


def main():
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
