# pip install mysql-connector-python
#https://www.youtube.com/watch?v=2R-BveCE-so&list=PLrSOXFDHBtfFMB2Qeuej6efzZRvjRdXo8&index=1

import mysql.connector as mc
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import *
try :
    connection = mc.connect(host = 'localhost', database = 'groupe5', user = user, password = password)
    cursor = connection.cursor()
    req = 'SELECT * FROM Users'
    cursor.execute(req)
    print(cursor.fetchall())
except mc.Error as e:
    print(e)

finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()

    
