import flask_jwt_simple
from app import app, api, jwt
from app.models.user import User
from app.middleware.auth import not_expired, EXPIRED
from flask import jsonify
from flask_restful import Resource, reqparse, abort, request
from flask_jwt_simple import create_jwt, decode_jwt, jwt_required
from passlib.hash import pbkdf2_sha256 as sha256

""" login arguments: 
    uid (str) : user id
    password (str) : user password """
usr_parser = reqparse.RequestParser()
usr_parser.add_argument('uid', help='user id', location='json', required=True)
usr_parser.add_argument('password', help='user password', location='json', required=True)

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
        return { "message" : "Login details are incorrect" }, 401

class Auth_Expire(Resource):
    decorators = [not_expired, jwt_required]
    def post(self):
        """ Expire token endpoint
        
            Args:
                access_token (str) : access token from header
            Returns:
                str: success or error message 
        """
        # get access token from header
        header_name = app.config['JWT_HEADER_NAME']
        jwt_header = request.headers.get(header_name, None)
        if len(jwt_header.split()) == 1:
            access_token = jwt_header
        elif len(jwt_header.split()) == 2:
            access_token = jwt_header.split()[1]
            
        user_id = decode_jwt(access_token)
        
        if user_id is not None:
            EXPIRED.append(access_token)
            app.logger.info("Expire token for user " + user_id['sub'])
            return { "message" : "The token has been manually expired." }, 200
        else:
            return { "message" : "The token could not expire." }, 400

api.add_resource(Auth, '/auth')
api.add_resource(Auth_Expire, '/auth/expire')

@jwt.expired_token_loader
def expired_token():
    return jsonify({ "message":"Access token has expired" }), 401

@jwt.invalid_token_loader
def invalid_token(error_msg):
    return jsonify({ "message":"Access token is invalid" }), 401

@jwt.unauthorized_loader
def unauthorized_token(error_msg):
    return jsonify({ "message":"Access token is invalid" }), 401