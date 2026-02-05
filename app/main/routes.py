from flask import render_template, g, session, current_app, flash, redirect, url_for
from ..utils import read_json, ensure_json_file
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

@bp.app_context_processor
def inject_user():
    return dict(current_user=g.current_user)

@bp.route('/')
def index():
    users = read_json(current_app.config['USERS_JSON'])
    posts = read_json(current_app.config['POSTS_JSON'])
    
    # Enrich posts with author info
    for p in posts:
        author = next((u for u in users if u['id'] == p.get('author_id')), None)
        p['author_nick'] = author['nickname'] if author else 'Anônimo'
        p['author_image'] = author['profile_image'] if author and author.get('profile_image') else ''
        
    tags = read_json(current_app.config['TAGS_JSON'])
    return render_template('index.html', posts=posts, tags=tags)

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

@bp.route('/profile')
def profile():
    """
    Rota para visualizar o próprio perfil (privado).
    
    Funcionalidades:
    - Verifica se usuário está logado
    - Carrega dados do usuário logado
    - Carrega posts e estatísticas
    - Renderiza template de perfil em modo edição
    """
    if not g.current_user:
        flash('Faça login para ver seu perfil', 'warning')
        return redirect(url_for('auth.login'))

    target = g.current_user
    posts = read_json(current_app.config['POSTS_JSON'])
    comments = read_json(current_app.config['COMMENTS_JSON'])

    # contagem de comentários por post
    comment_counts = {}
    for c in comments:
        pid = c.get('post_id')
        if pid:
            comment_counts[pid] = comment_counts.get(pid, 0) + 1

    user_posts = [p for p in posts if p.get('author_id') == target.get('id')]
    # ordena do mais recente
    user_posts.sort(key=lambda p: p.get('created_at', ''), reverse=True)

    for p in user_posts:
        p['author_nick'] = target['nickname']
        p['author_image'] = target.get('profile_image', '').replace('\\','/') if target.get('profile_image') else ''
        p['comments_count'] = comment_counts.get(p['id'], 0)
        if 'likes' not in p:
            p['likes'] = []
        if p.get('image_path'):
            p['image_path'] = p['image_path'].replace('\\', '/')

    is_owner = True
    # prepara joined_date
    created = target.get('created_at', '')
    joined_date = ''
    if created:
        tokens = created.replace(',', ' ').split()
        slash_date = next((t for t in tokens if t.count('/') == 2), None)
        if slash_date:
            joined_date = slash_date
        else:
            base = created.split(' ')[0]
            base = base.split('T')[0]
            if base.count('-') == 2:
                y, m, d = base.split('-')
                if len(d) >= 2:
                    d = d[:2]
                joined_date = f"{d}/{m}/{y}"
            else:
                joined_date = created

    return render_template('profile.html', user=target, posts=user_posts, is_owner=is_owner, joined_date=joined_date)


@bp.route('/games')
def games():
    """
    Rota da página de jogos educativos sobre meio ambiente.
    
    Funcionalidades:
    - Requer autenticação (usuários não logados são redirecionados para login)
    - Carrega lista de jogos do arquivo games.json
    - Exibe jogos interativos embarcados (iframes) de plataformas educativas
    - Jogos incluem quiz, caça-palavras, memória, palavras cruzadas sobre sustentabilidade
    """
    # Restrição: apenas usuários autenticados podem acessar a página de jogos
    if 'user_id' not in session:
        return redirect(url_for('auth.login', reason='Faça login para acessar os jogos'))
    
    # Carrega lista de jogos do JSON
    ensure_json_file(current_app.config['GAMES_JSON'])
    games_list = read_json(current_app.config['GAMES_JSON'])
    
    return render_template('games.html', games=games_list)

@bp.route('/coming-soon')
def coming_soon():
    return render_template('coming_soon.html')