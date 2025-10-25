from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
import secrets

from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

from ChangeSQLData import *
from mail import *

app = Flask(__name__)

"""
La secret_key est utilisée pour signer ces données de session. Flask utilise cette clé pour crypter les informations stockées dans la session, et elle est également utilisée pour vérifier que ces données n'ont pas été altérées entre le moment où elles ont été signées et le moment où elles sont lues.

Il est crucial de définir une secret_key sécurisée et complexe pour empêcher les attaques potentielles visant à manipuler les données de session.

"""

app.config['SECRET_KEY']  = secrets.token_hex(24)



@app.before_request
def before_request(): #redirige d'une adresse http à https
    if "prev_url" not in session:
        session["prev_url"] = []
    else:
        session["prev_url"] = session["prev_url"]
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        if "http://" not in request.url:
            url= f"https://{request.url}"
        code = 301 #le code 301 permet au navigateur de rediriger automatiquement les requêtes http vers https par la suite
        return redirect(url, code=code) 




@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code 
    print(e)
    return render_template("error.html", errorcode = code), code



@app.route('/index')
@app.route('/home')
@app.route('/') #définit le chemin de la page html dans l'url
def index():
    '''
    Postcondition : retourne home.html et des variables python pour la page d'acceuil du site web
    '''
    session["prev_url"].append(("home",))
    recentfilesdict = getRecentfilesDict() #la fonction récupère le dictionnaire des 4 derniers fichiers postés sur le site.
    return render_template("home.html", recentfilesdict=recentfilesdict)



@app.route('/search', methods=["POST", "GET"])
def search():
    '''
    '''
    #if files == None:
        #return render_template()
    if request.method == "POST":
        datas = request.form
        search = datas.get('search')
        return redirect(f"/search?s={search}")
    else:
        keywords = request.args.get('s')
        session["prev_url"].append(("search", keywords))
        files_search = searchFileDict(keywords)
        return render_template("search.html", files_search=files_search)



@app.route('/postcomment', methods=["POST"])
def post_comment():
    datas = request.form
    prev_url = session["prev_url"][-1]
    if prev_url[0] != "fs":
        return redirect(url_for('home'))
    fileShare = prev_url[1]     
    if 'username' not in session:
        return redirect(url_for('login'))
    comment_content = datas.get('comment')
    addComment(session['iduser'], fileShare, comment_content)
    return redirect(request.referrer)



@app.route('/file', methods=["POST", "GET"])
@app.route('/fileshare', methods=["POST", "GET"])
@app.route('/fs', methods=["POST", "GET"])
def fs():
    '''
    Postcondition : retourne la page pour créer une nouvelle publication de fichier
    '''
    if request.method == "POST":
        datas = request.form
        postType = datas.get('postType')
        userInfo = datas.get('userInfo')
        if postType =="delcomment":
            commentID = datas.get('commentID')
            commentInformation = getCommentInformationDict(commentID)
            if userInfo == session['iduser']:
                delComment(commentID)
                return redirect(f"/fs?f={commentInformation['idfileshare']}")
            else:
                return redirect("/")
    else:
        file_id = request.args.get('f')
        fileInfo = getFileShareInformationDict(file_id)
        userInfo = getUserInformationDict(fileInfo["iduser"])
        comments = getFileShareCommentsDict(file_id)
        fileRating = getAverageRatingFileShare(file_id)
        if "username" in session:
            userRating = getUserRatingDict(session["iduser"], file_id)["value"]
        else:
            userRating = 0
        session["prev_url"].append(("fs", file_id))
        return render_template("fs.html", fileInfo = fileInfo, userInfo = userInfo, comments=comments, fileRating=fileRating, userRating=userRating)



@app.route('/rate')
def rate():
    note = int(request.args.get('r'))
    prev_url = session["prev_url"][-1]
    if prev_url[0] != "fs":
        return redirect("/")
    fileShareId = prev_url[1]
    if note < 1 or note > 5:
        return redirect(request.referrer)
    if 'username' not in session:
        return redirect(url_for('login'))
    if not hasUserRatedFileshare(session['iduser'], fileShareId):
        rateFileShare(session['iduser'], fileShareId, note)
    return redirect(request.referrer)


@app.route('/removeRating')
def removeRate():
    prev_url = session["prev_url"][-1]    
    if prev_url[0] != "fs":
        return redirect("/")    
    fileShareId = prev_url[1]
    if 'username' not in session:
        return redirect(url_for('login'))
    if  hasUserRatedFileshare(session['iduser'], fileShareId):
        removeRating(session['iduser'], fileShareId)
    return redirect(request.referrer)



@app.route('/upload', methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        image_allowed_extensions = ['.webp, .jpeg, .heif, .jpg, .tiff, .psd, .gif, .raw, .bmp, ;indd, .png'] #liste des extensions de fichiers image acceptées
        
        #récuperation des données du formulaires concernant les informations du fichier qui sera posté
        title = request.form.get('title')
        description = request.form.get('Description')
        filetype = request.form.get('fileType')

        file = request.files['file']
        image = request.files['image']

        filename = secure_filename(file.filename)
        imagename = secure_filename(image.filename)

        if imagename == '' or imagename.split(".")[-1] not in image_allowed_extensions:
            imagename = None
        
        if len(filename.split(".")) > 1:
            file_extension = "." + filename.split('.')[-1].lower()
        else:
            file_extension = "No file extension"

        post = uploadFile(session['iduser'], title, filename, imagename, description, filetype, file_extension, file, image)
        
        print(post)
        return redirect(f"/fs?f={post['id']}")
        
    else:
        if 'iduser' not  in session:
            return redirect("/login") #si l'utilisateur ne s'est pas connecté, il sera rediriger vers la page de connexion avant de pouvoir posté un fichier
        session["prev_url"].append(("upload", ))
        return render_template("upload.html")



@app.route('/edit/fileshare', methods=["POST", "GET"])
@app.route('/editfileshare', methods=["POST", "GET"])
def editfile():
    if "username" in session:
                if request.method == "POST":
                    image_allowed_extensions = ['.webp, .jpeg, .heif, .jpg, .tiff, .psd, .gif, .raw, .bmp, ;indd, .png'] #liste des extensions de fichiers image acceptées

                    name = request.form.get('username')
                    description = request.form.get('Description')
                    filetype = request.form.get("fileType")

                    image = request.files['image']
                    imagename = secure_filename(image.filename)
                    
                    if imagename == '':
                        imagename = None
                    
                    editFileShare(session['idmodifiedfileshare'], name, imagename, image, description, filetype)
                    return redirect(f"/fs?f={session['idmodifiedfileshare']}")
                else:
                    prev_url = session["prev_url"][-1]
                    session["prev_url"].append(("editfileshare", ))
                    if prev_url[0] != "fs":
                        return redirect(url_for('/'))
                    else:
                        fileShare = prev_url[1]                      
                        fileInfo = getFileShareInformationDict(fileShare)
                        session['idmodifiedfileshare'] = fileShare
                        if fileInfo['iduser'] == session['iduser']:
                            return render_template("editfileshare.html", fileInfo=fileInfo)
                        else:
                            return redirect('/login')
    else:
        return redirect("/")



@app.route('/user')
def user():
    '''
    Postcondition : retourne la page de profil de l'tilisateur avec son nom, ses fichiers & commentaires publiés.
    '''
    user_id = request.args.get('u')
    options = request.args.get('options', default='')
    userInfo = getUserInformationDict(user_id) #on récupère le dictionnaire d'information utilisateur 
    userFiles = getUserFileSharesDict(user_id) #idem pour les fichiers postés
    comments = getUserCommentsDict(user_id) #idem pour les commentaires publiés
    subscribers = getUserSubscribersDict(user_id)
    subscribed = False
    Delete = False
    if 'username' in session:
        if isSubscribed(session['iduser'], user_id):
            subscribed = True
    session["prev_url"].append(("user", user_id))
    return render_template("user.html", userInfo=userInfo, userFiles=userFiles, comments = comments, subscribed=subscribed, subscribers=subscribers)



@app.route('/subscribe')
def subscribe():
    if 'username' in session:
        user_subscriber = session['iduser']
        user_subscribed = request.args.get('u')
        if not isSubscribed(user_subscriber, user_subscribed):
            user_subscribe(user_subscriber, user_subscribed)            
        else:
            user_unsubscribe(user_subscriber, user_subscribed)
        return redirect(f'/user?u={user_subscribed}')
    else:
        return redirect('/login')



@app.route('/subscribtions')
def subscribtions():
    if 'username' in session:
        list_Subscribtion = getUserSubscribtionsDict(session['iduser'])
        user_info = getUserInformationDict(session['iduser'])
        session["prev_url"].append(("subscribtions", ))
        return render_template("Subscribtionpage.html", list_Subscribtion = list_Subscribtion, user_dict = user_info)
    else:
        return redirect('/login')



@app.route('/editprofile', methods=["POST", "GET"])
@app.route('/user/editprofile', methods=["POST", "GET"])
@app.route('/edit/user', methods=["POST", "GET"])
@app.route('/edit/userprofile', methods=["POST", "GET"])
def editprofile():
    if 'username' in session:
        if request.method == "POST":
            image_allowed_extensions = ['.webp, .jpeg, .heif, .jpg, .tiff, .psd, .gif, .raw, .bmp, ;indd, .png'] #liste des extensions de fichiers image acceptées
        
            name = request.form.get('username') 
            description = request.form.get('Description')

            image = request.files['image']
            imagename = secure_filename(image.filename)
            
            if imagename == '':
                imagename = None
            
            editUserProfile(session["iduser"], name, imagename, image, description)
            
            return redirect(f"/user?u={session['iduser']}")

        else:
            user_id = session['iduser']
            userInfo = getUserInformationDict(user_id)
            session["prev_url"].append(("editprofile", ))
            return render_template("editprofile.html", userInfo=userInfo)        
    else:
        return redirect(url_for('login'))



@app.route('/login', methods=["POST", "GET"])
def login():
    '''
    Postcondition : retourne la page de connexion
    '''
    if request.method == "POST": 
        datas = request.form # on récupère les données entrées dans le formulaire de connexion
        email = datas.get('email')
        password = datas.get('passwd')

        loginInfo = loginUser(email, password) 
    
        if loginInfo[0]:
            session['username'] = loginInfo[1]['username']
            session['iduser'] = loginInfo[1]['id']
            return redirect(f"/user?u={session['iduser']}") #url_for(f"user?u={session['iduser']}")) | l'url change en fonction des informations rentrées
        else:
            flash(" Authentification error ")
            return redirect(request.url)
    else:
        if 'username' in session:
            return redirect(f"/user?u={session['iduser']}")
        else:
            session["prev_url"].append(("login", ))
            return render_template("login.html")


    return render_template("login.html")


    
@app.route('/signup', methods=["POST", "GET"])
def signup():
    '''
    Postcondition : retourne la page de création de compte
    '''
    if request.method == "POST": #formulaire pour récupérer les informations de compte
        datas = request.form
        email = datas.get('email')
        username = datas.get('username')
        password = datas.get('passwrd')
        confirm_password = datas.get('confirmpasswrd')
        if shearchUserInformationEmail(email) is not None:
            flash(" It seems that this email is already associated with an account ! ")
            return redirect('/signup') #
        elif password != confirm_password: #si la confirmation du mot de passe est differente du mot de passe rentré :
            flash(" Passwords do not match ! ")
            return redirect('/signup') #pertinence absolue
        else:
            idUser = signUpUser(email, password, username) #si les information d'identification sont correctes, l'utilisateur est connecté et redirigé sur la page de profil utilisateur
            return redirect(f"/user?u={idUser}")
    else:
        session["prev_url"].append(("signup", ))
        return render_template("signup.html")



@app.route('/logout')
def logout():
    '''
    Postcondition : le bouton de déconnexion sur le bandeau déconnecte l'utilisateur de la session en cours et le redirige sur la page de connexion
    '''
    session.pop('username', None) #supprime la session en cours
    session.pop('iduser', None)
    return redirect(url_for('login'))



@app.route('/forgotpassword', methods=["POST", "GET"])
def forgotpassword():
    if request.method == "POST":
        email = request.form.get('email')
        userInfo = shearchUserInformationEmailDict(email)
        if userInfo is not None:
            linkreset = "rimains.freeboxos.fr:5005/resetforgottenpassword?i=" + userHasForgotPassword(userInfo["id"])
            send_verification_mail(email, linkreset)
            flash(" An reset link was sent to you by email ")
        else:
            flash(" No account is associated with this email ")
        return redirect(request.url)
    else:
        session["prev_url"].append(("forgotpassword", ))
        return render_template("forgetpassword.html")



@app.route('/resetforgottenpassword', methods=["POST", "GET"])
def resetforgottenpassword():
    idreset = request.args.get('i')
    if isResetingPasswordStillPossible(idreset):
        if request.method == "POST":
            userChangesPassword(getPasswordResetingInformationDict(idreset)["iduser"], request.form.get("password"), idreset)
            return redirect("/login")
        else:
            return render_template("resetpassword.html", url=request.url)
    else:
        return redirect("/")



@app.route('/delete', methods=["GET", "POST"])
def deletebutton():
    if request.method == "POST":
        user_id = request.args.get('u')
        userFiles = getUserFileSharesDict(user_id)
        return render_template("user.html")


if __name__ ==  '__main__' :
    context = ('ssl/cert.pem', 'ssl/key.pem')
    app.run( host='127.0.0.1', port=5005, ssl_context=context, debug=True )
