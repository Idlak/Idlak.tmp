from app import api, jwt
from app.models.user import User
from flask import jsonify
from flask_restful import Resource, reqparse, abort, request
from flask_jwt_simple import create_jwt
from passlib.hash import pbkdf2_sha256 as sha256

""" login arguments:
    uid (str) : user id
    password (str) : user password """
usr_parser = reqparse.RequestParser()
usr_parser.add_argument('uid', help='user id', location='json', required=True)
usr_parser.add_argument('password', help='user password',
                        location='json', required=True)


class Auth(Resource):
    def post(self):
        """ Authentication endpoint

            Args:
                uid (str) : user id
                password (str) : user password
            Returns:
                str: access token if login details are correct, otherwise
                returns an error message
        """
        args = usr_parser.parse_args()
        user = User.query.get(args['uid'])
        if user and sha256.verify(args['password'], user.password):
            return {'access_token': create_jwt(identity=user.id)}, 200
        return {"message": "Login details are incorrect"}, 401


api.add_resource(Auth, '/auth')


@jwt.expired_token_loader
def expired_token():
    return jsonify({"message": "Access token has expired"}), 401


@jwt.invalid_token_loader
def invalid_token(error_msg):
    return jsonify({"message": "Access token is invalid"}), 401


@jwt.unauthorized_loader
def unauthorized_token(error_msg):
    return jsonify({"message": "Access token is invalid"}), 401
