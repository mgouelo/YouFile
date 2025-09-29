from flask import Flask, render_template, request, redirect, url_for, session,flash
# on importe le contenu du dossier routes 
from .. import routes

@routes.route("/acar2")

def f_acar2():
    return render_template("acar2/acar2.html")