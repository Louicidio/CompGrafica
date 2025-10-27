import tkinter as tk
from video import ProcessadorVideo
from interface import Interface


def main():
    """Função principal"""
    CAMINHO_MUSICA = r"C:\Users\luise\Desktop\2025-2\CompGrafica\TrabCompGrafica\homelander.wav"
    CAMINHO_MUSICA_PELUCIA = r"C:\Users\luise\Desktop\2025-2\CompGrafica\TrabCompGrafica\amongus.mp3"
    
    root = tk.Tk()
    
    processador = ProcessadorVideo(music_file=CAMINHO_MUSICA, music_file_objeto=CAMINHO_MUSICA_PELUCIA)
    
    app = Interface(root, processador)
    
    # Iniciar aplicação
    root.mainloop()
    
    processador.parar()


if __name__ == "__main__":
    main()
