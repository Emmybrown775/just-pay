import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
