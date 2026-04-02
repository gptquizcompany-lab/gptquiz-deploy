import flask

student_app = flask.Blueprint(
    name= 'student_app',
    import_name= 'student_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/student/'
)