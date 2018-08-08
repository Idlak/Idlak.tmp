import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, request
from flask_jwt_simple import JWTManager
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

handler = RotatingFileHandler('idlak-server.log', maxBytes=100000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

from app import models, endpoints, reqlogging

if __name__ == '__main__':
    app.run()
