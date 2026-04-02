import flask
from library_app.models import Quiz
from project.decorators import login_required, teacher_required

@login_required
@teacher_required
def render_admin_page():
    quizes= Quiz.query.filter(Quiz.is_draft == False).order_by(Quiz.id.desc()).all()

    return flask.render_template(
        template_name_or_list= 'admin.html',
        quizes = quizes,
        main_page = True
    )

def search():
    data = flask.request.get_json()
    search_text = data.get('search', '')

    quizes = Quiz.query.filter(Quiz.is_draft == False)

    if search_text:
        quizes = quizes.filter(Quiz.name.ilike(f'%{search_text}%'))

    quizes = quizes.order_by(Quiz.id.desc()).all()
    
    return flask.jsonify([q.to_dict() for q in quizes])