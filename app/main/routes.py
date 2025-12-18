from flask import render_template, g, session, current_app
from ..utils_json import read_json, ensure_json_file
from . import bp

@bp.before_app_request
def load_user():
    g.current_user = None
    ensure_json_file(current_app.config['USERS_JSON'])

    if 'user_id' in session:
        users = read_json(current_app.config['USERS_JSON'])
        user_id = session['user_id']
        me = next((u for u in users if u['id'] == user_id), None)

        if me:
            g.current_user = me
        else:
            session.clear()

@bp.route('/')
def index():
    users = read_json(current_app.config['USERS_JSON'])
    posts = read_json(current_app.config['POSTS_JSON'])
    
    # Enrich posts with author info
    for p in posts:
        author = next((u for u in users if u['id'] == p.get('author_id')), None)
        p['author_nick'] = author['nickname'] if author else 'Anônimo'
        p['author_image'] = author['profile_image'] if author and author.get('profile_image') else ''
        
    return render_template('index.html', posts=posts)
