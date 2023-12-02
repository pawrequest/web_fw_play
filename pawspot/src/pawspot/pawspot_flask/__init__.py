import os
from pathlib import Path

from flask import Flask, session
from flask_bootstrap import Bootstrap
from flask_session import Session

static = Path(__file__).resolve().parent.parent / 'static'

app = Flask(__name__, static_folder=static, template_folder=static/'templates')
Bootstrap(app)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


# todo focus noqa
from . import routes  # noqa
