import hashlib
import mysql.connector as mc
import sys, os
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import *
from unidecode import unidecode

from miscellaneous import *

connection = mc.connect(host = '127.0.0.1', database = 'YouFile', user = user, password = password)
cursor = connection.cursor()


def keyisintable(table:str, keyv, key:str="id"):
    '''
    Donne si la valeur keyv de la clé key est présente dans la table table
    '''
    return getTableInformation(table, keyv, key) is not None

def getTableInformation(table, keyv, key:str="id"):
    '''
    Renvoie les éléments de la table table dont la clé key (par défaut "id") est égale à la valeur keyv
    '''
    if type(keyv) == str:
        cursor.execute(f"SELECT * FROM {table} WHERE `{key}` = '{keyv}';")
    else:
        cursor.execute(f"SELECT * FROM {table} WHERE `{key}` = {keyv};")
    tablecontent = cursor.fetchall()
    if len(tablecontent) > 0: return tablecontent
    return None


def getRoleInformation(id):
    return getTableInformation('Roles', id)
def getRoleInformationDict(id):
    return(["id", "username", "email", "role", "creationdate", "profile age"], getRoleInformation(id)[0])


def getImageInformation(id):
    return getTableInformation('Images', id)
def getImageInformationDict(id):
    return convertToDictionnary(["id", "filep"], getImageInformation(id)[0])

def getUserInformation(id):
    return getTableInformation('Users', id)
def getUserInformationDict(id):
    return convertToDictionnary(["id", "username", "email", "role", "creationdate", "profileImage", "description", "password"], getUserInformation(id)[0])
def shearchUserInformationEmail(email):
    return getTableInformation('Users', email, key='email')
def shearchUserInformationEmailDict(email):
    try:
        return convertToDictionnary(["id", "username", "email", "role", "creationdate", "profileImage", "description", "password"], shearchUserInformationEmail(email)[0])
    except:
        return None
def getUserSubscribers(id):
    return getTableInformation('Subscribtions', id, 'idsubscribed')
def getUserSubscribersDict(id):
    subscribersList = getUserSubscribers(id)
    subscribersListDict = list()
    if subscribersList is not None:
        for subscriber in subscribersList:
            subscribersListDict.append(convertToDictionnary(["id", "idsubscriber", "idsubscribed", "datesubscribtion"], subscriber))
        return subscribersListDict
    else:
        return []

def getSubscriptionInformation(id):
    return getTableInformation('Subscribtions', id)
def getSubscriptionInformationDict(id):
    return convertToDictionnary(["id", "idsubscriber", "idsubscribed", "datesubscribtion"], getSubscriptionInformation(id)[0])

def getFileShareInformation(id):
    return getTableInformation('Files', id)
def getFileShareInformationDict(id):
    return convertToDictionnary(["id", "iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], getFileShareInformation(id)[0])

def getRatingInformation(id):
    return getTableInformation('Ratings', id)
def getRatingInformationDict(id):
    return convertToDictionnary(["id", "idfileshare", "iduser", "value"], getRatingInformation(id)[0])
def getUserRating(iduser, idfileshare):
    cmd = f"""
    SELECT `id`, `value`
    FROM `Ratings`
    WHERE `idfileshare` = '{idfileshare}'
    AND `iduser` = '{iduser}';
    """
    cursor.execute(cmd)
    rating = cursor.fetchall()
    if len(rating) == 0:
        return [(0, 0)]
    print(rating)
    return rating
def getUserRatingDict(iduser, idfileshare):
    return convertToDictionnary(["id", "value"], getUserRating(iduser, idfileshare)[0])
def hasUserRatedFileshare(iduser, idfileshare):
    rating = getUserRating(iduser, idfileshare)
    return rating != [(0, 0)]

def getCommentInformation(id):
    return getTableInformation('Comments', id)
def getCommentInformationDict(id):
    return convertToDictionnary(["id", "iduser", "idfileshare", "idcommentawnser", "content", "datepubl"], getCommentInformation(id)[0])

def getPasswordResetingInformation(id):
    return getTableInformation(' ForgottenPasswords', id)
def getPasswordResetingInformationDict(id):
    return convertToDictionnary(["id", "iduser", "limitdate", "used"], getPasswordResetingInformation(id)[0])

def closeDB():
    cursor.close()
    connection.close()

def getFileShareComments(id):
    cmd = f"""
    SELECT
        F.id,
        C.iduser,
        U.username,
        U.imagep,
        C.content,
        C.datepubl,
        C.id
    FROM
        Files AS F
    JOIN
        Comments AS C
        ON
            C.idfileshare = F.id
    JOIN
        Users AS U
        ON
            U.id = C.iduser
    WHERE
        F.id = '{id}';
    """
    cursor.execute(cmd)
    tablecontent = cursor.fetchall()
    return tablecontent
def getFileShareCommentsDict(id):
    commentList = getFileShareComments(id)
    commentsListDict = list()
    if commentList is not None:
        for comment in commentList:
            commentsListDict.append(convertToDictionnary(["idfileshare", "iduser", "username", "userimagep","content", "datepubl", "idcomment"], comment))
        return commentsListDict
    else:
        return None

def getUserComments(id):
    cmd = f"""
    SELECT
        F.id,
        U.id,
        U.username,
        U.imagep,
        C.content,
        C.datepubl,
        C.id,
        F.name
    FROM
        Users AS U
    JOIN
        Comments AS C
        ON
            C.iduser = U.id
    JOIN
        Files AS F
        ON
            F.id = C.idfileshare
    WHERE
        U.id = '{id}';
    """
    cursor.execute(cmd)
    tablecontent = cursor.fetchall()
    return tablecontent
def getUserCommentsDict(id):
    commentList = getUserComments(id)
    commentsListDict = list()
    if commentList is not None:
        for comment in commentList:
            commentsListDict.append(convertToDictionnary(["idfileshare", "iduser", "username", "userimagep","content", "datepubl", "idcomment", "filename"], comment))
        return commentsListDict
    else:
        return None

def getUserFileShares(iduser):
    return getTableInformation('Files', iduser, key='iduser')
def getUserFileSharesDict(iduser):
    filesList = getUserFileShares(iduser)
    filesListDict = list()
    try:
        for file in filesList:
            filesListDict.append(convertToDictionnary(["id", "iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], file))
        return filesListDict
    except:
        return None

def searchFile(search):
    '''
    Renvoie les fichiers comportant au moins un des mots de search. Ces fichiers sont triés du plus pertinent au moins pertinent. Le plus pertinent correspond à celui dont le titre resemble le plus à la recherche.
    '''
    listwords = unidecode(str(search)).lower().split(" ")
    files = []
    file_list = []
    for word in listwords:
        cmd =   """
        SELECT *
        FROM Files
        WHERE name LIKE %s;
        """
        #SELECT * FROM blah WHERE email LIKE CONCAT('%', %s, '%') limit 10
        cursor.execute(cmd, ("%" + word + "%",))
        files = cursor.fetchall()
        for elt in files:
            file_list.append(elt)
    return mostCommonElement(file_list)
    
def searchFileDict(search):
    lst = list()
    files = searchFile(search)
    for file in files:
        lst.append(convertToDictionnary(["id","iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], file))
    return lst

def getRecentfiles():
    '''
    Renvoie les fichiers mis en ligne le plus récemment
    '''
    cmd = f"""
    SELECT *
    FROM Files
    ORDER BY datepubli DESC
    LIMIT 4;   
    """
    cursor.execute(cmd)
    allfiles = cursor.fetchall()
    return allfiles

def getRecentfilesDict():
    files = getRecentfiles()
    files_list_dict = list()
    for file in files:
        files_list_dict.append(convertToDictionnary(["id", "iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], file))
    return files_list_dict

def isSubscribed(id_subscriber, id_subscribed):
    '''
    Renvoie True si l'utilisateur id_subsriber est abonné à id_subsribed, False sinon
    '''
    cmd = f"""
    SELECT *
    FROM `Subscribtions`
    WHERE `idsubscriber` = '{id_subscriber}'
    AND `idsubscribed` = '{id_subscribed}';
    """
    cursor.execute(cmd)
    result = cursor.fetchall()
    return len(result) != 0

def getAverageRatingFileShare(id):
    '''
    Renvoie la note moyenne associée à un fichier.
    '''
    results = getTableInformation('Ratings', id, key='idfileshare')
    if results  is not None:
        somme = float()
        for result in results:
            somme += result[3]
        return somme / len(results)
    else:
        return 'No Ratings'

def getUserSubscribtions(id):
    '''
    Renvoie les abonnements d'un utlisateur
    '''
    cmd = f"""
    SELECT U.id ,U.username, U.imagep, U.description
    FROM Subscribtions 
    JOIN Users AS U ON U.id = Subscribtions.idsubscribed
    WHERE Subscribtions.idsubscriber = '{id}';
    """
    cursor.execute(cmd)
    result = cursor.fetchall()
    return result

def getUserSubscribtionsDict(id):
    list_keys = ['id', 'username', 'imagep', 'description']
    list_tuple = getUserSubscribtions(id)
    list_dict = []
    for tup in list_tuple:
        list_dict.append(convertToDictionnary(list_keys, tup))
    return list_dict

def isResetingPasswordStillPossible(id):
    '''
    Renvoie si la rénitialisation d'un mot de passe avec la demande possédant l'id id est toujours possible
    '''
    result = getPasswordResetingInformationDict(id)
    return datetime.datetime.now().replace(microsecond=0) <= result["limitdate"] and result["used"] == 0