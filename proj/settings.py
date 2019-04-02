import os

from .admin_model import BASE_DIR


class Config:
    APP_ID = '2016092500594415'
    NOTIFY_URL = 'http://172.96.198.74:5000/process_pay'  # 回调商家地址
    RETURN_URL = 'http://172.96.198.74:5000/callback'  # 用户转跳界面
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'hyhy'
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = -1
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PORT = 5000
    STATIC_DIR = os.path.join(BASE_DIR, 'static')


class ProductionConfig(Config):
    pass


class ServerConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    INDEX_URL = 'http://172.96.198.74:5000'

    CELERY_BROKER = 'redis://127.0.0.1:6379/1'
    CELERY_BACKEND = 'redis://127.0.0.1:6379:6379/2'
    REDIS_URL = "redis://127.0.0.1:6379:6379/0"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://yuanzhu:123456@127.0.0.1:3306/hy?charset=utf8"


class LocalTestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://yuanzhu:123456@172.96.198.74:3306/hy?charset=utf8"
    CELERY_BROKER = 'redis://172.96.198.74:6379/1'
    CELERY_BACKEND = 'redis://172.96.198.74:6379/2'
    REDIS_URL = "redis://172.96.198.74:6379/0"
    DEBUG = True
    HOST = '127.0.0.1'
    INDEX_URL = 'http://127.0.0.1:5000'
