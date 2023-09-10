import os
import tempfile

env = os.environ


class Config:

    @staticmethod
    def init_app(app):
        pass
    pass


class DevelopmentConfig(Config):
    DOWNLOAD_DIR = env.get('DOWNLOAD_DIR', tempfile.gettempdir())
    FLASK_ENV = 'development'
    pass


class TestingConfig(Config):
    DOWNLOAD_DIR = env.get('DOWNLOAD_DIR', '/download')
    FLASK_ENV = 'testing'
    pass


class ProductionConfig(Config):
    DOWNLOAD_DIR = env.get('DOWNLOAD_DIR', '/download')
    FLASK_ENV = 'production'
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
