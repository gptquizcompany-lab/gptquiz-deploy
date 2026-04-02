import flask

home_app = flask.Blueprint(
    name= 'home_app',
    import_name= 'home_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/home/'
)