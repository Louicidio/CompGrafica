"""Módulo da interface."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import threading


class Interface:
    """Classe responsável pela interface gráfica"""
    
    def __init__(self, root, processador_video):
        self.root = root
        self.processador = processador_video
        self.current_image = None
        self.original_image = None
        
        self.root.title("Reconhecedor de pulador de madeira")
        self.root.geometry("1400x800")
        
        self.criar_widgets()
        # Atalho para parar rastreamento com a tecla P
        self.root.bind('<Key-p>', self._parar_rastreamento_evento)

    def _parar_rastreamento_evento(self, event=None):
        self.processador.parar_rastreamento()
    
    def criar_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame esquerdo com controles
        self._criar_painel_controles(main_frame)
        
        # Frame direito com display
        self._criar_painel_display(main_frame)
    
    def _criar_painel_controles(self, parent):
        left_frame = ttk.LabelFrame(parent, padding=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        # Criar seções de botões
        self._criar_secao_aquisicao(left_frame)
        self._criar_secao_filtros(left_frame)
        self._criar_secao_analise(left_frame)
        self._criar_secao_rastreamento(left_frame)
    
    def _criar_secao_aquisicao(self, parent):
        ttk.Label(parent, text="VÍDEO E IMAGEM", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(parent, text="Carregar Imagem", command=self.carregar_imagem, width=25).pack(pady=2)
        ttk.Button(parent, text="Carregar Vídeo", command=self.carregar_video, width=25).pack(pady=2)
        ttk.Button(parent, text="Iniciar Câmera", command=self.iniciar_camera, width=25).pack(pady=2)
        ttk.Button(parent, text="Pausar vídeo", command=self.pausar_video, width=25).pack(pady=2)
        ttk.Button(parent, text="Limpar Filtros Vídeo", command=self.limpar_filtros, width=25).pack(pady=2)
        ttk.Button(parent, text="Imagem original", 
                  command=self.resetar_imagem, width=25).pack(pady=2)
    
    def _criar_secao_filtros(self, parent):
        ttk.Label(parent, text="FILTROS", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(parent, text="Média", command=lambda: self.aplicar_filtro('mean'), width=25).pack(pady=2)
        ttk.Button(parent, text="Mediana", command=lambda: self.aplicar_filtro('median'), width=25).pack(pady=2)
        ttk.Button(parent, text="Canny (Bordas)", command=lambda: self.aplicar_filtro('canny'), width=25).pack(pady=2)
        ttk.Button(parent, text="Erosão", command=lambda: self.aplicar_filtro('erosion'), width=25).pack(pady=2)
        ttk.Button(parent, text="Dilatação", command=lambda: self.aplicar_filtro('dilation'), width=25).pack(pady=2)
        ttk.Button(parent, text="Abertura", command=lambda: self.aplicar_filtro('opening'), width=25).pack(pady=2)
        ttk.Button(parent, text="Fechamento", command=lambda: self.aplicar_filtro('closing'), width=25).pack(pady=2)
        ttk.Button(parent, text="Níveis de Cinza", command=lambda: self.aplicar_filtro('grayscale'), width=25).pack(pady=2)
        ttk.Button(parent, text="Negativo", command=lambda: self.aplicar_filtro('negative'), width=25).pack(pady=2)
        ttk.Button(parent, text="Binária (Otsu)", command=lambda: self.aplicar_filtro('binary'), width=25).pack(pady=2)
    
    def _criar_secao_analise(self, parent):
        ttk.Label(parent, text="ANÁLISE", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(parent, text="Histograma", command=self.mostrar_histograma, width=25).pack(pady=2)
        ttk.Button(parent, text="Métricas", command=self.calcular_metricas, width=25).pack(pady=2)
        ttk.Button(parent, text="Contar Objetos", command=self.contar_objetos, width=25).pack(pady=2)
    
    def _criar_secao_rastreamento(self, parent):
        ttk.Label(parent, text="RASTREAMENTO", font=('Arial', 10, 'bold')).pack(pady=(0, 5))
        ttk.Button(parent, text="Detectar Rosto + Música", command=self.alternar_deteccao_facial, width=25).pack(pady=2)
        ttk.Button(parent, text="Detectar Pelúcia + Música", command=self.alternar_reconhecimento_objeto, width=25).pack(pady=2)
    
    def _criar_painel_display(self, parent):
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(right_frame, bg='gray', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
            
    def exibir_imagem(self, image):
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
            
            image_pil = Image.fromarray(image_resized)
            image_tk = ImageTk.PhotoImage(image_pil)
            
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                    image=image_tk, anchor=tk.CENTER)
            self.canvas.image = image_tk
    
    # Métodos de controle
    
    def carregar_imagem(self):
        if self.processador.is_camera_running or self.processador.is_video_file_running:
            self.processador.parar()
        
        file_path = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.current_image = self.original_image.copy()
            self.exibir_imagem(self.current_image)
    
    def carregar_video(self):
        if self.processador.is_camera_running or self.processador.is_video_file_running:
            self.processador.parar()
        
        file_path = filedialog.askopenfilename(
            title="Selecione um vídeo",
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.processador.carregar_video(file_path)
            self.atualizar_video()
    
    def iniciar_camera(self):
        if self.processador.iniciar_camera():
            self.atualizar_camera()
    
    def parar_camera(self):
        self.processador.parar()
        if hasattr(self, 'video_after_id') and self.video_after_id:
            self.root.after_cancel(self.video_after_id)
            self.video_after_id = None
    
    def pausar_video(self):
        """Pausar/retomar vídeo"""
        status = self.processador.pausar_retomar()
    
    def atualizar_camera(self):
        if not self.processador.is_camera_running:
            return
        frame = self.processador.processar_frame_camera()
        if frame is not None:
            self.current_image = frame
            self.exibir_imagem(frame)
        # Atualiza a cada 30ms
        self.video_after_id = self.root.after(30, self.atualizar_camera)
    
    def atualizar_video(self):
        if not self.processador.is_video_file_running:
            return
        
        frame = self.processador.processar_frame_video()
        if frame is not None:
            self.exibir_imagem(frame)
        
        self.video_after_id = self.root.after(20, self.atualizar_video)
    
    def aplicar_filtro(self, filter_name):
        from filtros import Filtros
        
        if self.processador.is_camera_running or self.processador.is_video_file_running:
            adicionado = self.processador.adicionar_remover_filtro(filter_name)
            status = "ativado" if adicionado else "desativado"
            return
        
        # Para imagens estáticas
        if self.current_image is not None:
            self.current_image = Filtros.aplicar_filtros(self.current_image, [filter_name])
            self.exibir_imagem(self.current_image)
    
    def limpar_filtros(self):
        self.processador.limpar_filtros()
        pass
    
    def alternar_deteccao_facial(self):
        ativa = self.processador.alternar_deteccao_facial()
        pass
    
    def alternar_reconhecimento_objeto(self):
        """Alternar reconhecimento de objeto predefinido (pelúcia)"""
        import os
        # Caminho para o template da pelúcia
        template_path = os.path.join(os.path.dirname(__file__), "pelucia1.jpg")
        
        if not self.processador.objeto_recognition_enabled:
            # Ativar reconhecimento
            if self.processador.ativar_reconhecimento_objeto(template_path, threshold=0.5):
                messagebox.showinfo("Reconhecimento de Objeto", 
                                  "Reconhecimento de pelúcia ativado!\nO som tocará quando a pelúcia for detectada.\n\nDica: Observe o valor de 'Confiança' no canto da tela.")
            else:
                messagebox.showerror("Erro", 
                                   f"Não foi possível carregar o template 'pelucia.jpg'.\nVerifique se o arquivo existe em:\n{template_path}")
        else:
            # Desativar reconhecimento
            self.processador.desativar_reconhecimento_objeto()
            messagebox.showinfo("Reconhecimento de Objeto", "Reconhecimento de pelúcia desativado.")
    
    def mostrar_histograma(self):
        if self.current_image is None:
            return
        
        plt.figure(figsize=(10, 4))
        
        if len(self.current_image.shape) == 2:
            hist = cv2.calcHist([self.current_image], [0], None, [256], [0, 256])
            plt.plot(hist, color='black')
            plt.title('Histograma - Níveis de Cinza')
            plt.xlabel('Intensidade')
            plt.ylabel('Frequência')
        else:
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
    
    def calcular_metricas(self):
        if self.current_image is None:
            return
        
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            messagebox.showinfo("Info", "Nenhum objeto encontrado na imagem")
            return
        
        result_text = "MÉTRICAS DOS OBJETOS:\n\n"
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 100:
                perimeter = cv2.arcLength(contour, True)
                equivalent_diameter = np.sqrt(4 * area / np.pi)
                
                result_text += f"Objeto {i + 1}:\n"
                result_text += f"  Área: {area:.2f} pixels²\n"
                result_text += f"  Perímetro: {perimeter:.2f} pixels\n"
                result_text += f"  Diâmetro equivalente: {equivalent_diameter:.2f} pixels\n\n"
        
        messagebox.showinfo("Métricas", result_text)
    
    def contar_objetos(self):
        if self.current_image is None:
            return
        
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        visited = np.zeros_like(binary, dtype=bool)
        object_count = 0
        h, w = binary.shape
        
        def region_growing(start_y, start_x):
            queue = deque([(start_y, start_x)])
            visited[start_y, start_x] = True
            
            while queue:
                y, x = queue.popleft()
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < h and 0 <= nx < w and 
                            not visited[ny, nx] and binary[ny, nx] == 255):
                            visited[ny, nx] = True
                            queue.append((ny, nx))
        
        for y in range(h):
            for x in range(w):
                if binary[y, x] == 255 and not visited[y, x]:
                    region_growing(y, x)
                    object_count += 1
        
        colored = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(colored, contours, -1, (0, 255, 0), 2)
        
        for i, contour in enumerate(contours):
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(colored, str(i + 1), (cx, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        self.current_image = colored
        self.exibir_imagem(self.current_image)
        
        messagebox.showinfo("Contagem de Objetos", 
                           f"Total de objetos encontrados: {object_count}")
    
    def resetar_imagem(self):
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.exibir_imagem(self.current_image)
