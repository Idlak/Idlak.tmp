from app import db
from passlib.hash import pbkdf2_sha256 as sha256
import uuid

class User(db.Model):
	id = db.Column(db.String(16), primary_key=True)
	password = db.Column(db.String(128))
	admin = db.Column(db.Boolean)

	def __init__(self, id, password, admin):
		self.id = id
		self.password = password
		self.admin = admin

	def __repr__(self):
		return '<User {}:{}:{}>'.format(self.id, self.password, self.admin)

	@classmethod
	def new_user(self, isAdmin=False, user_id=uuid.uuid4().hex[:16]):
		# create id: take guid and split it
		#user_id = uuid.uuid4().hex[:16]
		# create password
		user_pass = uuid.uuid4().hex[:8]
		# hash password
		hashed_pass = sha256.hash(user_pass)
		# create user
		user = User(user_id, hashed_pass, isAdmin)
		# store it in db
		db.session.add(user)
		db.session.commit()
		# create user with the unhashed password
		user = User(user_id, user_pass, isAdmin)
		# return user with the unhashed password
		return user

	def generate_new_pass(self):
		# create password
		user_pass = uuid.uuid4().hex[:8]
		# hash password
		hashed_pass = sha256.hash(user_pass)
		self.password = hashed_pass
		db.session.merge(self)
		db.session.commit()
		return user_pass

	def delete(self):
		db.session.delete(self)
		db.session.commit()

def authenticate(user_id, password):
	user = User.query.get(user_id)
	if user and sha256.verify(password, user.password):
		return user

def identity(payload):
	user_id = payload['identity']
	return User.query.get(user_id)

