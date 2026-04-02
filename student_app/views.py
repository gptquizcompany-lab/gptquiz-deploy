import flask, flask_login, datetime
from classroom_app import Student, GroupClass
from library_app.models import Question, Room, SessionAnswer, SessionParticipant, StudentReport
from project.decorators import login_required, student_required
from user_app.models import User

@login_required
@student_required
def render_home_page():
    return flask.render_template(
        template_name_or_list= 'student_home.html',
        results = flask_login.current_user.my_reports,
        main_page= True
    )

@login_required
@student_required
def render_statistic_page():
    return flask.render_template(
        template_name_or_list= 'student_statistic.html',
        main_page= True
    )

@login_required
@student_required
def render_classroom_page():
    return flask.render_template(
        template_name_or_list= 'student_classroom.html',
        main_page= True
    )

@login_required
@student_required
def render_profile_page():
    return flask.render_template(
        template_name_or_list= 'student_profile.html',
        main_page= True
    )

@login_required
@student_required
def report_view(hash_code):
    report = StudentReport.query.filter_by(hash_code=hash_code).first_or_404()
    participant = SessionParticipant.query.get(report.participant_id)
    room = report.room
    questions = []
    host = User.query.get(room.host)
    name_teacher = f'{host.surname} {host.name}'
    skipped = 0
    total_time = 0
    for question_idx in range(room.index_question + 1):
        answer = SessionAnswer.query.filter_by(room_id=room.id, participant_id=participant.id, question_index = question_idx).first()
        q = room.roomsQuiz.questions[question_idx]
        if not answer:
            questions.append({
                "id": q.id,
                "text": q.name,
                "type": q.type,
                "your_answer": "Пропущений...",
                "correct_answer": "Правильної відповідді не буде відображено. Ви під'єднались пізніше ніж воно було пройдено",
                "is_correct": False,
                "is_skipped": True,
                "time_spent": 0
            })
            skipped += 1
        else:
            if answer.answer == "Пропущений..." or answer.answer == "Пропущений":
                skipped += 1
            questions.append({
                "id": q.id,
                "text": q.name,
                "type": q.type,
                "your_answer": answer.get_answer(answer.answer),
                "correct_answer": answer.right_answers(),
                "is_correct": answer.is_correct,
                "is_skipped": False,
                "time_spent": answer.time_spent
            })
            total_time += answer.time_spent
    
    roomsquiz = room.roomsQuiz    

    return flask.render_template(
        "student_report.html",
        name_teacher=name_teacher,
        report=report,
        participant=participant,
        quiz=roomsquiz,
        questions=questions,
        ignore_links=True,
        skipped_answers= skipped,
        average_time = round(total_time, 1)
    )

@login_required
@student_required
def get_student_stats(student_id):
    start_date_str = flask.request.args.get('start_date')
    end_date_str = flask.request.args.get('end_date')

    query = StudentReport.query.filter_by(student_id=student_id)

    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        query = query.filter(StudentReport.created_at >= start_date)

    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(StudentReport.created_at <= end_date)

    reports = query.order_by(StudentReport.created_at.asc()).all()

    data = {
        "dates": [r.created_at.strftime('%Y-%m-%d') for r in reports],
        "grades": [r.grade for r in reports],
        "hashes": [r.hash_code for r in reports],
        "pie_data": {}
    }

    for r in reports:
        g_label = f"Оцінка {r.grade}" if r.grade is not None else "Без оценки"
        data["pie_data"][g_label] = data["pie_data"].get(g_label, 0) + 1

    return flask.jsonify(data)

@login_required
@student_required
def get_active_quizes(classroom_id):
    classroom = GroupClass.query.get(classroom_id)
    response = {
        "status": 200,
        "response": []
    }
    if not classroom:
        response["status"] = 404
        return response
    active_quizes = Room.query.filter_by(
        group_class_id= classroom_id
    ).filter(
        Room.status != "ended"
    ).all()
    if len(active_quizes) == 0:
        response["status"] = 404
        return response
    
    for room in active_quizes:
        if room.index_question is None:
            text = "Очікування початку"
        else:
            text = f"Запитання №{room.index_question + 1}"
        participants = SessionParticipant.query.filter_by(room_id=room.id, is_connected=True).count()
        response["response"].append({
            "topic": room.roomsQuiz.name,
            "text": text,
            "count_students": participants,
            "code": room.redeem_codes[0].code_enter
        })
    return response