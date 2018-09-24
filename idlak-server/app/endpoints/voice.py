import json
from app import app, api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request
from datetime import date

vcs_parser = reqparse.RequestParser()
vcs_parser.add_argument('language', help='ISO 2 letter code', location='json')
vcs_parser.add_argument('accent', help='2 letter accent code', location='json')
vcs_parser.add_argument('gender', choices=['male', 'female'],
                        help='male|female', location='json')


class Voices(Resource):
    """ Class for Voices enpoint """
    def post(self):
        """ Voices enpoint

            Args:
                language (str, optional)
                accent (str, optional)
                gender (str, optional)

            Returns:
                obj: a list of voiced based on the optional parameters,
                     if no options are provided all voices are returned
                     with their details
        """
        # get available voices
        args = vcs_parser.parse_args()
        """ create a query based on the parameters """
        query = db.session.query(Voice)
        app.logger.debug(args['language'])
        if args['language'] is not None:
            query = query.filter(Voice.language == args['language'])
        if args['language'] is not None and args['accent'] is not None:
            query = query.filter(Voice.accent == args['accent'])
        if args['gender'] is not None:
            query = query.filter(Voice.gender == args['gender'])
        """ get voices based on the query """
        voices = query.all()
        """ check if the query returned any voices """
        if not voices:
            return {"message": "No voices were found"}, 204
        """ create a returnable list of voices and return it as response """
        ret_voices = [v.to_dict() for v in voices]
        return {'voices': ret_voices}


class VoiceDetails(Resource):
    """ Class for voice detail endpoint"""
    def get(self, voice_id):
        """ Voice details endpoint

            Args:
                voice_id (str): voice id
            Returns:
                dict: details of a voice
        """
        # get voice details
        voice = Voice.query.get(voice_id)
        if voice is None:
            return {"message": "Voice could not be found"}, 404
        return voice.to_dict()


api.add_resource(Voices, '/voices')
api.add_resource(VoiceDetails, '/voices/<voice_id>')
