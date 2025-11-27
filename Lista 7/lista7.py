from math import sin, cos, pi
import sys
try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from OpenGL.GLUT import *
except Exception as e:
	print("Erro ao importar PyOpenGL:", e)
	sys.exit(1)

try:
	from PIL import Image
	PIL_AVAILABLE = True
except Exception:
	PIL_AVAILABLE = False

# Configurações globais
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
paused = False
use_textures = True
wireframe = False
time_scale = 1.0

angle_day = 0.0  # rotação própria
angle_year = 0.0 # órbita geral (incremento base)

textures = {}
gif_frames = {}  # Armazena frames de GIFs animados
gif_current_frame = {}  # Frame atual de cada GIF

class Astro:
	def __init__(self, nome, raio_orbita, tamanho, vel_orbita, vel_rot, textura=None, cor=(1,1,1)):
		self.nome = nome
		self.raio_orbita = raio_orbita
		self.tamanho = tamanho
		self.vel_orbita = vel_orbita
		self.vel_rot = vel_rot
		self.textura = textura
		self.cor = cor
		self.angulo_orbita = 0.0
		self.angulo_rot = 0.0

# Definição dos planetas (valores estilizados, não reais)
# nome, raio_orbita, tamanho, vel_orbita, vel_rot, textura, cor fallback
planetas = [
	Astro("Mercurio", 4.0, 0.4, 4.15, 8.0, "textures/mercurymap.jpg", (0.7,0.6,0.5)),
	Astro("Venus", 6.5, 0.6, 1.62, 3.0, "textures/venusmap.jpg", (0.9,0.8,0.3)),
	Astro("Terra", 9.0, 0.65, 1.0, 6.0, "textures/earthmap1k.jpg", (0.2,0.3,0.8)),
	Astro("Marte", 11.5, 0.5, 0.53, 5.0, "textures/marsmap1k.jpg", (0.8,0.3,0.1)),
	Astro("Jupiter", 15.5, 1.3, 0.249, 12.0, "textures/jupiter2_1k.jpg", (0.9,0.7,0.4)),
	Astro("Saturno", 19.5, 1.1, 0.102, 10.0, "textures/saturnmap.jpg", (0.9,0.8,0.5)),
	Astro("Urano", 23.5, 0.9, 0.0357, 7.0, "textures/uranusmap.jpg", (0.5,0.8,0.9)),
	Astro("Netuno", 27.0, 0.85, 0.018, 7.0, "textures/neptunemap.jpg", (0.3,0.4,0.9)),
]

# Lua ligada à Terra
lua = Astro("Lua", 1.2, 0.18, 8.0, 10.0, "textures/moonmap1k.jpg", (0.8,0.8,0.8))

# Sol
sol = Astro("Sol", 0.0, 2.5, 0.0, 2.0, "textures/sunmap.jpg", (1.0,0.9,0.2))

def carregar_gif_frames(path):
	"""Carrega todos os frames de um GIF animado"""
	if not PIL_AVAILABLE:
		return None
	try:
		img = Image.open(path)
		frames = []
		frame_count = 0
		try:
			while True:
				frame = img.copy()
				frame = frame.convert('RGBA')
				frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
				data = frame.tobytes()
				w, h = frame.size
				
				tex_id = glGenTextures(1)
				glBindTexture(GL_TEXTURE_2D, tex_id)
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
				glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
				glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
				
				frames.append(tex_id)
				frame_count += 1
				img.seek(frame_count)
		except EOFError:
			pass  # Fim dos frames
		
		return frames if frames else None
	except Exception as e:
		print(f"Erro ao carregar GIF {path}: {e}")
		return None

def carregar_textura(path):
	if not use_textures:
		return None
	if path in textures:
		return textures[path]
	if not PIL_AVAILABLE:
		return None
	
	# Se for GIF, carrega como animação
	if path.lower().endswith('.gif'):
		if path not in gif_frames:
			frames = carregar_gif_frames(path)
			if frames:
				gif_frames[path] = frames
				gif_current_frame[path] = 0
		if path in gif_frames:
			# Retorna o frame atual
			frame_idx = gif_current_frame[path]
			return gif_frames[path][frame_idx]
		return None
	
	# Carregamento normal para imagens estáticas
	try:
		img = Image.open(path)
		img = img.transpose(Image.FLIP_TOP_BOTTOM)
		
		# Detecta se tem transparência
		if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
			img = img.convert('RGBA')
			data = img.tobytes()
			w, h = img.size
			tex_id = glGenTextures(1)
			glBindTexture(GL_TEXTURE_2D, tex_id)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
		else:
			img = img.convert('RGB')
			data = img.tobytes()
			w, h = img.size
			tex_id = glGenTextures(1)
			glBindTexture(GL_TEXTURE_2D, tex_id)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
		
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		textures[path] = tex_id
		return tex_id
	except Exception:
		return None

def aplicar_textura(astro):
	if use_textures and astro.textura:
		tex_id = carregar_textura(astro.textura)
		if tex_id:
			glEnable(GL_TEXTURE_2D)
			glBindTexture(GL_TEXTURE_2D, tex_id)
			return
	glDisable(GL_TEXTURE_2D)
	glColor3f(*astro.cor)

def init():
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_COLOR_MATERIAL)
	glEnable(GL_NORMALIZE)
	glShadeModel(GL_SMOOTH)
	glClearColor(0,0,0,1)

	# Luz dentro do Sol
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	light_pos = [0.0, 0.0, 0.0, 1.0]
	glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
	glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
	glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.1, 1.0])
	glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])

def reshape(w, h):
	if h == 0: h = 1
	glViewport(0,0,w,h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, w/float(h), 0.1, 200.0)
	glMatrixMode(GL_MODELVIEW)

def atualizar(val):
	global angle_year
	if not paused:
		# Atualiza órbita e rotação
		for p in planetas:
			p.angulo_orbita += p.vel_orbita * time_scale * 0.2
			p.angulo_rot += p.vel_rot * time_scale * 0.5
		lua.angulo_orbita += lua.vel_orbita * time_scale * 0.3
		lua.angulo_rot += lua.vel_rot * time_scale * 0.7
		sol.angulo_rot += sol.vel_rot * time_scale * 0.2
		
		# Atualiza frames dos GIFs (a cada 3 frames ~50ms)
		if val % 3 == 0:
			for path in gif_frames:
				gif_current_frame[path] = (gif_current_frame[path] + 1) % len(gif_frames[path])
	
	glutPostRedisplay()
	glutTimerFunc(16, atualizar, 0)

def desenhar_esfera(astro, wire=False):
	aplicar_textura(astro)
	quad = gluNewQuadric()
	if use_textures and astro.textura:
		gluQuadricTexture(quad, GL_TRUE)
	gluQuadricNormals(quad, GLU_SMOOTH)
	if wire or wireframe:
		gluQuadricDrawStyle(quad, GLU_LINE)
	gluSphere(quad, astro.tamanho, 32, 32)
	gluDeleteQuadric(quad)

def desenhar_aneis_saturno(saturno):
	glPushMatrix()
	glRotatef(25,1,0,0)  # pequena inclinação
	glColor3f(0.8,0.7,0.5)
	glDisable(GL_TEXTURE_2D)
	inner = saturno.tamanho*1.3
	outer = saturno.tamanho*2.1
	glBegin(GL_QUAD_STRIP)
	for i in range(0,361,5):
		ang = pi * i /180.0
		ci = cos(ang); si = sin(ang)
		glVertex3f(ci*inner, 0, si*inner)
		glVertex3f(ci*outer, 0, si*outer)
	glEnd()
	glPopMatrix()
	
def desenhar_aneis_uranus(uranus):
	glPushMatrix()
	glRotatef(90,0,0,1)  # deixa o anel na vertical
	
	# Pode usar GIF ou imagem estática
	# Para GIF: "textures/anel.gif"
	# Para PNG/JPG: "textures/uranusringcolour.jpg"
	tex_path = "textures/uranusringcolour.jpg"  # Mude para .gif se quiser animação
	tex_id = carregar_textura(tex_path)
	
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	if tex_id:
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, tex_id)
		glColor4f(1.0, 1.0, 1.0, 1.0)  # Branco com 70% opacidade
	else:
		glDisable(GL_TEXTURE_2D)
		glColor4f(0.8,0.7,0.5,0.5)  # cor com transparência

	inner = uranus.tamanho*1.3
	outer = uranus.tamanho*1.5
	glBegin(GL_QUAD_STRIP)
	for i in range(0,361,5):
		ang = pi * i /180.0
		ci = cos(ang); si = sin(ang)
		t = i / 360.0
		glTexCoord2f(t, 0.0)
		glVertex3f(ci*inner, 0, si*inner)
		glTexCoord2f(t, 1.0)
		glVertex3f(ci*outer, 0, si*outer)
	glEnd()

	if tex_id:
		glDisable(GL_TEXTURE_2D)
	glDisable(GL_BLEND)
	glPopMatrix()

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	# Posiciona câmera
	gluLookAt(0,8,35, 0,0,0, 0,1,0)

	# Desenha Sol
	glPushMatrix()
	glRotatef(sol.angulo_rot, 0,1,0)
	aplicar_textura(sol)
	desenhar_esfera(sol)
	glPopMatrix()

	# Desenha planetas
	for p in planetas:
		glPushMatrix()
		glRotatef(p.angulo_orbita, 0,1,0)
		glTranslatef(p.raio_orbita, 0, 0)
		glRotatef(p.angulo_rot, 0,1,0)
		desenhar_esfera(p)
		# Lua orbitando Terra
		if p.nome == "Terra":
			glPushMatrix()
			glRotatef(lua.angulo_orbita, 0,1,0)
			glTranslatef(lua.raio_orbita, 0, 0)
			glRotatef(lua.angulo_rot, 0,1,0)
			desenhar_esfera(lua)
			glPopMatrix()
		# Anéis de Saturno
		if p.nome == "Saturno":
			desenhar_aneis_saturno(p)
		# Anéis de Urano
		if p.nome == "Urano":
			desenhar_aneis_uranus(p)
		glPopMatrix()

	glutSwapBuffers()

def teclado(key, x, y):
	global paused, time_scale, use_textures, wireframe
	k = key.decode('utf-8').lower()
	if k == 'p':
		paused = not paused
	elif k == '+':
		time_scale *= 1.2
	elif k == '-':
		time_scale /= 1.2
	elif k == 't':
		use_textures = not use_textures
	elif k == 'w':
		wireframe = not wireframe
	elif k == '\x1b':  # ESC
		sys.exit(0)
	glutPostRedisplay()

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
	glutCreateWindow(b"Sistema Solar - Lista 7")
	init()
	glutDisplayFunc(display)
	glutReshapeFunc(reshape)
	glutKeyboardFunc(teclado)
	glutTimerFunc(16, atualizar, 0)
	glutMainLoop()

if __name__ == "__main__":
	main()

