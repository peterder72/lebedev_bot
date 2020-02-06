import os

from flask import Flask

from .memeq import memeq


def create_app():

    app = Flask(__name__)
    app.register_blueprint(memeq, url_prefix='/', static_url_path='/static')

    if not os.access('cache', os.F_OK):
        os.mkdir('cache')

    return app
