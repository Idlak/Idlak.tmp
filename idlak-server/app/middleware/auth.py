from app.models.user import User
from flask_jwt_simple import get_jwt_identity
from functools import wraps
from flask_restful import abort, request
from app import app


def admin_required(func):
    """ Decorator for endpoints that require admin access
        has to be used with jwt_required decorator 
        if the user does not have admin permissions, 
        an unauthorised message is returned """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        app.logger.info("User requesting access: {}".format(user.id))
        if user.admin:
            return func(*args, **kwargs)
        return abort(401, message="Admin permissions required")
    return wrapper