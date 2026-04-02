import flask
from flask_socketio import SocketIO
import flask_sqlalchemy
import flask_migrate, os

active_rooms_cache = {}

project = flask.Flask(
    import_name='project',
    template_folder='templates',
    static_folder='static'
)

project.config['SECRET_KEY'] = "secret"

db_url = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

project.config['SQLALCHEMY_DATABASE_URI'] = db_url

project.secret_key = os.environ.get('SECRET_KEY')

DATABASE = flask_sqlalchemy.SQLAlchemy(app=project)
migrate = flask_migrate.Migrate(app=project, db=DATABASE)

socketio = SocketIO(
    app=project,
    async_mode="eventlet",
    ping_timeout=10   
)
with project.app_context():
    DATABASE.create_all()


def background_cache_cleanup(app):
    with app.app_context():
        while True:
            print("Wait for 10 min to clear cache...")
            socketio.sleep(900) 
            print("Cache to clear:", active_rooms_cache)
            active_rooms_cache.clear()
            print("Cleanup: Cache cleared")
