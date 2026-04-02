import flask
from sqlalchemy import UniqueConstraint
from project.settings import DATABASE
from sqlalchemy.sql import func
import uuid

class StudentReport(DATABASE.Model):
    __tablename__ = "student_report"

    id = DATABASE.Column(DATABASE.Integer, primary_key=True)

    student_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("student.id"))

    participant_id = DATABASE.Column(
        DATABASE.Integer,
        DATABASE.ForeignKey("session_participant.id"),
        nullable=False,
        unique=True 
    )

    room_id = DATABASE.Column(
        DATABASE.Integer,
        DATABASE.ForeignKey("room.id"),
        nullable=True
    )

    total_questions = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)
    correct_answers = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)
    wrong_answers = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)

    score = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)
    max_score = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)
    percentage = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)

    grade = DATABASE.Column(DATABASE.Integer, nullable=True)

    hash_code = DATABASE.Column(DATABASE.String(64), unique=True,
        nullable=False,
        default=lambda: uuid.uuid4().hex
    )

    created_at = DATABASE.Column(DATABASE.DateTime, server_default=func.now())

    participant = DATABASE.relationship(
        "SessionParticipant",
        backref=DATABASE.backref("report", uselist=False),
        lazy=True
    )

    room = DATABASE.relationship(
        "Room",
        backref="student_reports"
    )


class Question(DATABASE.Model):
    __tablename__ = 'question'

    id = DATABASE.Column(DATABASE.Integer, primary_key=True)
    name = DATABASE.Column(DATABASE.String(100), nullable=False)
    type = DATABASE.Column(DATABASE.String(100), nullable=False)
    variant_1 = DATABASE.Column(DATABASE.String(100), nullable=False)
    variant_2 = DATABASE.Column(DATABASE.String(100), nullable=True)
    variant_3 = DATABASE.Column(DATABASE.String(100), nullable=True)
    variant_4 = DATABASE.Column(DATABASE.String(100), nullable=True)
    variant_5 = DATABASE.Column(DATABASE.String(100), nullable=True)
    correct_answer = DATABASE.Column(DATABASE.JSON)
    limit_time = DATABASE.Column(DATABASE.Float, default=60.0)
    quiz_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey('quiz.id'), nullable=False)
    image = DATABASE.Column(DATABASE.String(255), nullable=True)

    answers = DATABASE.relationship("SessionAnswer", back_populates="question_obj", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.name,
            "type": self.type,
            "variants": [v for v in [self.variant_1, self.variant_2, self.variant_3, self.variant_4, self.variant_5] if v],
            "correct_answer": self.correct_answer,
            "quiz_id": self.quiz_id,
            "image": self.image,
            "answers": [a.to_dict() for a in self.answers] if self.answers else []
        }
class RedeemCode(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    name = DATABASE.Column(DATABASE.String(100), nullable = False)
    quiz_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("quiz.id"))
    code_enter = DATABASE.Column(DATABASE.Integer)
    hosted_by = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    room_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("room.id"))

class Quiz(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    name = DATABASE.Column(DATABASE.String(100), nullable = False)
    description = DATABASE.Column(DATABASE.String, nullable = False)
    count_questions = DATABASE.Column(DATABASE.Integer, nullable = False)
    author_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey('user.id'))
    image = DATABASE.Column(DATABASE.String(100), nullable = False)
    is_draft = DATABASE.Column(DATABASE.Boolean, default=True)
    questions = DATABASE.relationship(Question, backref = 'quiz', lazy = True)
    codes = DATABASE.relationship("RedeemCode", backref="quiz")
    rooms = DATABASE.relationship("Room", backref="roomsQuiz", lazy=True)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "count_questions": self.count_questions,
            "author": {
                "name": self.user.name,
                "surname": self.user.surname
            } if self.user else None,
            "image": self.image,
            "codes": self.codes
        }   

class Room(DATABASE.Model):
    __tablename__ = 'room'
    id = DATABASE.Column(DATABASE.Integer, primary_key=True)
    students = DATABASE.Column(DATABASE.JSON())
    index_question = DATABASE.Column(DATABASE.Integer)
    status = DATABASE.Column(DATABASE.String, default= "waiting")
    answered_students = DATABASE.Column(DATABASE.Integer, default=0)
    date = DATABASE.Column(DATABASE.DateTime, server_default=func.now())
    archived = DATABASE.Column(DATABASE.Boolean, default=False)
    start_time = DATABASE.Column(DATABASE.Float, nullable=True)
    limit_time = DATABASE.Column(DATABASE.Float, default=60.0)

    quiz = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("quiz.id"))
    host = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    group_class_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("group_class.id"))
    course_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("course.id"), nullable=True)
    
    redeem_codes = DATABASE.relationship("RedeemCode", backref="room", lazy=True)
    session_participants = DATABASE.relationship("SessionParticipant", backref="room", lazy=True)
    answers = DATABASE.relationship("SessionAnswer", backref= "room", lazy=True)

    def get_report(self):
        from .models import SessionAnswer, Question

        participants = self.session_participants
        report = []

        for p in participants:
            if not p.is_connected:
                continue
            student_report = p.report
            answers_data = []
            for question_idx in range(self.index_question + 1):
                answer = SessionAnswer.query.filter_by(room_id=self.id, participant_id=p.id, question_index= question_idx).first()
                if not answer:
                    answers_data.append({
                        "question_id": self.roomsQuiz.questions[question_idx].id,
                        "question_text": self.roomsQuiz.questions[question_idx].name,
                        "your_answer": "Пропущений...",
                        "is_correct": False
                    })
                else:
                    q = Question.query.get(answer.question)
                    answers_data.append({
                        "question_id": q.id,
                        "question_text": q.name,
                        "your_answer": answer.answer,
                        "is_correct": answer.is_correct
                    })
            try:
                report.append({
                    "participant_id": p.id,
                    "nickname": f"{p.student_profile.surname} {p.student_profile.name}",
                    "percent": student_report.percentage,
                    "answers": answers_data,
                    "grade": student_report.grade,
                    "report": p.report
                })
            except:
                print("Error")

        return sorted(report, key=lambda x: x["percent"], reverse=True)

class SessionParticipant(DATABASE.Model):
    id = DATABASE.Column(DATABASE.Integer, primary_key = True)
    room_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("room.id"))
    is_connected = DATABASE.Column(DATABASE.Boolean, default=True)
    reconnect_hash = DATABASE.Column(DATABASE.String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex[:32])
    student_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("student.id"), nullable=True)
    answers = DATABASE.relationship("SessionAnswer", backref= "participant", lazy=True)
    

class SessionAnswer(DATABASE.Model):
    __tablename__ = "session_answer"

    id = DATABASE.Column(DATABASE.Integer, primary_key=True)
    room_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("room.id"), nullable=True)
    question = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("question.id"))
    participant_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("session_participant.id"))
    question_index = DATABASE.Column(DATABASE.Integer)
    answer = DATABASE.Column(DATABASE.JSON(), nullable=True)
    is_correct = DATABASE.Column(DATABASE.Boolean, default=False)
    time_spent = DATABASE.Column(DATABASE.Float, nullable=False)

    question_obj = DATABASE.relationship("Question", back_populates="answers")
    __table_args__ = (UniqueConstraint('room_id', 'participant_id', 'question', name='uq_answer_once'),)

    def to_dict(self):
        question = self.question_obj
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "question": self.question,
            "question_text": question.name if question else "",
            "variants": [v for v in [
                question.variant_1,
                question.variant_2,
                question.variant_3,
                question.variant_4,
                question.variant_5
            ] if v] if question else [],
            "answer": self.answer,
            "is_correct": self.is_correct
        }
    def right_answers(self):
        question = self.question_obj
        if not question:
            return []
        if question.type == "one answer":
            if int(question.correct_answer) == 1:
                return [question.variant_1]
            elif int(question.correct_answer) == 2:
                return [question.variant_2]
            elif int(question.correct_answer) == 3:
                return [question.variant_3]
            elif int(question.correct_answer) == 4:
                return [question.variant_4]
            elif int(question.correct_answer) == 5:
                return [question.variant_5]
        elif question.type == "multiple answers":
            answers = []
            for ans in question.correct_answer:
                if ans == "1":
                    answers.append(question.variant_1)
                elif ans == "2":
                    answers.append(question.variant_2)
                elif ans == "3":
                    answers.append(question.variant_3)
                elif ans == "4":
                    answers.append(question.variant_4)
                elif ans == "5":
                    answers.append(question.variant_5)
            return answers
        elif question.type == "enter answer":
            return question.correct_answer if question.correct_answer else []
        return []
    def get_answer(self, answersswer):
        question = self.question_obj
        if question.type == "one answer":
            if "Пропущений..." in [answersswer]:
                return ["Пропущений"]
            if int(answersswer) == 1:
                return [question.variant_1]
            elif int(answersswer) == 2:
                return [question.variant_2]
            elif int(answersswer) == 3:
                return [question.variant_3]
            elif int(answersswer) == 4:
                return [question.variant_4]
            elif int(answersswer) == 5:
                return [question.variant_5]
        elif question.type == "multiple answers":
            if isinstance(question.correct_answer, list):
                answers = []
                if not answersswer or "Пропущений..." in answersswer:
                    answers.append("Пропущений")
                    return answers
                for ans in answersswer:
                    if int(ans) == 1:
                        answers.append(question.variant_1)
                    elif int(ans) == 2:
                        answers.append(question.variant_2)
                    elif int(ans) == 3:
                        answers.append(question.variant_3)
                    elif int(ans) == 4:
                        answers.append(question.variant_4)
                    elif int(ans) == 5:
                        answers.append(question.variant_5)
                return answers
        elif question.type == "enter answer":
            return answersswer

