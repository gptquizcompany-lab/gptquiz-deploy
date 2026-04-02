import flask
import flask_login
import sib_api_v3_sdk
from classroom_app import Student
import project
from .models import User, VerificationCode
from project.settings import DATABASE
import random, re, os, dotenv

dotenv.load_dotenv()

def validate_data():
    data = flask.request.get_json()

    login = data.get("login", "").strip()
    first_name = data.get("first_name", "").strip()
    surname = data.get("surname", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    errors = {
        "success": True,
        "errors": []
    }

    if not all([login, first_name, surname, email, password]):
        errors["errors"].append({"success": False, "message": "Заповніть усі поля!", "type": "general"})
        errors["success"] = False

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors["errors"].append({"success": False, "message": "Некоректна адреса електронної пошти.", "type": "email"})
        errors["success"] = False

    if len(password) < 6:
        errors["errors"].append({"success": False, "message": "Пароль має містити щонайменше 6 символів.", "type": "password"})
        errors["success"] = False

    existing_user_email = User.query.filter_by(email=email).first()
    if existing_user_email:
        errors["errors"].append({"success": False, "message": "Ця поштова скринька вже використовується", "type": "email"})
        errors["success"] = False
        
    existing_user_username = User.query.filter_by(login=login).first()
    if existing_user_username:
        errors["errors"].append({"success": False, "message": "Цей логін вже використовується", "type": "login"})
        errors["success"] = False
    print(errors)
    

    if not errors["success"]:
        return flask.jsonify(errors), 400
    
    return flask.jsonify({"success": True, "message": "Реєстрація успішна!"}), 200

def send_code():
    data = flask.request.get_json()
    email = data.get('email')
    if not email:
        return flask.jsonify({'error': 'Email required'}), 400

    code = str(random.randint(100000, 999999))
    codeDB = VerificationCode(
        email = email,
        code = code
    )
    try: 
        DATABASE.session.add(codeDB)
        DATABASE.session.commit()
    except Exception as e:
        print(e)
    flask.session['email_code'] = codeDB.id
    print(f"Sending code to: {email}")
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"name": "GPTQuiz", "email": os.environ.get("MAIL_USERNAME")},
        subject="Ваш код підтвердження",
        html_content=f"""
            <html>
                <body>
                    <p>Ваш код підвертдження: <strong>{code}</strong></p>
                </body>
            </html>
        """
    )

    try:
        api_response = project.api_instance.send_transac_email(send_smtp_email)
        print("ОК: Письмо улетело, Respone:", api_response)
    except Exception as e:
        print("Ошибка отправки:", e)
    
    return flask.jsonify({'message': f'Код відправленно на {email}'})

def validate_code():
    data = flask.request.get_json()

    login = data.get("login", "").strip()
    first_name = data.get("first_name", "").strip()
    surname = data.get("surname", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    code = data.get("code", "").strip()
    
    if "email_code" not in flask.session:
        return flask.jsonify(success=False, message="Код підтвердження не знайдено у сессіі"), 400
    
    verify_code = VerificationCode.query.get(flask.session["email_code"])
    if not verify_code:
        return flask.jsonify(success = False, message = "Код не знайдено"), 500

    if code != verify_code.code:
        print(code, flask.session["email_code"])
        return flask.jsonify(success=False, message="Код підтвердження невірний."), 400
    user = User(
        login=login,
        name=first_name,
        surname=surname,
        email=email,
        password=password  
    )
    DATABASE.session.add(user)
    DATABASE.session.commit()
    flask.session.pop("email_code", None)
    return flask.jsonify(success=True, url="/login/"), 200

def render_signup():
    if flask.request.method == 'POST':
        user= User(
            login = flask.request.form['login'],
            name = flask.request.form['name'],
            surname = flask.request.form['surname'],
            email = flask.request.form['email'],
            password = flask.request.form['password']
        )
        try:
            DATABASE.session.add(user)
            DATABASE.session.commit()
            return flask.redirect('/login/')
        except:
            return "Не вдалося створити користувача"
    return flask.render_template(template_name_or_list='signup.html')


def render_login():
    error_msg = None
    selected = True
    if flask.request.method == "POST":
        if flask.request.form["button"] == "teacher":
            for user in User.query.filter_by(login = flask.request.form['login']):
                if user.password == flask.request.form['password']:
                    flask_login.login_user(user)
                    flask.session['user_role'] = 'teacher'
                    redirect_to = flask.request.args.get("redirect_to")
                    if redirect_to:
                        return flask.redirect(redirect_to)
                    return flask.redirect('/admin/')
            error_msg = "Неправильний логін або пароль"
        elif flask.request.form["button"] == "student":
            for student in Student.query.filter_by(login = flask.request.form['login']):
                if student.password == flask.request.form['password']:
                    flask_login.login_user(student)
                    flask.session['user_role'] = 'student'
                    redirect_to = flask.request.args.get("redirect_to")
                    if redirect_to:
                        return flask.redirect(redirect_to)
                    return flask.redirect('/student/')
            error_msg = "Неправильний логін або пароль"
            selected = False
    return flask.render_template(
        template_name_or_list= 'login.html',
        error_msg= error_msg,
        selected= selected
    )

def render_profile():
    user = flask_login.current_user
    return flask.render_template(
        template_name_or_list="profile.html",
        user = user,
        username = flask_login.current_user.login
    )

def create_admin():
    if flask.request.method == "POST":
        user= User(
            login = "admin",
            name = "name",
            surname = "surname",
            email = "",
            password = "admin"
        )
        try:
            DATABASE.session.add(user)
            DATABASE.session.commit()
            return {"login": "admin", "password": "admin"}
        except:
            return "Не вдалося створити користувача"

def logout():
    flask_login.logout_user()
    flask.session.clear()
    redirect_url = flask.request.args.get("redirect_to")
    if redirect_url:
        return flask.redirect(redirect_url)
    return flask.redirect("/")
    