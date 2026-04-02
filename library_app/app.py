import flask

library_app = flask.Blueprint(
    name= 'library_app',
    import_name= 'library_app',
    template_folder= 'templates',
    static_folder= 'static',
    static_url_path= '/library/'
)