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
        if user is not None:
            app.logger.info("User requesting access: {}".format(user.id))
        else:
            app.logger.info("None-existing user tried to request for access")
            return abort(401, message=("The user with such access token " +
                                       "does not exist"))
        if user.admin:
            return func(*args, **kwargs)
        return abort(401, message="Admin permissions required")
    return wrapper
