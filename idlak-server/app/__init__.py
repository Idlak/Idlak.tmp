import logging
import os
import subprocess
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config,load_config_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init as db_init, migrate as db_migrate, upgrade as db_upgrade, show
from flask_restful import Api, request
from flask_jwt_simple import JWTManager
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config())
load_config_file(app.config)
api = Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)

logging.basicConfig()
handler = RotatingFileHandler(app.config['LOG_FILE'],
                              maxBytes=100000,
                              backupCount=1)
handler.setLevel(app.config['LOGGING'])
app.logger.addHandler(handler)
app.logger.setLevel(app.config['LOGGING'])

from app import models, endpoints, reqlogging
from app.models.user import User

# if the database is not created, set it up
def db_setup():
    with app.app_context():
        if not os.path.isdir('migrations'):
            app.logger.info("The database is being created, to run the server it has to be run again afterwards")
            db_init()
            db_migrate()
            db_upgrade()
            return True
        return False

# this is the only way to make the initial db setup work since after running it, it shuts down the program
if db_setup():
    show()

# check if there are any users, if there are none, create an admin
if len(User.query.all()) == 0:
    admin_user = User.new_user_full('admin', 'admin', True)
    app.logger.info("An initial admin user has been created: {}".format(admin_user))


if __name__ == '__main__':
    app.run()
