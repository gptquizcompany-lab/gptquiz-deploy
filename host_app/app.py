import flask

host_app = flask.Blueprint(
    name = "host_app",
    import_name = "host_app",
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/host/",
    
    )