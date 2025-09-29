from flask import Flask, render_template
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY']  = secrets.token_hex(24)

@app.route("/")
def bonjour():
    return render_template("index.html")

@app.route("/heure")
def heure():
    date_heure = datetime.datetime.now()
    h = date_heure.hour
    m = date_heure.minute
    s = date_heure.second
    return render_template("heure.html", heure=h, minute=m, seconde=s)


if __name__ ==  '__main__' :
    context = ('ssl/cert.pem', 'ssl/key.pem')
    app.run( host='0.0.0.0', port=5005, ssl_context=context)
    # app.run(debug=True) # connexion locale
