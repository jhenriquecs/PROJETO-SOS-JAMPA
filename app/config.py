import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Classe de configuração da aplicação.
    Define caminhos de arquivos, chaves secretas e limites de upload.
    """
    SECRET_KEY = os.environ.get('SOS_JAMPA_SECRET', 'adivinha_ai_duvido')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    
    # Caminhos para os arquivos de dados JSON
    USERS_JSON = os.path.join(DATA_FOLDER, 'users.json')
    POSTS_JSON = os.path.join(DATA_FOLDER, 'posts.json')

    # Limites para uploads de arquivos
    MAX_PROFILE_MB = 2
    MAX_IMAGE_MB = 5
    MAX_IMAGE_DIM = 1600

    REMEMBER_COOKIE_DURATION = timedelta(days=7)
