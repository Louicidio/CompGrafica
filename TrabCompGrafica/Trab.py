import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import pygame
from collections import deque

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
        
        # Inicializar pygame para tocar música
        pygame.mixer.init()
        
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
        ttk.Button(left_frame, text="📹 Iniciar Câmera", command=self.start_camera, width=25).pack(pady=2)
        ttk.Button(left_frame, text="⏹ Parar Câmera", command=self.stop_camera, width=25).pack(pady=2)
        
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
        ttk.Button(left_frame, text="🎵 Detectar Rosto + Música", command=self.toggle_face_detection, width=25).pack(pady=2)
        
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
        """Parar captura de vídeo"""
        self.is_camera_running = False
        if self.video_capture:
            self.video_capture.release()
        self.status_label.config(text="Câmera parada")
        
    def update_camera(self):
        """Atualizar frame da câmera continuamente"""
        while self.is_camera_running:
            ret, frame = self.video_capture.read()
            if ret:
                # Aplicar rastreamento se habilitado
                if self.tracking_enabled and self.tracker and self.tracker_bbox:
                    success, bbox = self.tracker.update(frame)
                    if success:
                        x, y, w, h = [int(v) for v in bbox]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, "Rastreando", (x, y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Detecção de rosto
                if hasattr(self, 'face_detection_enabled') and self.face_detection_enabled:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) > 0 and not self.object_detected:
                        # Rosto detectado - tocar música
                        self.object_detected = True
                        threading.Thread(target=self.play_sound, daemon=True).start()
                        
                    if len(faces) == 0:
                        self.object_detected = False
                    
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        cv2.putText(frame, "ROSTO DETECTADO!", (x, y - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                
                self.current_image = frame
                self.display_image(frame)
                
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
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        if len(self.current_image.shape) == 3:
            self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            self.display_image(self.current_image)
            self.status_label.config(text="Convertido para níveis de cinza")
        else:
            messagebox.showinfo("Info", "A imagem já está em níveis de cinza")
            
    def convert_negative(self):
        """Converter para negativo"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        self.current_image = 255 - self.current_image
        self.display_image(self.current_image)
        self.status_label.config(text="Negativo aplicado")
        
    def convert_binary_otsu(self):
        """Converter para binária usando Otsu"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
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
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        self.current_image = cv2.blur(self.current_image, (5, 5))
        self.display_image(self.current_image)
        self.status_label.config(text="Filtro de média aplicado")
        
    def apply_median_filter(self):
        """Aplicar filtro de mediana"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        self.current_image = cv2.medianBlur(self.current_image, 5)
        self.display_image(self.current_image)
        self.status_label.config(text="Filtro de mediana aplicado")
        
    def apply_canny(self):
        """Aplicar detector de bordas Canny"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
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
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.erode(self.current_image, kernel, iterations=1)
        self.display_image(self.current_image)
        self.status_label.config(text="Erosão aplicada")
        
    def apply_dilation(self):
        """Aplicar dilatação"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.dilate(self.current_image, kernel, iterations=1)
        self.display_image(self.current_image)
        self.status_label.config(text="Dilatação aplicada")
        
    def apply_opening(self):
        """Aplicar abertura"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
        kernel = np.ones((5, 5), np.uint8)
        self.current_image = cv2.morphologyEx(self.current_image, cv2.MORPH_OPEN, kernel)
        self.display_image(self.current_image)
        self.status_label.config(text="Abertura aplicada")
        
    def apply_closing(self):
        """Aplicar fechamento"""
        if self.current_image is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro")
            return
            
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
        if not self.is_camera_running:
            messagebox.showwarning("Aviso", "Inicie a câmera primeiro")
            return
            
        if not hasattr(self, 'face_detection_enabled'):
            self.face_detection_enabled = False
            
        self.face_detection_enabled = not self.face_detection_enabled
        
        if self.face_detection_enabled:
            self.status_label.config(text="Detecção de rosto ATIVADA (música ao detectar)")
        else:
            self.status_label.config(text="Detecção de rosto DESATIVADA")
            
    def play_sound(self):
        """Tocar som quando objeto detectado"""
        try:
            # Criar um beep simples usando pygame
            # Nota: Em um projeto real, você carregaria um arquivo de música
            frequency = 440  # Hz
            duration = 1000  # ms
            
            # Gerar tom
            sample_rate = 22050
            n_samples = int(round(duration * sample_rate / 1000))
            
            buf = np.sin(2 * np.pi * np.arange(n_samples) * frequency / sample_rate)
            buf = (buf * 32767).astype(np.int16)
            
            # Stereo
            buf = np.column_stack((buf, buf))
            
            sound = pygame.sndarray.make_sound(buf)
            sound.play()
            
            print("🎵 ROSTO DETECTADO - Som tocado!")
            
        except Exception as e:
            print(f"Erro ao tocar som: {e}")
            
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
