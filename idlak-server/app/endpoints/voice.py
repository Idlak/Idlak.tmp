import json
from app import api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request
from datetime import date

vcs_parser = reqparse.RequestParser()
vcs_parser.add_argument('language', help='ISO 2 letter code', location='json')
vcs_parser.add_argument('accent', help='2 letter accent code', location='json')
vcs_parser.add_argument('gender', choices=['male','female'], \
                        help='male|female', location='json')


def serialize(obj):
    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial

    return obj.__dict__


class Voices(Resource):
    def get(self):
        # get available voices
        args = vcs_parser.parse_args()
        query = db.session.query(Voice)
        if args['language'] is not None:
            query = query.filter(Voice.language == args['language'])
        if args['language'] is not None and args['accent'] is not None:
            query = query.filter(Voice.accent == args['accent'])
        if args['gender'] is not None:
            query = query.filter(Voice.gender == args['gender'])
        voices = query.all()
        ret_voices = []
        for v in voices:
            ret_voices.append(v.toDict())
        return ret_voices

class VoiceDetails(Resource):
    def get(self, voice_id):
        # get voice details
        voice = Voice.query.get(voice_id)
        return voice.toDict()


api.add_resource(Voices, '/voices')
api.add_resource(VoiceDetails, '/voices/<voice_id>')
