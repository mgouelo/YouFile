from flask import Flask, render_template, request, redirect, url_for, session,flash
# on importe le contenu du dossier routes 
from .. import routes


@routes.route("/acar1_2")
def f_acar1_2():
    return render_template("acar1/page2.html")