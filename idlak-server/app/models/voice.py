from app import app, db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import inspect
from datetime import datetime
import uuid

class Voice(db.Model):
    """ A voice model used in speech sythesising. """
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(128))
    language = db.Column(db.String(2))
    accent = db.Column(db.String(2))
    gender = db.Column(db.String(6))
    directory = db.Column(db.Text())

    def __init__(self, id, name, language, accent, gender, directory):
        """ __init__ method for Voice class.
        
        Args:
            id (str): an id of the voice
            name (str): the name of the voice
            language (str): the language the voice speaks in, ISO format
            accent (str): the accent the voice speaks in, 2 letter format
            gender (str): gender of the voice (male|female)
            directory (str): directory of the voice files
        """
        self.id = id
        self.name = name
        self.language = language
        self.accent = accent
        self.gender = gender
        self.directory = directory

    def __repr__(self):
        """ __repr__ method of the Voice class """
        return '<Voice {}:{}:{}>'.format(self.id, self.name, self.language)

    def toDict(self):
        """ Turns object into a representable key value dictionary. """
        exceptions = ['directory']
        di = { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        for e in exceptions:
            del di[e]
        return di   

    @classmethod
    def new_voice(self, name, lang, acc, gndr, directory):
        """ Creates a new voice.
        
        A static method.
        
        Args:
            name (str): the name of the voice
            lang (str): the language the voice speaks in, ISO format
            acc (str): the accent the voice speaks in, 2 letter format
            gndr (str): gender of the voice (male|female)
            directory (str): directory of the voice files
            
        Returns:
            :obj:'Voice': the newly created voice that was stored in the database
        """
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
