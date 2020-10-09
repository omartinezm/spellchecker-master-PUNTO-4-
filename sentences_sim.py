import numpy as np
from numpy import linalg as la
from string import ascii_lowercase
from spell_checker import *

# Lista con vectores pre-entrenados de palabras: obtenido de la página
# https://www.kaggle.com/rtatman/pretrained-word-vectors-for-spanish
f = open("SBW-vectors-300-min5.txt", "r", encoding="utf8") #


# Cantidad de vectores y entradas por vector
n_words,n_entries=list(map(int,f.readline().split(" "))) 

# Diccionario con los vectores
w2v={} 
for i in range(n_words):
    tl=f.readline().split(" ")
    w2v[tl[0]]=list(map(float,tl[1:]))
f.close()

# Lista de posibles palabras
WORD_LIST=list(w2v.keys())

#Se actualiza la lista de palabras en la rutina que corrige las frases.
for word in WORD_LIST:
    if word in WORDS_INDEX:
        pass#WORDS_INDEX.update({word:WORDS_INDEX[word]+ 1})
    else:
        WORDS_INDEX[word] = 1
        
# Definimos la distancia entre palabras
def distance(v1,v2):
    """ Mide la distancia entre las palabras.
    
        Acá hay varias formas de medirlas, nos quedamos con el coseno.
    
        Parametros:
        -----------
        v1: list
            vector de floats
        v2: list
            vector de floats
    """
    return np.dot(v1,v2)/(la.norm(v1)*la.norm(v2))

# Definimos la similaridad de una palabra con un cada palabra de una frase
def similarity(v1,s):
    """ Mide la similaridad de una palabra con cada palabra de una frase dada
        
        Parametros:
        -----------
        v1: string
            palabra a comparar
        s: list
            frase a comparar
    """
    #return list(set(1/(1+distance(w2v[v1],w2v[x])) for x in v2))
    return list(set(np.dot(w2v[v1],w2v[x])/(la.norm(w2v[v1])*la.norm(w2v[x])) for x in s))

# Medimos la similaridad entre dos frases completas
def measureSimilarity(s1,s2):
    """ Mide la similaridad de contenido y motivo entre dos frases
        
        La forma en la cual se calcula es midiendo la fuerza de contexto que tiene una
        frase en la otra. Es decir, con qué fuerza poddemos cambiar algunas palabras de
        una frase por las palabras de la otra.
        
        Esto se basa en una extensión del método Word2Vec (https://code.google.com/archive/p/word2vec/)
        de Google. El cual transforma una palabra en un vector que mide la fuerza de relación
        con otras palabras.
        
        La implementación acá dada es una modificación de la mostrada por I. Sánchez en un trabajo
        de grado.
        
        Parametros:
        s1: list
            Primera frase
        s2: list
            Segunda frase
    """
    ss1=list(map(lambda x : x.strip('.,?¿%$¡!'), s1.split()))
    ss2 = list(map(lambda x : x.strip('.,?¿%$¡!'), s2.split()))
    s=ss1+ss2
    bow=[]
    for i in range(len(s)):
        bow.append(0) #Inicializamos el vector de comparación en ceros
    for i in range(len(ss1)): #Empezamos con la primera frase
        if ss1[i] in WORD_LIST and all(x in WORD_LIST for x in ss2):
            bow[i]=max(similarity(ss1[i],ss2))
            # Si la palabra no está en la frase, vemos qué similaridad tiene con las palabras de la frase
    for i in range(len(ss2)): #Ahora revisamos la segunda frase
        if ss2[i] in WORD_LIST and all(x in WORD_LIST for x in ss1):
            bow[i+len(ss1)]=max(similarity(ss2[i],ss1))
    sim = sum(bow)/len(bow)
    return sim

def bestChoice(options,answer):
    """ Selecciona la frase más parecida a la respuesta dada
        
        Basado en las opciones y en la respuesta dada, la función crea un vector
        de similaridades. La i-ésima entrada es la similaridad de la i-ésima frase
        con la respuesta. Este vector contiene números de cero a uno, entre más
        grande más similares son las frases.
        
        Caso 1: Hay dos frases en las opciones
            En este caso se compara la diferencia entre las dos entradas. Si esta
            diferencia es máyor a 0.05 se considera que la frase con más similaridad
            es una opción válida. En caso contrario no hay similaridad.
        Caso 2: Hay más de dos frases en las opciones
            Se estan estándariza el vector a un distribución normal estándar. Si la
            frase con mayor similitud está alejada una desviación estándar de la media
            enctonces se toma como opción válida. En casi contrario no hay similaridad
        
        Esta distinción se hace porque el método de estandarización no tiene sentido
        cuando son dos datos.
        
        Los umbrales se escogieron basados en una regresión que se hizo con pocos
        datos. Estoy seguro que con más datos y una revisión más minuciosa se puede
        lograr un modelo más robusto.
        
        Parámetros:
        -----------
        options: list
            Lista con las opciones de frases posibles dadas por el sistema
        answer: str
            Respuesta dada por el usuario.
    """
    sim=[]
    for op in options:
        sim.append(measureSimilarity(spell_check_sentence(op.lower()),spell_check_sentence(answer.lower())))
    maxsim=max(sim)
    minsim=min(sim)
    mean=np.mean(sim)
    std=np.std(sim)
    ust=(sim-mean)/std
    if(len(options)==2):
        if(maxsim-minsim>0.05):
            return options[sim.index(maxsim)]
        else:
            return "ninguno"
    if(max(ust)>1.0):
        return options[sim.index(maxsim)]
    else:
        return "ninguno"