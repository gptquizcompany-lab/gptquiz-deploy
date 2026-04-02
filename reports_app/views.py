import flask, flask_login
from library_app.models import Quiz, RedeemCode, StudentReport, Room, SessionParticipant, SessionAnswer
from project import DATABASE
from project.decorators import login_required, teacher_required

@login_required
@teacher_required
def render_reports_page():
    rooms = Room.query.filter_by(host=flask_login.current_user.id, archived = False).all()
    rooms.reverse()
    for room in rooms:
        reports = room.student_reports
        if reports and len(reports) > 0:
            
            room.success_rate = int(sum(r.percentage for r in reports) / len(reports))
        else:
            room.success_rate = 0
    return flask.render_template(
        template_name_or_list='reports.html',
        rooms=rooms,
        archive = False,
        main_page = True
    )

@login_required
@teacher_required
def render_archived_reports():
    rooms = Room.query.filter_by(host=flask_login.current_user.id, archived = True).all()
    rooms.reverse()
    for room in rooms:
        reports = room.student_reports
        if reports and len(reports) > 0:
            room.success_rate = int(sum(r.percentage for r in reports) / len(reports))
        else:
            room.success_rate = 0
    return flask.render_template(
        template_name_or_list='reports.html',
        rooms=rooms,
        username = flask_login.current_user.login,
        archive = True,
        main_page = True
    )

@login_required
@teacher_required
def render_detail_report(room_id):
    room = Room.query.get_or_404(room_id)
    if room.host != flask_login.current_user.id:
        return flask.redirect("/")
    report_data = room.get_report()
    

    return flask.render_template(
        "detail_report.html",
        report=report_data,
        room=room
    )

def get_student_report(student_id):
    participant = SessionParticipant.query.get(student_id)
    if not participant:
        return {"error": "not found"}, 404

    room = participant.room
    if not room:
        return {"error": "not found"}, 404
    
    quiz = participant.room.roomsQuiz
    if not quiz:
        return {"error": "not found"}, 404
    answers_to_send = []
    for question_idx in range(room.index_question + 1):
        answer = SessionAnswer.query.filter_by(participant_id = participant.id, question_index= question_idx).first()
        question = quiz.questions[question_idx]
        if not answer:
            answers_to_send.append({
                "question_text": question.name,
                "type": question.type,
                "answer": "Пропущенний...",
                "is_correct": False,
                "correct_answer": "Учень не був під'єднаний при відповідді на це запитання.",
                "time_spent": question.limit_time
            })
        else:
            answers_to_send.append({
                "question_text": answer.question_obj.name,
                "type": answer.question_obj.type,
                "answer": answer.get_answer(answer.answer),
                "is_correct": answer.is_correct,
                "correct_answer": answer.right_answers(),
                "time_spent": answer.time_spent
            })
    return {
        "id": participant.id,
        "nickname": f"{participant.student_profile.surname} {participant.student_profile.name}",
        "answers": answers_to_send,
    }

def get_quiz_questions_for_report(room_id):
    room = Room.query.get(room_id)
    if not room:
        return {"error": "room not found"}, 404
    
    if room.host != flask_login.current_user.id:
        return {"error": "forbidden"}, 403

    quiz = room.roomsQuiz
    if not quiz:
        return {"error": "quiz not found"}, 404

    stats_map = {}
    for question_idx in range(room.index_question + 1):
        average_time = 0.0
        for participant in room.session_participants:
            answer = SessionAnswer.query.filter_by(participant_id = participant.id, question_index = question_idx).first()
            
            if question_idx not in stats_map:
                stats_map[question_idx] = {'total': 0, 'correct': 0, "incorrect": 0, "skipped": 0}
            
            stats_map[question_idx]['total'] += 1
            if not answer:
                stats_map[question_idx]['skipped'] += 1
                continue
            if answer.is_correct:
                stats_map[question_idx]['correct'] += 1
            elif answer.answer == "Пропущений..." or answer.answer == "Пропущений":
                stats_map[question_idx]['skipped'] += 1
            else:
                stats_map[question_idx]["incorrect"] += 1
            average_time += answer.time_spent
        stats_map[question_idx]["average_time"] = average_time

    result = [
        {
            "id": q.id,
            "question_text": q.name,
            "type": q.type,
            "variants": [
                v for v in [
                    q.variant_1,
                    q.variant_2,
                    q.variant_3,
                    q.variant_4,
                    q.variant_5
                ] if v
            ],
            "image": q.image,
            "percentage": None
        }
        for q in quiz.questions
    ]
    for idx in sorted(stats_map.keys()):
        total = stats_map[idx]['total']
        correct = stats_map[idx]['correct']
        incorrect = stats_map[idx]["incorrect"]
        skipped = stats_map[idx]["skipped"]
        average_time = stats_map[idx]["average_time"]

        percantage_correct = int((correct / total) * 100) if total > 0 else 0
        percantage_incorrect = int((incorrect / total) * 100) if total > 0 else 0
        percantage_skipped = int((skipped / total) * 100) if total > 0 else 0
        
        result[idx]["percentage"] = {
            "correct": percantage_correct,
            "incorrect": percantage_incorrect,
            "skipped": percantage_skipped
        }
        result[idx]["numbers"] = {
            "correct": correct,
            "incorrect": incorrect,
            "skipped": skipped
        }
        result[idx]["average_time"] = average_time
    return flask.jsonify(result)

def get_report_answers(room_id):
    answers = SessionAnswer.query.filter_by(room_id=room_id).all()

    stats_map = {}

    for ans in answers:
        idx = ans.question_index
        if idx is None:
            continue
            
        if idx not in stats_map:
            stats_map[idx] = {'total': 0, 'correct': 0}
        
        stats_map[idx]['total'] += 1
        if ans.is_correct:
            stats_map[idx]['correct'] += 1
        stats_map[idx]["text"] = ans.question_obj.name

    result = []
    
    for idx in sorted(stats_map.keys()):
        total = stats_map[idx]['total']
        correct = stats_map[idx]['correct']
        percent = int((correct / total) * 100) if total > 0 else 0
        
        result.append({
            "question": f"Q{idx + 1}",
            "succesfull": percent,
            "text": stats_map[idx]["text"],
            "correctCount": correct,
            "totalCount": total,
        })

    return flask.jsonify(result)

def get_average_time(room_id):
    answers = SessionAnswer.query.filter_by(room_id=room_id).all()

    stats_map = {}

    for ans in answers:
        idx = ans.question_index
        if idx is None:
            continue
            
        if idx not in stats_map:
            stats_map[idx] = {'total': 0, 'time': 0}
        
        stats_map[idx]['total'] += 1
        
        stats_map[idx]['time'] += ans.time_spent

        stats_map[idx]["text"] = ans.question_obj.name

    result = []
    
    for idx in sorted(stats_map.keys()):
        total = stats_map[idx]['total']
        time = stats_map[idx]['time']
        
        avg_time = round(time / total, 1)
        
        result.append({
            "question": f"Q{idx + 1}",
            "text": stats_map[idx]["text"],
            "avg_time": avg_time,
        })

    return flask.jsonify(result)