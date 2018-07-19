from app import api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request


class Languages(Resource):
    def get(self):
        # get available voices
        langs = db.session.query(Voice.language.distinct().label("language")).all()
        ret_langs = []
        for l in langs:
            ret_langs.append(l[0])
        return { 'languages' : ret_langs }

class Accents(Resource):
    def get(self, lang_iso):
        # get voice details
        accents = db.session.query(Voice.accent).filter(Voice.language == lang_iso).distinct().all()
        ret_accents = []
        for a in accents:
            ret_accents.append(a[0])
        return { 'language' : lang_iso, 'accents' : ret_accents}


api.add_resource(Languages, '/languages')
api.add_resource(Accents, '/languages/<lang_iso>/accents')
