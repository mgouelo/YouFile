# le fichier __init__.py permet l'import des fichiers contenus dans le dossier routes.
# on y indique les emplacements des fichiers que contient le dossier routes


from flask import Blueprint
routes = Blueprint('routes', __name__)

from .index import *
from .acar1.acar1 import *
from .acar2.acar2 import *
from .acar1.page1 import *
from .acar1.page2 import *




