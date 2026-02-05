import os
import json
import uuid
from werkzeug.utils import secure_filename
from app.config import Config, BASE_DIR

def ensure_json_file(path):
    """
    Garante que o arquivo JSON exista no caminho especificado.
    Se o arquivo não existir, cria um novo com uma lista vazia.
    
    Args:
        path: Caminho completo do arquivo JSON
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def read_json(path):
    """
    Lê e retorna todos os registros de um arquivo JSON.
    
    Args:
        path: Caminho completo do arquivo JSON
        
    Returns:
        Lista com os dados do JSON, ou lista vazia se houver erro
    """
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo local ({path}): {e}")
    return []

def append_json(path, row_dict):
    """
    Adiciona um novo registro ao final do arquivo JSON.
    
    Args:
        path: Caminho completo do arquivo JSON
        row_dict: Dicionário com os dados a serem adicionados
    """
    data = read_json(path)
    data.append(row_dict)
    write_json(path, data)

def write_json(path, data):
    """
    Sobrescreve completamente o arquivo JSON com novos dados.
    
    Args:
        path: Caminho completo do arquivo JSON
        data: Lista ou dicionário a ser salvo no arquivo
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar arquivo local ({path}): {e}")


def _resolve_local_upload_path(image_url):
    """
    Converte uma URL de imagem local para caminho absoluto no sistema de arquivos.
    Remove prefixos como /static/ e static/ da URL.
    
    Args:
        image_url: URL da imagem (ex: /static/uploads/user/profile/image.jpg)
        
    Returns:
        Caminho absoluto no sistema de arquivos, ou None se for URL externa
    """
    if not image_url or image_url.startswith('http'):
        return None
    rel = image_url
    if rel.startswith('/static/'):
        rel = rel[len('/static/'):]
    if rel.startswith('static/'):
        rel = rel[len('static/'):]
    if rel.startswith('/'):
        rel = rel[1:]
    return os.path.join(BASE_DIR, rel)


def upload_image_local(file_storage, user_id, image_type='posts', old_image_url=None):
    """
    Faz upload de uma imagem para o armazenamento local do servidor.
    Salva em app/static/uploads/<user_id>/<tipo>/ com nome único.
    Se houver imagem antiga, remove ela antes de salvar a nova.
    
    Args:
        file_storage: Objeto FileStorage do Flask com o arquivo enviado
        user_id: ID do usuário dono da imagem
        image_type: Tipo da imagem (posts, profile, cover)
        old_image_url: URL da imagem anterior a ser removida (opcional)
        
    Returns:
        Caminho relativo da imagem salva (ex: /static/uploads/user/posts/uuid-file.jpg)
        ou None se não houver arquivo válido
    """
    if not file_storage or not file_storage.filename:
        return None

    clean_name = secure_filename(file_storage.filename)
    filename = f"{uuid.uuid4()}-{clean_name}"
    user_dir = os.path.join(Config.UPLOAD_FOLDER, user_id, image_type)
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, filename)

    # remove imagem antiga se for local
    old_path = _resolve_local_upload_path(old_image_url or '')
    if old_path and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            print(f"Erro ao remover imagem antiga: {e}")

    file_storage.save(file_path)

    static_root = os.path.join(BASE_DIR, 'static')
    rel_path = os.path.relpath(file_path, static_root).replace('\\', '/')
    return f'/static/{rel_path}'
