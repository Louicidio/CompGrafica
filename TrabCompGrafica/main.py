import tkinter as tk
from video import ProcessadorVideo
from interface import Interface


def main():
    """Função principal"""
    CAMINHO_MUSICA = r"C:\Users\Luis Eduardo\Desktop\2025\2 Semestre\CompGrafica\TrabCompGrafica\homelander.wav"
    
    root = tk.Tk()
    
    processador = ProcessadorVideo(music_file=CAMINHO_MUSICA)
    
    app = Interface(root, processador)
    
    # Iniciar aplicação
    root.mainloop()
    
    processador.parar()


if __name__ == "__main__":
    main()
