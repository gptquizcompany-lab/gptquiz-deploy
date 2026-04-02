import flask


user_app = flask.Blueprint(
    name= 'user_app',
    import_name= 'user_app',
    static_folder= 'static',
    static_url_path= '/user/',
    template_folder= 'templates'
)