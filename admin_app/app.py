import flask

admin_app = flask.Blueprint(
    name= 'admin_app',
    import_name= 'admin_app',
    static_folder= 'static',
    template_folder= 'templates',
    static_url_path= '/admin/'
)