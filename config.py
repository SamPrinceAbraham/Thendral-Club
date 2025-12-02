import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(BASE_DIR / 'instance' / 'thendral.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_MEDIA_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif',
    'mp4', 'mov', 'avi', 'webp'
}


    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'thendral123'

    # Optional email (set MAIL_ENABLED True and configure these)
    MAIL_ENABLED = False
    MAIL_SERVER = ''
    MAIL_PORT = 587
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_USE_TLS = True
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'thendrafriendsclub@gmail.com'
