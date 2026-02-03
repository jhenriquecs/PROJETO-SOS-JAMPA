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

@bp.route('/waste-info')
def waste_info():
    """
    Rota da página de informações sobre descarte de resíduos.
    
    Funcionalidades:
    - Carrega tipos de resíduos do arquivo wastes.json
    - Carrega pontos de coleta do arquivo collection_points.json
    - Agrupa pontos de coleta por tipo de resíduo
    - Associa locais de coleta a cada tipo de resíduo
    - Renderiza página com informações de descarte e mapa de pontos de coleta
    """
    # Carrega pontos de coleta do JSON
    ensure_json_file(current_app.config['COLLECTION_POINTS_JSON'])
    all_points = read_json(current_app.config['COLLECTION_POINTS_JSON'])
    
    # Agrupa pontos por tipo
    points_by_type = {}
    for p in all_points:
        t = p.get('type')
        if t not in points_by_type:
            points_by_type[t] = []
        points_by_type[t].append(p)

    # Carrega dados base dos tipos de resíduos do JSON
    ensure_json_file(current_app.config['WASTES_JSON'])
    wastes = read_json(current_app.config['WASTES_JSON'])
    
    # Adiciona locais de coleta a cada tipo de resíduo
    for waste in wastes:
        waste['locations'] = points_by_type.get(waste['id'], [])
    
    return render_template('waste_info.html', wastes=wastes)