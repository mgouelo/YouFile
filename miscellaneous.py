import random

def convertToDictionnary(keyslist:list or tuple, valueslist:list or tuple) -> dict:
    '''
    Convertit en dictionnaire des valeurs, en donnant des clés.
    Exemple: convertToDictionnary(['a', 'b', 'c'], (1, 2, 3)) renvoie {'a':1, 'b':2, 'c':3}
    '''
    assert len(keyslist) == len(valueslist)
    res = {}
    for i in range(len(keyslist)):
        res[keyslist[i]] = valueslist[i]
    return res

def randomID(lenght:int):
    '''
    Renvoie une suite de charactères aléatoire, de longeur lenght
    '''
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    id = str()
    while lenght != 0:
        id += characters[random.randint(0, len(characters) - 1)]
        lenght -= 1
    return id


def mostCommonElement(lst:list):
    '''
    Classe les éléments d'une liste du plus commun au plus rare
    '''
    return sorted(set(lst), key=lst.count, reverse=True)


def convertToAdequateFileSize(size:int):
    '''
    Renvoie la taille d'un fichier avec l'unitée la plus cohérente.
    Une taille 1x10^9 B renverra 1 GB, Une taille de 1090 B renverra 1.1 KB 
    '''
    if size >= 1000000000:
        return f"{round(size/1000000000, 1)} Gb"
    elif size >= 1000000:
        return f"{round(size/1000000, 1)} Mb"
    elif size >= 1000:
        return f"{round(size/1000, 1)} Kb"
    else:
        return f"{size}"