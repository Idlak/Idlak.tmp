from app.models.user import User
from flask_jwt_simple import get_jwt, decode_jwt, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta
from flask_restful import abort, request
from app import jwt, app

EXPIRED = []

def admin_required(func):
    """ Decorator for endpoints that require admin access
        has to be used with jwt_required decorator 
        if the user does not have admin permissions, 
        an unauthorised message is returned """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if user is not None:
            app.logger.info("User requesting access: {}".format(user.id))
        else:
            app.logger.info("None-existing user tried to request for access")
            return abort(401, message="The user with such access token does not exist")
        if user.admin:
            return func(*args, **kwargs)
        return abort(401, message="Admin permissions required")
    return wrapper

def not_expired(func):
    """ Decorator for endpoints that require for the token
        not to be manually expired
        has to be used with jwt_required decorator
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # get access token from header
        header_name = app.config['JWT_HEADER_NAME']
        jwt_header = request.headers.get(header_name, None)
        if len(jwt_header.split()) == 1:
            token = jwt_header
        elif len(jwt_header.split()) == 2:
            token = jwt_header.split()[1]
            
        # remove manually expired tokens that have actually expired
        remove_expired()
        
        if token in EXPIRED:
            return abort(401, message="Access token has expired")
        else:
            return func(*args, **kwargs)
    return wrapper

def remove_expired():
    for tk in EXPIRED:
        now = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        if now < decode_jwt(tk)['exp']
            del tk