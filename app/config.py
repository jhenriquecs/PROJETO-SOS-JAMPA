import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Classe de configuração da aplicação.
    Define caminhos de arquivos, chaves secretas e limites de upload.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 's0s_j4mp4_s3cr3t_k3y_t00_5tr0ng_t0_b3_gu3ss3d')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    
    # JSON Files
    # Caminhos para os arquivos de dados JSON
    USERS_JSON = os.path.join(DATA_FOLDER, 'users.json')
    POSTS_JSON = os.path.join(DATA_FOLDER, 'posts.json')
    COMMENTS_JSON = os.path.join(DATA_FOLDER, 'comments.json')
    TAGS_JSON = os.path.join(DATA_FOLDER, 'tags.json')
    
    COLLECTION_POINTS_JSON = os.path.join(DATA_FOLDER, 'collection_points.json')
    WASTES_JSON = os.path.join(DATA_FOLDER, 'wastes.json')
    GAMES_JSON = os.path.join(DATA_FOLDER, 'games.json')
    
    # CSV File (only banned) - caminho relativo sem usar os
    BANNED_CSV = 'app/data/banned.csv'

