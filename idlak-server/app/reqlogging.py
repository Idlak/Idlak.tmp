from app import app
from datetime import datetime
from flask_restful import request

@app.before_request
def before():
    app.logger.info("Local Timestamp: {}".format(str(datetime.now())))
    app.logger.info("Request Method: {}".format(request.method))
    app.logger.info("Request URL: {}".format(request.url))
    app.logger.info("Request Access Route: {}".format(request.access_route[0]))
    headers = ""
    for (key, value) in request.headers:
        if key == "Authorization":
            value = "[provided]" 
        headers += "{}: {}\n".format(key, value)
    app.logger.info("Request Headers:{}\n{}\n{}".format("-"*45,str(headers)[:-1], "-"*60))
    app.logger.info("Request Body: {}".format(request.json))


# Useful debugging interceptor to log all endpoint responses
@app.after_request
def after(response):
    app.logger.info("Local Timestamp: {}".format(str(datetime.now())))
    app.logger.info("Response Code: {}".format(response.status))
    app.logger.info("Response Headers:{}\n{}\n{}".format("-"*43,str(response.headers)[:-3], "-"*60))
    body = response.json
    if "password" in body:
        body['password'] = "[provided]"
    app.logger.info("Response Body: {}\n".format(body))
    return response

# Default handler for uncaught exceptions in the app
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return flask.make_response('server error', 500)

# Default handler for all bad requests sent to the app
@app.errorhandler(400)
def handle_bad_request(e):
    app.logger.info('Bad request', e)
    return flask.make_response('bad request', 400)


