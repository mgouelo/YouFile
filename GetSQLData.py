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

ALLOWED_TABLES = {"users", "files", "comments", "subscriptions", "ratings"}

def valueIsInTable(table:str, value, key:str="id"):
    '''
    Precondition : receives a table, a key (id by default) and a value
    Postcondition : returns True if the value of the key is present in the table, else False
    '''
    return getTableInfo(table, value, key) is not None


def getTableInfo(table, value, key:str="id"):
    '''
    Precondition : receives a table, a key and a value to compare
    Postcondition : returns the elements of the table whose key (default “id”) is equal to the value
    '''
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Error getTableInfo() : the table '{table}' doesn't exists")

    cursor.execute(f"SELECT * FROM `{table}` WHERE `{key}` = %s;", (value,))
    tablecontent = cursor.fetchall()
    if len(tablecontent) > 0:
        return tablecontent
    return None


def getUserInfo(user_id):
    '''
    Precondition : receives an user id
    Postcondition : return user's details from the DB
    '''
    return getTableInfo('users', user_id)


def getUserInfoDict(user_id):
    '''
    Precondition : receives an user id
    Postcondition : return a python dictionnary which contains user's details from the DB
    '''
    return convertToDictionnary(["id", "user_name", "email", "password_hash", "bio", "profile_pic", "creation_date", "last_update", "is_admin"], getUserInfo(user_id)[0])


def searchUserByEmail(email):
    '''
    Precondition : receives an email
    Postcondition : returns, if exists, the user associated with the provided email
    '''
    return getTableInfo('users', email, key='email')


def searchUserByEmailDict(email):
    '''
    Precondition : receives an email
    Postcondition : returns, if exists, a python dictionnary with the details about the user associated with the provided email
    '''
    try:
        return convertToDictionnary(["id", "user_name", "email", "password_hash"], searchUserByEmail(email)[0])
    except:
        return None

# subscriber_id est l'id de la personne qui s'est abonnée à subscribed_id
def getUserSubscribers(user_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns all user's subscribers
    '''
    return getTableInfo('subscriptions', user_id, 'subscribed_id')


def getUserSubscribersDict(user_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns, if exists, a dict of user's subscribers
    '''
    subList = getUserSubscribers(user_id)
    subDictofList = list()
    if subList is not None:
        for sub in subList:
            subDictofList.append(convertToDictionnary(["id", "subscriber_id", "subscribed_id", "subscription_date"], sub))
        return subDictofList
    else:
        return []


def getSubscriptionInfo(sub_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns all user's subscribers
    '''
    return getTableInfo('subscriptions', sub_id)


def getSubscriptionInfoDict(sub_id):
    '''
    Precondition : reveives a subscription id
    Postcondition : returns, if exists, a dict of subscription info
    '''
    return convertToDictionnary(["id", "subscriber_id", "subscribed_id", "subscription_date"], getSubscriptionInfo(sub_id)[0])


def getFileInfo(file_id):
    '''
    Precondition : reveives a file id
    Postcondition : returns, if exists, file's info
    '''
    return getTableInfo('files', file_id)


def getFileInfoDict(file_id):
    '''
    Precondition : reveives a file id
    Postcondition : returns, if exists, a dict with the file's info
    '''
    return convertToDictionnary(["id", "file_name", "description", "file_path", "file_type", "size_bytes", "thumbnail_path", "uploaded_at", "updated_at", "visibility", "user_id"], getFileInfo(file_id)[0])


def getRatingInfo(rate_id):
    '''
    Precondition : reveives a rate id
    Postcondition : returns, if exists, rate's info
    '''
    return getTableInfo('ratings', rate_id)


def getRatingInfoDict(rate_id):
    '''
    Precondition : reveives a rate id
    Postcondition : returns, if exists, a dict with the rate's info
    '''
    return convertToDictionnary(["id", "file_id", "user_id", "value"], getRatingInfo(rate_id)[0])


def getUserRating(user_id, file_id):
    """
    Precondition : receives an user id and a file id 
    Postcondition : returns user's note for this file
    """

    cmd = """
    SELECT id, value
    FROM ratings
    WHERE user_id = %s
    AND file_id = %s;
    
    """
    cursor.execute(cmd, (user_id, file_id,))
    rating = cursor.fetchall()
    if len(rating) == 0:
        return [(0, 0)]
    return rating


def getUserRatingDict(user_id, file_id):
    '''
    Precondition : reveives an user id and a file id
    Postcondition : returns, if exists, a dict with the rate's info
    '''
    return convertToDictionnary(["id", "value"], getUserRating(user_id, file_id)[0])


def hasUserRatedFileshare(user_id, file_id):
    '''
    Precondition : reveives an user id and a file id
    Postcondition : returns True if the user rated files, else False
    '''
    rate = getUserRating(user_id, file_id)
    return rate != [(0, 0)]


def getCommentInfo(comment_id):
    """
    Precondition : receives an comment id
    Postcondition : returns comment's info
    """
    return getTableInfo('comments', comment_id)


def getCommentInfoDict(comment_id):
    """
    Precondition : receives an comment id
    Postcondition : returns a dict with comment's info
    """
    return convertToDictionnary(["id", "user_id", "file_id", "parent_id", "content", "publi_date"], getCommentInfo(comment_id)[0])


def getPasswordResetInfo(resetPass_id):
    """
    Precondition : receives an password reset id
    Postcondition : returns password reseting's info
    """
    return getTableInfo('password_resets', resetPass_id)


def getPasswordResetInfoDict(resetPass_id):
    """
    Precondition : receives an password reset id
    Postcondition : returns a dict with password reseting's info
    """
    return convertToDictionnary(["id", "user_id", "token", "expiration", "used", "creation"], getPasswordResetInfo(resetPass_id)[0])


def closeDB():
    """
    Precondition : the DB should be open
    Postcondition : close properly the DB
    """
    cursor.close()
    connection.close()


def getFileShareComments(file_id):
    '''
    Precondition : receives the ID of a file
    Postcondition : returns the user's comment under the specified file
    '''

    cmd = """
    SELECT
        F.id,
        C.iduser,
        U.username,
        U.imagep,
        C.content,
        C.datepubl,
        C.id
    FROM
        files AS F
    JOIN
        comments AS C
        ON
            C.file_id = F.id
    JOIN
        users AS U
        ON
            U.id = C.user_id
    WHERE
        F.id = %s;
    """
    cursor.execute(cmd, (file_id,))
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


def getUserComments(user_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns user's comments
    '''

    cmd = """
    SELECT
        F.id,
        F.file_name,
        U.id,
        U.user_name,
        U.profile_pic,
        C.id,
        C.content,
        C.publi_date
        
    FROM
        users AS U
    JOIN
        comments AS C
        ON
            U.id = C.user_id
    JOIN
        files AS F
        ON
            C.file_id = F.id
    WHERE
        U.id = %s;
    """
    cursor.execute(cmd, (user_id,))
    contentTable = cursor.fetchall()
    return contentTable


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



def searchFile(search: str, limit: int = 10, offset: int = 0):
    """
    Precondition : fulltext research on files(file_name, description), mode 'natural language'.
    - search : user's research
    - limit : max number of files returned
    - offset : number of files to skip
    Postcondition : from most relevant to least relevant
    """
    query = unidecode((search or "").strip())
    if not query:
        return []

    sql = """
        SELECT
            f.id, f.file_name, f.file_path, f.description, f.publi_date, f.user_id,
            MATCH(f.file_name, f.description) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score
        FROM files f
        WHERE MATCH(f.file_name, f.description) AGAINST (%s IN NATURAL LANGUAGE MODE)
        ORDER BY score DESC, f.publi_date DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(sql, (query, query, limit, offset))
    result = cursor.fetchall()
    return result

    
def searchFileDict(search):
    lst = list()
    files = searchFile(search)
    for file in files:
        lst.append(convertToDictionnary(["id","iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], file))
    return lst


def getRecentfiles():
    '''
    Precondition : 
    Postcondition : returns the most recently published files
    '''

    cmd = """
    SELECT *
    FROM files
    ORDER BY updated_at DESC
    LIMIT 4;
    """
    cursor.execute(cmd)
    recentFiles = cursor.fetchall()
    return recentFiles


def getRecentfilesDict():
    files = getRecentfiles()
    files_list_dict = list()
    for file in files:
        files_list_dict.append(convertToDictionnary(["id", "iduser", "name", "datepubli", "filep", "imagep", "description", "filetype", "fileextension", "size"], file))
    return files_list_dict


def isSubscribed(id_subscriber, id_subscribed):
    '''
    Precondition : receives two users id
    Postcondition : returns True if the first user is subscribed to the second one
    '''

    if id_subscriber == id_subscribed:
        return False

    cmd = """
    SELECT EXISTS(
        SELECT 1
        FROM subscriptions
        WHERE subscriber_id = %s AND subscribed_id = %s
    );
    """
    cursor.execute(cmd, (id_subscriber, id_subscribed,))
    result = cursor.fetchone()
    if not result: # si cursor.fetchone() renvoie None => erreur coté SQL
        return False
    return result[0] == 1


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