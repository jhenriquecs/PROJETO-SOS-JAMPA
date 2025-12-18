from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, datetime
from ..utils_json import read_json, append_json, ensure_json_file
from . import bp

def user_by_email(email):
    """
    Busca um usuário pelo email no arquivo users.json.
    Retorna o dicionário do usuário ou None se não encontrar.
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
    Rota de Login.
    GET: Exibe o formulário de login.
    POST: Autentica o usuário.
    - Verifica banimento.
    - Valida email e senha.
    - Cria sessão do usuário.
    """
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pwd = request.form['password']
        user = user_by_email(email)
        if not user or not check_password_hash(user['password_hash'], pwd):
            flash('Credenciais inválidas', 'error')
            return redirect(url_for('auth.login'))

        session.clear()
        session['user_id'] = user['id']
        session['is_admin'] = bool(user.get('is_admin', False))
        session['nickname'] = user['nickname']
        session['email'] = user['email']
        flash('Logado com sucesso', 'success')
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """
    Rota de Logout.
    Encerra a sessão do usuário e redireciona para a Home.
    """
    session.clear()
    flash('Desconectado', 'info')
    return redirect(url_for('main.index'))
