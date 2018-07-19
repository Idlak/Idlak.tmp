from app import db
from passlib.hash import pbkdf2_sha256 as sha256
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

    @classmethod
    def new_voice(self, name, lang, acc, gndr, directory):
        id = uuid.uuid4().hex[:16]
        voice = Voice(id, name, lang, acc, gndr, directory)
        db.session.add(voice)
        db.session.commit()
        return voice
