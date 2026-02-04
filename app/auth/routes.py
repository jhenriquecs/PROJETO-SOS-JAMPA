from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, datetime
from ..utils import read_json, append_json, ensure_json_file, upload_image_local, write_json
from . import bp

def user_by_email(email):
    """
    Busca um usuário pelo endereço de email no banco de dados.
    
    Args:
        email: Endereço de email a ser buscado (case-insensitive)
        
    Returns:
        Dicionário com dados do usuário se encontrado, None caso contrário
    """
    users = read_json(current_app.config['USERS_JSON'])
    for u in users:
        if u['email'].lower() == email.lower():
            return u
    return None

@bp.before_request
def ensure_files():
    """
    Executado antes de cada requisição neste Blueprint.
    Garante que todos os arquivos de dados (JSON e CSV) necessários existam.
    """
    ensure_json_file(current_app.config['USERS_JSON'])
    ensure_json_file(current_app.config['POSTS_JSON'])

@bp.route('/register', methods=['GET','POST'])
def register():
    """
    Rota de Cadastro de Usuário.
    GET: Exibe o formulário de registro.
    POST: Processa o novo cadastro.
    - Valida senhas e existência do email.
    - Cria hash da senha.
    - Salva novo usuário em users.json.
    """
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pwd = request.form['senha']
        confirm_pwd = request.form['confirmar_senha']
        nome = request.form.get('nome', '')
        nickname = request.form.get('nome_usuario', email.split('@')[0])
        
        # Validação
        if pwd != confirm_pwd:
            flash('As senhas não correspondem', 'error')
            return redirect(url_for('auth.register'))
        
        if user_by_email(email):
            flash('Email já cadastrado', 'error')
            return redirect(url_for('auth.register'))
        
        uid = str(uuid.uuid4())
        password_hash = generate_password_hash(pwd)
        brasilia_tz = datetime.timezone(datetime.timedelta(hours=-3))
        row = {
            'id': uid,
            'email': email,
            'password_hash': password_hash,
            'nickname': nickname,
            'nome': nome,
            'is_admin': False,
            'profile_image': '',
            'created_at': datetime.datetime.now(brasilia_tz).strftime('%H:%M:%S %d/%m/%Y')
        }
        append_json(current_app.config['USERS_JSON'], row)
        flash('Conta criada! Faça login', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    """
    Rota de autenticação de usuários no sistema.
    
    GET: Exibe o formulário de login
    POST: Processa a autenticação do usuário
        - Verifica se o email está banido no arquivo CSV
        - Valida credenciais (email e senha)
        - Cria sessão com dados do usuário (ID, email, nickname, admin status)
        - Redireciona para a página inicial em caso de sucesso
    """
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pwd = request.form['password']
        is_banned = False
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
                    parts = line.split(',', 1)
                    if len(parts) > 0 and parts[0].strip().lower() == email:
                        is_banned = True
                        break
        except FileNotFoundError:
            is_banned = False
        except (IOError, Exception) as e:
            print(f"[ERRO] Falha ao verificar banimento: {e}")
            is_banned = False

        if is_banned:
            flash('Conta banida. Contate suporte através do email: sos.jpa@gmail.com', 'error')
            return redirect(url_for('auth.login'))
        user = user_by_email(email)
        if not user or not check_password_hash(user['password_hash'], pwd):
            flash('Credenciais inválidas', 'error')
            return redirect(url_for('auth.login'))
        
        session.clear()
        session['user_id'] = user['id']
        session['is_admin'] = bool(user.get('is_admin', False))
        session['nickname'] = user['nickname']
        session['email'] = user['email']
        session['profile_image'] = user.get('profile_image', '')
        flash('Logado com sucesso', 'success')
        return redirect(url_for('main.index'))
    # GET: opcionalmente mostra um aviso vindo por querystring
    reason = (request.args.get('reason') or '').strip()
    if reason:
        flash(reason, 'error')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """
    Rota de desconexão do usuário.
    Limpa todos os dados da sessão e redireciona para a página inicial.
    """
    session.clear()
    flash('Desconectado', 'info')
    return redirect(url_for('main.index'))

@bp.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    file = request.files.get('profile_image')
    
    if not file or not file.filename:
        flash('Nenhuma imagem selecionada.', 'error')
        return redirect(url_for('main.profile'))

    users = read_json(current_app.config['USERS_JSON'])
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Upload local
    new_url = upload_image_local(file, user_id, 'profile', user.get('profile_image'))
    
    if new_url:
        user['profile_image'] = new_url
        write_json(current_app.config['USERS_JSON'], users)
        session['profile_image'] = new_url # Atualiza sessão
        flash('Foto de perfil atualizada!', 'success')
    else:
        flash('Erro ao salvar imagem.', 'error')

    return redirect(url_for('main.profile'))

@bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    users = read_json(current_app.config['USERS_JSON'])
    user = next((u for u in users if u['id'] == user_id), None)

    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Update info
    nome = request.form.get('nome', '').strip()
    nickname = request.form.get('nickname', '').strip()
    
    if nome:
        user['nome'] = nome
    if nickname:
        # Check uniqueness if changed
        if nickname.lower() != user['nickname'].lower():
            # simple check
            exists = any(u for u in users if u['nickname'].lower() == nickname.lower() and u['id'] != user_id)
            if exists:
                flash(f'O nickname @{nickname} já está em uso.', 'error')
                return redirect(url_for('main.profile'))
        user['nickname'] = nickname
        session['nickname'] = nickname

    # Cover image
    cover_file = request.files.get('cover_image')
    if cover_file and cover_file.filename:
         new_cover = upload_image_local(cover_file, user_id, 'cover', user.get('cover_image'))
         if new_cover:
             user['cover_image'] = new_cover

    write_json(current_app.config['USERS_JSON'], users)
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('main.profile'))