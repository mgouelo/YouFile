from flask import Flask, render_template, request, redirect, url_for
from routes import *
import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY']  = secrets.token_hex(24)

app.register_blueprint(routes)

if __name__ ==  '__main__' :
    context = ('ssl/cert.pem', 'ssl/key.pem')
    app.run( host='0.0.0.0', port=5000,ssl_context=context)
    # app.run(debug=True) # connexion locale