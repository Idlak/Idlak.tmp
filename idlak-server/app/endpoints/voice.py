import json
from app import api, jwt, db, reqparser
from app.respmsg import mk_response
from app.models.voice import Voice
from flask import current_app
from flask_restful import Resource, abort, request
from datetime import date


vcs_parser = reqparser.RequestParser()
vcs_parser.add_argument('language', location='json')
vcs_parser.add_argument('accent', location='json')
vcs_parser.add_argument('gender', choices=['male', 'female'],
                        help='Valid choices: male|female', location='json')


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
        if isinstance(args, current_app.response_class):
            return args
        """ create a query based on the parameters """
        query = db.session.query(Voice)
        if 'language' in args:
            query = query.filter(Voice.language == args['language'])
        if 'language' in args and 'accent' in args:
            query = query.filter(Voice.accent == args['accent'])
        if 'gender' in args:
            query = query.filter(Voice.gender == args['gender'])
        """ get voices based on the query """
        voices = query.all()
        """ check if the query returned any voices """
        if 'accent' in args and 'language' not in args:
            return mk_response("For accent to be queried, language has " +
                               "to be provided as well.", 400)
        if not voices:
            return mk_response("No voices were found", 204)
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
            return mk_response("Voice could not be found", 404)
        return voice.to_dict()
