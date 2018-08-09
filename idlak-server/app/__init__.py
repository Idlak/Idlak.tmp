import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config,load_config_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, request
from flask_jwt_simple import JWTManager
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config())
load_config_file(app.config)
print app.config
api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

handler = RotatingFileHandler('idlak-server.log', maxBytes=100000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

from app import models, endpoints, reqlogging
from app.models.user import User

# check if there are any users, if there are none, create an admin
if len(User.query.all()) == 0:
    admin_user = User.new_user_full('admin', 'admin', True)
    app.logger.info("An initial admin user has been created:\n{}".format(admin_user))

if __name__ == '__main__':
    app.run()
