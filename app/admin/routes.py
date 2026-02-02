from flask import request, current_app, redirect, url_for, flash, session, render_template
from ..utils import read_json, write_json, append_json, ensure_json_file
import datetime
from geopy.geocoders import Nominatim
from . import bp

# bp = Blueprint('admin', __name__)


def admin_required():
    """
    Verifica se o usuário atual possui privilégios administrativos.
    
    Returns:
        bool: True se o usuário é admin, False caso contrário
    """
    return session.get('is_admin', False)

@bp.before_request
def ensure_files():
    """
    Hook executado antes de cada requisição no blueprint administrativo.
    Garante existência de posts.json, comments.json, tags.json e collection_points.json.
    """
    ensure_json_file(current_app.config['POSTS_JSON'])
    ensure_json_file(current_app.config['COMMENTS_JSON'])
    ensure_json_file(current_app.config['TAGS_JSON'])
    ensure_json_file(current_app.config['COLLECTION_POINTS_JSON'])

@bp.route('/')
def dashboard():
    """
    Rota do painel de controle administrativo.
    
    Funcionalidades:
        - Valida privilégios de administrador
        - Carrega lista de usuários do sistema
        - Carrega tags/órgãos responsáveis
        - Lê lista de usuários banidos do arquivo CSV
        - Carrega pontos de coleta
        - Renderiza dashboard com todas as informações para gestão
    """
    if not admin_required():
        flash('Acesso negado', 'error')
        return redirect(url_for('main.index'))
    
    users = read_json(current_app.config['USERS_JSON'])
    all_tags = read_json(current_app.config['TAGS_JSON'])
    banned_users = []
    banned_csv = current_app.config['BANNED_CSV']
    try:
        with open(banned_csv, 'r', newline='', encoding='utf-8') as f:
            lines = f.readlines()
            for line_idx, line in enumerate(lines):
                if line_idx == 0:
                    continue
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) >= 3:
                    email = parts[0].strip()
                    banned_at = parts[-1].strip()
                    reason = ','.join(parts[1:-1]).strip()
                    banned_users.append({
                        'email': email,
                        'reason': reason,
                        'banned_at': banned_at
                    })
    except FileNotFoundError:
        banned_users = []
    except Exception as e:
        print(f"[ERRO] Falha ao ler banimentos: {e}")
    collection_points = read_json(current_app.config['COLLECTION_POINTS_JSON'])

    return render_template('admin_dashboard.html', 
                           users=users, 
                           tags=all_tags, # Changed from user_tags to tags=all_tags for general management
                           banned_users=banned_users,
                           collection_points=collection_points)

@bp.route('/tags/add', methods=['POST'])
def add_tag():
    """
    Rota para adicionar novo órgão responsável/tag.
    Valida permissões, campos obrigatórios, gera ID e salva em tags.json.
    """    
    if not admin_required():
        flash('Acesso negado', 'error')
        return redirect(url_for('main.index'))
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    if not all([name, email, phone]):
        flash('Todos os campos são obrigatórios', 'error')
        return redirect(url_for('admin.dashboard'))

    import uuid
    new_tag = {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'phone': phone
    }
    
    append_json(current_app.config['TAGS_JSON'], new_tag)
    flash('Tag criada com sucesso', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/tags/delete', methods=['POST'])
def delete_tag():
    """Rota para remover um órgão responsável/tag do sistema."""
    if not admin_required():
        flash('Acesso negado', 'error')
        return redirect(url_for('main.index'))
    
    tag_id = request.form.get('tag_id')
    tags = read_json(current_app.config['TAGS_JSON'])
    
    new_tags = [t for t in tags if t['id'] != tag_id]
    
    write_json(current_app.config['TAGS_JSON'], new_tags)
    flash('Tag removida com sucesso', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/collection-point/add', methods=['POST'])
def add_collection_point():
    """
    Rota para adicionar novo ponto de coleta de resíduos.
    Faz geocodificação do endereço (latitude/longitude) usando Nominatim.
    """
    if not admin_required():
        flash('Acesso negado', 'error')
        return redirect(url_for('main.index'))
        
    name = request.form.get('name')
    type_ = request.form.get('type')
    street = request.form.get('street')
    number = request.form.get('number')
    neighborhood = request.form.get('neighborhood')
    
    if not all([name, type_, street, number, neighborhood]):
        flash('Todos os campos são obrigatórios', 'error')
        return redirect(url_for('admin.dashboard'))
        
    import uuid
    
    address_str = f"{street}, {number} - {neighborhood}"
    lat, lon = 0.0, 0.0
    
    try:
        geolocator = Nominatim(user_agent="projeto_pweb_waste_app")
        # Tenta geocodificar o endereço completo. 
        # Adicionando "João Pessoa, PB, Brasil" para melhorar a precisão se for local
        location = geolocator.geocode(f"{address_str}, João Pessoa, PB, Brasil")
        if location:
            lat = location.latitude
            lon = location.longitude
    except Exception as e:
        print(f"Erro ao geocodificar: {e}")

    point = {
        'id': str(uuid.uuid4()),
        'name': name,
        'type': type_,
        'address': address_str,
        'lat': lat,
        'lon': lon
    }
    
    append_json(current_app.config['COLLECTION_POINTS_JSON'], point)
    flash('Ponto de coleta adicionado', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/collection-point/delete', methods=['POST'])
def delete_collection_point():
    """Rota para remover um ponto de coleta do sistema."""
    if not admin_required():
        flash('Acesso negado', 'error')
        return redirect(url_for('main.index'))
        
    point_id = request.form.get('point_id')
    points = read_json(current_app.config['COLLECTION_POINTS_JSON'])
    points = [p for p in points if p['id'] != point_id]
    write_json(current_app.config['COLLECTION_POINTS_JSON'], points)
    
    flash('Ponto de coleta removido', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/ban_user', methods=['POST'])
def ban_user():
    """
    Rota para banir um usuário do sistema.
    
    Funcionalidades:
        - Valida privilégios de admin
        - Impede banimento de outros administradores
        - Valida email do usuário
        - Adiciona registro ao arquivo banned.csv
        - Impede duplo banimento do mesmo email
        - Registra motivo e timestamp do banimento
    """
    
    """
    - Valida email antes de banir.
    - Adiciona o email à lista de banidos (banned.csv).
    """
    if not admin_required():
        flash('Somente admins', 'error')
        return redirect(url_for('main.index'))
    
    email = request.form.get('email', '').strip().lower()
    
    # Validação básica de email
    if not email or '@' not in email:
        flash('Email inválido', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Verificar se o usuário alvo é admin
    users = read_json(current_app.config['USERS_JSON'])
    target_user = next((u for u in users if u['email'].lower() == email), None)
    
    if target_user and target_user.get('is_admin'):
        flash('Não é possível banir um administrador', 'error')
        return redirect(url_for('admin.dashboard'))
    
    reason = request.form.get('reason', '').strip()
    
    banned_csv = current_app.config['BANNED_CSV']
    already_banned = False
    try:
        try:
            with open(banned_csv, 'r', newline='', encoding='utf-8') as f:
                lines = f.readlines()
                for line_idx, line in enumerate(lines):
                    if line_idx == 0:
                        continue
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(',', 1)
                    if len(parts) > 0 and parts[0].strip().lower() == email:
                        already_banned = True
                        break
        except FileNotFoundError:
            with open(banned_csv, 'w', newline='', encoding='utf-8') as f:
                f.write('email,reason,banned_at\n')

        if not already_banned:
            brasilia_tz = datetime.timezone(datetime.timedelta(hours=-3))
            banned_at = datetime.datetime.now(brasilia_tz).strftime('%H:%M:%S %d/%m/%Y')
            reason_safe = (reason or '').strip()[:200].replace('\n', ' ').replace('\r', ' ')
            with open(banned_csv, 'a', newline='', encoding='utf-8') as f:
                f.write(f"{email},{reason_safe},{banned_at}\n")
    except Exception as e:
        print(f"[ERRO] Falha ao adicionar banimento: {e}")
        flash('Usuário já está banido ou erro ao banir', 'warning')
        return redirect(url_for('admin.dashboard'))

    if already_banned:
        flash('Usuário já está banido ou erro ao banir', 'warning')
    else:
        flash(f'Usuário {email} banido com sucesso', 'success')
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/promote_user', methods=['POST'])
def promote_user():
    """
    Rota para promover um usuário comum a administrador.
    Atualiza flag 'is_admin' para True em users.json.
    """
    if not admin_required():
        flash('Somente admins', 'error'); return redirect(url_for('main.index'))
    user_id = request.form.get('user_id')
    users = read_json(current_app.config['USERS_JSON'])
    
    changed = False
    for u in users:
        if u['id'] == user_id:
            u['is_admin'] = True
            changed = True
            break
    
    if changed:
        write_json(current_app.config['USERS_JSON'], users)
        flash('Usuário promovido a admin', 'success')
    else:
        flash('Usuário não encontrado', 'error')
        
    return redirect(url_for('admin.dashboard'))

@bp.route('/demote_user', methods=['POST'])
def demote_user():
    """
    Rota para remover privilégios administrativos de um usuário.
    Impede que um admin remova privilégios de outro admin (proteção).
    Atualiza flag 'is_admin' para False em users.json.
    """
    if not admin_required():
        flash('Somente admins', 'error')
        return redirect(url_for('admin.dashboard'))
        
    user_id = request.form.get('user_id')
    users = read_json(current_app.config['USERS_JSON'])
    
    # Verificar se o usuário alvo é admin
    target_user = next((u for u in users if u['id'] == user_id), None)
    
    if target_user and target_user.get('is_admin'):
        flash('Não é possível remover privilégios de outro administrador', 'error')
        return redirect(url_for('admin.dashboard'))
    
    changed = False
    for u in users:
        if u['id'] == user_id:
            u['is_admin'] = False
            changed = True
            break
            
    if changed:
        write_json(current_app.config['USERS_JSON'], users)
        flash('Privilégios de admin removidos', 'success')
    else:
        flash('Usuário não encontrado', 'error')
        
    return redirect(url_for('admin.dashboard'))

@bp.route('/unban_user', methods=['POST'])
def unban_user():
    """
    Rota para remover banimento de um usuário.
    Lê arquivo banned.csv, remove linha correspondente ao email e reescreve o arquivo.
    """
    if not admin_required():
        flash('Somente admins', 'error')
        return redirect(url_for('main.index'))
    
    email = request.form.get('email', '').strip().lower()
    
    # Validação básica de email
    if not email or '@' not in email:
        flash('Email inválido', 'error')
        return redirect(url_for('admin.dashboard'))
    
    banned_csv = current_app.config['BANNED_CSV']
    removed = False
    try:
        try:
            with open(banned_csv, 'r', newline='', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        lines_to_keep = []
        for line_idx, line in enumerate(lines):
            if line_idx == 0:
                lines_to_keep.append(line)
            else:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                parts = line_stripped.split(',', 1)
                email_in_line = parts[0].strip().lower() if parts else ''
                if email_in_line != email:
                    lines_to_keep.append(line)
                else:
                    removed = True

        if lines_to_keep:
            with open(banned_csv, 'w', newline='', encoding='utf-8') as f:
                f.writelines(lines_to_keep)
    except Exception as e:
        print(f"[ERRO] Falha ao remover banimento: {e}")

    if removed:
        flash(f'Usuário {email} desbanido com sucesso', 'success')
    else:
        flash('Usuário não encontrado na lista de banidos', 'warning')
    
    return redirect(url_for('admin.dashboard'))
