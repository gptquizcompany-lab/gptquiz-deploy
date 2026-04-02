import flask

execution_app = flask.Blueprint(
    name= 'execution_app',
    import_name= 'execution_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/execution/'
)