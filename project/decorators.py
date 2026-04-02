import flask
import flask_login
import functools

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_login.current_user.is_authenticated:
            target_url = flask.request.full_path
            return flask.redirect(flask.url_for("user_app.render_login", redirect_to=target_url))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session["user_role"]:
            target_url = flask.request.full_path
            return flask.redirect(flask.url_for("user_app.render_login", redirect_to=target_url))
        if flask.session["user_role"] != "student":
            return flask.redirect("/not-found")
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session["user_role"]:
            target_url = flask.request.full_path
            return flask.redirect(flask.url_for("user_app.render_login", redirect_to=target_url))
        if flask.session["user_role"] != "teacher":
            return flask.redirect("/not-found")
        return f(*args, **kwargs)
    return decorated_function