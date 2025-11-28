import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import time
import os

# Configurações do jogo
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_ROWS = 8
GRID_COLS = 5
FALL_SPEED = 0.03

# Funções auxiliares para desenhar formas 3D
def draw_cube(size=1.0):
    """Desenha um cubo com normais corretas"""
    s = size / 2.0
    
    # Frente
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glTexCoord2f(0, 0); glVertex3f(-s, -s, s)
    glTexCoord2f(1, 0); glVertex3f(s, -s, s)
    glTexCoord2f(1, 1); glVertex3f(s, s, s)
    glTexCoord2f(0, 1); glVertex3f(-s, s, s)
    
    # Trás
    glNormal3f(0, 0, -1)
    glTexCoord2f(1, 0); glVertex3f(-s, -s, -s)
    glTexCoord2f(1, 1); glVertex3f(-s, s, -s)
    glTexCoord2f(0, 1); glVertex3f(s, s, -s)
    glTexCoord2f(0, 0); glVertex3f(s, -s, -s)
    
    # Topo
    glNormal3f(0, 1, 0)
    glTexCoord2f(0, 1); glVertex3f(-s, s, -s)
    glTexCoord2f(0, 0); glVertex3f(-s, s, s)
    glTexCoord2f(1, 0); glVertex3f(s, s, s)
    glTexCoord2f(1, 1); glVertex3f(s, s, -s)
    
    # Base
    glNormal3f(0, -1, 0)
    glTexCoord2f(1, 1); glVertex3f(-s, -s, -s)
    glTexCoord2f(0, 1); glVertex3f(s, -s, -s)
    glTexCoord2f(0, 0); glVertex3f(s, -s, s)
    glTexCoord2f(1, 0); glVertex3f(-s, -s, s)
    
    # Direita
    glNormal3f(1, 0, 0)
    glTexCoord2f(1, 0); glVertex3f(s, -s, -s)
    glTexCoord2f(1, 1); glVertex3f(s, s, -s)
    glTexCoord2f(0, 1); glVertex3f(s, s, s)
    glTexCoord2f(0, 0); glVertex3f(s, -s, s)
    
    # Esquerda
    glNormal3f(-1, 0, 0)
    glTexCoord2f(0, 0); glVertex3f(-s, -s, -s)
    glTexCoord2f(1, 0); glVertex3f(-s, -s, s)
    glTexCoord2f(1, 1); glVertex3f(-s, s, s)
    glTexCoord2f(0, 1); glVertex3f(-s, s, -s)
    glEnd()

def draw_sphere(radius=1.0, slices=20, stacks=20):
    """Desenha uma esfera com normais e coordenadas de textura"""
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        z0 = radius * math.sin(lat0)
        zr0 = radius * math.cos(lat0)
        
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        z1 = radius * math.sin(lat1)
        zr1 = radius * math.cos(lat1)
        
        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * float(j) / slices
            x = math.cos(lng)
            y = math.sin(lng)
            
            glNormal3f(x * zr0, y * zr0, z0)
            glTexCoord2f(float(j) / slices, float(i) / stacks)
            glVertex3f(x * zr0, y * zr0, z0)
            
            glNormal3f(x * zr1, y * zr1, z1)
            glTexCoord2f(float(j) / slices, float(i + 1) / stacks)
            glVertex3f(x * zr1, y * zr1, z1)
        glEnd()

def draw_cylinder(radius=1.0, height=1.0, slices=20):
    """Desenha um cilindro com normais e coordenadas de textura"""
    # Tampa inferior
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, -1, 0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0, 0, 0)
    for i in range(slices + 1):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glTexCoord2f(x / radius * 0.5 + 0.5, z / radius * 0.5 + 0.5)
        glVertex3f(x, 0, z)
    glEnd()
    
    # Corpo
    glBegin(GL_QUAD_STRIP)
    for i in range(slices + 1):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glNormal3f(x, 0, z)
        glTexCoord2f(float(i) / slices, 0)
        glVertex3f(x, 0, z)
        glTexCoord2f(float(i) / slices, 1)
        glVertex3f(x, height, z)
    glEnd()
    
    # Tampa superior
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 1, 0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0, height, 0)
    for i in range(slices + 1):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glTexCoord2f(x / radius * 0.5 + 0.5, z / radius * 0.5 + 0.5)
        glVertex3f(x, height, z)
    glEnd()

def create_texture_from_color(color, width=64, height=64):
    """Cria uma textura simples a partir de uma cor"""
    r, g, b = color
    data = bytes([int(r*255), int(g*255), int(b*255), 255] * (width * height))
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Usar gluBuild2DMipmaps para gerar mipmaps automaticamente
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    # Usar filtros de mipmap para melhor qualidade
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    return texture_id

def create_grid_texture(size=64):
    """Cria uma textura de grid"""
    data = []
    for y in range(size):
        for x in range(size):
            if (x // 8 + y // 8) % 2 == 0:
                data.extend([40, 40, 60, 255])
            else:
                data.extend([30, 30, 50, 255])
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Usar gluBuild2DMipmaps para gerar mipmaps automaticamente
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, size, size, GL_RGBA, GL_UNSIGNED_BYTE, bytes(data))
    
    # Usar filtros de mipmap para melhor qualidade
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    return texture_id

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.load_textures()
    
    def load_textures(self):
        """Carrega todas as texturas do jogo"""
        # Texturas coloridas simples
        self.textures['star'] = create_texture_from_color((1.0, 0.84, 0.0))
        self.textures['coin'] = create_texture_from_color((0.75, 0.75, 0.75))
        self.textures['cube'] = create_texture_from_color((0.0, 0.8, 1.0))
        self.textures['player'] = create_texture_from_color((0.2, 0.6, 1.0))
        self.textures['wall'] = create_texture_from_color((0.1, 0.1, 0.3))
        self.textures['back_wall'] = create_texture_from_color((0.1, 0.2, 0.3))
        self.textures['floor'] = create_grid_texture()
        
        # Carregar textura da galáxia
        self.textures['galaxy'] = self.load_image_texture('images/galaxy.jpg')
        
        # Carregar texturas dos objetos colecionáveis
        self.textures['sun'] = self.load_image_texture('images/sun.jpg')
        self.textures['earth'] = self.load_image_texture('images/earth.jpg')
        self.textures['moon'] = self.load_image_texture('images/moon.jpg')

    
    def load_image_texture(self, filepath):
        """Carrega uma textura de um arquivo de imagem"""
        try:
            if not os.path.exists(filepath):
                print(f"Aviso: Arquivo de textura não encontrado: {filepath}")
                return create_texture_from_color((0.05, 0.05, 0.15))
            
            # Carregar imagem com Pygame
            image = pygame.image.load(filepath)
            image = pygame.transform.flip(image, False, True)  # Inverter verticalmente
            
            # Obter dados da imagem
            width, height = image.get_size()
            
            # Converter para RGBA
            image = image.convert_alpha()
            image_data = pygame.image.tostring(image, "RGBA", True)
            
            # Criar textura OpenGL
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # Usar gluBuild2DMipmaps para gerar mipmaps automaticamente
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, 
                            GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            
            # Configurar filtros de textura com mipmaps
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            # USAR CLAMP_TO_EDGE para evitar repetição em skybox
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            # Filtro anisotrópico (opcional, melhora qualidade em ângulos)
            try:
                from OpenGL.GL.EXT.texture_filter_anisotropic import GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, GL_TEXTURE_MAX_ANISOTROPY_EXT
                max_anisotropy = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(8.0, max_anisotropy))
            except:
                pass  # Extensão não disponível
            
            return texture_id
        except Exception as e:
            print(f"Erro ao carregar textura {filepath}: {e}")
            return create_texture_from_color((0.05, 0.05, 0.15))
    
    def bind(self, name):
        """Vincula uma textura pelo nome"""
        if name in self.textures:
            glBindTexture(GL_TEXTURE_2D, self.textures[name])

class Camera:
    def __init__(self):
        self.distance = 15
        self.rotation_x = 30
        self.rotation_y = 0
        self.zoom_speed = 0.5
        self.rotation_speed = 2
    
    def apply(self):
        glLoadIdentity()
        glTranslatef(0, -2, -self.distance)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
    
    def zoom_in(self):
        self.distance = max(8, self.distance - self.zoom_speed)
    
    def zoom_out(self):
        self.distance = min(30, self.distance + self.zoom_speed)
    
    def rotate_left(self):
        self.rotation_y -= self.rotation_speed
    
    def rotate_right(self):
        self.rotation_y += self.rotation_speed
    
    def rotate_up(self):
        self.rotation_x = min(80, self.rotation_x + self.rotation_speed)
    
    def rotate_down(self):
        self.rotation_x = max(-80, self.rotation_x - self.rotation_speed)

class Item:
    def __init__(self, item_type, position, texture_manager):
        self.type = item_type
        self.x, self.y, self.z = position
        self.collected = False
        self.rotation = 0
        self.texture_manager = texture_manager
        self.points = 1
        
        if item_type == 'estrela':
            self.points = 3
        elif item_type == 'moeda':
            self.points = 2
        
    def update(self, speed):
        if not self.collected:
            self.y -= speed
            self.rotation += 2
    
    def render(self):
        if self.collected:
            return
        
        glEnable(GL_TEXTURE_2D)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        
        if self.type == 'estrela':
            self.draw_star()
        elif self.type == 'moeda':
            self.draw_coin()
        else:
            self.draw_cube_item()
        
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)
    
    def draw_star(self):
        # Usar textura do sol para a estrela (esfera)
        self.texture_manager.bind('sun')
        glColor3f(1.0, 1.0, 1.0)  # Branco para não alterar a textura
        draw_sphere(0.3, 20, 20)
        
        # Pontas da estrela (sem textura, com cor dourada)
        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 0.84, 0.0)
        for i in range(5):
            angle = i * 72
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(0.4, 0, 0)
            glScalef(0.5, 0.2, 0.2)
            draw_cube(0.3)
            glPopMatrix()
        glEnable(GL_TEXTURE_2D)
    
    def draw_coin(self):
        # Usar textura da lua para a moeda (cilindro)
        self.texture_manager.bind('moon')
        glColor3f(1.0, 1.0, 1.0)  # Branco para não alterar a textura
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        draw_cylinder(0.3, 0.1, 20)
        glPopMatrix()
    
    def draw_cube_item(self):
        # Usar textura da Terra para o cubo
        self.texture_manager.bind('earth')
        glColor3f(1.0, 1.0, 1.0)  # Branco para não alterar a textura
        draw_cube(0.5)

class Player:
    def __init__(self, position, texture_manager):
        self.x, self.y, self.z = position
        self.width = 1.5
        self.depth = 1.5
        self.height = 0.3
        self.speed = 0.15
        self.collected_items = 0
        self.max_x = 4
        self.min_x = -4
        self.texture_manager = texture_manager
    
    def move_left(self):
        self.x = max(self.min_x, self.x - self.speed)
    
    def move_right(self):
        self.x = min(self.max_x, self.x + self.speed)
    
    def move_forward(self):
        self.z = max(self.min_x, self.z - self.speed)
    
    def move_backward(self):
        self.z = min(self.max_x, self.z + self.speed)
    
    def check_collision(self, item):
        if item.collected:
            return False
        
        dx = abs(self.x - item.x)
        dz = abs(self.z - item.z)
        dy = abs(self.y - item.y)
        
        if dx < self.width/2 + 0.3 and dz < self.depth/2 + 0.3 and dy < 0.5:
            return True
        return False
    
    def render(self):
        glEnable(GL_TEXTURE_2D)
        self.texture_manager.bind('player')
        
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Base do coletor
        glColor3f(0.2, 0.6, 1.0)
        glPushMatrix()
        glScalef(self.width, self.height, self.depth)
        draw_cube(1)
        glPopMatrix()
        
        # Bordas do coletor
        glColor3f(0.1, 0.3, 0.6)
        positions = [
            (-self.width/2, self.height/2, 0, 0.1, self.height*2, self.depth),
            (self.width/2, self.height/2, 0, 0.1, self.height*2, self.depth),
            (0, self.height/2, -self.depth/2, self.width, self.height*2, 0.1),
            (0, self.height/2, self.depth/2, self.width, self.height*2, 0.1)
        ]
        
        for px, py, pz, sx, sy, sz in positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glScalef(sx, sy, sz)
            draw_cube(1)
            glPopMatrix()
        
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

class Game:
    def __init__(self):
        self.state = 'MENU'
        self.objective = None
        self.texture_manager = TextureManager()
        self.player = Player([0, -3, 0], self.texture_manager)
        self.items = []
        self.score = 0
        self.lives = 3
        self.time_limit = 60
        self.start_time = None
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.difficulty = 'MEDIUM'
        self.item_speed = FALL_SPEED
        self.camera = Camera()
        self.best_scores = {'TIME': 0, 'CAPACITY': 0, 'SURVIVAL': 0}
        
        # Carregar sons
        self.load_sounds()
        
    def load_sounds(self):
        """Carrega os sons do jogo"""
        try:
            pygame.mixer.init()
            self.sounds = {
                'catch': pygame.mixer.Sound('catch.wav'),
                'miss': pygame.mixer.Sound('miss.wav'),
                'losing': pygame.mixer.Sound('losing.wav')
            }
            print("Sons carregados com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar sons: {e}")
            self.sounds = {
                'catch': None,
                'miss': None,
                'losing': None
            }
    
    def play_sound(self, sound_name):
        """Toca um som"""
        if self.sounds.get(sound_name):
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Erro ao tocar som {sound_name}: {e}")
        
    def set_objective(self, objective):
        self.objective = objective
        self.state = 'PLAYING'
        self.start_time = time.time()
        self.score = 0
        self.lives = 3
        self.items = []
        self.player.x = 0
        self.player.z = 0
        
        if objective == 'TIME':
            self.time_limit = 60
        elif objective == 'CAPACITY':
            self.time_limit = float('inf')
        elif objective == 'SURVIVAL':
            self.time_limit = float('inf')
    
    def spawn_item(self):
        item_types = ['estrela', 'moeda', 'cubo']
        item_type = random.choice(item_types)
        x = random.uniform(-4, 4)
        z = random.uniform(-4, 4)
        y = 8
        self.items.append(Item(item_type, [x, y, z], self.texture_manager))
    
    def update(self, delta_time):
        if self.state != 'PLAYING':
            return
        
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_item()
            self.spawn_timer = 0
        
        items_to_remove = []
        for item in self.items:
            item.update(self.item_speed)
            
            if self.player.check_collision(item):
                item.collected = True
                self.score += item.points
                items_to_remove.append(item)
                # Tocar som de captura
                self.play_sound('catch')
            
            elif item.y < -5:
                items_to_remove.append(item)
                # Tocar som de perda
                self.play_sound('miss')
                
                if self.objective == 'SURVIVAL':
                    self.lives -= 1
                    # Tocar som de perder vida
                    self.play_sound('losing')
                    
                    if self.lives <= 0:
                        self.state = 'GAME_OVER'
                        self.update_best_score()
        
        for item in items_to_remove:
            if item in self.items:
                self.items.remove(item)
        
        elapsed_time = time.time() - self.start_time
        
        if self.objective == 'TIME' and elapsed_time >= self.time_limit:
            self.state = 'GAME_OVER'
            self.update_best_score()
        elif self.objective == 'CAPACITY' and self.score >= 50:
            self.state = 'GAME_OVER'
            self.update_best_score()
    
    def update_best_score(self):
        if self.objective and self.score > self.best_scores[self.objective]:
            self.best_scores[self.objective] = self.score
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.state == 'MENU':
            self.render_menu()
        elif self.state == 'PLAYING':
            self.camera.apply()
            self.setup_lighting()
            self.render_scenario()
            self.player.render()
            for item in self.items:
                item.render()
        elif self.state == 'GAME_OVER':
            self.render_game_over()
    
    def setup_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Luz principal
        light_position = [5, 10, 5, 1]
        light_ambient = [0.3, 0.3, 0.4, 1]
        light_diffuse = [1, 1, 1, 1]
        light_specular = [1, 1, 1, 1]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    def render_scenario(self):
        # Desenhar skybox completo da galáxia
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        self.texture_manager.bind('galaxy')
        glDepthMask(GL_FALSE)  # Não escrever no depth buffer
        
        # Fundo (atrás)
        glPushMatrix()
        glTranslatef(0, 0, -20)
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Frente
        glPushMatrix()
        glTranslatef(0, 0, 20)
        glRotatef(180, 0, 1, 0)
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Esquerda
        glPushMatrix()
        glTranslatef(-20, 0, 0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Direita
        glPushMatrix()
        glTranslatef(20, 0, 0)
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Topo
        glPushMatrix()
        glTranslatef(0, 20, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.7, 0.8)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Fundo (chão) - mais escuro
        glPushMatrix()
        glTranslatef(0, -20, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.5, 0.5, 0.6)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        glDepthMask(GL_TRUE)  # Reativar escrita no depth buffer
        
        # Reativar iluminação
        glEnable(GL_LIGHTING)
        
        # Chão semi-transparente
        self.texture_manager.bind('floor')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.5, 0.5, 0.6, 0.0)  # Tornar mais transparente
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-5, -4, -5)
        glTexCoord2f(5, 0); glVertex3f(5, -4, -5)
        glTexCoord2f(5, 5); glVertex3f(5, -4, 5)
        glTexCoord2f(0, 5); glVertex3f(-5, -4, 5)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Parede de fundo (única parede)
        self.texture_manager.bind('back_wall')
        glColor4f(1, 1, 1, 0.0)
        glEnable(GL_BLEND)
        glPushMatrix()
        glTranslatef(0, 2, -5.5)
        glScalef(10, 12, 0.5)
        draw_cube(1)
        glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)
    
    def render_menu(self):
        """Renderiza um cenário 3D de fundo para o menu"""
        self.camera.apply()
        self.setup_lighting()
        
        # Desenhar skybox completo da galáxia
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        self.texture_manager.bind('galaxy')
        glDepthMask(GL_FALSE)
        
        # Fundo (atrás)
        glPushMatrix()
        glTranslatef(0, 0, -20)
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Frente
        glPushMatrix()
        glTranslatef(0, 0, 20)
        glRotatef(180, 0, 1, 0)
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Esquerda
        glPushMatrix()
        glTranslatef(-20, 0, 0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Direita
        glPushMatrix()
        glTranslatef(20, 0, 0)
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Topo
        glPushMatrix()
        glTranslatef(0, 20, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.7, 0.8)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Fundo (chão)
        glPushMatrix()
        glTranslatef(0, -20, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.5, 0.5, 0.6)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        glDepthMask(GL_TRUE)
        
        # Reativar iluminação para os objetos 3D
        glEnable(GL_LIGHTING)
        
        # Chão semi-transparente
        self.texture_manager.bind('floor')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.5, 0.5, 0.6, 0.3)
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-5, -4, -5)
        glTexCoord2f(5, 0); glVertex3f(5, -4, -5)
        glTexCoord2f(5, 5); glVertex3f(5, -4, 5)
        glTexCoord2f(0, 5); glVertex3f(-5, -4, 5)
        glEnd()
        
        glDisable(GL_BLEND)
        glColor3f(1, 1, 1)
        
        # Alguns itens decorativos flutuando
        glPushMatrix()
        glTranslatef(-2, 0, 0)
        glRotatef(time.time() * 20, 0, 1, 0)
        self.texture_manager.bind('sun')  # Textura do sol
        glColor3f(1.0, 1.0, 1.0)
        draw_sphere(0.4, 20, 20)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(2, 0, 0)
        glRotatef(time.time() * -20, 0, 1, 0)
        self.texture_manager.bind('moon')  # Textura da lua
        glColor3f(1.0, 1.0, 1.0)
        glRotatef(90, 1, 0, 0)
        draw_cylinder(0.4, 0.15, 20)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 1, -2)
        glRotatef(time.time() * 15, 1, 1, 0)
        self.texture_manager.bind('earth')  # Textura da Terra
        glColor3f(1.0, 1.0, 1.0)
        draw_cube(0.6)
        glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)
        
        # PAREDE REMOVIDA - sem parede de fundo no menu
    def render_game_over(self):
        """Renderiza um cenário 3D de fundo para a tela de game over"""
        self.camera.apply()
        self.setup_lighting()
        
        # Desenhar skybox completo da galáxia (escurecido)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        self.texture_manager.bind('galaxy')
        glDepthMask(GL_FALSE)
        
        # Fundo (atrás)
        glPushMatrix()
        glTranslatef(0, 0, -20)
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Frente
        glPushMatrix()
        glTranslatef(0, 0, 20)
        glRotatef(180, 0, 1, 0)
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Esquerda
        glPushMatrix()
        glTranslatef(-20, 0, 0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.45, 0.45, 0.45)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Direita
        glPushMatrix()
        glTranslatef(20, 0, 0)
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.45, 0.45, 0.45)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Topo
        glPushMatrix()
        glTranslatef(0, 20, 0)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.35, 0.35, 0.4)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        # Fundo (chão)
        glPushMatrix()
        glTranslatef(0, -20, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.25, 0.25, 0.3)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-20, -20, 0)
        glTexCoord2f(1, 0); glVertex3f(20, -20, 0)
        glTexCoord2f(1, 1); glVertex3f(20, 20, 0)
        glTexCoord2f(0, 1); glVertex3f(-20, 20, 0)
        glEnd()
        glPopMatrix()
        
        glDepthMask(GL_TRUE)
        
        # Reativar iluminação
        glEnable(GL_LIGHTING)
        
        # Chão semi-transparente escurecido
        self.texture_manager.bind('floor')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.3, 0.3, 0.3, 0.3)
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-5, -4, -5)
        glTexCoord2f(5, 0); glVertex3f(5, -4, -5)
        glTexCoord2f(5, 5); glVertex3f(5, -4, 5)
        glTexCoord2f(0, 5); glVertex3f(-5, -4, 5)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Parede de fundo escurecida
        self.texture_manager.bind('back_wall')
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0, 2, -5.5)
        glScalef(10, 12, 0.5)
        draw_cube(1)
        glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)

def draw_text_pygame(screen, text, position, font, color=(255, 255, 255)):
    """Desenha texto usando Pygame"""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Drop and Catch - Coletor de Estrelas 3D")
    
    # Fontes
    title_font = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    
    # Configurações OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.05, 0.05, 0.15, 1)
    
    # Configurar projeção inicial
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    game = Game()
    clock = pygame.time.Clock()
    last_time = time.time()
    
    running = True
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.state == 'MENU':
                    if event.key == pygame.K_1:
                        game.set_objective('TIME')
                    elif event.key == pygame.K_2:
                        game.set_objective('CAPACITY')
                    elif event.key == pygame.K_3:
                        game.set_objective('SURVIVAL')
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif game.state == 'PLAYING':
                    # Adicionar ESC para pausar/voltar ao menu durante o jogo
                    if event.key == pygame.K_ESCAPE:
                        game.state = 'MENU'
                elif game.state == 'GAME_OVER':
                    if event.key == pygame.K_ESCAPE:
                        game.state = 'MENU'
                    elif event.key == pygame.K_r:
                        if game.objective:
                            game.set_objective(game.objective)
        
        if game.state == 'PLAYING':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                game.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                game.player.move_right()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                game.player.move_forward()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                game.player.move_backward()
            
            if keys[pygame.K_q]:
                game.camera.zoom_in()
            if keys[pygame.K_e]:
                game.camera.zoom_out()
            if keys[pygame.K_j]:
                game.camera.rotate_left()
            if keys[pygame.K_l]:
                game.camera.rotate_right()
            if keys[pygame.K_i]:
                game.camera.rotate_up()
            if keys[pygame.K_k]:
                game.camera.rotate_down()
        
        game.update(delta_time)
        
        # Renderizar cena 3D
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        
        game.render()
        
        # Overlay 2D usando Pygame
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Criar surface transparente para overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        if game.state == 'MENU':
            overlay.fill((0, 0, 0, 200))
            
            # Título
            title = title_font.render("DROP AND CATCH", True, (255, 215, 0))
            subtitle = font.render("Coletor de Estrelas 3D", True, (255, 255, 255))
            overlay.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            overlay.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
            
            # Menu
            menu_y = 220
            menu_items = [
                "Escolha o modo de jogo:",
                "",
                "1 - Modo TEMPO (60 segundos)",
                "2 - Modo CAPACIDADE (50 pontos)",
                "3 - Modo SOBREVIVENCIA (3 vidas)",
                "",
                "Melhores Pontuacoes:",
                f"  Tempo: {game.best_scores['TIME']} pts",
                f"  Capacidade: {game.best_scores['CAPACITY']} pts",
                f"  Sobrevivencia: {game.best_scores['SURVIVAL']} pts",
                "",
                "Controles:",
                "  Setas/WASD - Mover coletor",
                "  Q/E - Zoom",
                "  I/K/J/L - Rotacionar camera",
                "",
                "ESC - Sair"
            ]
            
            for i, text in enumerate(menu_items):
                if text:
                    color = (255, 215, 0) if text.startswith(("1 -", "2 -", "3 -")) else (200, 200, 200)
                    font_to_use = small_font if not text.startswith(("Escolha", "Controles", "Melhores")) else font
                    text_surf = font_to_use.render(text, True, color)
                    x = SCREEN_WIDTH//2 - text_surf.get_width()//2
                    overlay.blit(text_surf, (x, menu_y + i * 30))
        
        elif game.state == 'PLAYING':
            # HUD semi-transparente
            hud_height = 80
            hud_surf = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
            hud_surf.fill((0, 0, 0, 150))
            
            score_text = font.render(f"Pontuacao: {game.score}", True, (255, 255, 0))
            hud_surf.blit(score_text, (20, 10))
            
            if game.objective == 'SURVIVAL':
                lives_text = font.render(f"Vidas: {'♥' * game.lives}", True, (255, 50, 50))
                hud_surf.blit(lives_text, (20, 45))
            elif game.objective == 'TIME':
                elapsed = time.time() - game.start_time
                remaining = max(0, int(game.time_limit - elapsed))
                time_text = font.render(f"Tempo: {remaining}s", True, (100, 200, 255))
                hud_surf.blit(time_text, (20, 45))
            elif game.objective == 'CAPACITY':
                progress_text = font.render(f"Meta: 50 pontos", True, (100, 255, 100))
                hud_surf.blit(progress_text, (20, 45))
            
            overlay.blit(hud_surf, (0, 0))
            
            # Dicas de controle
            hint_text = small_font.render("Q/E:Zoom | I/K/J/L:Camera | ESC:Menu", True, (150, 150, 150))
            overlay.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, SCREEN_HEIGHT - 30))
        
        elif game.state == 'GAME_OVER':
            overlay.fill((0, 0, 0, 220))
            
            title = title_font.render("FIM DE JOGO!", True, (255, 50, 50))
            overlay.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            
            score_text = font.render(f"Pontuacao Final: {game.score}", True, (255, 215, 0))
            overlay.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 280))
            
            if game.score == game.best_scores[game.objective]:
                best_text = small_font.render("NOVO RECORDE!", True, (0, 255, 0))
                overlay.blit(best_text, (SCREEN_WIDTH//2 - best_text.get_width()//2, 320))
            
            # Instruções para reiniciar ou voltar ao menu
            instructions = [
                "Pressione ESC para voltar ao menu",
                "ou",
                "Pressione R para reiniciar"
            ]
            
            for i, text in enumerate(instructions):
                text_surf = small_font.render(text, True, (255, 255, 255))
                overlay.blit(text_surf, (SCREEN_WIDTH//2 - text_surf.get_width()//2, 400 + i * 30))
        
        # Desenhar overlay na tela
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        texture_data = pygame.image.tostring(overlay, "RGBA", True)
        glDrawPixels(SCREEN_WIDTH, SCREEN_HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        glDisable(GL_BLEND)
        
        # Restaurar matrizes
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()