import flask_login
from project.decorators import login_required, student_required, teacher_required
from project.settings import DATABASE, socketio, active_rooms_cache
from flask_socketio import emit, join_room
from library_app.models import RedeemCode, Quiz, Room, Question, SessionParticipant, SessionAnswer, StudentReport
import json, flask, time
from flask import current_app, session


def update_room_cache(room):
    active_rooms_cache[room.id] = {
        "index_question": room.index_question,
        "limit_time": room.limit_time,
        "start_time": room.start_time,
    }

def get_room_state(room_id, app):

    state = active_rooms_cache.get(room_id)
    print(active_rooms_cache)
    if state:
        return state
    
    with app.app_context():
        room = Room.query.get(room_id)
        if room:
            update_room_cache(room)
            print(f"Room {room_id} loaded from DB to Cache")
            return active_rooms_cache[room_id]
            
    return None 

def auto_end_question(room_id, index_question, delay, code, app, original_limit):
    print("Starting timer for", delay)
    
    socketio.sleep(delay)
    cache = active_rooms_cache.get(room_id)
    
    if not cache:
        return
    if cache['index_question'] == index_question and cache['limit_time'] == original_limit:
        with app.app_context():
            if Room.query.get(room_id).status != "running_question":
                return
            else:
                print("Timer ignored (room.status is outdated)")
            print(f"room's timer (id: {room_id}) worked from cache")
            handle_end_question({"code": code})
    else:
        print("timer ignored (timer data from cache was updated)")

def create_student_report(participant, room_id):
    answers = SessionAnswer.query.filter_by(room_id=room_id, participant_id=participant.id).all()
    room = Room.query.get(room_id)
    total = room.index_question + 1
    correct = sum(1 for a in answers if a.is_correct)
    wrong = total - correct

    max_score = total
    score = correct
    percentage = round((correct / total) * 100) if total else 0

    grade = percentage / 100 * 12 // 1

    report = StudentReport(
        participant_id=participant.id,
        room_id=room_id,
        total_questions=total,
        correct_answers=correct,
        wrong_answers=wrong,
        score=score,
        max_score=max_score,
        percentage=percentage,
        grade=grade,
        student_id=participant.student_profile.id
    )

    DATABASE.session.add(report)
    DATABASE.session.commit()

    return report.hash_code

@socketio.on("join_room")
def handle_join(data):
    code_enter = data.get("code")
    student_id = data.get("student_id")

    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        emit("join_error", {"message": "Код не найден"})
        return

    room = redeem.room
    if not room:
        emit("join_error", {"message": "Комната не найдена"})
        return
    
    quiz = room.roomsQuiz
    if not quiz:
        emit("join_error", {"message": "Викторина не найдена"})
        return

    username = flask_login.current_user.surname + " " + flask_login.current_user.name
    
    existing_participiant = SessionParticipant.query.filter_by(student_id=student_id, room_id=room.id).first()

    if room.status == "ended":
        if not existing_participiant:
            emit("redirect_to", {
                "url": "/"
            })
            return
        result = StudentReport.query.filter_by(participant_id = existing_participiant.id, room_id = room.id).first()
        if not result:
            emit("redirect_to", {
                "url": "/"
            })
            return
        emit("redirect_to", {
            "url": f"/student/report/{result.hash_code}"
        })
        return
    
    if not existing_participiant:
        existing_participiant = SessionParticipant(
            room_id=room.id, 
            is_connected=True,
            student_id=flask_login.current_user.id
        )
        try:
            DATABASE.session.add(existing_participiant)
            DATABASE.session.commit()
            if not room.students:
                room.students = [[username, existing_participiant.reconnect_hash]]
            else:
                new_students = list(room.students)
                new_students.append([username, existing_participiant.reconnect_hash])
                room.students = new_students
            DATABASE.session.commit()
        except Exception as e:
            DATABASE.session.rollback()
            emit("join_error", {"message": "Не удалось добавить участника"})
            return
    elif existing_participiant.is_connected == False:
        existing_participiant.is_connected = True
        
        new_students = list(room.students)
        room.students = new_students
        DATABASE.session.commit()
    else:
        print("Участник есть в комнате")
        
    session['participant_id'] = existing_participiant.id
    
    join_room(str(room.id))
    join_room(f"student_{existing_participiant.id}")

    emit("joined_success", {"quiz_name": redeem.name, "hash": existing_participiant.reconnect_hash})
    socketio.emit("user_list_update", {"students": room.students}, room=str(room.id))
    if not room.index_question and room.index_question != 0:
        return
    
    
    current_question = quiz.questions[room.index_question]
    variants = [
        {"id": 1, "text": current_question.variant_1},
        {"id": 2, "text": current_question.variant_2},
        {"id": 3, "text": current_question.variant_3},
        {"id": 4, "text": current_question.variant_4}
    ]
    
    hashed_correct = ""
    for char in current_question.correct_answer:
        hashed_correct += "a" if char != " " else " "
        
    state = get_room_state(room.id, current_app._get_current_object())

    passed = time.time() - state["start_time"]
    remaining = state['limit_time'] - passed
    
    if remaining > 0:
        socketio.emit("question_timer", {"remaining": round(remaining)}, room = f"{room.id}")

    emit(
        "quiz_start_student", 
        {
            "quiz_name": quiz.name,
            "name": current_question.name,
            "type": current_question.type,
            "variants": variants,
            "correct_answer": hashed_correct,
            "image": current_question.image,
            "id": current_question.id,
            "current_question": room.index_question + 1
        },
    )
    answers = SessionAnswer.query.filter_by(room_id = room.id, question= current_question.id).all()
    answers_count = len(answers)
    for ans in answers:
        participant = SessionParticipant.query.get(ans.participant_id)
        user_answer_text = ans.get_answer(ans.answer)
        user_answer_text = user_answer_text if len(user_answer_text) > 1 else user_answer_text[0]
        if user_answer_text == "Пропущений" or user_answer_text == "Пропущений...":
            continue
        socketio.emit(
            'student_answer',
            {
                'hash': participant.reconnect_hash
            },
            room=f"{room.id}"
        )
    answer_status = SessionAnswer.query.filter_by(participant_id=existing_participiant.id, question=current_question.id).first()
    if answers_count != len(room.students):
        if answer_status:
            emit(
                "current_question_info",
                {
                    "question": current_question.type,
                    "is_correct": "wait",
                    "answer_id": None,
                }
            )
        elif not answer_status and remaining < 0:
            emit(
                "current_question_info",
                {
                    "question": current_question.type,
                    "is_correct": "skipped",
                    "answer_id": None,
                }
            )
    elif answer_status:
        emit(
            "current_question_info",
            {
                "question": current_question.type,
                "is_correct": answer_status.is_correct,
                "answer_id": answer_status.get_answer(answer_status.answer),
            }
        )
    else:
        emit(
            "current_question_info",
            {
                "question": current_question.type,
                "is_correct": "skipped",
                "answer_id": None,
            }
        )
    return

@socketio.on("remove_student")
def handle_remove_student(data):
    code_enter = data.get("code")
    student = data.get("student")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return
    room = redeem.room
    if not room:
        return
    participant = SessionParticipant.query.filter_by(room_id=room.id, reconnect_hash= student[1]).first()
    if not participant:
        return
    participant.is_connected = False
    DATABASE.session.commit()
    socketio.emit("remove_student_client", {"hash": student[1]}, room=str(room.id))

@socketio.on("host_join")
@login_required
def handle_host_join(data):
    if flask.session.get("user_role") != "teacher":
        emit("redirect_to", {
            "url": "/"
        })
        return
    code_enter = data.get("room")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return

    room = redeem.room
    if not room:
        emit("redirect_to", {
            "url": "/"
        })
        return

    if flask_login.current_user.id != room.host:
        emit("redirect_to", {
            "url": "/"
        })
        return
        
    join_room(str(room.id))
    join_room(f"teacher_{room.host}")

    participants = SessionParticipant.query.filter_by(room_id=room.id, is_connected=True).all()

    socketio.emit("user_list_update", {"students": room.students}, room=str(room.id))

    quiz = room.roomsQuiz
    
    if not room.index_question and room.index_question != 0:
        return
        
    if room.status == "ended":
        emit("redirect_to", {
            "url": f"/report/{room.id}"
        })
        return
    current_question = quiz.questions[room.index_question]

    variants = [
        {"id": 1, "text": current_question.variant_1},
        {"id": 2, "text": current_question.variant_2},
        {"id": 3, "text": current_question.variant_3},
        {"id": 4, "text": current_question.variant_4}
    ]
    
    hashed_correct = ""
    for char in current_question.correct_answer:
        hashed_correct += "a" if char != " " else " "
    question_data = {
        "id": current_question.id,
        "name": current_question.name,
        "type": current_question.type,
        "variants": variants,
        "correct_answer": hashed_correct,
        "image": current_question.image,
        "current_question": room.index_question + 1
    }

    state = get_room_state(room.id, current_app._get_current_object())
    
    passed = time.time() - state["start_time"]
    remaining = state['limit_time'] - passed

    if remaining > 0:
        socketio.emit("question_timer", {"remaining": round(remaining)}, room = f"{room.id}")

    emit("quiz_start_teacher", question_data)

    answers = SessionAnswer.query.filter_by(room_id=room.id, question=current_question.id).all()

    for ans in answers:
        participant = SessionParticipant.query.get(ans.participant_id)
        user_answer_text = ans.get_answer(ans.answer)
        user_answer_text = user_answer_text if len(user_answer_text) > 1 else user_answer_text[0]
        if user_answer_text == "Пропущений" or user_answer_text == "Пропущений...":
            continue
        emit(
            'student_answer',
            {
                'hash': participant.reconnect_hash
            }
        )

    if len(answers) != len(participants) and remaining > 0:
        return
    
    results = []
    total = len(answers)
    correct = 0
    wrong = 0
    skipped = 0
    count_answered = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0
    }
    for ans in answers:
        participant = SessionParticipant.query.get(ans.participant_id)
        correct_text = ans.right_answers()
        if isinstance(correct_text, list):
            correct_text = correct_text if len(correct_text) > 1 else correct_text[0]

        user_answer_text = ans.get_answer(ans.answer)
        user_answer_text = user_answer_text if len(user_answer_text) > 1 else user_answer_text[0]
        if ans.is_correct:
            correct += 1
        else: 
            if user_answer_text == "Пропущений" or user_answer_text == "Пропущений...":
                skipped += 1
            else:
                wrong += 1
        if current_question.type != "enter answer":
            if isinstance(ans.answer, list):
                for answer in ans.answer:
                    count_answered[str(answer)] += 1
            elif current_question.type == "one answer" and len(ans.answer) == 1:
                count_answered[str(ans.answer)] += 1

        results.append({
            "student_id": ans.participant_id,
            "nickname": participant.student_profile.surname + " " + participant.student_profile.name,
            "answer": user_answer_text,
            "is_correct": ans.is_correct,
            "correct_answer": correct_text,
            "answer_id": ans.answer,
            "correct_answer_id": current_question.correct_answer,
            "type": current_question.type,
            "hash": participant.reconnect_hash,
            "time_spent": ans.time_spent,
        })

    variants_with_answers = [
        {
            "id": 1,
            "text": current_question.variant_1,
            "answered": count_answered["1"]
        },
        {
            "id": 2,
            "text": current_question.variant_2,
            "answered": count_answered["2"]
        },
        {
            "id": 3,
            "text": current_question.variant_3,
            "answered": count_answered["3"]
        },
        {
            "id": 4,
            "text": current_question.variant_4,
            "answered": count_answered["4"]
        }
    ]
    socketio.emit(
        "teacher_results",
        {
            "donut_data": {
                "total_participiants": total,
                "correct": correct,
                "wrong": wrong,
                "skipped": skipped
            },
            "question_data": {
                "name": current_question.name,
                "type": current_question.type,
                "variants": variants_with_answers,
                "media": current_question.image
            },
            "results": results,
            "index_question": room.index_question,
            "total_questions": len(quiz.questions)
        },
        room=f"teacher_{room.host}"
    )
    return

@socketio.on("quiz_start")
@login_required
@teacher_required
def handle_start(data):
    code_enter = data.get("code")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return

    room = redeem.room

    quiz = room.roomsQuiz

    room.start_time = time.time()
    room.limit_time = 60.0

    room.index_question = 0
    room.status = "running_question"

    DATABASE.session.commit()
    now_question = quiz.questions[0]
    variants = [
        {"id": 1, "text": now_question.variant_1},
        {"id": 2, "text": now_question.variant_2},
        {"id": 3, "text": now_question.variant_3},
        {"id": 4, "text": now_question.variant_4},
    ]
    
    hashed_correct = ""
    for char in now_question.correct_answer:
        hashed_correct += "a" if char != " " else " "
    question_data = {
        "id": now_question.id,
        "name": now_question.name,
        "type": now_question.type,
        "variants": variants,
        "correct_answer": hashed_correct,
        "image": now_question.image,
        "current_question": room.index_question + 1
    }

    socketio.emit("quiz_start_student", question_data, room=str(room.id))
    socketio.emit("quiz_start_teacher", question_data, room=str(room.id))
    update_room_cache(room)

    socketio.start_background_task(
        auto_end_question, 
        room.id, 
        room.index_question, 
        room.limit_time, 
        code_enter, 
        current_app._get_current_object(),
        room.limit_time
    )
    
    socketio.emit("question_timer", {"remaining": int(room.limit_time)}, room=str(room.id))

@socketio.on("answer")
@login_required
@student_required
def handle_answer(data):
    question_id = data.get("question_id")
    answer = data.get("answer")   
    username = data.get("username")
    code_enter = data.get("code")
    my_hash = data.get("my_hash")   
    if not question_id:
        return

    question = Question.query.get(question_id)
    if not question:
        return
    participiant = SessionParticipant.query.get(session.get("participant_id"))
    
    if not participiant:
        return
    
    redeem = participiant.room.redeem_codes[0]
    room = participiant.room

    state = active_rooms_cache.get(room.id)
    
    if not state:
        return

    is_correct = False

    if question.type == "multiple answers":
        if isinstance(answer, str):
            try:
                answer = json.loads(answer)
            except:
                answer = [int(x) for x in answer.split(",")]

        if isinstance(question.correct_answer, str):
            try:
                correct = json.loads(question.correct_answer)
            except:
                correct = [int(x) for x in question.correct_answer.split(",")]
        else:
            correct = question.correct_answer

        is_correct = set(map(int, answer)) == set(map(int, correct))

    else:
        is_correct = str(answer).lower() == str(question.correct_answer).lower()

    now = time.time()
    time_spent = now - state['start_time']
    
    if time_spent > (state['limit_time'] + 0.5):
        return 
    
    session_answer = SessionAnswer(
        room_id = room.id,
        question = question.id,
        participant_id = participiant.id,
        answer = answer,
        is_correct = is_correct,
        question_index = room.index_question,
        time_spent= round(time_spent, 2)
    )

    try:
        DATABASE.session.add(session_answer)
        DATABASE.session.commit()
    except Exception as e:
        DATABASE.session.rollback()

    if redeem and room:
        room.answered_students = (room.answered_students or 0) + 1
        DATABASE.session.commit()

        socketio.emit('student_answer', {
            'username': username,
            "hash": my_hash,
            'answer': answer,
            'question_id': question_id
        }, room=str(room.id), include_self=False)

        answers = SessionAnswer.query.filter_by(
            room_id=room.id,
            question=question.id
        ).all()

        if len(answers) == SessionParticipant.query.filter_by(room_id=room.id).filter_by(is_connected = True).count():
            handle_end_question({"code": code_enter})

@socketio.on("next_question")
@login_required
@teacher_required
def handle_next(data):
    code_enter = data.get("code")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return

    room_id = str(redeem.room_id)
    room = Room.query.get(room_id)
    quiz = Quiz.query.get(room.quiz)

    if room.index_question is None:
        room.index_question = 0
    else:
        room.index_question += 1
    room.answered_students = 0
    room.start_time = time.time()
    room.limit_time = 60.0
    room.status = "running_question"

    DATABASE.session.commit()

    if room.index_question < len(quiz.questions):
        now_question = quiz.questions[room.index_question]
        
        variants = [
            {"id": 1, "text": now_question.variant_1},
            {"id": 2, "text": now_question.variant_2},
            {"id": 3, "text": now_question.variant_3},
            {"id": 4, "text": now_question.variant_4}
        ]
        

        hashed_correct = ""
        for char in now_question.correct_answer:
            hashed_correct += "a" if char != " " else " "
        
        question_data = {
            "id": now_question.id,
            "name": now_question.name,
            "type": now_question.type,
            "variants": variants,
            "correct_answer": hashed_correct,
            "image": now_question.image,
            "current_question": room.index_question + 1
        }

        socketio.emit("quiz_start_student", question_data, room=room_id)
        socketio.emit("quiz_start_teacher", question_data, room=room_id)
        socketio.emit("question_timer", {"remaining": int(room.limit_time)}, room=room_id)
        
        update_room_cache(room)
        socketio.start_background_task(
            auto_end_question,
            room.id,
            room.index_question,
            room.limit_time,
            code_enter,
            current_app._get_current_object(),
            room.limit_time
        )
    else:
        room.index_question = None
        DATABASE.session.commit()

@socketio.on("quiz_end_msg")
def handle_quiz_end_msg(data):
    code_enter = data.get("code")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return
    room = Room.query.get(redeem.room_id)
    room.status = "ended"
    for participiant in room.session_participants:
        report_hash = create_student_report(participant= participiant, room_id=room.id)
        socketio.emit(
            "end_quiz",
            {"hash_code": report_hash},
            room= f"student_{participiant.id}"
        )
    active_rooms_cache.pop(room.id, None)
    socketio.emit("end_msg", {}, room=str(room.id))

@socketio.on("show_quiz_results")
def handle_show_quiz_results(data):
    code_enter = data.get("code")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return

    room = Room.query.get(redeem.room_id)
    if not room:
        return
    emit("quiz_results", {"url": f"/report/{room.id}"})

@socketio.on("end_question")
def handle_end_question(data):
    room = RedeemCode.query.filter_by(code_enter=data.get("code")).first().room
    if not room:
        return

    quiz = room.roomsQuiz
    current_question = quiz.questions[room.index_question]

    answered_ids = {
        ans.participant_id for ans in SessionAnswer.query.filter_by(room_id=room.id, question=current_question.id).all()
    }

    all_participants = room.session_participants
    for participant in all_participants:
        if participant.id not in answered_ids:
            skip_answer = SessionAnswer(
                room_id=room.id,
                question=current_question.id,
                participant_id=participant.id,
                answer="Пропущений...",  
                is_correct=False,
                question_index = room.index_question,
                time_spent= round(time.time() - room.start_time, 1)
            )
            DATABASE.session.add(skip_answer)
    room.status = "waiting"
    DATABASE.session.commit()

    answers = SessionAnswer.query.filter_by(room_id=room.id, question=current_question.id).all()
    results = []
    total = len(all_participants)
    correct = 0
    wrong = 0
    skipped = 0
    count_answered = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0
    }
    for ans in answers:
        participant = SessionParticipant.query.get(ans.participant_id)
        correct_text = ans.right_answers() 
        if isinstance(correct_text, list):
            correct_text = correct_text if len(correct_text) > 1 else correct_text[0]

        user_answer_text = ans.get_answer(ans.answer) 
        user_answer_text = user_answer_text if len(user_answer_text) > 1 else user_answer_text[0]
        if ans.is_correct:
            correct += 1
        else: 
            if user_answer_text == "Пропущений" or user_answer_text == "Пропущений...":
                skipped += 1
            else:
                wrong += 1
        if current_question.type != "enter answer":
            if isinstance(ans.answer, list):
                for answer in ans.answer:
                    count_answered[str(answer)] += 1
            elif current_question.type == "one answer" and len(ans.answer) == 1:
                count_answered[str(ans.answer)] += 1
        results.append({
            "student_id": ans.participant_id,
            "nickname": participant.student_profile.surname + " " + participant.student_profile.name,
            "answer": user_answer_text,
            "is_correct": ans.is_correct,
            "correct_answer": correct_text,
            "answer_id": ans.answer,
            "correct_answer_id": current_question.correct_answer,
            "type": current_question.type,
            "time_spent": ans.time_spent,
            "hash": participant.reconnect_hash
        })

    for res in results:
        socketio.emit(
            "student_result",
            {
                "your_answer": res["answer"],
                "is_correct": res["is_correct"],
                "correct_answer": res["correct_answer"],
                "answer_id": res["answer_id"],
                "type": res["type"],
                "correct_answer_id": res["correct_answer_id"]
            },
            room=f"student_{res['student_id']}"
        )

    variants_with_answers = [
        {
            "id": 1,
            "text": current_question.variant_1,
            "answered": count_answered["1"]
        },
        {
            "id": 2,
            "text": current_question.variant_2,
            "answered": count_answered["2"]
        },
        {
            "id": 3,
            "text": current_question.variant_3,
            "answered": count_answered["3"]
        },
        {
            "id": 4,
            "text": current_question.variant_4,
            "answered": count_answered["4"]
        }
    ]
    
    top_participiants = []
    

    online_participants = SessionParticipant.query.filter_by(
        room_id = room.id,
        is_connected= True
    )
    for participant in online_participants:
        total_correct = SessionAnswer.query.filter_by(
            room_id=room.id, 
            participant_id=participant.id, 
            is_correct=True
        ).count()
        
        top_participiants.append({
            "participant": participant, 
            "total": total_correct
        })

    top_participiants.sort(key=lambda x: x["total"], reverse=True)
    
    room.students = [] 

    for item in top_participiants:
        p = item["participant"]
        username = f"{p.student_profile.surname} {p.student_profile.name}"
        room.students.append([username, p.reconnect_hash])
    
    DATABASE.session.commit()
    
    socketio.emit("user_list_update", {"students": room.students}, room=str(room.id))
    for ans in answers:
        participant = SessionParticipant.query.get(ans.participant_id)
        user_answer_text = ans.get_answer(ans.answer)
        user_answer_text = user_answer_text if len(user_answer_text) > 1 else user_answer_text[0]
        if user_answer_text == "Пропущений" or user_answer_text == "Пропущений...":
            continue
        socketio.emit(
            'student_answer',
            {
                'hash': participant.reconnect_hash
            },
            room=f"{room.id}"
        )
    socketio.emit(
        "teacher_results",
        {
            "donut_data": {
                "total_participiants": total,
                "correct": correct,
                "wrong": wrong,
                "skipped": skipped
            },
            "question_data": {
                "name": current_question.name,
                "type": current_question.type,
                "variants": variants_with_answers,
                "media": current_question.image
            },
            "results": results,
            "index_question": room.index_question,
            "total_questions": len(quiz.questions)
        },
        room=f"teacher_{room.host}"
    )

@socketio.on("add_15_sec")
@login_required
@teacher_required
def handle_add_time(data):
    code_enter = data.get("code")
    redeem = RedeemCode.query.filter_by(code_enter=code_enter).first()
    if not redeem:
        return

    room = redeem.room
    if not room:
        return
    
    room.limit_time += 15.0
    DATABASE.session.commit()
    
    update_room_cache(room)

    passed = time.time() - room.start_time
    new_remaining = room.limit_time - passed


    socketio.start_background_task(
        auto_end_question, 
        room.id, 
        room.index_question, 
        new_remaining, 
        code_enter, 
        current_app._get_current_object(),
        room.limit_time
    )
    socketio.emit("add_time", room=str(room.id))