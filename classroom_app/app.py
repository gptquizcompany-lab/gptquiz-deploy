import flask

classroom_app = flask.Blueprint(
    name= 'classroom_app',
    import_name= 'classroom_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/classroom/'
)