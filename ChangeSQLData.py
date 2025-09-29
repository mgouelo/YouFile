import hashlib
from GetSQLData import *
from miscellaneous import *

def loginUser(email, password):
    '''
    Fonction de connection pour l'utilisateur.
    '''
    userInfo = shearchUserInformationEmailDict(email)
    #penser à la possibilité que l'email ne soit pas dans la db
    return hashlib.md5(password.encode()).hexdigest() == userInfo['password'] , userInfo
def signUpUser(email, password, username):
    '''
    Fonction d'inscription de l'utilisateur
    '''
    id = randomID(11)
    if getUserInformation(id) is not None:
        return signUpUser(email, password, username)
    else:
        cmd = """
            INSERT
            INTO
                `Users`(
                    `id`,
                    `username`,
                    `email`,
                    `creationdate`,
                    `password`
                )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s
                )
        """
        values = (f'{id}',
                f'{username}',
                f'{email}',
                f'{datetime.datetime.now().replace(microsecond=0)}',
                f'{hashlib.md5(password.encode()).hexdigest()}')
        cursor.execute(cmd, values)
        connection.commit()
        return id

def userHasForgotPassword(user_id):
    '''
    Permet à l'utlisateur de rénitialiser son mot de passe
    '''
    id = randomID(15)
    cmd = """
    INSERT
        INTO `ForgottenPasswords` 
            ( `id`,
                `iduser`,
            `limitdateavalaible`)
        VALUES 
        (
            %s,
            %s,
            %s
        )    
    """
    values = (id, user_id, datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=5))
    cursor.execute(cmd, values)
    connection.commit()
    return id

def userChangesPassword(user_id, newpassword, id_password_reset):
    '''
    Modifie le mot de place de l'utlisateur
    '''
    cmd = """
    UPDATE `Users`
    SET `password` = %s
    WHERE `id` = %s;
    """
    values = (hashlib.md5(newpassword.encode()).hexdigest(), user_id)
    cursor.execute(cmd, values)
    connection.commit()
    cmd = """
    UPDATE `ForgottenPasswords`
    SET `Used` = 1
    WHERE `id` = %s
    """
    values = (id_password_reset, )
    cursor.execute(cmd, values)
    connection.commit()


def addComment(userId:str, fileShareId:str, commentContent:str):
    cmd = """INSERT
                INTO 
                    `Comments`
                        (`iduser`,
                        `idfileshare`,
                        `idcommentawnser`,
                        `content`,
                        `datepubl`)
                 VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s)
            """
    values = (f'{userId}',
            f'{fileShareId}',
            None,
            f'{commentContent}',
            f'{datetime.datetime.now().replace(microsecond=0)}')
    cursor.execute(cmd, values)
    connection.commit()

def rateFileShare(iduser, fileShareId, rating):
    cmd = """INSERT
                INTO `Ratings` (
                    `idfileshare`,
                    `iduser`,
                    `value`)
                VALUES (
                    %s,
                    %s,
                    %s);
            """
    values = (fileShareId, iduser, rating)
    cursor.execute(cmd, values)
    connection.commit()
def removeRating(iduser, idfileshare):
    cmd = """ 
        DELETE FROM `Ratings`
        WHERE `idfileshare` = %s
        AND `iduser` = %s;"""
    values = (idfileshare, iduser)
    cursor.execute(cmd, values)
    connection.commit()

def uploadFile(iduser, title, filename, imagename, description, filetype, file_extension, FILE, IMAGE):
    id = randomID(11)
    if getFileShareInformation(id) is not None:
        return uploadFile(iduser, title, filename, imagename, description, filetype, file_extension, FILE, IMAGE)
    else:
        os.makedirs(f"static/Imgs/{id}")

        if imagename is None:
            imagep = "TestImgs.png"
        else:
            imagep = "image" + "." + imagename.split(".")[-1]
            IMAGE.save(os.path.join(f"static/Imgs/{id}", imagep))
        cmd = """INSERT
                    INTO
                        `Files`(
                            `id`,
                            `iduser`,
                            `name`,
                            `datepubli`,
                            `filep`,
                            `imagep`,
                            `Description`,
                            `fileType`,
                            `fileextension`,
                            `Size`
                        )
                    VALUES(
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )"""


        file_extension = "." + filename.split(".")[-1]
        filep = id + "--" + filename

        FILE.save(os.path.join("static/fileshares", filep[:len(file_extension)]))
        file_size = convertToAdequateFileSize(os.path.getsize(f"static/fileshares/{filep[:len(file_extension)]}"))

        values = (
            id,
            iduser,
            title,
            datetime.datetime.now().replace(microsecond=0),
            filep[:len(file_extension)],
            imagep,
            description,
            filetype,
            file_extension,
            file_size
        )

        cursor.execute(cmd, values)
        connection.commit()
        return {"id":id, }

def editFileShare(idfileshare, name, imagename, IMAGE, description, filetype):
    if imagename is None:
        cmd = """
        UPDATE 
            `Files`
        SET 
            `name`= %s,
            `Description` = %s,
            `fileType` =  %s
        WHERE `id` = %s
    """
        values = (
            name,
            description,
            filetype,
            idfileshare
        )
    else:
        imagep = "image" + idfileshare
        IMAGE.save(os.path.join("static/Imgs", imagep))
        cmd = """
            UPDATE 
                `Files`
            SET 
                `name`= %s,
                `imagep` = %s,
                `Description` = %s,
                `fileType` =  %s
            WHERE `id` = %s;
        """
        values = (
            name,
            imagep,
            description,
            filetype,
            idfileshare
        )
    
    cursor.execute(cmd, values)
    connection.commit()

def user_subscribe(user_subscriber, user_subscribed):
    cmd = """
    INSERT
        INTO
            `Subscribtions`
                (
                `idsubscriber`,
                `idsubscribed`,
                `datesubscribtion`)
        VALUES 
            (%s,
            %s,
            %s)
    """
    values = (
        user_subscriber,
        user_subscribed,
        datetime.datetime.now().replace(microsecond=0)
    )
    cursor.execute(cmd, values)
    connection.commit()

def user_unsubscribe(user_subscriber, user_subscribed):
    cmd = f"""
    DELETE FROM `Subscribtions`
    WHERE `idsubscriber` = '{user_subscriber}'
    AND `idsubscribed` = '{user_subscribed}';
    """
    cursor.execute(cmd)
    connection.commit()

def editUserProfile(iduser, name, imagename, IMAGE, description):
    if imagename is None:
        cmd = """
        UPDATE 
            `Users`
        SET 
            `username`= %s,
            `Description` = %s
        WHERE `id` = %s
    """
        values = (
            name,
            description,
            iduser
        )
    else:
        imagep = "pimage" + iduser + "." + imagename.split(".")[-1]
        IMAGE.save(os.path.join("static/Imgs", imagep))
        cmd = """
            UPDATE 
                `Users`
            SET 
                `username`= %s,
                `imagep` = %s,
                `Description` = %s
            WHERE `id` = %s;
        """
        values = (
                name,
                imagep,
                description,
                iduser
                )
    cursor.execute(cmd, values)
    connection.commit()

def delComment(commentID):
    cmd = f"DELETE FROM `Comments` WHERE `Comments`.`id` = {commentID}"
    cursor.execute(cmd)
    connection.commit()

def deletefile(id_file):
    cmd = f"""
    DELETE FROM Files
    WHERE id = '{id_file}';
    """
    cursor.execute(cmd)
    connection.commit()