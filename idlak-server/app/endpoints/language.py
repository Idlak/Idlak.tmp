from app import api, jwt, db
from app.models.voice import Voice
from flask_restful import Resource, reqparse, abort, request


class Languages(Resource):
    def get(self):
        """ Language list endpoint
            
            Returns:
                obj: a list of available languages in iso format
        """
        langs = db.session.query(Voice.language.distinct().label("language")).all()
        """ convert language list into a returnable format """
        ret_langs = [l[0] for l in langs]
        return { 'languages' : ret_langs }

class Accents(Resource):
    def get(self, lang_iso):
        """ Accent list endpoint
        
            Args:
                lang_iso (str): language in iso format
            Returns:
                obj: a list of accents of the language in a two letter format
        """
        accents = db.session.query(Voice.accent).filter(Voice.language == lang_iso).distinct().all()
        if not accents:
            return { 'message' : 'Language could not be found' }, 404
        ret_accents = []
        for a in accents:
            ret_accents.append(a[0])
        return { 'language' : lang_iso, 'accents' : ret_accents}


api.add_resource(Languages, '/languages')
api.add_resource(Accents, '/languages/<lang_iso>/accents')
