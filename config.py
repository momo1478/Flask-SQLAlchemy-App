## This file contains configuration options that flask or SQLAlchemy might need.
import os

HOST = "127.0.0.1"
PORT = 5000

## Directory to config.py on any computer.
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
