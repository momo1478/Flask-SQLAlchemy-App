#### This file initializes the flask app. Initialization, including configuration
#### hookup goes here.

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

## Start Flask app here
fapp = Flask(__name__)

## Get configuration info from config.py (setup options for flask app)
fapp.config.from_object('config') 

## Startup Database
db = SQLAlchemy(fapp)

#Import models of DB after we start up the database
from app import views, models

models.init_db()
