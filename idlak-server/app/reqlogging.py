import copy
from app import app
from datetime import datetime
from flask_restful import request

@app.before_request
def before():
    """ Handling logging before request is processed """
    app.logger.info("Local Timestamp: {}".format(str(datetime.now())))
    app.logger.info("Request Method: {}".format(request.method))
    app.logger.info("Request URL: {}".format(request.url))
    app.logger.info("Request Access Route: {}".format(request.access_route[0]))
    headers = ""
    for (key, value) in request.headers:
        # hide authorization header from logs
        if key == "Authorization":
            value = "[provided]" 
        headers += "{}: {}\n".format(key, value)
    app.logger.info("Request Headers:{}\n{}\n{}".format("-"*45,str(headers)[:-1], "-"*60))
    body = copy.deepcopy(request.json)
    if type(body) is dict and "password" in body:
        body['password'] = "[provided]"
    app.logger.info("Request Body: {}".format(body))


# Useful debugging interceptor to log all endpoint responses
@app.after_request
def after(response):
    """ Handling logging after request is processed """
    app.logger.info("Local Timestamp: {}".format(str(datetime.now())))
    app.logger.info("Response Code: {}".format(response.status))
    app.logger.info("Response Headers:{}\n{}\n{}".format("-"*43,str(response.headers)[:-3], "-"*60))
    # hide password from logs
    body = response.json
    if type(body) is dict and "password" in body:
        body['password'] = "[provided]"
    if type(body) is dict and "access_token" in body:
        body['access_token'] = "[provided]"
    app.logger.info("Response Body: {}\n".format(body))
    return response

# Default handler for uncaught exceptions in the app
@app.errorhandler(500)
def internal_error(exception):
    """ Handling logging when an exception is being thrown """
    app.logger.error(exception)
    return flask.make_response('server error', 500)

# Default handler for all bad requests sent to the app
@app.errorhandler(400)
def handle_bad_request(e):
    """ Handling logging when a bad request is received """
    app.logger.info('Bad request', e)
    return flask.make_response('bad request', 400)


