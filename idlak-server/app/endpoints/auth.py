from app import api, jwt
from app.models.user import User
from flask import jsonify
from flask_restful import Resource, reqparse, abort, request
from flask_jwt_simple import create_jwt
from passlib.hash import pbkdf2_sha256 as sha256

usr_parser = reqparse.RequestParser()
usr_parser.add_argument('uid', help='user id', location='json', required=True)
usr_parser.add_argument('password', help='user password', location='json', required=True)


class Auth(Resource):
	def post(self):
		# login users
		args = usr_parser.parse_args()
		user = User.query.get(args['uid'])
		if user and sha256.verify(args['password'], user.password):
			return {'access_token': create_jwt(identity=user.id)}, 200
		return { "message" : "User id doesn't exist" }, 401

api.add_resource(Auth, '/auth')
