import uuid
import flask_login
from sqlalchemy import UniqueConstraint
from project.settings import DATABASE

class Student(DATABASE.Model, flask_login.UserMixin):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)

    login= DATABASE.Column(DATABASE.String(40), nullable= False)
    name= DATABASE.Column(DATABASE.String(30), nullable= False)
    surname= DATABASE.Column(DATABASE.String(30), nullable= False)
    password= DATABASE.Column(DATABASE.String(5), nullable= False, default=lambda: uuid.uuid4().hex[:5])

    my_reports = DATABASE.relationship("StudentReport", backref='student', lazy=True)
    sessions = DATABASE.relationship("SessionParticipant", backref="student_profile", lazy=True)
    courses = DATABASE.relationship("Course", secondary="student_course", backref="students_enrolled", lazy='dynamic')
    my_class_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("group_class.id"))

class GroupClass(DATABASE.Model):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)

    number = DATABASE.Column(DATABASE.Integer,   nullable= False)
    char   = DATABASE.Column(DATABASE.String(1), nullable= False)

    teacher_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    students = DATABASE.relationship("Student", backref="classroom", lazy=True)
    courses = DATABASE.relationship("Course", backref="classroom", lazy=True)
    rooms = DATABASE.relationship("Room", backref="classroom", lazy=True)

class StudentCourse(DATABASE.Model):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)

    student_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("student.id"))
    course_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("course.id"))

    UniqueConstraint('student_id', 'course_id')

class Course(DATABASE.Model):
    id= DATABASE.Column(DATABASE.Integer, primary_key= True)

    name = DATABASE.Column(DATABASE.String(50), nullable= False)
    description = DATABASE.Column(DATABASE.String(200), nullable= False)
    created_at = DATABASE.Column(DATABASE.DateTime, nullable=False, default=DATABASE.func.now())
    is_active = DATABASE.Column(DATABASE.Boolean, default=True)

    group_class_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("group_class.id"))
    teacher_id = DATABASE.Column(DATABASE.Integer, DATABASE.ForeignKey("user.id"))
    students = DATABASE.relationship("Student", secondary="student_course", backref="courses_enrolled", lazy='dynamic')
    rooms = DATABASE.relationship("Room", backref="course", lazy=True)
    def connect_all_students(self):
        group_class = self.classroom
        if not group_class:
            return

        for student in group_class.students:
            if not StudentCourse.query.filter_by(student_id=student.id, course_id=self.id).first():
                enrollment = StudentCourse(student_id=student.id, course_id=self.id)
                DATABASE.session.add(enrollment)
        
        DATABASE.session.commit()