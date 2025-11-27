from OpenGL.GL import * 
from OpenGL.GLUT import * 

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glBegin(GL_POLYGON)
    glVertex3f(0.25, 0.25, 0.0)
    glVertex3f(0.75, 0.25, 0.0)
    glVertex3f(0.75, 0.75, 0.0)
    glVertex3f(0.25, 0.75, 0.0)
    glEnd()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"OpenGL Window")
    glutDisplayFunc(display)
    glutReshapeFunc()
    glutMainLoop()

def init():

    glClearColor(0.0, 0.0, 5.0, 5.0) #color 

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(500,500)
    glutInitWindowPosition(0,0)
    glutCreateWindow(b"Hello World")
    init()
    glutDisplayFunc(display)
    glutMainLoop()
    reshape(500,500)

def reshape(width, height):
    glViewport(0,0,width,height)

# def reshape(width, height):
#     size = width if width < height else height
#     glViewport(0,0, size, size)


if __name__ == "__main__":
    main()
    