from flask import Flask

from app.config import Config


def create_app(config_class: Config = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import main
    app.register_blueprint(main)

    return app
