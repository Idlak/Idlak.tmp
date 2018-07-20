from app import app, db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import inspect
from datetime import datetime
import uuid

class Voice(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(128))
    language = db.Column(db.String(2))
    accent = db.Column(db.String(2))
    gender = db.Column(db.String(6))
    directory = db.Column(db.Text())

    def __init__(self, id, name, language, accent, gender, directory):
        self.id = id
        self.name = name
        self.language = language
        self.accent = accent
        self.gender = gender
        self.directory = directory

    def __repr__(self):
        return '<Voice {}:{}:{}>'.format(self.id, self.name, self.language)

    def toDict(self):
        exceptions = ['directory']
        di = { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        for e in exceptions:
            del di[e]
        return di   

    @classmethod
    def new_voice(self, name, lang, acc, gndr, directory):
        id = uuid.uuid4().hex[:16]
        voice = Voice(id, name, lang, acc, gndr, directory)
        db.session.add(voice)
        db.session.commit()
        app.logger.debug("[{}] New voice created:\n{{\n"
                         "\tid: {}\n"
                         "\tname: {}\n"
                         "\tlanguage: {}\n"
                         "\taccent: {}\n"
                         "\tgender: {}\n"
                         "\tdirectory: {}\n}}"
                         .format(datetime.now(), id, name, lang, acc, gndr, directory))
        return voice
