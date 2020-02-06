from flask import Blueprint

memeq = Blueprint('memeq', __name__)

from . import views
