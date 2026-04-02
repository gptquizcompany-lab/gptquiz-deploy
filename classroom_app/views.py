from datetime import datetime
import flask, flask_login
from project import DATABASE
from project.decorators import login_required, teacher_required
from .models import GroupClass, Student, Course

@login_required
@teacher_required
def render_classrooms():
    errors = None
    if flask.request.method == "POST":
        form_type = flask.request.form.get("form_type")
        if form_type == "classroom":
            number = flask.request.form["number"]
            char   = flask.request.form["char"].upper()
            if GroupClass.query.filter_by(number=number, char=char, teacher_id = flask_login.current_user.id).first():
                errors = "У вас уже є такий клас"
            else:
                new_class = GroupClass(
                    number= number,
                    char= char,
                    teacher_id = flask_login.current_user.id
                )
                try:
                    DATABASE.session.add(new_class)
                    DATABASE.session.commit()
                except:
                    print("Error while creating new class", number, char)
        elif form_type == "course":
            name = flask.request.form["name"]
            group_class_id = flask.request.form["classroom"]
            if Course.query.filter_by(name=name, group_class_id=group_class_id, teacher_id=flask_login.current_user.id).first():
                errors = "У вас уже є такий курс в цьому класі"
            else:
                new_course = Course(
                    name=name,
                    description="",
                    group_class_id=group_class_id,
                    teacher_id=flask_login.current_user.id
                )
                try:
                    DATABASE.session.add(new_course)
                    DATABASE.session.commit()
                    new_course.connect_all_students()
                except Exception as e:
                    print("Error while creating new course", name, e)
    class_groups = GroupClass.query.filter_by(teacher_id = flask_login.current_user.id).all()
    courses = Course.query.filter_by(teacher_id = flask_login.current_user.id).all()
    return flask.render_template(
        "classrooms.html",
        class_groups = class_groups,
        courses = courses,
        errors=errors,
        main_page = True
    )

@login_required
@teacher_required
def render_classroom(id):
    errors = None
    classroom = GroupClass.query.get(id)
    if not classroom:
        return flask.redirect("/classrooms/")
    new_student = None
    if flask.request.method == "POST":
        student_login = flask.request.form["student_login"]
        student_name = flask.request.form["student_name"]
        student_surname = flask.request.form["student_surname"]
        if Student.query.filter_by(login=student_login).first():
            errors = "Учень з такім логіном вже існує"
        elif Student.query.filter_by(name=student_name, surname=student_surname,  my_class_id = id).first():
            errors = "У цьому класі вже є такий учень"
        else:
            new_student = Student(
                login= student_login,
                name= student_name,
                surname= student_surname,
                my_class_id = id
            )
            try:
                DATABASE.session.add(new_student)
                DATABASE.session.commit()
            except:
                print("Error while creating new student", student_login, student_name, student_surname)
    print(errors)
    return flask.render_template(
        "class.html",
        classroom= classroom,
        new_student= new_student,
        errors=errors
    )

@login_required
@teacher_required
def render_course(id):
    course = Course.query.get(id)
    errors = None

    if not course:
        return flask.redirect("/not-found/", 404)
    if course.classroom.teacher_id != flask_login.current_user.id and course.teacher_id != flask_login.current_user.id:
        return flask.redirect("/admin/", 403)
    
    if flask.request.method == "POST":
        student_id = flask.request.form["student_id"]
        student = Student.query.get(student_id)
        if not student:
            errors = "Учень не знайдений"
        elif course.students.filter_by(id=student.id).first():
            errors = "У цьому курсі вже є такий учень"
        else:
            student.courses.append(course)
            try:
                DATABASE.session.commit()
            except Exception as e:
                print("Error while adding student to course", student.login, student.name, student.surname, e)
    
    return flask.render_template(
        "course.html",
        course=course,
        errors=errors
    )

@login_required
@teacher_required
def render_student_information(id):
    student = Student.query.get(id)
    if not student:
        return flask.redirect("/not-found/", 404)
    if student.classroom.teacher_id != flask_login.current_user.id:
        return flask.redirect("/admin/", 403)
    
    return flask.render_template(
        "student.html",
        student=student
    )

@login_required
@teacher_required
def get_data_login_student(id_student, id_classroom):
    response = {
        "status": 200,
        "login": "",
        "password": ""
    }
    student = Student.query.get(id_student)
    if not student:
        response["status"] = 404
        return response
    if student.classroom.id != id_classroom:
        response["status"] = 403
        return response
    classroom = GroupClass.query.get(id_classroom)
    if not classroom:
        response["status"] = 404
        return response
    if classroom.teacher_id != flask_login.current_user.id:
        response["status"] = 403
        return response
    response["login"] = student.login
    response["password"] = student.password
    return response

@login_required
@teacher_required
def get_course_stats(id):
    start_date_str = flask.request.args.get('start_date')
    end_date_str = flask.request.args.get('end_date')

    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

    course = Course.query.get(id)
    if not course:
        return flask.jsonify({"labels": [], "success_rates": []})

    all_stats = []
    try:
        for room in course.rooms:
            room_date = room.date.date()

            if start_dt and room_date < start_dt: continue
            if end_dt and room_date > end_dt: continue

            percentages = [report.percentage for report in room.student_reports]
            
            if percentages:
                avg_room_success = round(sum(percentages) / len(percentages), 1)
                all_stats.append({
                    "date": room_date.strftime('%Y-%m-%d'),
                    "code": f"({room.redeem_codes[0].code_enter})", 
                    "rate": avg_room_success,
                    "id": room.id
                })
    except:
        pass
    all_stats.sort(key=lambda x: x['date'])

    labels = [[item['date'], f"{item['code']}"] for item in all_stats]
    rates = [item['rate'] for item in all_stats]
    ids = [item['id'] for item in all_stats]

    return flask.jsonify({
        "labels": labels,
        "success_rates": rates,
        "ids": ids
    })

@login_required
@teacher_required
def get_class_stats(id):
    start_date_str = flask.request.args.get('start_date')
    end_date_str = flask.request.args.get('end_date')

    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

    classroom = GroupClass.query.get(id)
    if not classroom:
        return flask.jsonify({"labels": [], "success_rates": []})

    all_stats = []
    try:
        for room in classroom.rooms:
            room_date = room.date.date()

            if start_dt and room_date < start_dt: continue
            if end_dt and room_date > end_dt: continue

            percentages = [report.percentage for report in room.student_reports]
            
            if percentages:
                avg_room_success = round(sum(percentages) / len(percentages), 1)
                all_stats.append({
                    "date": room_date.strftime('%Y-%m-%d'),
                    "code": f"({room.redeem_codes[0].code_enter})", 
                    "rate": avg_room_success,
                    "id": room.id
                })
    except:
        pass
    all_stats.sort(key=lambda x: x['date'])

    labels = [[item['date'], f"{item['code']}"] for item in all_stats]
    rates = [item['rate'] for item in all_stats]
    ids = [item['id'] for item in all_stats]

    return flask.jsonify({
        "labels": labels,
        "success_rates": rates,
        "ids": ids
    })

@login_required
@teacher_required
def get_login_passwords_data_students(id):
    response = {
        "status": 200,
        "data": ""
    }
    classroom = GroupClass.query.get(id)
    if not classroom:
        response["status"] = 404
        return response
    if classroom.teacher_id != flask_login.current_user.id:
        response["status"] = 403
        return response
    
    students = classroom.students
    for i, student in enumerate(students, 1):
        response["data"] += f"{i}. {student.surname} {student.name} - Логин: {student.login}   Пароль: {student.password}\n"
    response["data"][:-1].strip()
    return response