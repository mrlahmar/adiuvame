from functools import wraps
from flask import request, redirect, url_for, session, render_template
from datetime import datetime

def login_required(f):
    """ Decorate routes to require login. """

    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function

def error(message="",code="400"):
    if code == "400":
        code = "400 BAD REQUEST"
        code_description="The server cannot or will not process the request due to an apparent client error (e.g., malformed request syntax, size too large, invalid request message framing, or deceptive request routing)."
    else:
        code = "500 Internal Server Error"
        message = "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."
        code_description = ""
    return render_template("error.html",message=message,code=code,code_description=code_description)

def timestampformat(timestamp):
    dateobject = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    return dateobject