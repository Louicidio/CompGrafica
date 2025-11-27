import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


g_arm_rotation = 0.0
g_gripper_angle = 30.0

def init():
    """Função de inicialização do OpenGL."""
    glClearColor(0.0, 0.0, 0.0, 0.0) # Cor de fundo preta
    glEnable(GL_DEPTH_TEST) # Habilita o teste de profundidade

def draw_box(width, height, depth):

    glPushMatrix()
    glScalef(width, height, depth) # Aplica a escala para "achatar" o cubo 
    glutSolidCube(1.0) # Desenha um cubo de arame de tamanho 1 [cite: 494]
    glPopMatrix()

def display():
    """Função principal de desenho."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() # Carrega a matriz identidade 
    glTranslatef(0.0, 0.0, -10.0) # [cite: 45, 171]

    glPushMatrix()
    glRotatef(g_arm_rotation, 0.0, 1.0, 0.0) # 

    glColor3f(0.7, 0.7, 0.7) # Cinza
    draw_box(4.0, 0.4, 0.4)

    glTranslatef(2.0, 0.0, 0.0) 

    glPushMatrix() # Salva o estado do sistema de coordenadas no "pulso" 
    glColor3f(1.0, 0.0, 0.0) # Vermelho
    glRotatef(g_gripper_angle, 0.0, 0.0, 1.0) # [cite: 520]
    glTranslatef(0.75, 0.0, 0.0)
    draw_box(1.5, 0.2, 0.4)
    glPopMatrix() # Restaura o sistema de coordenadas para o "pulso"

    glPushMatrix() # Salva o estado do sistema de coordenadas no "pulso" novamente
    glColor3f(1.0, 0.0, 0.0) # Vermelho
    glRotatef(-g_gripper_angle, 0.0, 0.0, 1.0) # [cite: 538]
    glTranslatef(0.75, 0.0, 0.0)
    draw_box(1.5, 0.2, 0.4)
    glPopMatrix() 

    glPopMatrix()

    glutSwapBuffers()

def autorotate_arm(value):
    """Função para autorotacionar o braço."""
    global g_arm_rotation
    g_arm_rotation += 2.0
    if g_arm_rotation >= 360.0:
        g_arm_rotation -= 360.0
    glutPostRedisplay() 
    glutTimerFunc(33, autorotate_arm, 0) # Aproximadamente 30 FPS

def reshape(w, h):
    """Função chamada quando a janela é redimensionada."""
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION) # Seleciona a pilha de matriz de projeção
    glLoadIdentity()
    gluPerspective(60.0, w/h, 1.0, 20.0)
    glMatrixMode(GL_MODELVIEW) # Retorna para a pilha de modelagem/visualização 
    glLoadIdentity()

def keyboard(key, x, y):
    """Função para tratar eventos de teclado."""
    global g_arm_rotation, g_gripper_angle

    key_str = key.decode("utf-8").lower()
    
    if key_str == 'a':
        g_arm_rotation += 5.0 # Gira para a esquerda
    elif key_str == 'd':
        g_arm_rotation -= 5.0 # Gira para a direita

    elif key_str == 'w': 
        g_gripper_angle += 5.0
        if g_gripper_angle > 45.0: # Limite máximo de abertura
            g_gripper_angle = 45.0
    elif key_str == 's': # 'S' 
        g_gripper_angle -= 5.0
        if g_gripper_angle < 5.0: 
            g_gripper_angle = 5.0
    
    elif ord(key) == 27: 
        sys.exit(0)

    glutPostRedisplay() 

def main():
    """Função principal."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Garra do Robo")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()