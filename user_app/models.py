import flask_login
from project.settings import DATABASE
from library_app.models import Quiz, RedeemCode

class User(DATABASE.Model, flask_login.UserMixin):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)
    
    login= DATABASE.Column(DATABASE.String(40), nullable= False)
    name= DATABASE.Column(DATABASE.String(30), nullable= False)
    surname= DATABASE.Column(DATABASE.String(30), nullable= False)
    email= DATABASE.Column(DATABASE.String(255), nullable= False)
    password= DATABASE.Column(DATABASE.String(30), nullable= False)
    is_student = DATABASE.Column(DATABASE.Boolean, default= False)
    created_quizes = DATABASE.relationship(Quiz, backref = 'user', lazy = True)
    hosted = DATABASE.relationship(RedeemCode, backref = 'hosted', lazy = True)
    classes = DATABASE.relationship("GroupClass", backref="teacher", lazy=True)
    courses = DATABASE.relationship("Course", backref="teacher", lazy=True)

class VerificationCode(DATABASE.Model):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)

    email = DATABASE.Column(DATABASE.String)
    code = DATABASE.Column(DATABASE.String)

    