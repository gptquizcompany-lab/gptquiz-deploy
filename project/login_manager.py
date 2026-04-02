import flask_login, flask
from classroom_app import Student
from .settings import project
from user_app.models import User

project.secret_key = "key1"

login_manager = flask_login.LoginManager(app=project)

@login_manager.user_loader
def load_user(user_id):
    role = flask.session.get('user_role') 
    
    if role == 'teacher':
        return User.query.get(int(user_id))
    if role == 'student':
        return Student.query.get(int(user_id))
    
    return None