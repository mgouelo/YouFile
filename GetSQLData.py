import hashlib
import mysql.connector as mc
import sys, os
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import *
from unidecode import unidecode

connection = mc.connect(
    host='127.0.0.1',
    database='YouFile',
    user=user,
    password=password
)
cursor = connection.cursor(dictionary=True) # les résultats des requêtes sont renvoyés sous forme de dictionnaire Python

# ────────────────────────────────────────────────
#  Whitelist
# ────────────────────────────────────────────────

ALLOWED_TABLES = {"users", "files", "comments", "subscriptions", "ratings", "password_resets"}

ALLOWED_COLUMNS = {
    "users": {"id","user_name","email","password_hash","bio","profile_pic","creation_date","last_update","is_admin"},
    "files": {"id","file_name","description","file_path","file_type","size_bytes","thumbnail_path","uploaded_at","updated_at","visibility","user_id"},
    "comments": {"id","user_id","file_id","parent_id","content","publi_date"},
    "subscriptions": {"id","subscriber_id","subscribed_id","subscription_date"},
    "ratings": {"id","file_id","user_id","value"},
    "password_resets": {"id","user_id","token","expiration","used","creation"},
}

# ────────────────────────────────────────────────
#  General functions
# ────────────────────────────────────────────────

def getTableInfo(table, value, key="id"):
    '''
    Precondition : receives a table, a key and a value to compare
    Postcondition : returns the elements of the table whose key (default “id”) is equal to the value
    '''

    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' non autorisée.")
    if key not in ALLOWED_COLUMNS[table]:
        raise ValueError(f"Colonne '{key}' non autorisée pour '{table}'.")
    sql = f"SELECT * FROM `{table}` WHERE `{key}` = %s;"
    cursor.execute(sql, (value,))
    rows = cursor.fetchall()
    return rows or None

def valueIsInTable(table, value, key="id"):
    '''
    Precondition : receives a table, a key (id by default) and a value
    Postcondition : returns True if the value of the key is present in the table, else False
    '''
    rows = getTableInfo(table, value, key)
    return bool(rows)

def closeDB():
    """
    Precondition : the DB should be open
    Postcondition : close properly the DB
    """
    cursor.close()
    connection.close()

# ────────────────────────────────────────────────
#  Users
# ────────────────────────────────────────────────

def getUserInfo(user_id):
    '''
    Precondition : receives an user id
    Postcondition : return user's details from the DB
    '''
    rows = getTableInfo('users', user_id)
    return rows[0] if rows else None

def searchUserByEmail(email):
    '''
    Precondition : receives an email
    Postcondition : returns, if exists, the user associated with the provided email
    '''
    rows = getTableInfo('users', email, key='email')
    return rows[0] if rows else None

# ────────────────────────────────────────────────
#  Subscriptions
# ────────────────────────────────────────────────

def getUserSubscribers(user_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns, if exists, a dict of user's subscribers
    '''
    return getTableInfo('subscriptions', user_id, 'subscribed_id') or []

def getSubscriptionInfo(sub_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns all user's subscribers
    '''
    rows = getTableInfo('subscriptions', sub_id)
    return rows[0] if rows else None

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
    ) AS subscribed;
    """
    cursor.execute(cmd, (id_subscriber, id_subscribed))
    result = cursor.fetchone()
    return result and result["subscribed"] == 1

def getUserSubscriptions(user_id):
    '''
    Precondition : receives an user id
    Postcondition : returns user's subscriptions (Renvoie les abonnements d'un utilisateur)
    '''

    cmd = """
    SELECT U.id AS user_id, U.user_name, U.profile_pic, U.bio
    FROM subscriptions AS S
        JOIN users AS U ON U.id = S.subscribed_id
    WHERE S.subscriber_id = %s;
    """
    cursor.execute(cmd, (user_id,))
    return cursor.fetchall()

# ────────────────────────────────────────────────
#  Files
# ────────────────────────────────────────────────

def getFileInfo(file_id):
    '''
    Precondition : reveives a file id
    Postcondition : returns, if exists, file's info
    '''
    rows = getTableInfo('files', file_id)
    return rows[0] if rows else None

def getUserFile(user_id):
    """
    Precondition : receives an user id
    Postcondition : returns files shared by the user
    """
    return getTableInfo('files', user_id, key='user_id') or []

def getAverageRatingFile(file_id):
    '''
    Precondition : receives a file id
    Postcondition : return the average note of the file
    '''
    results = getTableInfo('ratings', file_id, key='file_id')
    if not results:
        return None
    somme = sum(r["value"] for r in results)
    return somme / len(results)

def getRecentFiles(limit=4):
    '''
    Precondition : no requirement
    Postcondition : returns the most recently published files
    '''
    cursor.execute("SELECT * FROM files ORDER BY updated_at DESC LIMIT %s;", (limit,))
    return cursor.fetchall()

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
            F.*, 
            MATCH(F.file_name, F.description) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score
        FROM files AS F
        WHERE MATCH(F.file_name, F.description) AGAINST (%s IN NATURAL LANGUAGE MODE)
        ORDER BY score DESC, F.updated_at DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(sql, (query, query, limit, offset))
    return cursor.fetchall()

# ────────────────────────────────────────────────
#  Comments
# ────────────────────────────────────────────────

def getCommentInfo(comment_id):
    """
    Precondition : receives an comment id
    Postcondition : returns comment's info
    """
    rows = getTableInfo('comments', comment_id)
    return rows[0] if rows else None

def getFileShareComments(file_id):
    '''
    Precondition : receives the ID of a file
    Postcondition : returns the user's comment under the specified file
    '''

    cmd = """
    SELECT
        F.id AS file_id,
        C.user_id,
        U.user_name,
        U.profile_pic,
        C.id AS comment_id,
        C.content,
        C.publi_date
    FROM files AS F
    JOIN comments AS C ON C.file_id = F.id
    JOIN users AS U ON U.id = C.user_id
    WHERE F.id = %s;
    """
    cursor.execute(cmd, (file_id,))
    return cursor.fetchall()

def getUserComments(user_id):
    '''
    Precondition : reveives an user id
    Postcondition : returns user's comments
    '''

    cmd = """
    SELECT
        F.id AS file_id,
        F.file_name,
        U.id AS user_id,
        U.user_name,
        U.profile_pic,
        C.id AS comment_id,
        C.content,
        C.publi_date
    FROM users AS U
    JOIN comments AS C ON U.id = C.user_id
    JOIN files AS F ON C.file_id = F.id
    WHERE U.id = %s;
    """
    cursor.execute(cmd, (user_id,))
    return cursor.fetchall()

# ────────────────────────────────────────────────
#  Notes
# ────────────────────────────────────────────────

def getUserRating(user_id, file_id):
    """
    Precondition : receives an user id and a file id 
    Postcondition : returns user's note for this file
    """

    cmd = """
    SELECT id, value
    FROM ratings
    WHERE user_id = %s AND file_id = %s;
    """
    cursor.execute(cmd, (user_id, file_id))
    return cursor.fetchone()

def hasUserRatedFile(user_id, file_id):
    '''
    Precondition : reveives an user id and a file id
    Postcondition : returns True if the user rated files, else False
    '''
    return bool(getUserRating(user_id, file_id))

# ────────────────────────────────────────────────
#  Password reset
# ────────────────────────────────────────────────

def getPasswordResetInfo(resetPass_id):
    """
    Precondition : receives an password reset id
    Postcondition : returns password reseting's info
    """
    rows = getTableInfo('password_resets', resetPass_id)
    return rows[0] if rows else None

def isResetingPasswordStillPossible(resetPass_id):
    '''
    Precondition : receives a reset password id
    Postcondition : Returns True whether password reset with request ID id is still possible else False
    '''
    info = getPasswordResetInfo(resetPass_id)
    if not info:
        return False
    return datetime.datetime.now().replace(microsecond=0) <= info["expiration"] and info["used"] == False
