from app import api, jwt
from app.models.user import User
from app.middleware.auth import admin_required
from app.middleware.log import log_request
from flask_restful import Resource, reqparse, abort, request
from flask_jwt_simple import jwt_required, get_jwt_identity
from functools import wraps

usr_parser = reqparse.RequestParser()
usr_parser.add_argument('uid', help='user id', location='json')
usr_parser.add_argument('admin', type=bool, \
    help='does user need admin permissions', location='json')


class Users(Resource):
    """ Class for endpoints responsible for providing information about 
        users and creating a new user """
    decorators = [admin_required, jwt_required]
    def get(self):
        """ Get info of all users endpoint 
            To access, access token and admin permissions are required 
            returns a list of existing users with their info """
        users = User.query.all()
        usersJSON = []
        for u in users:
            usersJSON.append({'id':u.id, 'admin':u.admin})
        return { 'users' : usersJSON }

    
    def post(self):
        """ Create a new user account endpoint
            To create, access token and admin permissions are required 
            Takes in id and admin as optional parameters in json body
            returns details of the new user with a password provided """
        args = usr_parser.parse_args()
        """ convert admin parameter into a boolean """
        admin = bool(args['admin'])
        """ check if the id of user is provided """
        if args['uid'] is not None:
            user = User.new_user(admin, args['uid'])
        else:
            user = User.new_user(admin)
        """ check if the user is created, 
            if the user with the same id exists it won't be created """
        if user is None:
            return abort(422, message="User id already exists")
        """ create an object to represent the user with the password provided
            and return it as a response """
        userToReturn = { 'uid' : user.id, 'password':user.password,'admin':user.admin }
        return userToReturn


class Users_Password(Resource):
    """ Class for generating new user password endpoint """
    decorators = [admin_required, jwt_required]
    def post(self, user_id):
        """ Reset password endpoint 
            To reset, access token and admin permissions are required
            Takes in an id of a user that needs to have its password reset
            Returns the new changed password """
        user = User.query.get(user_id)
        if user is None:
            return abort(422, message="User does not exist")
        password = user.generate_new_pass()
        return { 'password' : password }

class Users_Delete(Resource):
    """ Class for deleting a user endpoint """
    decorators = [admin_required, jwt_required]
    def delete(self, user_id):
        """ Delete user endpoint
            To delete, access token and admin permissions are required 
            Takes in an id of a user that needs to be deleted
            Returns an error or success message """
        user = User.query.get(user_id)
        """ check if user exists """
        if user is None:
            return abort(422, message="User does not exist")
        """ check if the user is not trying to delete itself """
        if user.id == get_jwt_identity():
            return abort(422, message="You cannot delete your own user!")
        user.delete()
        return { 'message': "User '{}' has been deleted".format(user.id) }


api.add_resource(Users, '/users')
api.add_resource(Users_Password, '/users/<user_id>/password')
api.add_resource(Users_Delete, '/users/<user_id>')
