from app import api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request


class Languages(Resource):
    """ Class for language list endoint """
    def get(self):
        """ Language endpoint
            returns a list of available languages in iso format """
        """ query the voice table in database """
        langs = db.session.query(Voice.language.distinct().label("language")).all()
        """ convert language list into a returnable format """
        ret_langs = []
        for l in langs:
            ret_langs.append(l[0])
        return { 'languages' : ret_langs }

class Accents(Resource):
    """ Class for accent list endoint """
    def get(self, lang_iso):
        """ Accent endpoint
            provided with a language in iso format
            returns a list of accents of the language in a two letter format """
        accents = db.session.query(Voice.accent).filter(Voice.language == lang_iso).distinct().all()
        if not accents:
            return { 'message' : 'Language could not be found' }, 404
        ret_accents = []
        for a in accents:
            ret_accents.append(a[0])
        return { 'language' : lang_iso, 'accents' : ret_accents}


api.add_resource(Languages, '/languages')
api.add_resource(Accents, '/languages/<lang_iso>/accents')
