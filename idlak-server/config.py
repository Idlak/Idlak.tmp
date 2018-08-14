import os
<<<<<<< HEAD
from datetime import timedelta
=======
import configparser
import uuid
from datetime import timedelta

>>>>>>> 0d65f968c7b8ecc9c1080ae5cae487ba38fc8210
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
<<<<<<< HEAD
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'super-secret'
    JWT_AUTH_USERNAME_KEY = 'uid'
    JWT_EXPIRATION_DELTA = timedelta(minutes=30)
=======
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JWT_SECRET_KEY = str(uuid.uuid4())
    
def load_config_file(conf):
    config = configparser.ConfigParser()
    config.read('config.ini')
    # JWT
    conf['JWT_EXPIRATION_DELTA'] = timedelta(minutes=int(config['JWT']['TOKEN_EXPIRATION_DELTA']))
    # load all default
    for key in config['DEFAULT']:
        conf[key.upper()] = config['DEFAULT'][key]
    return conf
>>>>>>> 0d65f968c7b8ecc9c1080ae5cae487ba38fc8210
