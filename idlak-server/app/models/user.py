from app import app, db
from passlib.hash import pbkdf2_sha256 as sha256
from flask_restful import abort
import uuid


class User(db.Model):
    """ A user model used in authentication and authorisation """
    id = db.Column(db.String(16), primary_key=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean)

    def __init__(self, id, password, admin):
        """ __init__ method for User class.
        
        Args:
            id (str): Id of the user.
            password (str): user password.
            admin (bool): determines whether user is an admin or not .
        """
        self.id = id
        self.password = password
        self.admin = admin

    def __repr__(self):
        return '<User {}:{}:{}>'.format(self.id, self.password, self.admin)

    
    @classmethod
    def new_user(self, isAdmin=False, user_id=uuid.uuid4().hex[:16]):
        """ Creates a new user.
        
        Args:
            isAdmin (bool, optional): if user to be created is an admin.
            user_id (str, optional): user id.
            
        Returns:
            :obj:'User': info of the new user (with id and password).
        """
        # create id: take guid and split it
        if User.query.get(user_id) is not None:
            return None
        # create password
        user_pass = uuid.uuid4().hex[:8]
        hashed_pass = sha256.hash(user_pass)
        # create user & store it in db
        user = User(user_id, hashed_pass, isAdmin)
        db.session.add(user)
        db.session.commit()
        app.logger.debug("New user created:\n{{\n"
                         "\tuid: {},\n"
                         "\tpassword: {},\n"
                         "\tencrypted-password: {},\n"
                         "\tadmin: {}\n}}"
                         .format(user.id, user_pass, user.password, user.admin))
        # create user with the unhashed password
        user = User(user_id, user_pass, isAdmin)
        return user
    
    @classmethod
    def new_user_full(self, user_id, user_pass, admin):
        """ Creates a new user provided all details.
        
        Args:
            admin (bool): if user to be created is an admin.
            user_id (str): user id.
            user_pass (str): user password.
            
        Returns:
            :obj:'User': info of the new user (with id and password).
        """
        # hash password
        hashed_pass = sha256.hash(user_pass)
        # create user & store it in db
        user = User(user_id, hashed_pass, admin)
        db.session.add(user)
        db.session.commit()
        app.logger.debug("New user created:\n{{\n"
                         "\tuid: {},\n"
                         "\tpassword: {},\n"
                         "\tencrypted-password: {},\n"
                         "\tadmin: {}\n}}"
                         .format(user.id, user_pass, user.password, user.admin))
        # create user with the unhashed password
        user = User(user_id, user_pass, admin)
        return user

    def generate_new_pass(self):
        """ Created new password for a user.
        
        Returns:
            str: the new generated password.
        """
        # create password
        user_pass = uuid.uuid4().hex[:8]
        # hash password
        hashed_pass = sha256.hash(user_pass)
        self.password = hashed_pass
        db.session.merge(self)
        db.session.commit()
        app.logger.debug("Password for user {} has been changed into {}".format(self.id, user_pass))
        return user_pass
    
    
    def toggle_admin(self):
        """ Toggles users admin status """
        self.admin = not self.admin
        db.session.merge(self)
        db.session.commit()
        app.logger.debug("Admin status for user {} has been changed into {}".format(self.id, self.admin))

    def delete(self):
        """ Deletes user from a database. """
        db.session.delete(self)
        db.session.commit()
        app.logger.debug("User {} has been deleted".format(self.id))


def authenticate(user_id, password):
    """ Checks if user exists and its password is correct.
    
    Used for the jwt module.
    
    Args:
        user_id (str): The user id provided on login.
        password (str): The user password provided on login.
    
    Returns:
        :obj:'User': user that has matching id and correct password.
    """
    user = User.query.get(user_id)
    if user and sha256.verify(password, user.password):
            return user

def identity(payload):
    """ Extracts identity of the user from the payload.
    
    Used for the jwt module.
    
    Args:
        payload (dict): a payload object that must have an identity key value pair.
    
    Returns:
        :obj:'User': the user that is found by the identity in the payload.
    """
    user_id = payload['identity']
    return User.query.get(user_id)

