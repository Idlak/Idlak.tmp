from app import api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request

vcs_parser = reqparse.RequestParser()
vcs_parser.add_argument('language', help='ISO 2 letter code', location='json')
vcs_parser.add_argument('accent', help='2 letter accent code', location='json')
vcs_parser.add_argument('gender', choices=['male','female'], \
                        help='male|female', location='json')


class Voices(Resource):
    def get(self):
        # get available voices
        args = vcs_parser.parse_args()
        query = db.session.query(Voice.id)
        if args['language'] is not None:
            query = query.filter(Voice.language == args['language'])
        if args['accent'] is not None:
            query = query.filter(Voice.accent == args['accent'])
        if args['gender'] is not None:
            query = query.filter(Voice.gender == args['gender'])
        voice_ids = query.all()
        ret_voices = []
        for v in voice_ids:
            ret_voices.append(v[0])
        return ret_voices

class VoiceDetails(Resource):
    def get(self, voice_id):
        # get voice details
        voice = Voice.query.get(voice_id)
        ret_voice = {
                'id' : voice.id,
                'name' : voice.name,
                'language' : voice.language,
                'accent' : voice.accent,
                'gender' : voice.gender
        }
        return ret_voice


api.add_resource(Voices, '/voices')
api.add_resource(VoiceDetails, '/voices/<voice_id>')
