from flask import request, render_template, redirect, url_for, flash, current_app, session, jsonify, g
from ..utils import read_json, append_json, ensure_json_file, write_json
import uuid, datetime
from . import bp

# bp = Blueprint('posts', __name__)

def login_required():
    """
    Verifica se o usuário está autenticado na aplicação.
    
    Retorna:
        bool: True se 'user_id' existe na sessão, False caso contrário
    """
    return 'user_id' in session

@bp.before_request
def ensure_files():
    """
    Hook executado antes de cada requisição no blueprint de posts.
    Garante a existência dos arquivos de dados posts.json e comments.json.
    """
    ensure_json_file(current_app.config['POSTS_JSON'])
    ensure_json_file(current_app.config['COMMENTS_JSON'])

@bp.route('/create', methods=['GET','POST'])
def create_post():
    """
    Rota para criar uma nova denúncia/postagem no sistema.
    
    GET: Redireciona para a página inicial (formulário fica no modal da home)
    POST: Processa a criação da nova denúncia
        - Valida autenticação do usuário
        - Recebe descrição, endereço e tag do órgão responsável
        - Faz upload da foto da denúncia (se enviada)
        - Gera ID único e timestamp no fuso de Brasília (UTC-3)
        - Salva denúncia em posts.json
        - Exibe mensagem com dados de contato do órgão responsável
        - Redireciona para a página de visualização da denúncia
    """
    if not login_required():
        flash('Faça login para criar denúncia', 'error')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        desc = request.form.get('description','').strip()
        address = request.form.get('address','').strip()
        tag_id = request.form.get('tag_id')
        
        # Obter detalhes da tag
        tags_data = read_json(current_app.config['TAGS_JSON'])
        selected_tag = next((t for t in tags_data if t['id'] == tag_id), None)
        
        tag_name = selected_tag['name'] if selected_tag else ''
        tag_msg = ""
        if selected_tag:
            phone = selected_tag.get('phone', '')
            # Formata o telefone se estiver apenas números e tiver 11 dígitos
            # Ex: 83999999999 -> (83) 99999-9999
            import re
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 11:
                phone = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
                
            tag_msg = f" Contate o órgão responsável: Email: {selected_tag.get('email')} / Tel: {phone}"
        
        f = request.files.get('image')
        imgpath = ''
        if f and f.filename:
            from app.utils import upload_image_local
            imgpath = upload_image_local(f, session['user_id'], 'posts') or ''
        pid = str(uuid.uuid4())
        # Horário de Brasília (UTC-3)
        brasilia_tz = datetime.timezone(datetime.timedelta(hours=-3))
        timestamp = datetime.datetime.now(brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')
        row = {
            'id': pid,
            'author_id': session['user_id'],
            'image_path': imgpath,
            'description': desc,
            'address': address,
            'created_at': timestamp,
            'tags': tag_name, # Salvando o nome para compatibilidade
            'tag_id': tag_id
        }
        append_json(current_app.config['POSTS_JSON'], row)
        flash(f'Denúncia criada.{tag_msg}', 'info')
        return redirect(url_for('posts.view_post', post_id=pid))
    # Se for GET, redireciona para a home onde está o formulário
    return redirect(url_for('main.index'))

@bp.route('/<post_id>', methods=['GET','POST'])
def view_post(post_id):
    """
    Rota para visualizar os detalhes completos de uma denúncia específica.
    
    Args:
        post_id: ID único da denúncia (UUID)
    
    GET: Exibe a denúncia com todos os comentários
        - Carrega dados da denúncia e do autor
        - Carrega informações da tag/órgão responsável
        - Lista todos os comentários com dados dos autores
        - Conta quantidade de curtidas e comentários
        
    POST: Adiciona um novo comentário na denúncia
        - Valida autenticação do usuário
        - Gera ID e timestamp para o comentário
        - Salva comentário em comments.json
        - Redireciona de volta para a página da denúncia
    """
    posts = read_json(current_app.config['POSTS_JSON'])
    post = next((p for p in posts if p['id']==post_id), None)
    if not post:
        flash('Post não encontrado', 'error')
        return redirect(url_for('main.index'))
    users = read_json(current_app.config['USERS_JSON'])
    author = next((u for u in users if u['id']==post['author_id']), None)
    post['author_nick'] = author['nickname'] if author else 'Anônimo'
    post['author_image'] = author['profile_image'].replace('\\','/') if author and author.get('profile_image') else ''
    comments = [c for c in read_json(current_app.config['COMMENTS_JSON']) if c['post_id']==post_id]
    
    # Prepara dados para o post_card
    post['comments_count'] = len(comments)
    if 'likes' not in post:
        post['likes'] = []
    if post.get('image_path'):
        post['image_path'] = post['image_path'].replace('\\', '/')

    # Carrega dados da tag se o post tiver tag_id
    post['tag_info'] = None
    if post.get('tag_id'):
        tags = read_json(current_app.config['TAGS_JSON'])
        tag = next((t for t in tags if t['id'] == post['tag_id']), None)
        if tag:
            post['tag_info'] = tag

    for c in comments:
        u = next((x for x in users if x['id']==c['author_id']), None)
        c['author_nick'] = u['nickname'] if u else 'Anônimo'
        c['author_image'] = u['profile_image'].replace('\\','/') if u and u.get('profile_image') else ''
    if request.method == 'POST':
        if not login_required():
            flash('Faça login para comentar', 'error')
            return redirect(url_for('auth.login'))
        text = request.form.get('comment','').strip()
        if text:
            cid = str(uuid.uuid4())
            # Horário de Brasília (UTC-3)
            brasilia_tz = datetime.timezone(datetime.timedelta(hours=-3))
            timestamp = datetime.datetime.now(brasilia_tz).strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'id': cid,
                'post_id': post_id,
                'author_id': session['user_id'],
                'text': text,
                'created_at': timestamp
            }
            append_json(current_app.config['COMMENTS_JSON'], row)
            flash('Comentário adicionado', 'success')
            return redirect(url_for('posts.view_post', post_id=post_id))
    return render_template('post_view.html', post=post, comments=comments, current_user=g.current_user)

@bp.route('/list')
def list_posts():
    """
    Rota para listar denúncias com filtros de busca e tags.
    
    Query Parameters:
        q: Termo de busca (busca em descrição, endereço e tags)
        tag: Filtro por tag específica
    
    Funcionalidades:
        - Aplica filtros de busca textual (case-insensitive)
        - Filtra por tag selecionada
        - Ordena resultados do mais recente para o mais antigo
        - Enriquece cada post com dados do autor
        - Normaliza caminhos de imagens
        - Renderiza feed com resultados filtrados
    """
    q = request.args.get('q','').lower()
    tag = request.args.get('tag','').lower()
    posts = read_json(current_app.config['POSTS_JSON'])
    users = read_json(current_app.config['USERS_JSON'])
    if q:
        posts = [p for p in posts if q in (p.get('description','') or '').lower() or q in (p.get('address','') or '').lower() or q in (p.get('tags','') or '').lower()]
    if tag:
        posts = [p for p in posts if tag in (p.get('tags','') or '').lower()]
    posts.sort(key=lambda p: p.get('created_at',''), reverse=True)
    for p in posts:
        author = next((u for u in users if u['id']==p['author_id']), None)
        p['author_nick'] = author['nickname'] if author else 'Anônimo'
        p['author_image'] = author['profile_image'].replace('\\','/') if author and author.get('profile_image') else ''
        # Normaliza image_path para usar / em vez de \
        if p.get('image_path'):
            p['image_path'] = p['image_path'].replace('\\', '/')
    return render_template('index.html', posts=posts)

@bp.route('/like/<post_id>', methods=['POST'])
def toggle_like(post_id):
    """
    Endpoint API para curtir ou descurtir uma denúncia.
    
    Args:
        post_id: ID único da denúncia (UUID)
    
    Funcionalidades:
        - Valida autenticação (retorna 401 se não logado)
        - Adiciona user_id à lista de likes se ainda não curtiu
        - Remove user_id da lista de likes se já tinha curtido (toggle)
        - Salva mudanças em posts.json
        - Retorna JSON com nova contagem de likes e status (liked: true/false)
    
    Returns:
        JSON: {'likes_count': int, 'liked': bool} ou {'error': str}
    """
    if not login_required():
        return jsonify({
            'error': 'Login required',
            'redirect': url_for('auth.login', reason='Você precisa estar logado para curtir posts.')
        }), 401
    
    user_id = session['user_id']
    posts = read_json(current_app.config['POSTS_JSON'])
    
    post_index = next((i for i, p in enumerate(posts) if p['id'] == post_id), None)
    if post_index is None:
        return jsonify({'error': 'Post not found'}), 404
    
    post = posts[post_index]
    if 'likes' not in post:
        post['likes'] = []
        
    liked = False
    if user_id in post['likes']:
        post['likes'].remove(user_id)
        liked = False
    else:
        post['likes'].append(user_id)
        liked = True
        
    write_json(current_app.config['POSTS_JSON'], posts)
    
    return jsonify({
        'likes_count': len(post['likes']),
        'liked': liked
    })

@bp.route('/delete/<post_id>', methods=['POST'])
def delete_post(post_id):
    """
    Rota para excluir uma denúncia do sistema.
    
    Args:
        post_id: ID único da denúncia (UUID)
    
    Funcionalidades:
        - Valida autenticação do usuário
        - Verifica permissões (apenas autor ou admin podem deletar)
        - Remove arquivo de imagem do servidor (se existir)
        - Remove denúncia de posts.json
        - Remove todos os comentários associados de comments.json
        - Redireciona para a página inicial
    """
    if not login_required():
        flash('Login necessário', 'error')
        return redirect(url_for('auth.login'))
    
    posts = read_json(current_app.config['POSTS_JSON'])
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if not post:
        flash('Post não encontrado', 'error')
        return redirect(url_for('main.index'))
        
    # Verifica permissões
    is_author = post['author_id'] == session['user_id']
    is_admin = session.get('is_admin', False)
    
    if not (is_author or is_admin):
        flash('Você não tem permissão para excluir este post', 'error')
        return redirect(url_for('main.index'))
        
    # Deleta imagem se existir
    if post.get('image_path'):
        try:
            # image_path ex: "uploads/post/arquivo.jpg"
            full_path = os.path.join(current_app.static_folder, post['image_path'])
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Erro ao deletar imagem: {e}")
            
    # Remove post
    posts = [p for p in posts if p['id'] != post_id]
    write_json(current_app.config['POSTS_JSON'], posts)
    
    # Remove comentários órfãos
    comments = read_json(current_app.config['COMMENTS_JSON'])
    new_comments = [c for c in comments if c['post_id'] != post_id]
    if len(comments) != len(new_comments):
        write_json(current_app.config['COMMENTS_JSON'], new_comments)
    
    flash('Post excluído com sucesso', 'success')
    
    # Redirecionamento inteligente
    next_page = request.args.get('next') or request.form.get('next')
    if next_page:
        return redirect(next_page)
        
    return redirect(url_for('main.index'))

@bp.route('/comment/<comment_id>/delete', methods=['DELETE', 'POST'])
def delete_comment_api(comment_id):
    """
    Endpoint API para excluir um comentário.
    
    Args:
        comment_id: ID único do comentário (UUID)
    
    Funcionalidades:
        - Valida autenticação (retorna 401 se não logado)
        - Verifica permissões (apenas autor ou admin podem deletar)
        - Remove comentário de comments.json
        - Retorna JSON de sucesso ou erro
    
    Returns:
        JSON: {'success': True} ou {'error': str}
    """
    if not login_required():
        return jsonify({
            'error': 'Login required',
            'redirect': url_for('auth.login', reason='Você precisa estar logado para excluir comentários.')
        }), 401
        
    comments = read_json(current_app.config['COMMENTS_JSON'])
    comment = next((c for c in comments if c['id'] == comment_id), None)
    
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
        
    is_author = comment['author_id'] == session['user_id']
    is_admin = session.get('is_admin', False)
    
    if not (is_author or is_admin):
        return jsonify({'error': 'Permission denied'}), 403
        
    comments = [c for c in comments if c['id'] != comment_id]
    write_json(current_app.config['COMMENTS_JSON'], comments)
    
    return jsonify({'success': True})

@bp.route('/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Endpoint API para buscar todos os comentários de uma denúncia.
    
    Args:
        post_id: ID único da denúncia (UUID)
    
    Funcionalidades:
        - Filtra comentários pelo post_id
        - Enriquece cada comentário com dados do autor
        - Determina se usuário atual pode deletar cada comentário
        - Retorna lista em formato JSON
    
    Returns:
        JSON: Lista de comentários com campos: id, post_id, text, created_at, 
              author_id, author_nick, author_image, can_delete
    """
    comments = read_json(current_app.config['COMMENTS_JSON'])
    users = read_json(current_app.config['USERS_JSON'])
    
    post_comments = [c for c in comments if c['post_id'] == post_id]
    
    current_user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    results = []
    for c in post_comments:
        author = next((u for u in users if u['id'] == c['author_id']), None)
        results.append({
            'id': c['id'],
            'post_id': c['post_id'], # Adicionado para o frontend saber qual post atualizar
            'text': c['text'],
            'created_at': c['created_at'],
            'author_id': c['author_id'],  # Importante para identificar comentários próprios
            'author_nick': author['nickname'] if author else 'Anônimo',
            'author_image': author.get('profile_image', '') if author else '',
            'can_delete': (current_user_id == c['author_id']) or is_admin
        })
        
    return jsonify(results)

@bp.route('/<post_id>/comment', methods=['POST'])
def add_comment_api(post_id):
    """
    Endpoint API para adicionar um comentário via AJAX.
    
    Args:
        post_id: ID único da denúncia (UUID)
    
    Request Body (JSON):
        text: Conteúdo do comentário
    
    Funcionalidades:
        - Valida autenticação (retorna 401 se não logado)
        - Valida que o texto não está vazio
        - Gera ID único e timestamp no fuso de Brasília
        - Salva comentário em comments.json
        - Atualiza contador de comentários no post
        - Retorna JSON com dados completos do novo comentário
    
    Returns:
        JSON: Dados do comentário criado + comments_count atualizado
    """
    if not login_required():
        return jsonify({
            'error': 'Login required',
            'redirect': url_for('auth.login', reason='Você precisa estar logado para comentar.')
        }), 401
        
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Empty comment'}), 400
        
    comments = read_json(current_app.config['COMMENTS_JSON'])
    posts = read_json(current_app.config['POSTS_JSON'])
    
    post_index = next((i for i, p in enumerate(posts) if p['id'] == post_id), None)
    if post_index is None:
        return jsonify({'error': 'Post not found'}), 404
        
    new_comment = {
        'id': str(uuid.uuid4()),
        'post_id': post_id,
        'author_id': session['user_id'],
        'text': text,
        'created_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime('%Y-%m-%d %H:%M:%S')
    }
    comments.append(new_comment)
    write_json(current_app.config['COMMENTS_JSON'], comments)
    
    # Atualiza contador no post (opcional, já que calculamos dinamicamente no index, mas bom manter sincronizado)
    posts[post_index]['comments_count'] = posts[post_index].get('comments_count', 0) + 1
    write_json(current_app.config['POSTS_JSON'], posts)
    
    users = read_json(current_app.config['USERS_JSON'])
    author = next((u for u in users if u['id'] == session['user_id']), None)
    
    return jsonify({
        'id': new_comment['id'],
        'post_id': post_id,
        'text': new_comment['text'],
        'created_at': new_comment['created_at'],
        'author_nick': author['nickname'] if author else 'Anônimo',
        'author_image': author['profile_image'].replace('\\', '/') if author and author.get('profile_image') else '',
        'comments_count': posts[post_index]['comments_count'],
        'can_delete': True # O próprio autor acabou de criar
    })
