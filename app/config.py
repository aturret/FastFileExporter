import os
import tempfile
from typing import Optional

env = os.environ


def get_bool(value: Optional[str], default: bool = True) -> bool:
    true_values = ("True", "true", "1", "yes", "on")
    false_values = ("False", "false", "0", "no", "off")

    if value is None:
        return default
    value = value.lower()

    if value in true_values:
        return True
    elif value in false_values:
        return False
    else:
        return default


def get_env_bool(env, var_name: Optional[str], default: bool = False) -> bool:
    """Retrieve environment variable as a boolean."""
    value = env.get(var_name, "").lower()
    return get_bool(value, default)


class Config:
    LOCAL_MODE = get_bool(env.get("LOCAL_MODE", 'false'), False)
    BASE_URL = env.get("BASE_URL", "localhost:4000")
    PROXY_MODE = get_bool(env.get("PROXY_MODE", 'false'), False)
    PROXY_URL = env.get("PROXY_URL", "http://localhost:4000")
    YOUTUBE_COOKIE = get_bool(env.get("YOUTUBE_COOKIE", 'false'), False)

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
