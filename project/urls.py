from .settings import project
import home_app, user_app, admin_app, library_app, execution_app, reports_app, host_app, classroom_app, student_app

home_app.home_app.add_url_rule(
    rule= '/',
    view_func= home_app.render_home_page
)
project.register_blueprint(blueprint= home_app.home_app)
# 
user_app.user_app.add_url_rule(
    rule= '/signup/',
    view_func= user_app.render_signup,
    methods= ["POST", "GET"]
)
user_app.user_app.add_url_rule(
    rule= '/login/',
    view_func= user_app.render_login,
    methods= ["POST", "GET"]
)
user_app.user_app.add_url_rule(
    rule= '/logout/',
    view_func= user_app.logout
)
user_app.user_app.add_url_rule(
    rule = '/profile/',
    view_func = user_app.render_profile
)
user_app.user_app.add_url_rule(
    rule= '/validate/',
    view_func= user_app.validate_data,
    methods= ["POST"]
)
user_app.user_app.add_url_rule(
    rule= '/sendcode/',
    view_func= user_app.send_code,
    methods= ["POST"]
)
user_app.user_app.add_url_rule(
    rule = '/validate-code/',
    view_func = user_app.validate_code,
    methods= ["POST", "GET"]
)
user_app.user_app.add_url_rule(
    rule= '/create_admin/',
    view_func= user_app.create_admin,
    methods= ["POST"]
)

project.register_blueprint(blueprint= user_app.user_app)
admin_app.admin_app.add_url_rule(
    rule= '/admin/',
    view_func= admin_app.render_admin_page,
    methods= ["POST", "GET"]
)
admin_app.admin_app.add_url_rule(
    rule= '/search-quizes/',
    view_func= admin_app.search,
    methods= ["POST"]
)
project.register_blueprint(blueprint= admin_app.admin_app)

library_app.library_app.add_url_rule(
    rule= '/library/',
    view_func= library_app.render_library,
    methods= ['POST', 'GET']
)

library_app.library_app.add_url_rule(
    rule= '/get-draft/',
    view_func= library_app.get_draft,
    methods= ["POST", "GET"]
)

library_app.library_app.add_url_rule(
    rule= '/create-quiz/',
    view_func= library_app.render_create_quiz,
    methods= ["POST", "GET"]
)

library_app.library_app.add_url_rule(
    rule= '/search-library/',
    view_func= library_app.search_in_library,
    methods= ["POST"]
)

project.register_blueprint(blueprint= library_app.library_app)

execution_app.execution_app.add_url_rule(
    rule = '/login_student/',
    view_func = execution_app.render_login_student,
    methods = ["POST", "GET"]
)

execution_app.execution_app.add_url_rule(
    rule = '/execution/',
    view_func = execution_app.render_enter_code,
    methods = ["POST", "GET"]
)

project.register_blueprint(blueprint = execution_app.execution_app)

reports_app.reports_app.add_url_rule(
    rule= '/reports/',
    view_func= reports_app.render_reports_page,
    methods= ["POST", "GET"]
)
reports_app.reports_app.add_url_rule(
    rule="/report/<int:room_id>/",
    view_func=reports_app.render_detail_report,
    methods = ["GET", "POST"]
)
reports_app.reports_app.add_url_rule(
    rule="/report/student/<int:student_id>",
    view_func=reports_app.get_student_report,
    methods = ["GET"]
)
reports_app.reports_app.add_url_rule(
    rule= '/reports/archive/',
    view_func= reports_app.render_archived_reports,
    methods= ["POST", "GET"]
)
reports_app.reports_app.add_url_rule(
    rule= "/reports/room_stats/<int:room_id>",
    view_func= reports_app.get_report_answers,
    methods= ["GET"]
)
reports_app.reports_app.add_url_rule(
    rule= "/reports/room_time_stats/<int:room_id>",
    view_func= reports_app.get_average_time,
    methods= ["GET"]
)
reports_app.reports_app.add_url_rule(
    rule= "/reports/<int:room_id>/questions",
    view_func= reports_app.get_quiz_questions_for_report,
    methods= ["GET"]
)
project.register_blueprint(blueprint= reports_app.reports_app)

host_app.host_app.add_url_rule(
    rule = '/host/<int:quizid>',
    view_func = host_app.render_host_app,
    methods= ["POST", "GET"]
)
host_app.host_app.add_url_rule(
    rule = '/hosting/<code>/',
    view_func = host_app.render_hosting_quiz,
    methods= ["POST", "GET"]
)
project.register_blueprint(blueprint = host_app.host_app) 

classroom_app.classroom_app.add_url_rule(
    rule= '/',
    view_func= classroom_app.render_classrooms,
    methods= ["POST", "GET"]
)

classroom_app.classroom_app.add_url_rule(
    rule= '/<int:id>',
    view_func= classroom_app.render_classroom,
    methods= ["POST", "GET"]
)

classroom_app.classroom_app.add_url_rule(
    rule= '/courses/<int:id>',
    view_func= classroom_app.render_course,
    methods= ["POST", "GET"]
)

classroom_app.classroom_app.add_url_rule(
    rule= '/get-student-info/<int:id_student>/<int:id_classroom>',
    view_func= classroom_app.get_data_login_student,
    methods= ["GET"]
)

classroom_app.classroom_app.add_url_rule(
    rule= '/get-login-data-students/<int:id>',
    view_func= classroom_app.get_login_passwords_data_students,
    methods= ["GET"]
)

classroom_app.classroom_app.add_url_rule(
    rule= "/student/<int:id>",
    view_func= classroom_app.render_student_information,
    methods = ["GET", "POST"]
)

classroom_app.classroom_app.add_url_rule(
    rule= "/class_stats/<int:id>",
    view_func= classroom_app.get_class_stats,
    methods = ["GET"]
)

project.register_blueprint(
    blueprint= classroom_app.classroom_app,
    url_prefix= "/classrooms/"
)

student_app.student_app.add_url_rule(
    rule="/",
    view_func= student_app.render_home_page,
    methods= ["GET"]
)
student_app.student_app.add_url_rule(
    rule="/statistic",
    view_func= student_app.render_statistic_page,
    methods= ["GET"]
)
student_app.student_app.add_url_rule(
    rule="/my-classroom",
    view_func= student_app.render_classroom_page,
    methods= ["GET"]
)
student_app.student_app.add_url_rule(
    rule="/me",
    view_func= student_app.render_profile_page,
    methods= ["GET"]
)

student_app.student_app.add_url_rule(
    rule = '/report/<hash_code>',
    view_func = student_app.report_view,
    methods = ["GET", "POST"]
)
student_app.student_app.add_url_rule(
    rule="/api/student_stats/<int:student_id>",
    view_func= student_app.get_student_stats,
    methods = ["GET", "POST"]
)
student_app.student_app.add_url_rule(
    rule="/get_active_quizes/<int:classroom_id>",
    view_func= student_app.get_active_quizes,
    methods = ["GET"]
)

project.register_blueprint(
    blueprint= student_app.student_app,
    url_prefix= "/student/"
)