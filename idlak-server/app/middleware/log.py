from functools import wraps
from flask_restful import request
from app import app
from datetime import datetime

def log_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        app.logger.info("Local Timestamp UTC: {}".format(str(datetime.now())));
        app.logger.info("Request Method: <[{}]>,".format(request.method));
        app.logger.info("Request URL: {},".format(request.url));
        app.logger.info("Request Headers: {},".format(request.headers));
        ret = func(*args, **kwargs)
        app.logger.info("Response Body: {}".format(ret))
        return ret
    return wrapper

