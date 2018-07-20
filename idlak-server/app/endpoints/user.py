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
    decorators = [admin_required, jwt_required]
    def get(self):
        # get all users
        users = User.query.all()
        usersJSON = []
        for u in users:
            usersJSON.append({'id':u.id, 'admin':u.admin})
        return { 'users' : usersJSON }

    def post(self):
        # create new user account
        args = usr_parser.parse_args()
        admin = bool(args['admin'])
        if args['uid'] is not None:
            user = User.new_user(admin, args['uid'])
        else:
            user = User.new_user(admin)
        if user is None:
            return abort(422, message="User id already exists")
        userToReturn = { 'uid' : user.id, 'password':user.password,'admin':user.admin }
        return userToReturn


class Users_Password(Resource):
    decorators = [admin_required, jwt_required]
    def post(self, user_id):
        # reset password
        user = User.query.get(user_id)
        password = user.generate_new_pass()
        return { 'password' : password }

class Users_Delete(Resource):
    decorators = [admin_required, jwt_required]
    def delete(self, user_id):
        # delete account
        user = User.query.get(user_id)
        if user.id == get_jwt_identity():
            return abort(422, message="You cannot delete your own user!")
        user.delete()
        return "Account '{}' has been deleted".format(user.id)


api.add_resource(Users, '/users')
api.add_resource(Users_Password, '/users/<user_id>/password')
api.add_resource(Users_Delete, '/users/<user_id>')
