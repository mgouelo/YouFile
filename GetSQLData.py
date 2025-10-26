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

ALLOWED_COLUMNS = {
    "users": {"id","user_name","email","password_hash","bio","profile_pic","creation_date","last_update","is_admin"},
    "files": {"id","file_name","description","file_path","file_type","size_bytes","thumbnail_path","uploaded_at","updated_at","visibility","user_id"},
    "comments": {"id","user_id","file_id","parent_id","content","publi_date"},
    "subscriptions": {"id","subscriber_id","subscribed_id","subscription_date"},
    "ratings": {"id","file_id","user_id","value"},
    "password_resets": {"id","user_id","token","expiration","used","creation"},
}

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
    if key not in ALLOWED_COLUMNS[table]:
        raise ValueError(f"Error getTableInfo(): column '{key}' not allowed for '{table}'")

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
    rows =  getUserInfo(user_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "user_name", "email", "password_hash", "bio", "profile_pic", "creation_date", "last_update", "is_admin"], rows[0])


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
    rows = searchUserByEmail(email)
    if not rows:
        return None
    return convertToDictionnary(["id", "user_name", "email", "password_hash"], rows[0])


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
    rows = getSubscriptionInfo(sub_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "subscriber_id", "subscribed_id", "subscription_date"], rows[0])


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
    rows = getFileInfo(file_id)
    if not rows:
        return None
    return convertToDictionnary(["file_id", "file_name", "description", "file_path", "file_type", "size_bytes", "thumbnail_path", "uploaded_at", "updated_at", "visibility", "user_id"], rows[0])


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
    rows = getRatingInfo(rate_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "file_id", "user_id", "value"], rows[0])


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
        return None
    return rating


def getUserRatingDict(user_id, file_id):
    '''
    Precondition : reveives an user id and a file id
    Postcondition : returns, if exists, a dict with the rate's info
    '''
    rows = getUserRating(user_id, file_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "value"], rows[0])


def hasUserRatedFileshare(user_id, file_id):
    '''
    Precondition : reveives an user id and a file id
    Postcondition : returns True if the user rated files, else False
    '''
    rate = getUserRating(user_id, file_id)
    return rate != None


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
    rows = getCommentInfo(comment_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "user_id", "file_id", "parent_id", "content", "publi_date"], rows[0])


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
        C.user_id,
        U.user_name,
        U.profile_pic,
        C.id,
        C.content,
        C.publi_date
        
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


def getFileCommentsDict(file_id):
    """
    Precondition : receives a file id
    Postcondition : returns a list of dicts of comments under the provided file
    """
    commentList = getFileShareComments(file_id)
    commentsListDict = list()
    if commentList is not None:
        for comment in commentList:
            commentsListDict.append(convertToDictionnary(["file_id", "user_id", "user_name", "profile_pic", "comment_id", "content", "publi_date"], comment))
        return commentsListDict
    else:
        return []


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


def getUserCommentsDict(user_id):
    """
    Precondition : receives an user id
    Postcondition : returns a list of dicts of user's comments
    """
    commentList = getUserComments(user_id)
    commentsListDict = list()
    if commentList is not None:
        for comment in commentList:
            commentsListDict.append(convertToDictionnary(["file_id", "file_name", "user_id", "user_name", "profile_pic", "comment_id", "content", "publi_date"], comment))
        return commentsListDict
    else:
        return []


def getUserFile(user_id):
    """
    Precondition : receives an user id
    Postcondition : returns files shared by the user
    """
    return getTableInfo('files', user_id, key='user_id')


def getUserFileDict(user_id):
    filesList = getUserFile(user_id)
    if not filesList:
        return []
    else:
        filesListDict = list()
        for file in filesList:
            filesListDict.append(convertToDictionnary(["file_id", "file_name", "description", "file_path", "file_type", "size_bytes", "thumbnail_path", "uploaded_at", "updated_at", "visibility", "user_id"], file))
        return filesListDict


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
            F.id, F.file_name, F.description, F.file_path, F.file_type, F.size_bytes, F.thumbnail_path, F.uploaded_at, F.updated_at, F.visibility, F.user_id,
            MATCH(F.file_name, F.description) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score
        FROM files AS F
        WHERE MATCH(F.file_name, F.description) AGAINST (%s IN NATURAL LANGUAGE MODE)
        ORDER BY score DESC, F.updated_at DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(sql, (query, query, limit, offset))
    result = cursor.fetchall()
    return result

    
def searchFileDict(search):
    '''
    Precondition : receives user's research
    Postcondition : returns the most recently published files
    '''
    resultListDict = list()
    files = searchFile(search)
    for file in files:
        resultListDict.append(convertToDictionnary(["file_id", "file_name", "description", "file_path", "file_type", "size_bytes", "thumbnail_path", "uploaded_at", "updated_at", "visibility", "user_id"], file))
    return resultListDict


def getRecentFiles():
    '''
    Precondition : no requirement
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


def getRecentFilesDict():
    '''
    Precondition : no requirement
    Postcondition : returns a list of dict of the most recently published files
    '''
    files = getRecentFiles()
    fileListDict = list()
    for file in files:
        fileListDict.append(convertToDictionnary(["file_id", "file_name", "description", "file_path", "file_type", "size_bytes", "thumbnail_path", "uploaded_at", "updated_at", "visibility", "user_id"], file))
    return fileListDict


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


def getAverageRatingFile(file_id):
    '''
    Precondition : receives a file id
    Postcondition : return the average note of the file
    '''
    results = getTableInfo('ratings', file_id, key='file_id')
    if results is not None:
        somme = float()
        for result in results:
            somme += result[3]
        return somme / len(results)
    else:
        return None


def getUserSubscriptions(user_id):
    '''
    Precondition : receives an user id
    Postcondition : returns user's subscriptions (Renvoie les abonnements d'un utilisateur)
    '''
    cmd = """
    SELECT U.id, U.user_name, U.profile_pic, U.bio
    FROM subscriptions AS S
        JOIN users AS U 
            ON U.id = S.subscribed_id
    WHERE S.subscriber_id = %s;
    """
    cursor.execute(cmd, (user_id,))
    result = cursor.fetchall()
    return result


def getUserSubscriptionsDict(user_id):
    '''
    Precondition : receives an user id
    Postcondition : returns a list of dicts of user's subscriptions (Renvoie les abonnements d'un utilisateur)
    '''
    list_keys = ['user_id', 'user_name', 'profile_pic', 'bio']
    list_tuple = getUserSubscriptions(user_id)
    subListDict = []
    for tup in list_tuple:
        subListDict.append(convertToDictionnary(list_keys, tup))
    return subListDict


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
    rows = getPasswordResetInfo(resetPass_id)
    if not rows:
        return None
    return convertToDictionnary(["id", "user_id", "token", "expiration", "used", "creation"], rows[0])


def isResetingPasswordStillPossible(resetPass_id):
    '''
    Precondition : receives a reset password id
    Postcondition : Returns True whether password reset with request ID id is still possible else False
    '''
    result = getPasswordResetInfoDict(resetPass_id)
    return datetime.datetime.now().replace(microsecond=0) <= result["expiration"] and result["used"] == False