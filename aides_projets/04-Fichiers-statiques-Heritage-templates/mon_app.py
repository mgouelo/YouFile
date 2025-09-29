#https://www.techwithtim.net/tutorials/flask

from flask import Flask, render_template, request, redirect, url_for
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY']  = secrets.token_hex(24)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/traitement", methods=["POST", "GET"])
def traitement():
    if request.method == "POST":
        donnees = request.form
        nom = donnees.get('nom')
        mdp = donnees.get('mdp')
        if nom == 'admin' and mdp == '1234':
            return render_template("traitement.html", nom_utilisateur=nom)
        else:
            return render_template("traitement.html")
    else:
        return redirect(url_for('index'))

if __name__ ==  '__main__' :
    context = ('../../ssl/cert.pem', '../../ssl/key.pem')
    app.run( host='0.0.0.0', port=5005,ssl_context=context)
    # app.run(debug=True) # connexion local
