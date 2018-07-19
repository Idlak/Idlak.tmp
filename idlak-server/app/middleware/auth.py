from app.models.user import User
from flask_jwt_simple import get_jwt_identity
from functools import wraps
from flask_restful import abort

def admin_required(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if User.query.get(get_jwt_identity()).admin:
			return func(*args, **kwargs)
		return abort(401, message="Admin permissions required")
	return wrapper

