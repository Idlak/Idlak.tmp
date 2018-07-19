from app import api, jwt
from flask_restful import Resource, reqparse, abort, request

vcs_parser = reqparse.RequestParser()
vcs_parser.add_argument('language', help='ISO 2 letter code', location='json')
vcs_parser.add_argument('accent', help='2 letter accent code', location='json')
vcs_parser.add_argument('gender', choices=['male','female'], \
	help='male|female', location='json')


class Voices(Resource):
	def get(self):
		# get available voices
		return "get available voices"

class Voice(Resource):
	def get(self, voice_id):
		# get voice details
		return "get voice details"


api.add_resource(Voices, '/voices')
api.add_resource(Voice, '/voices/<voice_id>')
