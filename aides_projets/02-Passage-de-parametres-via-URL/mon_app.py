from flask import Flask, render_template, request
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY']  = secrets.token_hex(24)


@app.route("/")
def bonjour():
    return render_template("index.html")

liste_eleves = [
    {'nom': 'Dupont', 'prenom': 'Jean', 'classe': '2A'},
    {'nom': 'Dupont', 'prenom': 'Jeanne', 'classe': 'TG2'},
    {'nom': 'Marchand', 'prenom': 'Marie', 'classe': '2A'},
    {'nom': 'Martin', 'prenom': 'Adeline', 'classe': '1G1'},
    {'nom': 'Dupont', 'prenom': 'Lucas', 'classe': '2A'}
]

@app.route("/eleves")
def eleves():
    # 127.0.0.1:5000/eleves?c=2A
    classe = request.args.get('c')
    if classe:
        eleves_selectionnes = [eleve for eleve in liste_eleves if eleve['classe'] == classe]
    else:
        eleves_selectionnes = []

    return render_template("eleves.html", eleves=eleves_selectionnes)

if __name__ ==  '__main__' :
    app.run( host='0.0.0.0', port=5005)
    # app.run(debug=True) # connexion locale

