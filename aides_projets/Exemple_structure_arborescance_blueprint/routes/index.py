from flask import Flask, render_template, request, redirect, url_for, session,flash
from . import routes


@routes.route("/")
def index():
    return render_template("index.html")
