import re
from string import ascii_lowercase



def fetch_words(read_mode):
    '''Función no alterda por el ataque'''
    '''Agregué la opción `enconding="utf8"`'''

    words_from_dictionary = [ word.strip() for word in open('words.txt', encoding="utf8").readlines() ]
    words_from_books = re.findall(r'\w+', open('BOOKS.txt', read_mode, encoding="utf8").read())
    
    return words_from_dictionary + words_from_books

# El archivo se había abierto como escritura, pero se debe abrir en modo lectura.
WORDS = fetch_words('r') #<<<---
LETTERS = list(ascii_lowercase) + ['ñ', 'á', 'é', 'í', 'ó', 'ú']
SYMBOLS = ',.-¡!¿?#$@&%`´'
OPENSYMBOL = "¡¿`"
CLOSESYMBOL = "!?´"
OTHERSYMBOL = ',.-#$@&%`´'
# Definimos un índice de palabras en el cual guardamos la frecuencia con la que se utiliza en nuestros
# textos de referencia
WORDS_INDEX = {}

# Las ordenes estaban mal y/o al reves.
for word in WORDS:
    if word in WORDS_INDEX:
        WORDS_INDEX.update({word:WORDS_INDEX[word]+ 1})
    else:
        WORDS_INDEX[word] = 1

for symbol in SYMBOLS:
    WORDS_INDEX[symbol]=1
    
def possible_corrections(word):
    if filter_real_numbers(word):
        return filter_real_numbers(word)
    cap=word[0].isupper()
    lword=word.lower()
    single_word_possible_corrections = filter_real_words([lword])
    one_length_edit_possible_corrections = filter_real_words(one_length_edit(lword))
    two_lenght_edit_possible_corrections = filter_real_words(two_lenght_edit(lword))
    no_correction_at_all = word
    if single_word_possible_corrections:
        if cap:
            return {option.title() for option in single_word_possible_corrections}
        return single_word_possible_corrections
    elif one_length_edit_possible_corrections:
        if cap:
            return {option.title() for option in one_length_edit_possible_corrections}
        return one_length_edit_possible_corrections
    elif two_lenght_edit_possible_corrections:
        if cap:
            return {option.title() for option in two_lenght_edit_possible_corrections}
        return two_lenght_edit_possible_corrections
    else:
        return no_correction_at_all
    
def spell_check_sentence(sentence):
    stripped_sentence = correct_split(sentence)#list(map(lambda x : x, lower_cased_sentence.split()))
    checked = map(spell_check_word, stripped_sentence) #<<-- Ojo que cambié ese filter por map
    checked_words=list(checked)
    return correct_join(checked_words)#' '.join(checked_words)

def spell_check_word(word):
    cap=word[0].isupper()
    options=possible_corrections(word.lower())
    res=max(options, key=language_model)
    if word.replace("a","á") in options:
        return word.replace("a","á")
    if word.replace("e","é") in options:
        return word.replace("e","é")
    if word.replace("i","í") in options:
        return word.replace("i","í")
    if word.replace("o","ó") in options:
        return word.replace("o","ó")
    if word.replace("u","ú") in options:
        return word.replace("u","ú")
    if not cap:
        return res
    else:
        return res.title()

#def spell_check_word(word):
#    cap=word[0].isupper()
#    if not cap:
#        return max(possible_corrections(word.lower()), key=language_model)
#    else:
#        return max(possible_corrections(word.lower()), key=language_model).title()
    
def language_model(word):
    return WORDS_INDEX.get(word, 0)

def filter_real_words(words):
    return set(word for word in words if word.lower() in WORDS_INDEX)

def filter_real_numbers(word):
    try:
        temp=int(word)
        return set([word])
    except:
        return set()

def one_length_edit(word):
    '''Función no alterda por el ataque'''
    
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    #print(splits)
    removals_of_one_letter = []
    
    for left, right in splits:
        if right:
            removals_of_one_letter.append(left + right[1:])
            
    two_letters_transposes = []
    
    for left, right in splits:
        if len(right) > 1:
            two_letters_transposes.append(left + right[1] + right[0] + right[2:])
            
    one_letter_replaces = []
    
    for left, right in splits:
        if right:
            for c in LETTERS:
                one_letter_replaces.append(left + c + right[1:])
                
    one_letter_insertions = []
    
    for left, right in splits:
        for c in LETTERS:
            one_letter_insertions.append(left + c + right)
    
    one_length_editions = removals_of_one_letter + two_letters_transposes + one_letter_replaces + one_letter_insertions
    
    return list(set(one_length_editions))

def correct_split(sentence):
    """ Esta función crea una lista que divide la frase ubicando los signos aparte
        de las palabras
        
        Parametros
        ----------
        sentence: str
                La frase que se desea partir
    """
    stripped = list(map(lambda x : x, sentence.split()))
    stripped_sentence=[]
    for word in stripped:
        if any(car in word for car in SYMBOLS):
            stripped_sentence.extend(word_split(word))
        else:
            stripped_sentence.append(word)
    return stripped_sentence

def word_split(word):
    punt=SYMBOLS
    if not any(p in word for p in punt):
        return [word]
    tw=word
    carry=[]
    while(len(punt)>0):
        if(tw.find(punt[0])!=-1):
            ri=tw[:tw.find(punt[0])]
            c=tw[tw.find(punt[0])]
            rd=tw[tw.find(punt[0])+1:]
            if(len(ri)!=0):
                carry.extend(word_split(ri))
            carry.append(c)
            if(len(rd)!=0):
                carry.extend(word_split(rd))
            break
        punt=punt[1:]
    return carry

def correct_join(words):
    """ Esta función crea la frase con el formato correcto de las palabras
    
        Parametro
        ---------
        words: list
             Las palabras que se desean conectar, puede contener signos de puntuación
    """
    sentence=""
    for i in range(len(words)):
        if any(car in words[i] for car in OPENSYMBOL):
            sentence+=words[i]
        elif any(car in words[i] for car in CLOSESYMBOL):
            if len(sentence)>0:
                sentence=sentence[:-1]+words[i]
        elif not any(car in words[i] for car in OTHERSYMBOL):
            sentence+=words[i]
            if i<len(words)-1:
                sentence+=" "
        elif any(car in words[i] for car in OTHERSYMBOL):
            if len(sentence)!=0:
                if any(car in words[i-1] for car in CLOSESYMBOL):
                    sentence+=words[i]
                else:
                    sentence=sentence[:-1]+words[i]
                if i<len(words)-1:
                    sentence+=" "
    return sentence

def two_lenght_edit(word):
    '''Función no alterda por el ataque'''
    return [e2 for e1 in one_length_edit(word) for e2 in one_length_edit(e1)]

