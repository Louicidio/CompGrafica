import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def criar_imagem_figura1():
    figura1_vetor = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=np.uint16)
    
    figura1 = figura1_vetor * 255 # converte pra cinza
    
    return figura1

def criar_elementos_estruturantes():
    # Elemento Estruturante (a) - retângulo 3x3
    estruturante_a = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    # Elemento Estruturante (b) - formato de cruz
    estruturante_b = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    
    return estruturante_a, estruturante_b

def aplicar_operacoes_morfologicas(figura1, estruturante_a, estruturante_b):
    """
    Aplica todas as operações morfológicas solicitadas
    """
    # i. Erosão com SE 2(a)
    erosao_a = cv2.erode(figura1, estruturante_a, iterations=1)
    
    # ii. Erosão com SE 2(b)
    erosao_b = cv2.erode(figura1, estruturante_b, iterations=1)
    
    # iii. Dilatação com SE 2(a)
    dilatacao_a = cv2.dilate(figura1, estruturante_a, iterations=1)
    
    # iv. Dilatação com SE 2(b)
    dilatacao_b = cv2.dilate(figura1, estruturante_b, iterations=1)
    
    return erosao_a, erosao_b, dilatacao_a, dilatacao_b


def main():
   
    figura1 = criar_imagem_figura1()
    
    #2. Criar os elementos estruturantes da Figura 2
    estruturante_a, estruturante_b = criar_elementos_estruturantes()
    
    #3. Aplicar as operações solicitadas
    erosao_a, erosao_b, dilatacao_a, dilatacao_b = aplicar_operacoes_morfologicas(
        figura1, estruturante_a, estruturante_b
    )
    visualizar_resultados_simples(figura1, erosao_a, erosao_b, dilatacao_a, dilatacao_b)

def visualizar_resultados_simples(figura1, erosao_a, erosao_b, dilatacao_a, dilatacao_b):
    
    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    axs[0, 0].imshow(figura1, cmap='gray')
    axs[0, 0].set_title('Original')
    axs[0, 0].axis('off')

    axs[0, 1].imshow(erosao_a, cmap='gray')
    axs[0, 1].set_title('Erosão com 2(a)')
    axs[0, 1].axis('off')

    axs[0, 2].imshow(erosao_b, cmap='gray')
    axs[0, 2].set_title('Erosão com 2(b)')
    axs[0, 2].axis('off')

    axs[1, 0].imshow(figura1, cmap='gray')
    axs[1, 0].set_title('Original')
    axs[1, 0].axis('off')

    axs[1, 1].imshow(dilatacao_a, cmap='gray')
    axs[1, 1].set_title('Dilatação com 2(a)')
    axs[1, 1].axis('off')

    axs[1, 2].imshow(dilatacao_b, cmap='gray')
    axs[1, 2].set_title('Dilatação com 2(b)')
    axs[1, 2].axis('off')

    plt.tight_layout()
    plt.savefig("ex1_resultado.png")
    plt.show()


# exercicio 2
def exercicio2_quadrados():
    img = cv2.imread('quadrados.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem quadrados.png não encontrada!')
        return
    
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    tamanho_se = 45
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (tamanho_se, tamanho_se))
    
    img_erodida = cv2.erode(img_bin, se, iterations=1)
    
    img_restaurada = cv2.dilate(img_erodida, se, iterations=1)
    
    cv2.imwrite('quadrados_erodida.png', img_erodida)
    cv2.imwrite('quadrados_restaurada.png', img_restaurada)
    
    plt.figure(figsize=(12,4))
    plt.subplot(1,3,1)
    plt.imshow(img_bin, cmap='gray')
    plt.title('Original binária')
    plt.axis('off')
    plt.subplot(1,3,2)
    plt.imshow(img_erodida, cmap='gray')
    plt.title('Após Erosão')
    plt.axis('off')
    plt.subplot(1,3,3)
    plt.imshow(img_restaurada, cmap='gray')
    plt.title('Após Dilatação')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('quadrados_exercicio2_resultado.png')
    plt.show()

# exercicio 3
def exercicio3_ruidos():
    img = cv2.imread('ruidos.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem ruidos.png não encontrada!')
        return
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # i. Abertura 
    abertura = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, se)
    cv2.imwrite('ruidos_abertura.png', abertura)
    # ii. Fechamento
    fechamento = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, se)
    cv2.imwrite('ruidos_fechamento.png', fechamento)
    # Exibir
    plt.figure(figsize=(12,4))
    plt.subplot(1,3,1)
    plt.imshow(img_bin, cmap='gray')
    plt.title('Original binária')
    plt.axis('off')
    plt.subplot(1,3,2)
    plt.imshow(abertura, cmap='gray')
    plt.title('Abertura (fundo limpo)')
    plt.axis('off')
    plt.subplot(1,3,3)
    plt.imshow(fechamento, cmap='gray')
    plt.title('Fechamento (objeto limpo)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('ruidos_exercicio3_resultado.png')
    plt.show()

# exercicio 4
def exercicio4_fronteiras():
    img = cv2.imread('cachorro.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem cachorro.png não encontrada!')
        return
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # Bordas internas: original - erosão
    erosao = cv2.erode(img_bin, se, iterations=1)
    borda_interna = img_bin - erosao
    cv2.imwrite('cachorro_borda_interna.png', borda_interna)
    # Bordas externas: dilatação - original
    dilatacao = cv2.dilate(img_bin, se, iterations=1)
    borda_externa = dilatacao - img_bin
    cv2.imwrite('cachorro_borda_externa.png', borda_externa)
    # Exibir
    plt.figure(figsize=(12,4))
    plt.subplot(1,3,1)
    plt.imshow(img_bin, cmap='gray')
    plt.title('Original binária')
    plt.axis('off')
    plt.subplot(1,3,2)
    plt.imshow(borda_interna, cmap='gray')
    plt.title('Borda interna')
    plt.axis('off')
    plt.subplot(1,3,3)
    plt.imshow(borda_externa, cmap='gray')
    plt.title('Borda externa')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('cachorro_exercicio4_resultado.png')
    plt.show()

# exercicio 5
def exercicio5_preenchimento():
    img = cv2.imread('gato.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem gato.png não encontrada!')
        return
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    seed = (img_bin.shape[0]//2, img_bin.shape[1]//2)
    mask = np.zeros((img_bin.shape[0]+2, img_bin.shape[1]+2), np.uint8) #preenchimento
    img_flood = img_bin.copy()
    cv2.floodFill(img_flood, mask, seedPoint=(seed[1], seed[0]), newVal=128)
    preenchida = np.where(img_flood==128, 255, 0).astype(np.uint8)
    cv2.imwrite('gato_preenchido.png', preenchida)
    # Exibir
    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.imshow(img_bin, cmap='gray')
    plt.title('Binária (invertida)')
    plt.axis('off')
    plt.subplot(1,2,2)
    plt.imshow(preenchida, cmap='gray')
    plt.title('Região preenchida')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('gato_exercicio5_resultado.png')
    plt.show()

# exercicio 6
def exercicio6_componentes_conectados(ponto=None):
    img = cv2.imread('quadrados.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem quadrados.png não encontrada!')
        return
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    # Se não passar ponto, pega o centro da imagem
    if ponto is None:
        ponto = (img_bin.shape[1]//2, img_bin.shape[0]//2)
    mask = np.zeros((img_bin.shape[0]+2, img_bin.shape[1]+2), np.uint8)
    img_color = cv2.cvtColor(img_bin, cv2.COLOR_GRAY2BGR)
    # Preencher com amarelo
    cv2.floodFill(img_color, mask, seedPoint=ponto, newVal=(0,255,255))
    componente = np.all(img_color == [0,255,255], axis=2).astype(np.uint8) * 255
    cv2.imwrite('quadrado80_amarelo.png', img_color)
    cv2.imwrite('quadrado80_sozinho.png', componente)
    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.imshow(img_color)
    plt.title('Componente em amarelo')
    plt.axis('off')
    plt.subplot(1,2,2)
    plt.imshow(componente, cmap='gray')
    plt.title('Só o componente')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('quadrado80_exercicio6_resultado.png')
    plt.show()


# exercicio 7
def exercicio7_img_aluno():
    img = cv2.imread('img_aluno.jpg', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Imagem img_aluno.jpg não encontrada!')
        return
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    # Dilatação
    dilatada = cv2.dilate(img, se, iterations=1)
    # Erosão
    erodida = cv2.erode(img, se, iterations=1)
    # Gradiente morfológico
    gradiente = dilatada - erodida
    cv2.imwrite('img_aluno_dilatada.png', dilatada)
    cv2.imwrite('img_aluno_erodida.png', erodida)
    cv2.imwrite('img_aluno_gradiente.png', gradiente)
    # Exibir
    plt.figure(figsize=(12,4))
    plt.subplot(1,4,1)
    plt.imshow(img, cmap='gray')
    plt.title('Original')
    plt.axis('off')
    plt.subplot(1,4,2)
    plt.imshow(dilatada, cmap='gray')
    plt.title('Dilatação')
    plt.axis('off')
    plt.subplot(1,4,3)
    plt.imshow(erodida, cmap='gray')
    plt.title('Erosão')
    plt.axis('off')
    plt.subplot(1,4,4)
    plt.imshow(gradiente, cmap='gray')
    plt.title('Gradiente')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('img_aluno_exercicio7_resultado.png')
    plt.show()

# Para rodar cada exercício, basta chamar a função correspondente:
# exercicio2_quadrados()
# exercicio3_ruidos()
# exercicio4_fronteiras()
# exercicio5_preenchimento()
# exercicio6_componentes_conectados((15, 15)) # informe o ponto inicial
exercicio7_img_aluno()
