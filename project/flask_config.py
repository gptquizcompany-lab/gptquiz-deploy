from dotenv import load_dotenv
import flask_mail, os
from .settings import project

load_dotenv()


project.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
project.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
project.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
project.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
project.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
project.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = flask_mail.Mail(project)

# This is a workaround to prevent ngrok's browser warning when using ngrok for local development.
# Will be removed in production. Only needed for development and testing by some users.
@project.after_request
def add_header(response):
    response.headers['ngrok-skip-browser-warning'] = '1'
    return response