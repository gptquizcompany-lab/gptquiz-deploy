from library_app.models import Quiz, RedeemCode, Room, Question
import flask, random, flask_login
from project import DATABASE
from project.decorators import login_required, teacher_required

def generate_code():
    num1= random.randint(1,9)
    num2= random.randint(0,9)
    num3= random.randint(0,9)
    num4= random.randint(0,9)
    num5= random.randint(0,9)
    num6= random.randint(0,9)
    
    code= f"{num1}{num2}{num3}{num4}{num5}{num6}"
    return int(code)

@login_required
@teacher_required
def render_host_app(quizid):
    quiz = Quiz.query.get(ident=quizid)
    code = 000000
    if flask.request.method == "POST":
        if flask.request.form["btn"] == "host":
            redeem_code= generate_code()
            group_class_parts = flask.request.form.get('group_class').split(" ")
            course_id = group_class_parts[1] if len(group_class_parts) > 1 else None
            room = Room(
                quiz= quiz.id,
                host= flask_login.current_user.id,
                group_class_id= group_class_parts[0],
                course_id= course_id
            )
            DATABASE.session.add(room)
            DATABASE.session.flush()
            
            code_db= RedeemCode(
                quiz= quiz,
                name = quiz.name,
                code_enter= redeem_code,
                hosted_by= flask_login.current_user.id,
                room_id= room.id
            )
            try:
                DATABASE.session.add(code_db)
                DATABASE.session.commit()
                code = redeem_code
                return flask.redirect(flask.url_for("host_app.render_hosting_quiz", code=code))
            except Exception as e:
                print(e)
        elif flask.request.form["btn"] == "delete":
            try:
                questions = Question.query.filter_by(quiz_id=quiz.id).all()
                for q in questions:
                    DATABASE.session.delete(q)
                DATABASE.session.delete(quiz)
                DATABASE.session.commit()
            except Exception as e:
                DATABASE.session.rollback()
                print("Error: ", e)
            return flask.redirect("/admin/")
    return flask.render_template(
        "previewQuiz.html", quiz = quiz, code= code,
        username = flask_login.current_user.login,
        user = flask_login.current_user
        )

@login_required
@teacher_required
def render_hosting_quiz(code):
    codeBD = RedeemCode.query.filter_by(code_enter = code).first()
    if not codeBD:
        return flask.redirect("/")
    if flask_login.current_user.id != codeBD.hosted_by:
        return flask.redirect("/")
    
    return flask.render_template(
        "hosting.html",
        code= code,
        quiz= codeBD.quiz
    )