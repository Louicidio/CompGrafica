#!/usr/bin/env python
# coding: utf-8

# # Filtragem espacial
# 
# Adaptado dos exemplos de Moacir A. Ponti, ICMC/USP, 2021)

# In[2]:


import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys


# A filtragem espacial de imagens utiliza um elemento (filtro) para realizar operações que considerem não apenas o pixel atual, mas também outros pixels da imagem, comumente de acordo com uma vizinhança local (ou seja, pixels com coordenadas similares à do pixel sendo processado).
# Há métodos conhecidos como de filtragem não-local que operam sobre pixels distan distantes em termos de coordenadas, mas próximos com relação à similaridade de intensidade. Esses métodos tem resultados interessantes, mas não abordaremos nesse documento.
# A operação matemática que define a filtragem espacial local é conhecida por convolução, dada pelo operador asterisco ou estrela * (é importante diferenciar esse de um simples produto, que em notação matemática não é dado por esse mesmo símbolo):
# $$ g = w * f$$
# A equação acima significa que uma nova imagem g é obtida pela convolução do filtro w com a imagem de entrada f
# Para filtrar um pixel na imagem f centrado na coordenada (x,y), produzindo um novo pixel g(x,y), temos:
# $$ g(x,y) = \sum_{s=-a}^{a} \sum_{t=-b}^{b} w(s,t) \cdot f(x-s, y-t)$$
# A idéia dessa equação é que o filtro w tenha dimensões diferentes de f. Vamos dizer que w tem tamanho m x n e que f tenha tamanho M x N.
# Outra questão importante é que a equação assume que o filtro w é centrado na posição (0,0). Isso complica um pouco a equação, mas na prática a operação é bem simples.
# Para que a equação anterior funcione é preciso que m = 2a+1 e n = 2b+1
# 
# In[44]:

#2x2 -> 0,0
#3x3 -> 1,1
#4x4 -> 0,0
#5x5 -> 2,2
#6x6 -> 0,0
#7x7 -> 3,3

def image_convolution(f, w, debug=False):
	N, M = f.shape
	n, m = w.shape

	a = int((n-1)/2)
	b = int((m-1)/2)
	g = np.zeros(f.shape, dtype=np.uint8)

	for x in range(a, N-a):
		for y in range(b, M-b):
			sub_f = f[x-a:x+a+1, y-b:y+b+1]
			g[x,y] = np.sum(np.multiply(sub_f, w)).astype(np.uint8)

	return g


# vamos implementar uma funcao que executa convolucao para todos os pixels (x,y) da imagem
'''def image_convolution(f, w, debug=False):
    N,M = f.shape
    n,m = w.shape
    
    a = int((n-1)/2)
    b = int((m-1)/2)

    # obtem filtro invertido
    w_flip = np.flip( np.flip(w, 0) , 1)

    g = np.zeros(f.shape, dtype=np.uint8)

    # para cada pixel:
    print(a,N-a,b,M-b)
    for x in range(a,N-a):
        for y in range(b,M-b):
            # obtem submatriz a ser usada na convolucao
            sub_f = f[ x-a : x+a+1 , y-b:y+b+1 ]
            if (debug==True):
                print(str(x)+","+str(y)+" - subimage:\n"+str(sub_f))
            # calcula g em x,y
            g[x,y] = np.sum( np.multiply(sub_f, w_flip)).astype(np.uint8)

    return g'''


# ### Filtragem de imagens
# 
# Os filtros podem ser projetados com finalidades diferentes.
# Os filtros mais comuns usados são: filtros **smoothing**, que produzem imagens com menor variação local, reduzindo o ruído, mas também suprimindo pequenos detalhes e texturas; e filtros **diferenciais**, que funcionam como operador derivado, que podem ser usados para detectar transições locais, realçar a variação local, aumentando detalhes e ruídos se presentes na imagem.
# 
# Vamos mostrar alguns exemplos

# In[16]:


img1 = cv2.imread("pattern.png")
img2 = cv2.imread("gradient_noise.png")
img3 = cv2.imread("board.jpg")

#so convertendo devido ao BGR do opencv
img1_pb = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) 
img2_pb = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) 
img3_pb = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)


# In[17]:


# filtro de média 3x3 (simétrico) que considera a 4-vizinhança
w_med = np.matrix([[1, 1, 1], [1, 1, 1], [1, 1, 1]])/9.0
print(w_med)


# In[18]:


img2_media = image_convolution(img2_pb, w_med)
#sys.exit(0)

# exibindo imagem original e filtrada por w_med
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img2_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem original, ruidosa")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img2_media, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("imagem convoluída com filtro de media")
plt.axis('off')
plt.show()

sys.exit(0)


# Note que a imagem da direita tem uma borda com pixels pretos (valor 0) - isso ocorre porque não processamos os a pixels da borda, dado por: $a = (m-1)/2$, onde m é o tamanho do filtro. Nesse caso a = 1 e portanto a borda com valores 0 tem 1 pixel.
# Por exemplo, se aplicarmos um filtro maior, de tamanho 7, então teremos 3 pixels de borda.
# A seguir daremos outros exemplos de filtro, incluindo filtros diferenciais e também um exemplo de filtro aleatório.

# In[19]:


w_diff = np.matrix([[ 0, -1,  0], 
                    [-1,  4, -1], 
                    [ 0, -1,  0]])
print(w_diff)

img1_diff = image_convolution(img1_pb, w_diff)

plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(cv2.cvtColor(img1_pb, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("original image")
plt.axis('off')
plt.subplot(122)
plt.imshow(cv2.cvtColor(img1_diff, cv2.COLOR_BGR2RGB), cmap="gray", vmin=0, vmax=255)
plt.title("image filtered with differential filter")
plt.axis('off')


# In[20]:


w_vert = np.matrix([[-1, 0, 1], 
                    [-1, 0, 1], 
                    [-1, 0, 1]])
print(w_vert)

img1_vert = image_convolution(img1_pb, w_vert)

# exibindo imagem 1 e filtrada por w_diff
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img1_pb, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1")
plt.axis('off')
plt.subplot(122)
plt.imshow(img1_vert, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1 convoluída com filtro diferencial vertical")
plt.axis('off')


# Se você inspecionar os filtros acima, todos eles são projetados para produzir algum tipo de efeito em termos de difusão dos valores de pixel (suavização, por exemplo, filtro médio) ou detecção de transições (filtros diferenciais, por exemplo, bordas verticais).
# 
# Mas e se tivermos um * filtro aleatório *?

# In[21]:


# filtro de valores aleatorios 7x7
w_rand = np.random.random([7,7])
print(w_rand)
img3_wrand = image_convolution(img3_pb, w_rand)

# exibindo imagem 3 e filtrada por w_2 aleatorio
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img3_pb, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 3")
plt.axis('off')
plt.subplot(122)
plt.imshow(img3_wrand, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 3 convoluída com filtro aleatorio")
plt.axis('off')


# Não parece bom! Mas é um efeito do filtro aleatório ou há mais alguma coisa errada?
# 
# Nosso filtro tem valores positivos que somam muito mais que 1, a energia das regiões locais vai aumentar. Isso, a princípio, aumentaria apenas o brilho da imagem. Mas, na verdade, porque estamos operando em 8 bits, o efeito de tais convoluções sucessivas é * estouro *
# 

# In[22]:


np.sum(w_rand)


# Podemos normalizar o filtro pra somar 1

# In[23]:


w_rand = np.random.random([7,7])
w_rand = w_rand/np.sum(w_rand)
print(w_rand)
img3_wrand = image_convolution(img3_pb, w_rand)

plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img3, cmap="gray", vmin=0, vmax=255)
plt.title("image board")
plt.axis('off')
plt.subplot(122)
plt.imshow(img3_wrand, cmap="gray", vmin=0, vmax=255)
plt.title("filtering with a normalized random filter")
plt.axis('off')


# In[24]:


#Criando ruidos na imagem para poder testar os filtros
img4 = cv2.imread("lena.png")
img4_pb = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY) 
#0 a 15 os valores criados para ruido. Experimente adicionar mais valores.
noise = np.random.normal(0, 15, img4_pb.shape)
noisy = img4_pb + noise
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img4_pb, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1")
plt.axis('off')
plt.subplot(122)
plt.imshow(noisy, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1 convoluída com filtro diferencial vertical")
plt.axis('off')


# 

# In[46]:


#filtro passa baixa - 1/9
w_passaBaixa = np.matrix([[1,1,1],
                    [1,1,1],
                    [1,1,1]
                 ])
print(w_passaBaixa)
#aqui novamente houve um estouro da imagem, portanto, normalizamos.
w_passaBaixa = w_passaBaixa/np.sum(w_passaBaixa)
img4_passaBaixa = image_convolution(noisy, w_passaBaixa)


# exibindo imagem 1 e filtrada por w_diff
plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(noisy, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1")
plt.axis('off')
plt.subplot(122)
plt.imshow(img4_passaBaixa, cmap="gray", vmin=0, vmax=255)
plt.title("imagem 1 convoluída com filtro passa baixa")
plt.axis('off')


# ## Filtro passa alta

# In[47]:


#filtro passa alta utilizando passa baixa



# ## Sobel

# In[52]:


#ksize = janela 5x5


img_sobelx = cv2.Sobel(img4_pb,cv2.CV_8U,1,0,ksize=5)
img_sobely = cv2.Sobel(img4_pb,cv2.CV_8U,0,1,ksize=5)
sobel = img_sobelx + img_sobely

plt.figure(figsize=(12,12)) 
plt.subplot(122)
plt.imshow(sobel, cmap="gray", vmin=0, vmax=255)
plt.title("Sobel")
plt.axis('off')

plt.subplot(121)
plt.imshow(img4_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")


# ## Prewitt

# In[56]:


#FIltro de Prewitt nao tem no opencv, mas é so definir o valor do filtro x e y e somar os dois. 
import math

kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
#ao inves de usar a funcao convolucional dos exemplos acima, vc define o valor do filtro e usa no filter2D
img_prewittx = cv2.filter2D(img4_pb, -1, kernelx)
img_prewitty = cv2.filter2D(img4_pb, -1, kernely)
img_prewitt = img_prewittx + img_prewitty

plt.figure(figsize=(12,12)) 
plt.subplot(121)
plt.imshow(img4_pb, cmap="gray", vmin=0, vmax=255)
plt.title("Original")
plt.axis('off')
plt.subplot(122)
plt.imshow(img_prewitt, cmap="gray", vmin=0, vmax=255)
plt.title("Prewitt")


# ## Canny 
# 
# Como já foi detalhado acima, costumamos usar o operador de sobel e prewitt para calcular o gradiente.
# Como forma de simplificar o resultado final costumamos reduzir a borda pra minima possivel. 
# Como exatamente o algoritmo sabe se uma borda fraca está conectada a uma borda forte? O algoritmo de borda Canny determina isso considerando cada pixel de borda fraco e seus 8 pixels vizinhos. Se qualquer um de seus pixels adjacentes fizer parte de uma borda forte, considera-se que ele está conectado a uma borda forte. Assim, este pixel é preservado em nosso resultado final. Em contraste, se nenhum dos pixels vizinhos for forte, presume-se que não faz parte de uma aresta forte e, portanto, é suprimido.
# Decidir o que é realmente borda e o que é ruído. 
# Uma primeira abordagem é definir um limite, acima dele tudo é
# uma borda verdadeira e abaixo dele apagamos tudo
# 
# Após alguma experimentação, escolho 100 e 200 para nossos valores de limite baixo e alto, respectivamente. Na minha opinião, esses valores produzem o melhor resultado. No entanto, eles são um tanto subjetivos, então eu o encorajo a experimentar outros. Você pode encontrar outros valores de limite que produzem resultados melhores!
# 

# In[57]:


edges = cv2.Canny(img4_pb,100,200)

fig, ax = plt.subplots(ncols=2,figsize=(15,5))
ax[0].imshow(img4_pb,cmap = 'gray')
ax[0].set_title('Original Image') 
ax[0].axis('off')
ax[1].imshow(edges,cmap = 'gray')
ax[1].set_title('Edge Image')
ax[1].axis('off')
plt.show()


# In[ ]:




