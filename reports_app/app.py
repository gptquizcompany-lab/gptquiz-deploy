import flask

reports_app = flask.Blueprint(
    name= 'reports_app',
    import_name= 'reports_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/reports/'
)